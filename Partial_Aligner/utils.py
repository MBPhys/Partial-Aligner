#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 29 09:32:34 2021

@author: Marc Boucsein
"""
import numpy as np 

def radtoangle(rad):
    angle=rad*180/ np.pi
    return angle

def angletorad(angle):
    rad= angle*np.pi/180
    return rad

def shear_matrix_3D(shear_x, shear_y, shear_z ):
    Shear_matrix= np.array(
        [
            [1,  shear_y, shear_x],
            [0, 1,  shear_z],
            [0,0, 1],
        ]
    )
    return Shear_matrix

