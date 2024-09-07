import os
import time
import sys
import json
import logging
import subprocess
from art import *
from cache import *
from utils import *
from config import *
from status import *
from uuid import uuid4
from constants import *
from classes.Tts import TTS
from termcolor import colored
from classes.YouTube import YouTube
from prettytable import PrettyTable
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, StaleElementReferenceException

# Setup logging
logging.basicConfig(filename='moneyprinter.log', level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Suppress unwanted logs from TTS
logging.getLogger('TTS').setLevel(logging.ERROR)

def click_element(driver, by, value, timeout=10):
    """
    Click an element identified by the given locator.
    
    Args:
    driver: Selenium WebDriver instance
    by: Locator strategy (e.g., By.ID, By.CSS_SELECTOR)
    value: Locator value
    timeout: Maximum time to wait for the element (default: 10 seconds)
    
    Returns:
    True if the element was clicked successfully, False otherwise
    """
    try:
        element = WebDriverWait(driver, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
        element.click()
        return True
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException) as e:
        logger.error(f"Failed to click element: {by}={value}. Error: {str(e)}")
        return False

def setup_youtube_accounts():
    """
    Set up YouTube accounts by creating a JSON file with account information.
    """
    logger.info("Setting up YouTube accounts.")
    print(colored("Setting up YouTube accounts...", "cyan"))
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
        logger.debug("Created tmp directory.")

    firefox_profile_path = get_firefox_profile_path()
    language = get_twitter_language()
    headless = get_headless()

    youtube = YouTube(
        account_uuid=str(uuid4()),
        account_nickname="",
        fp_profile_path=firefox_profile_path,
        niche="",
        language=language
    )

    try:
        youtube.browser.get("https://www.youtube.com")
        logger.info("Navigated to YouTube.")
        print(colored("Navigated to YouTube.", "green"))
        time.sleep(5)

        if not click_element(youtube.browser, By.CSS_SELECTOR, "button[id='avatar-btn']"):
            raise Exception("Failed to click avatar button")

        if not click_element(youtube.browser, By.XPATH, "//yt-formatted-string[contains(text(), 'Switch account')]"):
            raise Exception("Failed to click switch account button")

        time.sleep(5)
        channels_items = WebDriverWait(youtube.browser, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-account-item-renderer[thumbnail-size='48']"))
        )
        logger.info(f"Found {len(channels_items)} YouTube channels.")
        print(colored(f"Found {len(channels_items)} YouTube channels.", "green"))

        accounts = []
        for channel_item in channels_items:
            channel_name = channel_item.find_element(By.CSS_SELECTOR, "yt-formatted-string").text
            logger.info(f"Channel found: {channel_name}")
            print(colored(f"Channel found: {channel_name}", "yellow"))
            niche = input(colored(f"Enter niche for {channel_name}: ", "cyan"))
            account_uuid = str(uuid4())

            accounts.append({
                "id": account_uuid,
                "nickname": channel_name,
                "firefox_profile": firefox_profile_path,
                "niche": niche,
                "language": language,
                "videos": []
            })

        youtube_json_path = "tmp/youtube.json"
        with open(youtube_json_path, "w") as file:
            json.dump({"accounts": accounts}, file, indent=4)
        logger.info(f"Saved accounts to {youtube_json_path}")
        print(colored(f"Saved accounts to {youtube_json_path}", "green"))

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        print(colored(f"An error occurred: {str(e)}", "red"))
    finally:
        youtube.browser.quit()
        logger.info("Closed the browser.")
        print(colored("Closed the browser.", "yellow"))

def get_active_channel_name(youtube):
    """
    Get the name of the currently active YouTube channel.
    
    Args:
    youtube: YouTube instance
    
    Returns:
    The name of the active channel or None if it fails
    """
    try:
        logger.info("Attempting to get active channel name.")
        print(colored("Checking active channel name...", "cyan"))
        if not click_element(youtube.browser, By.CSS_SELECTOR, "button[id='avatar-btn']"):
            raise Exception("Failed to click avatar button")

        active_channel_name = WebDriverWait(youtube.browser, 20).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "yt-formatted-string[id='account-name']"))
        ).text
        logger.info(f"Active channel name: {active_channel_name}")
        print(colored(f"Active channel name: {active_channel_name}", "green"))

        return active_channel_name
    except Exception as e:
        logger.error(f"Failed to get active YouTube channel name: {str(e)}")
        print(colored(f"Failed to get active YouTube channel name: {str(e)}", "red"))
        return None

