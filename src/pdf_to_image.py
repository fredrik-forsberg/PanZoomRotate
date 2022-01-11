#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: pdf_to_image.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2022-01-04
    Python Version: 3.8
"""

import numpy as np
import cv2
import fitz as PyMuPDF  # "fitz" is a historical name for the rendering engine PyMuPDF uses

###


def pdf_to_image(pdf_path, dpi=300, page_index=0, alpha_channel=False):
    """
    Reads a page of a PDF-file and returns an OpenCV image

    :param pdf_path: str: The path to the PDF-file
    :param dpi: int: Dots per inch. Resolution of the returned image (default=300)
    :param page_index: int: The page of the PDF to read as an image. The first page corresponds to index 0 (default=0)
    :param alpha_channel: bool: Whether to retrieve the alpha channel (transparency) of the image (default=False)
    :return: np.array: OpernCV image
    :raise: RuntimeError: If pdf_path does not refer a file
    """
    # Based on a StackOverflow answer by JJPty and edited by Vishal Singh ( https://stackoverflow.com/a/55480474 )
    # and a comment regarding DPI by Josiah Yoder on the aforementioned answer
    doc = PyMuPDF.open(pdf_path)
    png_bytes = doc.load_page(page_index).get_pixmap(matrix=PyMuPDF.Matrix(dpi/72, dpi/72),
                                                   alpha=alpha_channel).tobytes()
    doc.close()
    return cv2.imdecode(np.frombuffer(png_bytes, np.uint8), cv2.IMREAD_COLOR)

###


if __name__ == "__main__":
    import os
    from tkinter.filedialog import askopenfilename

    pdf = askopenfilename(initialdir=os.path.expanduser('~'), title='Open PDF', filetypes=[('PDF', ("*.pdf",))])

    if pdf and os.path.isfile(pdf):

        img = pdf_to_image(pdf)

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
