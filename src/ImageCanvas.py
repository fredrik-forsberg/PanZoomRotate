#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: ImageCanvas.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2020-11-11
    Python Version: 3.8
"""

import numpy as np
import cv2
from PIL import Image, ImageTk
import platform
import tkinter as tk

from src.ImageControl import ImageControl

###


class ImageCanvas(tk.Canvas):

    def __init__(self, parent, pan=True, zoom=True, rotate=True, scroll_factor=1.10, centered_zoom=True,
                 centered_rotation=True, rotate_nonresponsive_radius_fraction=0.05, *args, **kwargs):
        """
        A custom Tkinter canvas which can display an image and pan, zoom, and rotate said display

        Pan - Left mouse button
        Zoom - Scroll wheel
        Rotate - Right mouse button

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
        :param kwargs: Keyword arguments passed along to the parental class tkinter.Canvas. If nothing else is spedified
            kwargs['background'] is set to 'black'. However, kwargs['highlightthickness'] is always set to 0,
            kwargs['takefocus'] to True, and kwargs['highlightbackground'] to the same as
            kwargs['background'] no matther which other values are provided.
        """

        if not any([x in kwargs for x in ['background', 'bg']]):  # Check if 'background' has been provided in kwargs
            kwargs['background'] = 'black'
        kwargs['highlightbackground'] = kwargs['background']
        kwargs['highlightcolor'] = kwargs['background']
        kwargs['highlightthickness'] = 0
        kwargs['takefocus'] = True
        super().__init__(parent, *args, **kwargs)  # Initiation of the parental class tkinter.Canvas

        self.scroll_factor = scroll_factor
        self.centered_zoom = centered_zoom
        self.centered_rotation = centered_rotation
        self.rotate_nonresponsive_radius_fraction = rotate_nonresponsive_radius_fraction

        self._tk_image = None
        self.image_id = -1

        self.image_control = ImageControl()

        # Events

        self.bind('<Configure>', self.callback_resize)

        if pan:
            self.left_button_pos = np.array((0, 0), dtype=np.float64)
            self.bind('<Button-1>', self.callback_left_button_press)
            self.bind('<B1-Motion>', self.callback_left_button_motion)

        if rotate:
            self.right_button_pos = np.array((0, 0), dtype=np.float64)
            self.right_button_pos_center = np.array((0, 0), dtype=np.float64)
            self.bind('<Button-3>', self.callback_right_button_press)
            self.bind('<B3-Motion>', self.callback_right_button_motion)

        if zoom:
            if platform.system() == 'Linux':
                # For Linux
                self.bind_all("<Button-4>", self.callback_mousewheel_linux)
                self.bind_all("<Button-5>", self.callback_mousewheel_linux)
            elif platform.system() == 'Windows':
                # For Windows
                self.bind_all("<MouseWheel>", self.callback_mousewheel_windows)
            else:
                # For MacOS or other OS
                self.bind_all("<MouseWheel>", self.callback_mousewheel_other)

    def update(self):
        """
        Updates the displayed image and the Tkinter canvas
        Overrides tkinter.Canvas.update()

        :return: None
        """
        img = self.image_control.get_image()
        if img.size > 0:
            if self.image_id != -1:
                self.delete(self.image_id)
            self._tk_image = ImageTk.PhotoImage(image=Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)))
            self.image_id = self.create_image(0, 0, image=self._tk_image, anchor=tk.NW)
        super().update()

    def set_centered_zoom(self, state=None):
        """
        Changes how the zoom action works.
        If state=True then the center of the canvas is uneffected by the zoom.
        If state=False then where the mouse pointer is pointing remains uneffected.

        :param state: bool or None: True activates canvas middle centered zoom, False actives mouse centered zoom,
            and None toggles the behaviour.
        :return: None
        """
        if state is None:
            self.centered_zoom = not self.centered_zoom
        else:
            self.centered_zoom = state

    def set_centered_rotation(self, state=None):
        """
        Changes how the rotate action works.
        If state=True then the center of the canvas is uneffected by the rotation.
        If state=False then where the mouse pointer is pointing remains uneffected.

        :param state: bool or None: True activates canvas middle centered rotation, False actives mouse centered
            rotation, and None toggles the behaviour.
        :return: None
        """
        if state is None:
            self.centered_rotation = not self.centered_rotation
        else:
            self.centered_rotation = state

    def callback_resize(self, event):
        """
        Resizes the image and updates the canvas when the canvas has been resized

        :param event: tkinter.Event: The mouse's position (event.width, event.height) is used
        :return: None
        """
        self.image_control.resize((event.width, event.height))
        self.update()

    def callback_left_button_press(self, event):
        """
        The left mouse button has been pressed down
        Save the mouse position in anticipation for a motion-event

        :param event: tkinter.Event: The mouse's position (event.width, event.height) is used
        :return: None
        """
        self.left_button_pos = np.array((event.x, event.y), dtype=np.float64)

    def callback_left_button_motion(self, event):
        """
        The mouse has been moved while the left mouse button was pressed down
        Pan the image accordingly and save the current position

        :param event: tkinter.Event: The mouse's position (event.width, event.height) is used
        :return: None
        """
        new_pos = np.array((event.x, event.y), dtype=np.float64)
        delta = self.left_button_pos - new_pos
        self.image_control.pan(delta)
        self.left_button_pos = new_pos
        self.update()

    def callback_right_button_press(self, event):
        """
        The right mouse button has been pressed down
        Save the mouse position in anticipation for a motion-event
        Also save the position in case self.centered_rotation=False and the rotation is to be performed around
             the current point

        :param event: tkinter.Event: The mouse's position (event.width, event.height) is used
        :return: None
        """
        self.right_button_pos = np.array((event.x, event.y), dtype=np.float64)
        self.right_button_pos_center = np.array((event.x, event.y), dtype=np.float64)

    def callback_right_button_motion(self, event):
        """
        The mouse has been moved while the right mouse button was pressed down
        Rotate the image accordingly and save the current position
        If the mouse is too close (determined by self.rotate_nonresponsive_radius_fraction) to the rotation center then
            no rotation will occur

        :param event: tkinter.Event: The mouse's position (event.width, event.height) is used
        :return: None
        """
        new_pos = np.array((event.x, event.y), dtype=np.float64)
        if self.centered_rotation:
            center = np.array([self.winfo_width(), self.winfo_height()], dtype=np.float64) / 2
        else:
            center = self.right_button_pos_center

        if ((new_pos == center).all() or (self.right_button_pos == center).all() or
                np.linalg.norm(center - new_pos) < np.min(center) * self.rotate_nonresponsive_radius_fraction):
            self.right_button_pos = new_pos
        else:
            a = new_pos - center
            b = self.right_button_pos - center
            try:
                delta_angle = np.arcsin(np.cross(a / np.linalg.norm(a), b / np.linalg.norm(b)))
            except (RecursionError, ZeroDivisionError):
                return
            else:
                self.image_control.rotate(delta_angle, center)
                self.right_button_pos = new_pos
                self.update()

    def callback_mousewheel_linux(self, event):
        """
        The mouse wheel has been scrolled and the image should subsequently be zoomed
        How tkinter.Event represents the scrolled amount depends on the operating system (OS)
        This method is specific for Linux distributions

        :param event: tkinter.Event: The mouse's position (event.width, event.height) is used, as well as the scroll
            amount event.delta
        :return: None
        """
        if event.num == 4:
            factor = -1
        else:  # event.num == 5
            factor = 1
        if event.delta != 0:
            factor = int(factor*(event.delta/120))
        if self.centered_zoom:
            center = (self.winfo_width() / 2, self.winfo_height() / 2)
        else:
            center = (event.x, event.y)
        self.image_control.zoom(np.float_power(self.scroll_factor, factor), zoom_center=center)
        self.update()

    def callback_mousewheel_windows(self, event):
        """
        The mouse wheel has been scrolled and the image should subsequently be zoomed
        How tkinter.Event represents the scrolled amount depends on the operating system (OS)
        This method is specific for Windows

        :param event: tkinter.Event: The mouse's position (event.width, event.height) is used, as well as the scroll
            amount event.delta
        :return: None
        """
        factor = int(-1*(event.delta/120))
        if self.centered_zoom:
            center = (self.winfo_width() / 2, self.winfo_height() / 2)
        else:
            center = (event.x, event.y)
        self.image_control.zoom(np.float_power(self.scroll_factor, factor), zoom_center=center)
        self.update()

    def callback_mousewheel_other(self, event):
        """
        The mouse wheel has been scrolled and the image should subsequently be zoomed
        How tkinter.Event represents the scrolled amount depends on the operating system (OS)
        This method is more general, but should work for macOS

        :param event: tkinter.Event: The mouse's position (event.width, event.height) is used, as well as the scroll
            amount event.delta
        :return: None
        """
        factor = int(-1*event.delta)
        if self.centered_zoom:
            center = (self.winfo_width() / 2, self.winfo_height() / 2)
        else:
            center = (event.x, event.y)
        self.image_control.zoom(np.float_power(self.scroll_factor, factor), zoom_center=center)
        self.update()
