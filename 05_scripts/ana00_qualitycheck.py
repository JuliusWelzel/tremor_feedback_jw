# Script to check data format validity from tremor feedback paradigm

import pyxdf
import pylsl
import os
import numpy as np
from scipy import stats
from pathlib import Path
import sys

sys.path.append('..') # add parent dir for full project access
from utilities.utl import findLslStream, find_nearest

# (import) helper functions
MAINPATH = Path(__file__).parent.parent.absolute()
DATARAWPATH = Path.joinpath(MAINPATH, "04_data","00_raw")

f_list = os.listdir(DATARAWPATH)
str_match = 'archer'
fnms = [s for s in f_list if str_match in s]



## extract data from loop



for f in fnms:
    # load xdf file
    streams, hd = pyxdf.load_xdf(os.path.join('..','04_data','00_raw',f))
    fsr  = findLslStream(streams, 'HX711')
    mrk = findLslStream(streams, 'PsychoPyMarkers')
    
    plt.plot(fsr["time_series"])



