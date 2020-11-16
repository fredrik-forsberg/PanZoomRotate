#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: clipboard_windows.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2020-11-11
    Python Version: 3.8
"""

import numpy as np
import cv2
import win32clipboard

###


def get_clipboard_image():
    """
    Gets an OpenCV image from the Windows clipboard, if there indeed is one

    :return: np.array: OpenCV image from clipboard
             None: No (compatible) image found in the clipboard
    """
    win32clipboard.OpenClipboard()
    if not win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_DIB):
        win32clipboard.CloseClipboard()

    else:
        try:
            image_bytes = win32clipboard.GetClipboardData(win32clipboard.CF_DIB)
        finally:
            win32clipboard.CloseClipboard()

        try:
            if not image_bytes:
                return None
            return cv2.imdecode(np.fromstring(image_bytes, np.uint8), cv2.IMREAD_COLOR)
        except NameError:
            return None


def set_clipboard_image(opencv_image):
    """
    Sets an OpenCV image to the Windows clipboard in jpg-format

    :param opencv_image: np.array: OpenCV image to set to clipboard
    :return: None
    """
    if opencv_image.size == 0:
        return
    win32clipboard.OpenClipboard()
    try:
        win32clipboard.EmptyClipboard()
        image_bytes = cv2.imencode('.jpg', opencv_image)[1].tostring()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, image_bytes)
    finally:
        win32clipboard.CloseClipboard()
