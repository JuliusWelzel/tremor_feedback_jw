# -*- coding: utf-8 -*-
"""
Created on Thu Dec  9 13:21:37 2021

@author: User
"""
import cv2
import numpy as np
import os
from matplotlib import pyplot as plt
import pyxdf
import sys
from scipy import signal, stats


## (import) helper functions

sys.path.append('..') # add parent dir for full project access
fnms = [f for f in os.listdir('../04_data/00_raw') if f.endswith('.xdf') and "archer_replicate" in f]


from utilities.utl import findLslStream, find_nearest

for f in fnms:
    # load xdf file
    streams, hd = pyxdf.load_xdf(os.path.join('..','04_data','00_raw',f))
    fsr  = findLslStream(streams, 'HX711')
    mrk = findLslStream(streams, 'PsychoPyMarkers')
    
    plt.plot(fsr["time_series"])
    