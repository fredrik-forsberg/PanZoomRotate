#! /usr/bin/env python3
# -*- coding: utf-8 -*-

"""
    File name: affine_transform.py
    Author: Fredrik Forsberg
    Date created: 2020-11-11
    Date last modified: 2020-11-11
    Python Version: 3.8
"""

import numpy as np

###


def affine_transform(coords_in_frame1, coords_in_frame2):
    """
    An affine transform from frame 1 (R^n) to frame 2 (R^n) which requires n+1 coordinates in both frames

    :param coords_in_frame1: Either a numpy array of either shape (n+1, n) or (n, n+1),
                             or a list containg n+1 numpy arrays of shape (n, )
                             Represents points in frame 1 which span R^n and correspond to the points 'coords_in_frame2'
                             in frame 2
    :param coords_in_frame2: Same as 'coords_in_frame1' but for frame 2
    :return: Numpy array of shape (n+1, n+1). Describes an affine transform from R^n (frame 1) to R^n (frame 2)
    """

    if not isinstance(coords_in_frame1, np.ndarray):
        coords_in_frame1 = np.asarray(coords_in_frame1)

    if not isinstance(coords_in_frame2, np.ndarray):
        coords_in_frame2 = np.asarray(coords_in_frame2)

    if coords_in_frame1.shape != coords_in_frame2.shape:
        raise ValueError('The shapes of coords_in_frame1 ' + str(coords_in_frame1.shape) + ' and of coords_in_frame2 '
                         + str(coords_in_frame2.shape) + ' are not aligned')

    if coords_in_frame1.shape[0] - coords_in_frame1.shape[1] not in [-1, 1]:
        raise ValueError('Expected cordinates of shape (n, n+1) or (n+1, n). Recieved ' + str(coords_in_frame1.shape))

    if coords_in_frame1.shape[0] > coords_in_frame1.shape[1]:
        coords_in_frame1 = coords_in_frame1.T
        coords_in_frame2 = coords_in_frame2.T

    offset1 = coords_in_frame1[:, 0].reshape((coords_in_frame1.shape[0], 1))
    offset2 = coords_in_frame2[:, 0].reshape((coords_in_frame2.shape[0], 1))

    delta_coords1 = (coords_in_frame1 - offset1)[:, 1:]
    delta_coords2 = (coords_in_frame2 - offset2)[:, 1:]

    inner_matrix = delta_coords2.dot(np.linalg.inv(delta_coords1))

    translation = offset2 - inner_matrix.dot(offset1)

    return np.concatenate((np.concatenate((inner_matrix, np.zeros((1, inner_matrix.shape[1]))), axis=0),
                           np.concatenate((translation, np.ones((1, 1))), axis=0)),
                          axis=1)

#


def affine_inverse(affine_transform_matrix):
    """
    Inverse of an affine transform

    :param affine_transform_matrix: Numpy array of shape (n+1, n+1). Describes an affine transform from R^n (frame 1)
        to R^n (frame 2).
    :return: Numpy array of shape (n+1, n+1). Describes an affine transform from R^n (frame 2) to R^n (frame 1)
    """

    rows, cols = affine_transform_matrix.shape

    translation = affine_transform_matrix[:rows-1, -1].reshape((rows-1, 1))
    inner_matrix = affine_transform_matrix[:-1, :-1]

    inner_inverse = np.linalg.inv(inner_matrix)
    new_translation = -inner_inverse.dot(translation)

    return np.concatenate((np.concatenate((inner_inverse, np.zeros((1, cols-1))), axis=0),
                           np.concatenate((new_translation, np.ones((1, 1))), axis=0)),
                          axis=1).astype(affine_transform_matrix.dtype)

#


def affine_multiplication(affine_transform_matrix, vector):
    """
    Applying an affine transform to a vector

    :param affine_transform_matrix: Numpy array of shape (n+1, n+1). Describes an affine transform from R^n (1) to
        R^n (2)
    :param vector: Numpy array with shape of either (n, 1), (1, n), or (n,)
    :return: Numpy array with the same shape as the input 'vector' array
    """

    if (len(affine_transform_matrix.shape) != 2 or
            affine_transform_matrix.shape[0] != affine_transform_matrix.shape[1]):
        raise TypeError('The affine transform matrix has the shape ' + str(affine_transform_matrix.shape) +
                        ' and is thusly not a 2-dim square matrix')

    if len(vector.shape) == 1 and vector.size == affine_transform_matrix.shape[0] - 1:
        v = np.concatenate((vector.reshape((vector.size, 1)), np.ones((1, 1))), axis=0)

    elif vector.shape[1] == affine_transform_matrix.shape[0] - 1 and len(vector.shape) > 1:
        v = np.concatenate((vector.T, np.ones((1, vector.shape[0]))), axis=0)

    elif vector.shape[0] == affine_transform_matrix.shape[0] - 1 and len(vector.shape) > 1:
        v = np.concatenate((vector, np.ones((1, vector.shape[1]))), axis=0)

    else:
        raise TypeError("The vector's shape " + str(vector.shape) +
                        " is incompatilbe with the affine transform matrix' shape " +
                        str(affine_transform_matrix.shape) + ". Expected either (" +
                        str(affine_transform_matrix.shape[0] - 1) + ", n) or (n, " +
                        str(affine_transform_matrix.shape[0] - 1) + " where n >= 0.")

    return affine_transform_matrix.dot(v)[:-1].reshape(vector.shape)

###


if __name__ == "__main__":
    print("""
               |                      X    1
               |                      |
     2    X    |          ->          2    0
               |                      |
    _0____1____|_________    _________|_________
               |                      |         """)

    points1 = np.asarray([[-2, 0], [-1, 0], [-2, 1]])
    x1 = np.asarray([[-1, 1]])
    points2 = np.asarray([[1, 1], [1, 2], [0, 1]])

    T = affine_transform(points1, points2)
    T_inv = affine_inverse(T)

    print('\nAffine transform:')
    print(T)

    print('\nInverse affine transform:')
    print(T_inv)

    x2 = affine_multiplication(T, x1)
    inv_x2 = affine_multiplication(T_inv, x2)

    print('\n\nTransformation of ' + str(x1) + ':')
    print(x2)

    print('\nInverse transform back from ' + str(x2) + ':')
    print(inv_x2)
