#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Nov 16 00:21:42 2021

@author: marc
"""

import numpy as np
from skimage import data
# Points generator
def get_grid(x, y, homogenous=False):
    coords = np.indices((x, y)).reshape(2, -1)
    if homogenous:
       return np.vstack((coords, np.ones(coords.shape[1]))) 
    else:
        coords# Define Transformations
def get_rotation(angle):
    angle = np.radians(angle)
    return np.array([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle),  np.cos(angle), 0],
        [0, 0, 1]
    ])
def get_translation(tx, ty):
    return np.array([
        [1, 0, tx],
        [0, 1, ty],
        [0, 0, 1]
    ])
def get_scale(s):
    return np.array([
        [s, 0, 0],
        [0, s, 0],
        [0, 0, 1]
    ])



height, width = data.camera().shape#[:2]
tx, ty = np.array((width // 2, height // 2))
angle = np.radians(45)
scale = 2.0
R = np.array([
    [np.cos(angle), np.sin(angle), 0],
    [-np.sin(angle), np.cos(angle), 0],
    [0, 0, 1]])
T = np.array([
    [1, 0, tx],
    [0, 1, ty],
    [0, 0, 1]
])
S = np.array([
    [scale, 0, 0],
    [0, scale, 0],
    [0, 0, 1]
])
A = T @ R @ S @ np.linalg.inv(T)
# Grid to represent image coordinate
# set up pixel coordinate I'(x, y)
coords = get_grid(width, height, True).astype(np.int)
print(coords.dtype)
x2, y2 = coords[0], coords[1]# Apply inverse transform and round it (nearest neighbour interpolation)
print(x2)
warp_coords = (np.linalg.inv(A)@coords).astype(np.int32)
x1, y1 = warp_coords[0, :], warp_coords[1, :]# Get pixels within image boundaries
indices = np.where((x1 >= 0) & (x1 < width) &
                   (y1 >= 0) & (y1 < height))
xpix1, ypix1 = x2[indices], y2[indices]
xpix2, ypix2 = x1[indices], y1[indices]
print(y2.dtype)
# Map Correspondence
data.camera()[ypix2,xpix2].shape
canvas = np.zeros_like(data.camera())
canvas[ypix1, xpix1] = data.camera()[ypix2,xpix2]
print(canvas[ypix1, xpix1])