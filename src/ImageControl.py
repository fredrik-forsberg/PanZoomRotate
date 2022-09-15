#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: ImageControl.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2022-01-03
    Python Version: 3.8
"""

import numpy as np

from src.affine.affine_transform import affine_transform, affine_inverse, affine_multiplication
from src.affine.affine_image_transform import affine_image_transform

###


class ImageControl:

    def __init__(self, image=None, size=(0, 0), background_color=(0, 0, 0)):
        """
        Controls the pan, zoom, and rotation of an image and the resulting transformed image

        :param image: None or np.array: Inital OpenCV image (defalut=None)
        :param size: tuple (int, int): The desired size of the output image (default=(0, 0))
        :param background_color: tuple (int, int, int): Background colour for areas where there is no image
            (default=(0, 0, 0) (black))
        """
        self.core_image = np.ndarray((0,))

        self.affine_transform_matrix = np.zeros((3, 3), dtype=np.float64)
        self.corners = np.zeros((2, 3), dtype=np.float64)
        self.size = size

        self.background_color = background_color

        if image is not None:
            self.load_image(image)

    def get_image(self):
        """
        Get the transformed image

        :return: np.array: OpenCV image
        """
        if self.core_image.size == 0:
            return self.core_image

        self.update_affine_transform_matrix()  # Backup method call, should be done by each method after alterations
        
        try:
            image = affine_image_transform(self.core_image, affine_inverse(self.affine_transform_matrix),
                                        self.size, self.background_color)
            
            return image
            
        except np.linalg.LinAlgError:
            # The affine matrix is not invertable
            # Can occur if the image has not loaded in properly
            return np.ndarray((0,))

    def update_affine_transform_matrix(self):
        """
        Update the affine matrix controlling the image transformation
        Has to be done if the output size (self.size) or the desired view (self.corners) have changed

        :return: None
        """
        self.affine_transform_matrix = affine_transform(self.get_coords_from_size(self.size), self.corners)

    def resize(self, new_size):
        """
        Change the size of the output image (self.size)

        :param new_size: tuple (int, int): New desired output size in pixels
        :return: None
        """
        if self.core_image.size != 0 and self.size != (0, 0):
            self.zoom((new_size[0] / self.size[0], new_size[1] / self.size[1]))

        self.size = new_size

        if self.core_image.size != 0:
            self.update_affine_transform_matrix()

    def load_image(self, core_image):
        """
        Loads a new image to be transformed and resets the view to contain the entire new image

        :param core_image: np.array: OpenCV image to transform
        :return: None
        """
        self.core_image = core_image
        self.reset_corners()

    def reset_corners(self):
        """
        Resets the view centered on the image without rotation and zoomed to contain the entire image

        :return: None
        """
        if (0 in self.size) or (self.core_image.size == 0) or (0 in self.core_image.shape[:2]):
            return
        size = self.size
        img_shape = self.core_image.shape

        if img_shape[0]/img_shape[1] == size[1]/size[0]:
            height, width = img_shape[:2]
            offset = np.zeros((2, 1), dtype=np.float64)

        elif img_shape[0]/img_shape[1] > size[1]/size[0]:
            height = img_shape[0]
            width = size[0]/size[1]*height
            offset = np.array([[(width - img_shape[1]) / 2], [0]], dtype=np.float64)

        else:
            width = img_shape[1]
            height = size[1]/size[0]*width
            offset = np.array([[0], [(height - img_shape[0]) / 2]], dtype=np.float64)

        self.corners = self.get_coords_from_size((width, height)) - offset
        self.update_affine_transform_matrix()

    @staticmethod
    def get_coords_from_size(size):
        """
        An array representing 3 points in 2D
        [[  0. size[0]      0.]
         [  0.      0. size[1]]]
         If "size" is the size of an image then the three points represent the top left corner, the bottom left corner,
             and the top right corner of the image in pixel coordinates

        :param size: tuple (int, int): x-value of point 2 and y-value of point 3
        :return: np.array: Array of shape (2, 3) representing 3 2D points (dtype=np.float64)
        """
        return np.asarray([[0, size[0], 0], [0, 0, size[1]]], dtype=np.float64)

    #

    def pan(self, delta):
        """
        Move the view of the output image according to the cordinate delta

        :param delta: Container (i.e. tuple, list, ...) of length 2: 2D pixel coordinate representing the pan
        :return: None
        """
        if self.core_image.size == 0:
            return

        if not isinstance(delta, np.ndarray):
            delta = np.array(delta).reshape((2, 1))

        elif delta.shape != (2, 1):
            delta = delta.reshape((2, 1))

        self.corners = affine_multiplication(self.affine_transform_matrix,
                                             self.get_coords_from_size(self.size) + delta)
        self.update_affine_transform_matrix()

    def zoom(self, zoom_factor, zoom_center=None):
        """
        Zoom the view of the output image

        :param zoom_factor: float: Factor by which to zoom. 1.0 means nothing happens, 1.5 zooms out 50%,
            and 0.5 zooms in 200%
        :param zoom_center: None or container (i.e. tuple, list, ...) of length 2: 2D pixel coordinate for point
            uneffected by the zoom. None represents the center (default=None)
        :return: None
        """
        if self.core_image.size == 0:
            return

        if not isinstance(zoom_factor, (list, tuple)):
            zoom_factor = (zoom_factor, zoom_factor)

        if zoom_center is None:
            zoom_center = np.array(self.size, dtype=np.float64).reshape((2, 1)) / 2
        elif not isinstance(zoom_center, np.ndarray):
            zoom_center = np.array(zoom_center, dtype=np.float64).reshape((2, 1))
        elif zoom_center.shape != (2, 1):
            zoom_center = zoom_center.reshape((2, 1))

        zoom_matrix = np.asarray([[zoom_factor[0], 0], [0, zoom_factor[1]]], dtype=np.float64)

        delta = zoom_matrix.dot(zoom_center) - zoom_center

        self.corners = affine_multiplication(self.affine_transform_matrix,
                                             zoom_matrix.dot(self.get_coords_from_size(self.size)) - delta)

        self.update_affine_transform_matrix()

    def rotate(self, rad_angle, rot_center=None):
        """
        Rotate the view of the output image

        :param rad_angle: float: Angle in radians by which to rotate
        :param rot_center: None or container (i.e. tuple, list, ...) of length 2: 2D pixel coordinate for constant
            point during rotation. None represents the center (default=None)
        :return: None
        """
        if self.core_image.size == 0:
            return

        if rot_center is None:
            rot_center = np.array(self.size, dtype=np.float64).reshape((2, 1)) / 2
        elif not isinstance(rot_center, np.ndarray):
            rot_center = np.array(rot_center, dtype=np.float64).reshape((2, 1))
        elif rot_center.shape != (2, 1):
            rot_center = rot_center.reshape((2, 1))

        transformed_center = affine_multiplication(self.affine_transform_matrix, rot_center)

        cos_angle = np.cos(rad_angle)
        sin_angle = np.sin(rad_angle)
        rotation_matrix = np.array([[cos_angle, -sin_angle],
                                    [sin_angle, cos_angle]], dtype=np.float64)

        self.corners = rotation_matrix.dot(self.corners - transformed_center) + transformed_center

        self.update_affine_transform_matrix()
