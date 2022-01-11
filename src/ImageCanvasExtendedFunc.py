#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: ImageCanvasExtendedFunc.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2022-01-11
    Python Version: 3.8
"""

import os
import numpy as np
import cv2
import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename
import tkinter.messagebox as messagebox

from src.ImageCanvas import ImageCanvas
from src.pdf_to_image import pdf_to_image

# Clipboard
from src.clipboard_image_functions.clipboard_image_functions import get_clipboard_image, is_copy_to_clipboard_supported
try:
    from src.clipboard_image_functions.clipboard_image_functions import set_clipboard_image
except ImportError:
    def set_clipboard_image(*args): pass

###


class ImageCanvasExtendedFunc(ImageCanvas):

    def __init__(self, parent, pan=True, zoom=True, rotate=True, scroll_factor=1.10, centered_zoom=True,
                 centered_rotation=True, rotate_nonresponsive_radius_fraction=0.05, *args, **kwargs):
        """
        Extended functionality for a custom Tkinter canvas which can display an image and pan, zoom, and rotate said
        display

            Standard functionality from ImageCanvas:
        Pan - Left mouse button
        Zoom - Scroll wheel
        Rotate - Right mouse button

            Extended functionality:
        Zoom - Also using "+" and "-" keys
        Reset view - "R"
        Open image file or PDF-file - Ctrl+O
        Save view as an image file - Ctrl+S
        Paste image from the clipboard - Ctrl+V
        Copy image to the clipboard - Ctrl+C    (If supported by the system)
        Support for displaying text


        :param parent: The tkinter master widget of this ImageCanvas
        :param pan: bool: Enable panning the image using the left mouse button (default=True)
        :param zoom: bool: Enable zooming of the image using the scroll wheel (default=True)
        :param rotate: bool: Enable rotation of the image using the right mouse button (default=True)
        :param scroll_factor: float: By how much the bounding box should increase while zooming out. 1.00 represents
            no zoom what so ever. 1.10 represents a 10% increase. Zooming out will result in a change of the
            boundry box by the factor of the inverse scroll_factor. (default=1.10)
        :param centered_zoom: bool: If True, zooms to the center of the ImageCanvas. If False, zoom to the position of
            the mouse pointer. (default=True)
        :param centered_rotation: bool: If True, rotate around the center of the ImageCanvas. If False, rotate around
            the position of the mouse pointer. (default=True)
        :param rotate_nonresponsive_radius_fraction: float: Determines the radius around the rotation point where
            moving the mouse does not rotate the image. This behaviour is implemented to mitigate the large and sudden
            rotations which occur when a short mouse movement corresponds to a large change in rotational angle.
            The non-responsive radius is calculated as
            radius = min(canvas_width, canvas_height) / 2 * rotate_nonresponsive_radius_fraction,
            where 0. < rotate_nonresponsive_radius_fraction < 1. (default=0.05)
        :param args: Additional arguments passed along to the parental class tkinter.Canvas (aside from the canvas'
            master which is specified seperately in the parameter "parent")
        :param kwargs: Keyword arguments passed along to the parental class tkinter.Canvas. If nothing else is specified
            kwargs['background'] is set to 'black'. However, kwargs['highlightthickness'] is always set to 0,
            kwargs['takefocus'] to True, and kwargs['highlightbackground'] to the same as
            kwargs['background'] no matther which other values are provided.
        """

        super().__init__(parent, pan=pan, zoom=zoom, rotate=rotate, scroll_factor=scroll_factor,
                         centered_zoom=centered_zoom, centered_rotation=centered_rotation,
                         rotate_nonresponsive_radius_fraction=rotate_nonresponsive_radius_fraction, *args, **kwargs)

        self.filechooser_dir = os.path.abspath(os.getcwd())

        self.text_id = -1

        # Events

        self.bind('r', self.callback_reset)
        
        if zoom:
            self.bind_all("+", self.callback_zoom_key)
            self.bind_all("<KP_Add>", self.callback_zoom_key)
            self.bind_all("-", self.callback_zoom_key)
            self.bind_all("<KP_Subtract>", self.callback_zoom_key)

        self.bind_all("<Control-o>", self.callback_open_file)

        self.bind_all("<Control-s>", self.callback_save_file)

        self.bind_all("<Control-v>", self.callback_clipboard_paste)

        # Check if copy to clipboard is supported by the system before assigning it to Ctrl+C
        if is_copy_to_clipboard_supported():
            self.bind_all("<Control-c>", self.callback_clipboard_copy)

    def update(self):
        """
        Removes text if necessary, updates the displayed image, and the Tkinter canvas
        Overrides ImageCanvas.update()

        :return: None
        """
        if self.text_id != -1 and self.image_control.core_image.size > 0:
            self.remove_text()
        super().update()

    def callback_resize(self, event):
        """
        Re-draws text if needed, resizes the image, and updates the canvas when the canvas has been resized
        Overrides ImageCanvas.callback_resize(event)

        :param event: tkinter.Event: Passed along to super().callback_resize(event)
        :return: None
        """
        if self.text_id != -1 and self.image_control.core_image.size == 0:
            text = self.itemcget(self.text_id, 'text')
            self.remove_text()
            self.draw_text(text)
        super().callback_resize(event)

    def callback_reset(self, event=None):
        """
        Resets the view so that the entire image is displayed without rotation

        :param event: tkinter.Event or None: An event argument is needed for tkinter callbacks. Not used. (default=None)
        :return: None
        """
        self.image_control.reset_corners()
        self.update()

    def callback_zoom_key(self, event):
        """
        Zooms using the "+" and "-" keys

        :param event: tkinter.Event: event.char is used to determine if "+" or "-" was pressed
        :return: None
        """
        if event.char == '-':
            factor = 1
        else:  # event.char == '+'
            factor = -1

        if self.centered_zoom:
            center = (self.winfo_width() / 2, self.winfo_height() / 2)
        else:
            center = (event.x, event.y)

        self.image_control.zoom(np.float_power(self.scroll_factor, factor), zoom_center=center)
        self.update()

    def callback_open_file(self, event=None):
        """
        Opens a dialogue window to chose an image file or PDF-file which is then displayed
        Draws text while the image is loading
        Supported file formats: pdf, png, jpg, jpeg, jpe, jp2, gif, tif, tiff, bmp, dib, pbm, pgm, ppm, sr, ras

        :param event: tkinter.Event or None: An event argument is needed for tkinter callbacks. Not used. (default=None)
        :return: None
        """
        image_path = askopenfilename(initialdir=self.filechooser_dir, title='Open image',
                                     filetypes=[('Image files and PDF', ("*.pdf", "*.PDF",
                                                                         "*.png", "*.PNG",
                                                                         "*.jpg", "*.JPG",
                                                                         "*.jpeg", "*.JPEG",
                                                                         "*.jpe", "*.JPE",
                                                                         "*.jp2", "*.JP2",
                                                                         "*.gif", "*.GIF",
                                                                         "*.tif", "*.TIF",
                                                                         "*.tiff", "*.TIFF",
                                                                         "*.bmp", "*.BMP",
                                                                         "*.dib", "*.DIB",
                                                                         "*.pbm", "*.PBM",
                                                                         "*.pgm", "*.PGM",
                                                                         "*.ppm", "*.PPM",
                                                                         "*.sr", "*.SR",
                                                                         "*.ras", "*.RAS"))])

        if image_path and os.path.isfile(image_path):
            self.filechooser_dir = os.path.dirname(image_path)

            self.remove_text()
            self.draw_text('Loading image...')
            self.update()

            if self.read_image_from_path(image_path):
                self.update()
            else:
                if messagebox.askretrycancel(title="Unable to open image",
                                             message="Failed to open image file.\n" +
                                                     "Do you want to open a different image file?"):

                    self.after(1, lambda: self.callback_open_file(None))
                else:
                    self.remove_text()
                    self.draw_text('Failed to open image file')
                    self.update()

    def read_image_from_path(self, image_path):
        """
        Reads an image from either an image file or a PDF-file and displays it

        :param image_path: str: The path to the file which is to be opened
        :return: bool: Indicates success in reading and loading the file
        """
        if image_path.endswith(".pdf") or image_path.endswith(".PDF"):
            try:
                opencv_image = pdf_to_image(image_path, dpi=300, page_index=0, alpha_channel=False)
            except Exception:
                opencv_image = None
        else:
            opencv_image = cv2.imread(image_path)

        if opencv_image is not None:
            self.image_control.load_image(opencv_image)
            self.image_control.reset_corners()
            return True
        else:
            return False

    def draw_text(self, text):
        """
        Draws text in the middle of the canvas
        The font size is 1/26:th of the canvas' height
        Replaces any image or prviously displayed text

        :param text: str: Text to be displayed
        :return: None
        """
        # Text without image in the center
        position = (int(self.winfo_width() / 2), int(self.winfo_height() / 2))
        font_size = int(self.winfo_height() / 26)

        if self.text_id != -1:
            self.delete(self.text_id)

        if text:
            self.text_id = self.create_text(position[0], position[1], text=text,
                                            justify=tk.CENTER, anchor=tk.CENTER, fill="white",
                                            font=('TkDefaultFont', font_size))
        else:
            self.text_id = -1

        if self.image_id != -1 and self.text_id != -1:
            self.image_control.load_image(np.ndarray((0,)))
            self.delete(self.image_id)
            self.image_id = -1

    def remove_text(self):
        """
        Removes any displayed text if there indeed is any

        :return: None
        """
        if self.text_id != -1:
            self.delete(self.text_id)
            self.text_id = -1

    def callback_save_file(self, event=None):
        """
        Opens a dialogue window to chose where to save the displayed image, then saves it
        Supported file formats: png, jpg, jpeg, jpe, jp2, gif, tif, tiff, bmp, dib, pbm, pgm, ppm, sr, ras

        :param event: tkinter.Event or None: An event argument is needed for tkinter callbacks. Not used. (default=None)
        :return: None
        """
        if self.image_control.core_image.size == 0:
            return
        image_path = asksaveasfilename(initialdir=self.filechooser_dir, title='Save image',
                                       filetypes=[('Image files', ("*.png", "*.PNG",
                                                                   "*.jpg", "*.JPG",
                                                                   "*.jpeg", "*.JPEG",
                                                                   "*.jpe", "*.JPE",
                                                                   "*.jp2", "*.JP2",
                                                                   "*.gif", "*.GIF",
                                                                   "*.tif", "*.TIF",
                                                                   "*.tiff", "*.TIFF",
                                                                   "*.bmp", "*.BMP",
                                                                   "*.dib", "*.DIB",
                                                                   "*.pbm", "*.PBM",
                                                                   "*.pgm", "*.PGM",
                                                                   "*.ppm", "*.PPM",
                                                                   "*.sr", "*.SR",
                                                                   "*.ras", "*.RAS"))])

        if image_path:
            new_dir = os.path.dirname(image_path)
            if os.path.isdir(new_dir):
                self.filechooser_dir = new_dir

            if self.write_image_to_path(image_path):
                self.update()
            else:
                if messagebox.askretrycancel(title="Unable to save image",
                                             message="Failed to save image file.\n" +
                                                     "Do you want to try again?"):

                    self.after(1, lambda: self.callback_save_file(None))

    def write_image_to_path(self, image_path):
        """
        Saves the displayed image to an image file

        :param image_path: str: File path to save the displayed image to
        :return: bool: True=Successful, False=Failed
        """
        return cv2.imwrite(image_path, self.image_control.get_image())

    def callback_clipboard_paste(self, event=None):
        """
        Tries to read the clipboard. If it contains an image, then display it.

        :param event: tkinter.Event or None: An event argument is needed for tkinter callbacks. Not used. (default=None)
        :return: None
        """
        img = get_clipboard_image()
        if img is not None:
            self.image_control.load_image(img)
            self.update()

    def callback_clipboard_copy(self, event=None):
        """
        Copies the displayed image into the clipboard (if such an action is supported by the system)

        :param event: tkinter.Event or None: An event argument is needed for tkinter callbacks. Not used. (default=None)
        :return: None
        """
        set_clipboard_image(self.image_control.get_image())