def switch_account(youtube, account_nickname):
    """
    Switch to a different YouTube account.
    
    Args:
    youtube: YouTube instance
    account_nickname: The nickname of the account to switch to
    
    Returns:
    True if the switch was successful, False otherwise
    """
    try:
        logger.info(f"Attempting to switch to YouTube account: {account_nickname}")
        print(colored(f"Attempting to switch to YouTube account: {account_nickname}", "cyan"))
        if not click_element(youtube.browser, By.XPATH, "//yt-formatted-string[contains(text(), 'Switch account')]"):
            raise Exception("Failed to click switch account button")

        time.sleep(5)
        channels_items = WebDriverWait(youtube.browser, 20).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "ytd-account-item-renderer[thumbnail-size='48']"))
        )
        logger.info(f"Found {len(channels_items)} YouTube channels.")
        print(colored(f"Found {len(channels_items)} YouTube channels.", "yellow"))

        for channel_item in channels_items:
            channel_name = channel_item.find_element(By.CSS_SELECTOR, "yt-formatted-string").text
            if channel_name == account_nickname:
                try:
                    channel_item.click()
                    logger.info(f"Switched to YouTube channel: {account_nickname}")
                    print(colored(f"Successfully switched to YouTube channel: {account_nickname}", "green"))
                    time.sleep(5)
                    return True
                except Exception as e:
                    logger.error(f"Failed to click channel item: {str(e)}")
                    print(colored(f"Failed to click channel item: {str(e)}", "red"))
                    return False

        logger.error(f"Failed to find the YouTube channel: {account_nickname}")
        print(colored(f"Failed to find the YouTube channel: {account_nickname}", "red"))
        return False
    except Exception as e:
        logger.error(f"Failed to switch YouTube channel: {str(e)}")
        print(colored(f"Failed to switch YouTube channel: {str(e)}", "red"))
        return False

def target_channel(youtube, target_channel_name):
    """
    Ensure the target channel is active for video upload.
    
    Args:
    youtube: YouTube instance
    target_channel_name: The name of the target channel for upload
    
    Returns:
    True if the target channel is active, False otherwise
    """
    try:
        logger.info(f"Verifying target channel: {target_channel_name}")
        print(colored(f"Verifying target channel: {target_channel_name}", "cyan"))
        
        current_channel = get_active_channel_name(youtube)
        if current_channel == target_channel_name:
            logger.info(f"Target channel {target_channel_name} is already active.")
            print(colored(f"Target channel {target_channel_name} is already active.", "green"))
            return True
        
        logger.info(f"Switching to target channel: {target_channel_name}")
        print(colored(f"Switching to target channel: {target_channel_name}", "yellow"))
        if switch_account(youtube, target_channel_name):
            time.sleep(5)  # Wait for the switch to complete
            current_channel = get_active_channel_name(youtube)
            if current_channel == target_channel_name:
                logger.info(f"Successfully switched to target channel: {target_channel_name}")
                print(colored(f"Successfully switched to target channel: {target_channel_name}", "green"))
                return True
            else:
                logger.error(f"Failed to switch to target channel: {target_channel_name}")
                print(colored(f"Failed to switch to target channel: {target_channel_name}", "red"))
                return False
        else:
            logger.error(f"Failed to switch to target channel: {target_channel_name}")
            print(colored(f"Failed to switch to target channel: {target_channel_name}", "red"))
            return False
    except Exception as e:
        logger.error(f"Error in target_channel function: {str(e)}")
        print(colored(f"Error in target_channel function: {str(e)}", "red"))
        return False

def process_accounts():
    """
    Process all YouTube accounts, generating and uploading videos.
    """
    while True:
        try:
            with open("tmp/youtube.json", "r") as file:
                accounts = json.load(file)["accounts"]
            logger.info(f"Loaded {len(accounts)} accounts from tmp/youtube.json")
            print(colored(f"Loaded {len(accounts)} accounts from tmp/youtube.json", "cyan"))

            for account in accounts:
                youtube = YouTube(
                    account["id"],
                    account["nickname"],
                    account["firefox_profile"],
                    account["niche"],
                    account["language"]
                )
                logger.info(f"Processing account: {account['nickname']}")
                print(colored(f"Processing account: {account['nickname']}", "yellow"))

                try:
                    tts = TTS()
                    youtube.generate_video(tts)
                    logger.info("Generated video.")
                    print(colored("Generated video.", "green"))

                    youtube.browser.get("https://www.youtube.com")
                    time.sleep(5)

                    if target_channel(youtube, account["nickname"]):
                        youtube.upload_video()
                        logger.info("Uploaded video to YouTube.")
                        print(colored("Uploaded video to YouTube.", "green"))
                    else:
                        logger.error("Failed to set target channel. Skipping upload.")
                        print(colored("Failed to set target channel. Skipping upload.", "red"))

                except Exception as e:
                    logger.error(f"Error processing account {account['nickname']}: {str(e)}")
                    print(colored(f"Error processing account {account['nickname']}: {str(e)}", "red"))

                finally:
                    youtube.browser.quit()
                    logger.info("Closed the browser.")
                    print(colored("Closed the browser.", "yellow"))

            logger.info("All accounts processed. Waiting for 10 minutes before restarting.")
            print(colored("All accounts processed. Waiting for 10 minutes before restarting.", "cyan"))
            for i in range(600, 0, -1):
                sys.stdout.write(f"\rWaiting for {i // 60} minutes and {i % 60} seconds...")
                sys.stdout.flush()
                time.sleep(1)
            print("\n")

        except Exception as e:
            logger.error(f"An error occurred during account processing: {str(e)}")
            print(colored(f"An error occurred during account processing: {str(e)}", "red"))
            time.sleep(60)  # Wait for 1 minute before retrying

if __name__ == "__main__":
    print_banner()
    first_time = get_first_time_running()
    if first_time:
        print(colored("Hey! It looks like you're running MoneyPrinter V2 for the first time. Let's get you setup first!", "yellow"))
        setup_youtube_accounts()

    assert_folder_structure()
    rem_temp_files()
    fetch_songs()

    process_accounts()
