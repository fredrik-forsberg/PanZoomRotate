#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: clipboard_gtk.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2022-01-11
    Python Version: 3.8
"""

# Based on https://python-gtk-3-tutorial.readthedocs.io/en/latest/clipboard.html

import numpy as np
import cv2

import warnings

# GTK
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib


###


def set_clipboard_image(opencv_image, gtk_clipboard=None):
    """
    Sets an OpenCV image to the clipboard using GTK

    :param opencv_image: np.array: OpenCV image to set to clipboard. Either BGR or BGRA
                                   (standard OpenCV colour space, with or without alpha channel (transparency))
    :param gtk_clipboard: Gtk.Clipboard: Optional GTK clipboard to use if provided,
                                         otherwise creates a new one (default=None)
    :return: None
    """
    # Check the image
    if not hasattr(opencv_image, 'shape') or len(opencv_image.shape) != 3 or opencv_image.shape[2] not in [3, 4]:
        return None

    if gtk_clipboard is None:
        gtk_clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    gtk_pixbuf = opencv2pixbuf(opencv_image)

    return gtk_clipboard.set_image(gtk_pixbuf)


def get_clipboard_image(gtk_clipboard=None):
    """
    Gets an OpenCV image from the clipboard using GTK, if there indeed is one

    :param gtk_clipboard: Gtk.Clipboard: Optional GTK clipboard to use if provided,
                                         otherwise creates a new one (default=None)
    :return: np.array: OpenCV image from clipboard. Either BGR or BGRA depending on the clipboard image
             None: No (compatible) image found in the clipboard
    """
    if gtk_clipboard is None:
        gtk_clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)

    gtk_pixbuf = gtk_clipboard.wait_for_image()

    if gtk_pixbuf is None:
        return None

    return pixbuf2opencv(gtk_pixbuf)


def opencv2pixbuf(opencv_image):
    """
    Converts an OpenCV image to a GdkPixbuf.Pixbuf

    :param opencv_image: np.array: OpenCV image to convert. Either BGR or BGRA (standard OpenCV colour space, with or
                                                                                without alpha channel (transparency))
    :return: GdkPixbuf.Pixbuf: Pixbuf representation of the OpenCV image
    """
    # Based on https://stackoverflow.com/a/41714464 by am70
    # Contains a workaround for possible segmentation fault caused by GdkPixbuf.Pixbuf.new_from_data by instead using
    #     GdkPixbuf.Pixbuf.new_from_bytes

    # GdkPixbuf.Pixbuf.new_from_data(data:list, colorspace:GdkPixbuf.Colorspace, has_alpha:bool, bits_per_sample:int,
    #                                width:int, height:int, rowstride:int,
    #                                destroy_fn:GdkPixbuf.PixbufDestroyNotify=None,
    #                                destroy_fn_data=None) -> GdkPixbuf.Pixbuf
    #
    # colorspace: Only RGB is supported
    #                 (https://developer.gnome.org/pygtk/stable/class-gdkpixbuf.html#function-gdk--pixbuf-new-from-data)
    # bits_per_sample: 8 since opencv_image has (or will be converted to have) dtype uint8
    # rowstride: The number of bytes between the start of a row and the start of the next row

    assert opencv_image.shape[2] == 3 or opencv_image.shape[2] == 4

    if opencv_image.shape[2] == 4:
        opencv_rgb = cv2.cvtColor(opencv_image, cv2.COLOR_BGRA2RGBA)
    else:
        opencv_rgb = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)

    if hasattr(GdkPixbuf.Pixbuf, 'new_from_bytes'):
        return GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(opencv_rgb.astype('uint8').tobytes()),
                                               GdkPixbuf.Colorspace.RGB, opencv_rgb.shape[2] == 4, 8,
                                               opencv_rgb.shape[1], opencv_rgb.shape[0], 3 * opencv_rgb.shape[1])

    return GdkPixbuf.Pixbuf.new_from_data(opencv_rgb.astype('uint8').tobytes(), GdkPixbuf.Colorspace.RGB,
                                          opencv_rgb.shape[2] == 4, 8, opencv_rgb.shape[1], opencv_rgb.shape[0],
                                          3 * opencv_rgb.shape[1])


def pixbuf2opencv(gtk_pixbuf):
    """
    Converts a GdkPixbuf.Pixbuf to an OpenCV image

    :param gtk_pixbuf: GdkPixbuf.Pixbuf: Pixbuf to convert
    :return: np.array: OpenCV from Pixbuf. Either BGR or BGRA depending on the number of channels in Pixbuf
                                           (standard OpenCV colour space, with or without alpha channel (transparency))
    """
    # Based on https://stackoverflow.com/a/41714464 by am70
    assert gtk_pixbuf.get_colorspace() == GdkPixbuf.Colorspace.RGB
    assert gtk_pixbuf.get_bits_per_sample() == 8

    width, height, channels, rowstride = (gtk_pixbuf.get_width(), gtk_pixbuf.get_height(), gtk_pixbuf.get_n_channels(),
                                          gtk_pixbuf.get_rowstride())

    if gtk_pixbuf.get_has_alpha():
        assert channels == 4
    else:
        assert channels == 3

    assert rowstride >= width * channels

    numpy_pixels = np.frombuffer(gtk_pixbuf.get_pixels(), dtype=np.uint8)

    if numpy_pixels.shape[0] == width * channels * height:
        opencv_rgb = numpy_pixels.reshape((height, width, channels))

        if channels == 4:
            return cv2.cvtColor(opencv_rgb.reshape((height, width, channels)), cv2.COLOR_RGBA2BGRA)
        else:
            return cv2.cvtColor(opencv_rgb.reshape((height, width, channels)), cv2.COLOR_RGB2BGR)

    else:
        opencv_rgb = np.zeros((height, width * channels), 'uint8')

        for row in range(height):
            opencv_rgb[row, :] = numpy_pixels[rowstride * row: rowstride * row + width * channels]

        if channels == 4:
            return cv2.cvtColor(opencv_rgb.reshape((height, width, channels)), cv2.COLOR_RGBA2BGRA)
        else:
            return cv2.cvtColor(opencv_rgb.reshape((height, width, channels)), cv2.COLOR_RGB2BGR)
