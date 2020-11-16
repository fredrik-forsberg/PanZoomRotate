#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: clipboard_tkinter.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2020-11-11
    Python Version: 3.8
"""

import numpy as np
import cv2
import tkinter as tk

###

# tkinter has currently no way of copying an image to the clipboard
# There is therefore no "set_clipboard_image"-function


def get_clipboard_image(tk_object=None):
    """
    Gets an OpenCV image from the clipboard using tkinter, if there indeed is one

    :param tk_object: Optional tkinter class inheriting from tkinter.Misc (which include widgets and Tk-root)
                      If no object is provided and tkinter has been initiated, then the main default root is used
                      If no object is provided and tkinter has not been initiated, then temporarily initiate tkinter
                      (default=None)
    :return: np.array: OpenCV imageimage from clipboard. Either BGR or BGRA depending on the clipboard image
             None: No (compatible) image found in the clipboard
    """
    temp_tk_root_created = False

    if tk_object is None and tk._default_root is None:
        tk_object = tk.Tk()
        tk_object.withdraw()
        temp_tk_root_created = True

    elif tk_object is None and tk._default_root is not None:
        tk_object = tk._default_root

    try:
        clipboard_content = tk_object.clipboard_get(type='image/png')
    except tk.TclError:
        return None

    if temp_tk_root_created is True:
        tk_object.update()
        tk_object.destroy()

    b = bytearray()

    for x in clipboard_content.split(' '):
        try:
            b.append(int(x, base=16))
        except (TypeError, ValueError):
            pass

    if len(b):
        return cv2.imdecode(np.frombuffer(b, np.uint8), cv2.IMREAD_COLOR)  # Returns None on failiure

###


if __name__ == "__main__":
    clipboard_image = get_clipboard_image()

    if clipboard_image is None:
        print("No image was found on the clipboard and None was returned")

    else:
        print("An OpenCV image with shape " + str(clipboard_image.shape) + " was returned")
