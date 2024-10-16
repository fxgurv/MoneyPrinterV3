import os
import random
import zipfile
import requests
import platform

from status import *
from config import *

def close_running_selenium_instances() -> None:
    """
    Closes any running Selenium instances.

    Returns:
        None
    """
    try:
        info(" => Closing running Selenium instances...")

        # Kill all running Firefox instances
        if platform.system() == "Windows":
            os.system("taskkill /f /im firefox.exe")
        else:
            os.system("pkill firefox")

        success(" => Closed running Selenium instances.")

    except Exception as e:
        error(f"Error occurred while closing running Selenium instances: {str(e)}")

def build_url(youtube_video_id: str) -> str:
    """
    Builds the URL to the YouTube video.

    Args:
        youtube_video_id (str): The YouTube video ID.

    Returns:
        url (str): The URL to the YouTube video.
    """
    return f"https://www.youtube.com/watch?v={youtube_video_id}"

def rem_temp_files() -> None:
    """
    Removes temporary files in the `tmp` directory.

    Returns:
        None
    """
    # Path to the `tmp` directory
    tmp_dir = os.path.join(ROOT_DIR, "tmp")
    files = os.listdir(tmp_dir)    
#    mp_dir = os.path.join(ROOT_DIR, "tmp")
#    files = os.listdir(mp_dir)
    for file in files:
        if not file.endswith(".json"):
            os.remove(os.path.join(tmp_dir, file))

def fetch_music() -> None:
    """
    Downloads music into music/ directory to use with geneated videos.

    Returns:
        None
    """
    try:
        info(f" => Fetching music...")

        files_dir = os.path.join(ROOT_DIR, "music")
        if not os.path.exists(files_dir):
            os.mkdir(files_dir)
            if get_verbose():
                info(f" => Created directory: {files_dir}")
        else:
            # Skip if music are already downloaded
            return

        # Download music
        response = requests.get(get_zip_url() or "https://filebin.net/bb9ewdtckolsf3sg/drive-download-20240209T180019Z-001.zip")

        # Save the zip file
        with open(os.path.join(files_dir, "music.zip"), "wb") as file:
            file.write(response.content)

        # Unzip the file
        with zipfile.ZipFile(os.path.join(files_dir, "music.zip"), "r") as file:
            file.extractall(files_dir)

        # Remove the zip file
        os.remove(os.path.join(files_dir, "music.zip"))

        success(" => Downloaded music to ../music.")

    except Exception as e:
        error(f"Error occurred while fetching music: {str(e)}")

def choose_random_song() -> str:
    """
    Chooses a random music from the music/ directory.

    Returns:
        str: The path to the chosen music.
    """
    try:
        music = os.listdir(os.path.join(ROOT_DIR, "music"))
        music = random.choice(music)
        success(f" => Chose music: {music}")
        return os.path.join(ROOT_DIR, "music", music)
    except Exception as e:
        error(f"Error occurred while choosing random music: {str(e)}")
