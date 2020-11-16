#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: clipboard_image_functions.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2020-11-11
    Python Version: 3.8
"""

# Script used to import system compatible clipboard image functions
#     since there is no cross-platform way of copying to the clipboard

# Clipboard
try:
    # Try to import Windows clipboard functions
    from src.clipboard_image_functions.clipboard_windows import get_clipboard_image, set_clipboard_image
except (ModuleNotFoundError, OSError):
    try:
        # Try to import GTK clipboard functions, most commonly but not exclusively found on Linux computers
        from src.clipboard_image_functions.clipboard_gtk import get_clipboard_image, set_clipboard_image
    except (ModuleNotFoundError, OSError):
        # Use tkinter only as a fallback since it does not support copying to the clipboard
        from src.clipboard_image_functions.clipboard_tkinter import get_clipboard_image

###


def is_copy_to_clipboard_supported():
    """
    There is no way of copying an image to the clipboard if tkinter has to be used as a fallback. This function test
    whether or not a system compatible function to copy an image to the clipboard has successfully been imported.

    :return: bool: Is there a system compatible way of copying an image to the clipboard?
    """
    try:
        set_clipboard_image
    except NameError:
        # Neither Windows-specific clipboard operations nor GTK-supported clipboard operations are supported
        # Clipboard paste is therefore handled by a built-in tkinter method
        # Copy is however not supported by tkinter
        return False
    else:
        return True
