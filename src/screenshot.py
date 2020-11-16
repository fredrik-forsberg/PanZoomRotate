#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: screenshot.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2020-11-11
    Python Version: 3.8
"""

import numpy as np
import cv2
from PIL import ImageGrab

###


def pil_screenshot(all_screens=True):
    """
    Returns a PIL image of what is currently displayed on screen

    :param all_screens: bool: Returns an image containing all screens if True (default=True)
    :return: PIL.Image: Screenshot image
    """
    return ImageGrab.grab(all_screens=all_screens)


def opencv_screenshot(all_screens=True):
    """
    Returns an OpenCV image of what is currently displayed on screen

    :param all_screens: bool: Returns an image containing all screens if True (default=True)
    :return: np.array: OpenCV screenshot image
    """
    return cv2.cvtColor(np.asarray(pil_screenshot(all_screens=all_screens)), cv2.COLOR_RGB2BGR)

###


if __name__ == "__main__":
    img = opencv_screenshot()

    # Show image
    window_name = "imshow"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, img)
    key_code = -1
    try:
        # KeyboardInterrupt works when waitKey is done repeatedly
        while cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) > 0 and key_code == -1:
            key_code = cv2.waitKey(500)
    except KeyboardInterrupt:
        pass
    cv2.destroyWindow(window_name)
