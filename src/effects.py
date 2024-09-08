# MoneyPrinterV2/effects.py
import math
from PIL import Image
import numpy
from moviepy.editor import CompositeVideoClip

def zoom_in_effect(clip, zoom_ratio=0.04):
    def effect(get_frame, t):
        img = Image.fromarray(get_frame(t))
        base_size = img.size

        new_size = [
            math.ceil(img.size[0] * (1 + (zoom_ratio * t))),
            math.ceil(img.size[1] * (1 + (zoom_ratio * t)))
        ]

        new_size[0] = new_size[0] + (new_size[0] % 2)
        new_size[1] = new_size[1] + (new_size[1] % 2)

        img = img.resize(new_size, Image.LANCZOS)

        x = math.ceil((new_size[0] - base_size[0]) / 2)
        y = math.ceil((new_size[1] - base_size[1]) / 2)

        img = img.crop([
            x, y, new_size[0] - x, new_size[1] - y
        ]).resize(base_size, Image.LANCZOS)

        result = numpy.array(img)
        img.close()

        return result

    return clip.fl(effect)

def slide_in(clip, duration=0.3, side="right"):
    def effect(get_frame, t):
        frame = get_frame(t)
        if side == "right":
            offset = int(clip.w * (1 - t / duration))
            frame = numpy.roll(frame, offset, axis=1)
        elif side == "left":
            offset = int(clip.w * (t / duration - 1))
            frame = numpy.roll(frame, offset, axis=1)
        return frame

    return clip.fl(effect, apply_to=["mask", "video"])

def slide_out(clip, duration=0.3, side="left"):
    def effect(get_frame, t):
        frame = get_frame(t)
        if side == "left":
            offset = int(clip.w * (t / duration))
            frame = numpy.roll(frame, offset, axis=1)
        elif side == "right":
            offset = int(clip.w * (1 - t / duration))
            frame = numpy.roll(frame, offset, axis=1)
        return frame

    return clip.fl(effect, apply_to=["mask", "video"])
