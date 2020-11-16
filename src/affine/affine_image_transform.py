#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: affine_image_transform.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2020-11-11
    Python Version: 3.8
"""

import cv2

###


def affine_image_transform(image, affine_transform_matrix, size, background_color=(0, 0, 0)):
    """
    Returns an image based on the provided affine transform matrix

    :param image: np.aray: OpenCV image
    :param affine_transform_matrix: np.array: Numpy array of shape (3, 3). Describes an affine transform from R^2 to R^2
    :param size: tuple: (rows, columns); Integers
    :param background_color: tuple: Background colour. (B, G, R); Integers 0-255
    :return: np.array: OpenCV image of size 'size' from 'image' based on the transform of 'affine_transform_matrix'
    """

    if affine_transform_matrix.shape == (3, 3):
        affine_transform_matrix = affine_transform_matrix[:-1]

    elif affine_transform_matrix.shape != (2, 3):
        raise TypeError('The affine transformation matrix must have either the shape (3, 3) or (2, 3), not '
                        + str(affine_transform_matrix.shape))

    return cv2.warpAffine(image, affine_transform_matrix, size, borderValue=background_color)
