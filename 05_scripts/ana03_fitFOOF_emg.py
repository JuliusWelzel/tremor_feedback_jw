# -*- coding: utf-8 -*-
"""
Created on Wed Oct 14 13:45:26 2020

@author: juliu
"""

# Use NeuroDSP for time series simulations & analyses
from neurodsp import sim
from neurodsp.utils import create_times, set_random_seed
from neurodsp.spectral import compute_spectrum_welch
from neurodsp.plts import plot_time_series, plot_power_spectra


import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import re
import pyxdf

from scipy import signal

import mne
from mne.time_frequency import psd_multitaper


# Import the FOOOF object
from fooof import FOOOF

# Import a utility to download and load example data
from fooof.utils.download import load_fooof_data

# set paths
xdf_root = r'C:\Users\juliu\Desktop\kiel\int_trmr_eeg\04_data\00_main_pilot'
figs_out = r'C:\Users\juliu\Desktop\kiel\int_trmr_eeg\05_plots\01_all_pilot\fitFOOF'

if not os.path.exists(figs_out):
    os.mkdir(figs_out)

sub = os.listdir(xdf_root)
nms_sub = [s.split('_')[1] for s in sub]


for s in sub:
    print('Now working on {} for spec'.format(s))
    fname = os.path.abspath(os.path.join(xdf_root,s))
    #psd_spect,psd_freq = get_spec(fname)
    
    streams, fileheader = pyxdf.load_xdf(fname)    
    for stream in streams:
        if stream['info']['name'] == ['Delsys']:
            emg = stream
            print('Delsys found')


    # get config variable
    s_rate = round(len(emg['time_stamps'])/(emg['time_stamps'][-1]-emg['time_stamps'][0]),0)
    
    # Compute a power spectrum of the Dirac delta
    f, Pxx_den = signal.welch(emg['time_series'][:,3], s_rate, nperseg=10000)
    plt.semilogy(f, Pxx_den)
    freqs, powers = compute_spectrum_welch(emg['time_series'][:,3], s_rate)    
    
    fm = FOOOF(peak_width_limits = [2, 12],peak_threshold = 1, max_n_peaks = 8) 
    fm.fit(f, Pxx_den, [1, 30])
    fm.plot()
    #plt.savefig(os.path.join(figs_out,'{}_fooof_on.png'.format(s.split("-")[1])))
   # plt.close()
    


  
    
    
    
    
    
    
    
    
    
    
    
def get_spec(fname):
    """
    https://github.com/mne-tools/mne-python/blob/master/examples/time_frequency/plot_compute_raw_data_spectrum.py
    ==================================================
    Compute the power spectral density of raw data
    ==================================================
    This script shows how to compute the power spectral density (PSD)
    of measurements on a raw dataset. It also show the effect of applying SSP
    to the data to reduce ECG and EOG artifacts.
    """
    # Authors: Alexandre Gramfort <alexandre.gramfort@inria.fr>
    #          Martin Luessi <mluessi@nmr.mgh.harvard.edu>
    #          Eric Larson <larson.eric.d@gmail.com>
    # License: BSD (3-clause)
    
    
    print(__doc__)
    
    ###############################################################################
    # Load data
    # ---------
    #
    # We'll load a sample MEG dataset, along with SSP projections that will
    # allow us to reduce EOG and ECG artifacts. For more information about
    # reducing artifacts, see the preprocessing section in :ref:`documentation`.
    
    ## follow https://mne.tools/mne-bids/stable/auto_examples/read_bids_datasets.html
    
    streams, fileheader = pyxdf.load_xdf(fname)    
    for stream in streams:
        if stream['info']['name'] == ['Delsys']:
            emg = stream
            print('Delsys found')

        
    fmin, fmax = 1, 50  # look at frequencies between 1 and 50 Hz
    n_fft = 1024  # the FFT size (n_fft). Ideally a power of 2
    tmin, tmax = 60 * 1, 60 * 3  # use the first 60s of data
    
    ###############################################################################
    # Plot a cleaned PSD
    # ------------------
    #
    # Next we'll focus the visualization on a subset of channels.
    # This can be useful for identifying particularly noisy channels or
    # investigating how the power spectrum changes across channels.
    #
    # We'll visualize how this PSD changes after applying some standard
    # filtering techniques. We'll first apply the SSP projections, which is
    # accomplished with the ``proj=True`` kwarg. We'll then perform a notch filter
    # to remove particular frequency bands.
    
    
    
    # And now do the same with SSP + notch filtering
    # Pick all channels for notch since the SSP projection mixes channels together
    spectra, freqs = mne.time_frequency.psd_welch(emg['time_series'], fmin=fmin, fmax=fmax, tmin=tmin, tmax=tmax,
                           n_overlap=150, n_fft=n_fft,average='mean')
    
    spectra = spectra.mean(axis=0)
    
    return spectra, freqs

