#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: MainWindow.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2020-11-11
    Python Version: 3.8
"""

import os
import sys
import tkinter as tk
from pynput import keyboard
import json

from src.ImageCanvasExtendedFunc import ImageCanvasExtendedFunc
from src.screenshot import opencv_screenshot

# Clipboard (used here soley for testing whether copy to clipboard is supported or not)
from src.clipboard_image_functions.clipboard_image_functions import is_copy_to_clipboard_supported

###


class MainWindow(tk.Tk):

    def __init__(self, scroll_factor=1.10, hotkey_repr='§', centered_zoom=True, centered_rotation=True,
                 rotate_nonresponsive_radius_fraction=0.05):
        """
        Tkinter window containg a canvas in which an image can be panned, zoomed, and rotated

            Functionality:
        Pan - Left click and drag
        Zoom - Scroll wheel or "+"/"-"-keys
        Rotate - Right click and drag

        Global screenshot hotkey - Preset to "§" but can be changed in the menu during runtime (se below)
        Options menu - M, Alt-, or Menu-key

        Fullscreen - F
        Reset view - R

        Copy image to clipboard - Ctrl+C    (If supported by the system)
        Paste image from clipboard - Ctrl+V
        Open image or PDF - Ctrl+O
        Save image - Ctrl+S

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
        """
        super().__init__()

        # Settings

        # Try to read settings from a settings file
        settings_dict = self.read_from_settings_file()

        if 'hotkey' in settings_dict:
            hotkey_repr = settings_dict['hotkey']

        if 'centered_zoom' in settings_dict:
            centered_zoom = bool(settings_dict['centered_zoom'])

        if 'centered_rotation' in settings_dict:
            centered_rotation = bool(settings_dict['centered_rotation'])

        if 'geometry' in settings_dict:
            geometry = settings_dict['geometry']
        else:
            geometry = "%dx%d+0+0" % (self.winfo_screenwidth(), self.winfo_screenheight())

        # Create the window

        self.title("PanZoomRotate")
        self.geometry(geometry)

        self.fullscreen = False

        self.image_canvas = ImageCanvasExtendedFunc(self, pan=True, zoom=True, rotate=True,
                                                    scroll_factor=scroll_factor, centered_zoom=centered_zoom,
                                                    centered_rotation=centered_rotation,
                                                    rotate_nonresponsive_radius_fraction=
                                                    rotate_nonresponsive_radius_fraction)
        self.image_canvas.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True)
        self.image_canvas.focus_set()

        # Hotkey listener
        self.hotkey = keyboard.HotKey(keyboard.HotKey.parse(hotkey_repr), self.show_screenshot)
        self.hotkey_listener = keyboard.Listener(on_press=self.for_hotkey_canonical(self.hotkey.press),
                                                 on_release=self.for_hotkey_canonical(self.hotkey.release))
        self.hotkey_listener.start()

        # Show initial text
        self.image_canvas.draw_text(self.get_greeting_text())

        # Set up a menu
        self.menu = self.AltMenu(self, centered_zoom=centered_zoom,
                                 centered_rotation=centered_rotation, relief=tk.FLAT)

        # Events

        self.bind('f', lambda dummy_event: self.set_fullscreen())

        self.bind('<Escape>', lambda dummy_event: self.set_fullscreen(state=False))

        self.bind("<KeyRelease-Alt_L>", self.show_menu)
        self.bind("<KeyRelease-Alt_R>", self.show_menu)
        self.bind("m", self.show_menu)
        try:
            self.bind("<Menu>", self.show_menu)
        except tk.TclError:
            pass
        try:
            self.bind("<App>", self.show_menu)
        except tk.TclError:
            pass   

    @staticmethod
    def read_from_settings_file():
        """
        Tries to read a json settings file located in the same folder as the main script
        and named "main/path/MainScriptName_settings.json"

        :return: dict: Settings dictionary contained in the json-file or an empty dictionary if no such file exists
        """
        main_file_path = os.path.abspath(sys.argv[0])
        settings_file_path = os.path.splitext(main_file_path)[0] + '_settings.json'

        if not os.path.isfile(settings_file_path):
            return dict()

        else:
            with open(settings_file_path, 'r') as f:
                settings_dict = json.load(f)
            return settings_dict

    def save_to_settings_file(self):
        """
        Saves a json settings file to the same folder as the main script
        and named "main/path/MainScriptName_settings.json"

        :return: None
        """
        main_file_path = os.path.abspath(sys.argv[0])
        settings_file_path = os.path.splitext(main_file_path)[0] + '_settings.json'
        settings_dict = {'hotkey': self.get_hotkey_reverse_parse_string(),
                         'centered_zoom': self.image_canvas.centered_zoom,
                         'centered_rotation': self.image_canvas.centered_rotation,
                         'geometry': self.winfo_geometry()}

        with open(settings_file_path, 'w+') as f:
            json.dump(settings_dict, f, sort_keys=True, indent=4)

    def get_greeting_text(self, padding_value=0):
        """
        Generate the greeting text which is displayed on startup

        :param padding_value: int: Value for the amount of padding to use in the middle.
            Effects the line width, but does not directly correspond to line width. (default=0)
        :return: str: The greeting text
        """
        hotkey_str = self.get_hotkey_reverse_parse_string_readable(str_connector=" + ")

        s = "PanZoomRotate controls:\n\n"

        s += "Pan" + " " * (padding_value + 49) + "Left click and drag\n"
        s += "Zoom" + " " * (padding_value + 31) + 'Scroll wheel or "+"/"-"-keys\n'
        s += "Rotate" + " " * (padding_value + 42) + "Right click and drag\n\n"

        s += "Global screenshot hotkey" + " " * (padding_value + 44 -
                                                 (len(hotkey_str) - hotkey_str.count(' ')) * 2 -
                                                 hotkey_str.count(' ')) + hotkey_str + "\n"
        s += "Options menu" + " " * (padding_value + 30) + "M, Alt-, or Menu-key\n\n"

        s += "Fullscreen" + " " * (padding_value + 66) + "F\n"
        s += "Reset view" + " " * (padding_value + 65) + "R\n\n"

        if is_copy_to_clipboard_supported():
            s += "Copy image to clipboard" + " " * (padding_value + 34) + "Ctrl + C\n"
        s += "Paste image from clipboard" + " " * (padding_value + 29) + "Ctrl + V\n"
        s += "Open image or PDF" + " " * (padding_value + 42) + "Ctrl + O\n"
        s += "Save image" + " " * (padding_value + 54) + "Ctrl + S"

        return s

    def set_fullscreen(self, state=None):
        """
        Changes the window to/from fullscreen

        :param state: bool or None: Whether to set to fullscreen. None toggles the state.
        :return: bool: False if the desired state is already the current state. True if successful.
        """
        if state is None:
            return self.set_fullscreen(state=(not self.fullscreen))

        if state == self.fullscreen:
            return False

        self.attributes("-fullscreen", state)
        self.fullscreen = state
        return True

    def show_menu(self, event=None):
        """
        Displays an options menu

        :param event: tkinter.Event or None: Used to determine where to place the menu's upper left corner.
            If tkinter.Event; At the mouse pointer (event.x_root, event.y_root).
            If None; The top left corner of the window.
        :return: None
        """
        if event is None:
            x, y = (self.winfo_rootx, self.winfo_rooty)
        else:
            x, y = (event.x_root, event.y_root)
        self.menu.tk_popup(x, y)

    def show_screenshot(self):
        """
        Activates fullscreen, takes a screenshot and displays the image, changes focus to the canvas

        :return: None
        """
        self.set_fullscreen(state=True)
        self.image_canvas.image_control.load_image(opencv_screenshot())
        self.image_canvas.update()
        self.focus_force()
        self.image_canvas.focus_set()

    def for_hotkey_canonical(self, func):
        """
        Used by pynput.keyboard.Listener to turn a function into an adapted lambda function

        :param func: function: Function to be turned into an adapted lambda function
        :return: function: lambda function needed by pynput.keyboard.Listener
        """
        return lambda k: func(self.hotkey_listener.canonical(k))

    def get_hotkey_reverse_parse_list(self):
        """
        The current screenshot hotkey as a list of string representations of the keyboard keys

        :return: list of str: List of string representations of the current screenshot hotkey
        """
        keys = self.hotkey._keys.copy()  # _keys is protected, but it is seemingly the only way of accessing the hotkeys
        str_repr_list = []
        for key in list(keys)[::-1]:
            if isinstance(key, keyboard.KeyCode) and hasattr(key, "char") and key.char is not None:
                # Some KeyCodes' "char" is None if no char is associated to that specific key
                str_repr_list.append(key.char)
            elif isinstance(key, keyboard.Key) and hasattr(key, "name") and key.name is not None:
                str_repr_list.append("<" + str(key.name) + ">")
        return sorted(str_repr_list)

    def get_hotkey_reverse_parse_string(self, reverse_parse_list=None):
        """
        The current screenshot hotkey as a string representations of the keyboard keys separated by "+"
        This form is the one needed for pynput.keyboard.HotKey.parse() while initiating a hotkey

        :param reverse_parse_list: list of str or None: List of string representations of the current screenshot hotkey
            If None; Will use self.get_hotkey_reverse_parse_list() to acquire this
        :return: str: A string representation of the current screenshot hotkey as the string representations of
            the keyboard keys separated by "+"
        """
        if reverse_parse_list is None:
            reverse_parse_list = self.get_hotkey_reverse_parse_list()
        return "+".join(reverse_parse_list)

    def get_hotkey_reverse_parse_string_readable(self, reverse_parse_list=None, str_connector=" + "):
        """
        The current screenshot hotkey as a more readable string representations of the keyboard keys separated by " + "
        Replaces "+" with "<+>" and "-" with "<->"

        :param reverse_parse_list: list of str or None: List of string representations of the current screenshot hotkey
            If None; Will use self.get_hotkey_reverse_parse_list() to acquire this
        :param str_connector: str: String separator inbetween key string representations (default=" + ")
        :return: str: A string representation of the current screenshot hotkey as the string representations of
            the keyboard keys
        """
        if reverse_parse_list is None:
            reverse_parse_list = self.get_hotkey_reverse_parse_list()
        replacements = {"+": "<+>", "-": "<->"}
        return str_connector.join([replacements.get(x, x) for x in reverse_parse_list])

    def destroy(self):
        """
        Stop the hotkey listener and completely close this window
        Overrides tkinter.Tk.destroy()

        :return: None
        """
        self.hotkey_listener.stop()
        super().destroy()

    #

    class AltMenu(tk.Menu):

        def __init__(self, main_root, centered_zoom=True, centered_rotation=True, *args, **kwargs):
            """
            Options pop-out menu.
            A "Right-click-menu" which doesn't need to be activated by the right mouse button.

                Menu options:
            Open (Ctrl+O)
            Save (Ctrl+S)
            ---
            Copy (Ctrl+C)
            Paste (Ctrl+V)
            ---
            Fullscreen (F)
            Reset view (R)
            ---
            - Screen centered zoom    (Radiobutton)
            - Mouse centered zoom    (Radiobutton)
            ---
            - Screen centered rotation    (Radiobutton)
            - Mouse centered rotation    (Radiobutton)
            ---
            Change screenshot hotkey
            Save settings to file

            :param main_root: tk.Tk: The tkinter window and parent
            :param centered_zoom: bool: If True, zooms to the center of the ImageCanvas. If False, zoom to the position
                of the mouse pointer. Used to set the correct menu radiobutton value. (default=True)
            :param centered_rotation: bool: If True, rotate around the center of the ImageCanvas. If False, rotate
                around the position of the mouse pointer. Used to set the correct menu radiobutton value. (default=True)
            :param args: Additional arguments passed along to the parental class tkinter.Menu (aside from the menu's
                master which is specified seperately in the parameter "main_root")
            :param kwargs: Keyword arguments passed along to the parental class tkinter.Menu.
                kwargs['tearoff'] is set to False if nothing else is specified.
            """
            if 'tearoff' not in kwargs:
                kwargs['tearoff'] = False
            super().__init__(main_root, *args, **kwargs)

            self.root = main_root

            self.centered_zoom = tk.BooleanVar(self, value=centered_zoom)
            self.centered_rotation = tk.BooleanVar(self, value=centered_rotation)

            self.add_command(label="Open (Ctrl+O)", command=self.root.image_canvas.callback_open_file)
            self.add_command(label="Save (Ctrl+S)", command=self.root.image_canvas.callback_save_file)

            self.add_separator()
            self.add_command(label="Copy (Ctrl+C)", command=lambda: print("Copy (Ctrl+C)"),
                             state=[tk.DISABLED, tk.NORMAL][is_copy_to_clipboard_supported()])
            self.add_command(label="Paste (Ctrl+V)", command=lambda: print("Paste (Ctrl+V)"))

            self.add_separator()
            self.add_command(label="Fullscreen (F)", command=self.root.set_fullscreen)
            self.add_command(label="Reset view (R)", command=self.root.image_canvas.callback_reset)

            self.add_separator()
            self.add_radiobutton(label="Screen centered zoom", value=True, variable=self.centered_zoom,
                                 command=lambda: self.root.image_canvas.set_centered_zoom(True))
            self.add_radiobutton(label="Mouse centered zoom", value=False, variable=self.centered_zoom,
                                 command=lambda: self.root.image_canvas.set_centered_zoom(False))

            self.add_separator()
            self.add_radiobutton(label="Screen centered rotation", value=True, variable=self.centered_rotation,
                                 command=lambda: self.root.image_canvas.set_centered_rotation(True))
            self.add_radiobutton(label="Mouse centered rotation", value=False, variable=self.centered_rotation,
                                 command=lambda: self.root.image_canvas.set_centered_rotation(False))

            self.add_separator()
            self.add_command(label="Change screenshot hotkey",
                             command=lambda: self.root.ChangeHotkeyToplevel(self.root))
            self.add_command(label="Save settings to file", command=lambda: self.root.save_to_settings_file())

    #

    class ChangeHotkeyToplevel(tk.Toplevel):

        def __init__(self, main_root, *args, **kwargs):
            """
            A seperate pop-up window from which a new screenshot hotkey can be set.

            :param main_root: tkinter.Tk:  The tkinter window and parent
            :param args: Additional arguments passed along to the parental class tkinter.Toplevel (aside from the
                toplevel's master which is specified seperately in the parameter "main_root")
            :param kwargs: Keyword arguments passed along to the parental class tkinter.Toplevel
            """
            super().__init__(master=main_root, *args, **kwargs)

            self.root = main_root

            # Get the current hotkey used by the main window
            self.root_hotkey_list = self.root.get_hotkey_reverse_parse_list()

            # List to hold the new hotkey
            self.new_hotkey_list = self.root_hotkey_list.copy()

            # Stop the main window's hotkey since it otherwise can interfere
            self.root.hotkey_listener.stop()

            # Placeholder for pynput.keyboard.Listener
            self.new_hotkey_listener = None
            # Bool for if a new hotkey is currently being recorded
            self.recording = False

            self.title("Change screenshot hotkey")

            self.hotkey_stringvar = tk.StringVar()
            self.hotkey_stringvar.set(self.root.get_hotkey_reverse_parse_string_readable(self.root_hotkey_list))

            hotkey_label = tk.Label(self, textvariable=self.hotkey_stringvar, relief=tk.SUNKEN)
            hotkey_label.grid(row=0, column=0, columnspan=3, sticky=tk.N+tk.W+tk.E+tk.S)
            self.grid_rowconfigure(0, weight=1)

            self.recording_button_texts = ["Record new hotkey combination", "Stop recording new hotkey combination"]
            self.record_button_stringvar = tk.StringVar()
            self.record_button_stringvar.set(self.recording_button_texts[self.recording])

            self.record_button = tk.Button(self, textvariable=self.record_button_stringvar, command=self.record)
            self.record_button.grid(row=1, column=0, sticky=tk.N+tk.W+tk.E+tk.S)
            self.grid_columnconfigure(0, weight=1)

            self.apply_button = tk.Button(self, text="Apply", command=self.apply)
            self.apply_button.grid(row=1, column=1, sticky=tk.N+tk.W+tk.E+tk.S)
            self.grid_columnconfigure(1, weight=1)

            self.cancel_button = tk.Button(self, text="Cancel", command=self.destroy)
            self.cancel_button.grid(row=1, column=2, sticky=tk.N+tk.W+tk.E+tk.S)
            self.grid_columnconfigure(2, weight=1)

            # Place the window in the middle of the screen
            self.withdraw()
            self.update_idletasks()
            self.geometry("+%d+%d" % ((self.winfo_screenwidth() - self.winfo_reqwidth()) / 2,
                                      (self.winfo_screenheight() - self.winfo_reqheight()) / 2))
            self.deiconify()

        def record(self):
            """
            Toggle the recording of keystrokes and registering which keys are being held down
            If not currently recording: Start
            If currently recording: Stop

            :return: None
            """
            if self.recording is False:
                # Start recording
                self.new_hotkey_list = []
                self.hotkey_stringvar.set('')
                self.new_hotkey_listener = keyboard.Listener(on_press=self.add_key_press,
                                                             on_release=self.remove_key_press)
                self.new_hotkey_listener.start()
                self.recording = True

                # Remove the Apply- and Cancel-buttons while recording
                self.apply_button.grid_remove()
                self.cancel_button.grid_remove()

            else:
                # Stop recording
                self.new_hotkey_listener.stop()
                self.recording = False

                if len(self.new_hotkey_list) == 0:
                    # No pressed down keys recorded. Reset to the main window's current hotkey configuration
                    self.new_hotkey_list = self.root_hotkey_list.copy()
                    self.hotkey_stringvar.set(self.root.get_hotkey_reverse_parse_string_readable(self.new_hotkey_list))

                # Place back the Apply- and Cancel-buttons
                self.apply_button.grid()
                self.cancel_button.grid()

            self.record_button_stringvar.set(self.recording_button_texts[self.recording])

        def add_key_press(self, key):
            """
            Callback class for when a new hotkey combination is being recorded and a key is being pressed down.
            Adds a string representation of said key press to self.new_hotkey_list if it's new

            :param key: pynput.keyboard.KeyCode or pynput.keyboard.Key or None: pynput representation of key press event
            :return: None
            """
            if isinstance(key, keyboard.KeyCode) and hasattr(key, "char"):
                if key.char is None:
                    return  # Some KeyCodes' "char" is None if no char is associated to that specific key
                str_repr = key.char
            elif isinstance(key, keyboard.Key) and hasattr(key, "name"):
                if key.name is None:
                    return
                str_repr = "<" + str(key.name) + ">"
            else:
                return

            if str_repr not in self.new_hotkey_list and str_repr is not None:
                self.new_hotkey_list.append(str_repr)
                self.hotkey_stringvar.set(self.root.get_hotkey_reverse_parse_string_readable(self.new_hotkey_list))

        def remove_key_press(self, key):
            """
            Callback class for when a new hotkey combination is being recorded and a key is being released.
            Removes a string representation of said key press from self.new_hotkey_list if exists.

            :param key: pynput.keyboard._xorg.KeyCode: pynput representation of key release event
            :return: None
            """
            if isinstance(key, keyboard.KeyCode) and hasattr(key, "char"):
                if key.char is None:
                    return  # Some KeyCodes' "char" is None if no char is associated to that specific key
                str_repr = key.char
            elif isinstance(key, keyboard.Key) and hasattr(key, "name"):
                if key.name is None:
                    return
                str_repr = "<" + str(key.name) + ">"
            else:
                return

            if str_repr in self.new_hotkey_list:
                self.new_hotkey_list.remove(str_repr)
                self.hotkey_stringvar.set(self.root.get_hotkey_reverse_parse_string_readable(self.new_hotkey_list))

        def apply(self):
            """
            Apply the new hotkey combination as the main window's screenshot hotkey.
            If able to set a new hotkey: Write "Successfully applied hotkey!" and close this toplevel window after 2s
            If unable to set a new hotkey Write "Failed to apply hotkey" and keep this toplevel window open

            :return: None
            """
            if self.recording:
                self.new_hotkey_listener.stop()
                self.recording = False

            failed = False

            if len(self.new_hotkey_list) == 0:
                failed = True

            elif sorted(self.new_hotkey_list) == sorted(self.root_hotkey_list):
                self.hotkey_stringvar.set("No changes were made")
                self.after(2000, lambda: self.hotkey_stringvar.set(self.root.get_hotkey_reverse_parse_string_readable(
                    self.new_hotkey_list)))

            else:
                try:
                    keyboard.HotKey.parse(self.root.get_hotkey_reverse_parse_string(self.new_hotkey_list))

                except ValueError:
                    failed = True

                else:
                    self.root_hotkey_list = self.new_hotkey_list.copy()
                    self.hotkey_stringvar.set("Successfully applied hotkey!")
                    self.record_button.config(state=tk.DISABLED)
                    self.apply_button.config(state=tk.DISABLED)
                    self.cancel_button.config(state=tk.DISABLED)
                    self.after(2000, self.destroy)

            if failed:
                self.hotkey_stringvar.set("Failed to apply hotkey")
                self.after(2000, lambda: self.hotkey_stringvar.set(self.root.get_hotkey_reverse_parse_string_readable(
                    self.new_hotkey_list)))

        def destroy(self):
            """
            Stop if currently recording, reinitiate the main window's hotkey listener, and close this toplevel window
            Overrides tkinter.Toplevel.destroy()

            :return: None
            """
            # Close
            if self.recording:
                self.new_hotkey_listener.stop()
                self.recording = False

            # self.root_hotkey_list is either the main window's old hotkey or a new one if one successfully has been
            #   recorded
            keyboard_input = keyboard.HotKey.parse(self.root.get_hotkey_reverse_parse_string(self.root_hotkey_list))
            self.root.hotkey = keyboard.HotKey(keyboard_input, self.root.show_screenshot)
            self.root.hotkey_listener = keyboard.Listener(on_press=self.root.for_hotkey_canonical(
                                                                                                self.root.hotkey.press),
                                                          on_release=self.root.for_hotkey_canonical(
                                                                                              self.root.hotkey.release))
            self.root.hotkey_listener.start()

            if self.root.image_canvas.text_id != -1:
                self.root.image_canvas.draw_text(self.root.get_greeting_text())

            super().destroy()

###


if __name__ == "__main__":
    root = MainWindow()
    root.mainloop()
