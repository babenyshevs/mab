import time
from typing import Optional

import pyautogui


def take_screenshot(
    save_path: str,
    left_trim: int = 0,
    right_trim: int = 0,
    top_trim: int = 0,
    bottom_trim: int = 0,
):
    """
    Takes a single screenshot of a specified region on the screen.

    Args:
        save_path (str): The file path to save the screenshot.
        left_trim (int): Number of pixels to trim from the left side of the screenshot.
        right_trim (int): Number of pixels to trim from the right side of the screenshot.
        top_trim (int): Number of pixels to trim from the top of the screenshot.
        bottom_trim (int): Number of pixels to trim from the bottom of the screenshot.

    Example:
        take_screenshot((0, 0, 1920, 1080), 'screenshot.png', left_trim=100, right_trim=50, top_trim=0, bottom_trim=0)
    """
    width, height = pyautogui.size()
    screenshot = pyautogui.screenshot(
        region=(
            left_trim,
            top_trim,
            width - left_trim - right_trim,
            height - top_trim - bottom_trim,
        )
    )
    screenshot.save(save_path)
    print(f"Screenshot saved: {save_path}")
