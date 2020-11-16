#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: PanZoomRotate.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2020-11-11
    Python Version: 3.8
"""

# Main file

from src.MainWindow import MainWindow

if __name__ == '__main__':
    root = MainWindow(hotkey_repr='§')
    root.mainloop()
