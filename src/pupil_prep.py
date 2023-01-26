import os
import sys
import numpy as np
import matplotlib.pyplot as plt
import pyxdf
from scipy.stats import median_absolute_deviation as mad
from utilities.utl import fill_nan

#from statsmodels.stats.anova import AnovaRM
#import statsmodels.formula.api as smf
#import pandas as pd

def confidence_threshold(data, conf, thr, doplot):
    """
    apply confidence threshold

    Args:
      data: 1D numpy array (pupil diameter, time series)
      conf: 1D numpy array (confidence values, time series). same length as data
      thr: scalar threshold value \in [0,1], refers to confidence values

    Returns:
      data_thresh: 1D numpy array, same length as data
    """
    print("Apply confidence threshold")
    idx_subthresh = np.where(conf < thr)[0]
    data_thr = data.copy()
    data_thr[idx_subthresh] = np.nan
    
    print("number of low-confidence data points: ", len(idx_subthresh))
    p_subthresh = 1.*len(idx_subthresh)/len(data)
    print(f"proportion of low-confidence data points: {p_subthresh:.2f}")

    if doplot:
        fig, ax = plt.subplots(2, 1, figsize=(16,6), sharex=True)
        ax[0].plot(data, '-k', label='pupil diameter')
        ax[0].plot(idx_subthresh, data[idx_subthresh], 'or', ms=4, alpha=0.5, \
                   label='deleted values')
        ax[0].set_title("pupil diameter")
        ax[0].legend(loc=2, fontsize=16)
        ax[1].plot(conf, '-k')
        ax[1].axhline(thr, color='r')
        ax[1].set_title("confidence")
        plt.tight_layout()
        plt.show()

    return idx_subthresh, data_thr

def delete_outliers(data, whsize, n_mad, doplot):
    """
    Find statistical outliers using a sliding window,
    replace outliers with NaN

    Args:
      data : 1D numpy array, (pupil diameter, time series)
      whsize : sliding window half-size, window will be [t-whsize:t+whsize+1]
      n_mad : float, threshold will be n_mad*mean_absolute_deviation

    Returns:
      data_out : output variable, 1D numpy array, same length as data, outliers
                 are set to np.nan
    """
    print("Delete diameter outliers (sliding window)")
    n = len(data)
    data_out = data.copy()
    outlier_idx = []
    for t in range(whsize,n-whsize):
        batch = data_out[t-whsize:t+whsize+1]
        med_batch = np.nanmedian(batch)
        mad_batch = mad(batch)
        if (mad_batch > 0): # avoid division by zero
            dev = np.abs((data[t]-med_batch)/mad_batch)
            if (dev > n_mad):
                #print(f"outlier detected t={t:d}")
                outlier_idx.append(t)
                data_out[t] = np.nan
    
    print("number of detected outliers: ", len(outlier_idx))
    p_outlier = 1.*len(outlier_idx)/n
    print(f"proportion of detected outliers: {p_outlier:.2f}")

    if doplot:
        plt.figure(figsize=(16,3))
        plt.plot(data, '-k')
        plt.plot(outlier_idx, data[outlier_idx], 'or', ms=8, alpha=0.5, \
                 label='outliers')
        plt.legend()
        plt.title("Diameter outliers")
        plt.tight_layout()
        plt.show()

    return outlier_idx, data_out

    
def delete_velocity_outliers(data, whsize, n_mad, doplot=False):
    """
    Find statistical outliers of the data's first derivative,
    replace outliers with NaN.

    Args:
      data : 1D numpy array, (pupil diameter, time series)
      whsize : sliding window half-size, window will be [t-whsize:t+whsize+1]
      n_mad : float, threshold will be n_mad*mean_absolute_deviation

    Returns:
      data_out : output variable, 1D numpy array, same length as data, outliers
                 are set to np.nan
    """
    print("Delete diameter velocity outliers (sliding window)")
    data_out = data.copy()
    data_diff = np.diff(data) # assuming equidistant sampling
    n = len(data_diff)

    #''' without sliding window
    diff_med = np.nanmedian(data_diff)
    diff_mad = mad(data_diff,nan_policy='omit')
    outlier_idx = np.where( np.abs((data_diff-diff_med)/diff_mad) > n_mad )[0]
    data_out[outlier_idx] = np.nan
    #'''

    ''' with sliding window
    outlier_idx = []
    for t in range(whsize,n-whsize):
        batch = data_diff[t-whsize:t+whsize+1]
        dev = np.abs( (data_diff[t]-np.nanmedian(batch)) / mad(batch) )
        if (dev > n_mad):
            #print(f"outlier detected t={t:d}")
            outlier_idx.append(t)
            data_out[t] = np.nan
    '''

    print("number of detected outliers: ", len(outlier_idx))
    p_outlier = 1.*len(outlier_idx)/n
    print(f"proportion of detected outliers: {p_outlier:.2f}")

    if doplot:
        plt.figure(figsize=(16,3))
        plt.plot(data, '-k')
        plt.plot(outlier_idx, data[outlier_idx], 'or', ms=8, alpha=0.5, \
                 label='outliers')
        plt.legend()
        plt.title("Velocity outlier detection")
        plt.tight_layout()
        plt.show()

    return outlier_idx, data_out

def blink_detection( x , w_smooth=9, doplot=False):
    """
    Detect eyeblinks in pupillometry data.
    Adapted from:
    Hershman et al., Behavior Research Methods (2018), 50:107-114.

    Args:
      x: 1D numpy array (pupil diameter, time series)
      w_smooth: integer, boxcar filter width for data prefiltering

    Returns:
      nan_idx: indices of added NaN values
      xc: 1D numpy array (pupil diameter, time series)
    """
    xc = x.copy() # keep a copy for comparison

    # [1] 0 -> nan
    xc[x==0] = np.nan

    # [2] nan -> 1, else -> 0
    id_nan = 1.0*np.isnan(xc)
    # 1: nan on (blink start), -1: nan off (blink end)
    d_nan = np.diff(id_nan)
    d_nan = np.insert(d_nan,0,d_nan[0]) # duplicate 1st value to align with x

    # [3] smooth the time course
    h_boxcar = np.ones(w_smooth, dtype=np.float)/w_smooth
    xc = fill_nan(xc)
    xc = np.convolve(xc, h_boxcar, 'same')
    # derivative of the smoothed time course
    dx = np.diff(xc)

    # [4] preliminary eyeblink on and off points
    ons_prelim  = np.where(d_nan == 1)[0]
    offs_prelim = -1+np.where(d_nan == -1)[0] # account for diff offset

    # [5] definite on and off points
    # on points: go backwards while slope < 0  
    ons = []
    for t in ons_prelim:
        r_on = np.where(dx[:t] > 0)[0]
        if len(r_on) > 0:
            ons.append(np.max(r_on))
    # off points: go forward while slope > 0
    offs = []
    for t in offs_prelim:
        r_off = np.where(dx[t:] < 0)[0]
        if len(r_off) > 0:
            offs.append(t + np.min(r_off))

    # [6] replace the eyeblink slopes with NaNs
    idx_blink = [] # collect added NaN indices
    for t0, t1 in zip(ons, ons_prelim):
        xc[t0:t1] = np.nan
        for i in range(t0,t1):
            idx_blink.append(i)
    for t0, t1 in zip(offs_prelim, offs):
        xc[t0:t1] = np.nan
        for i in range(t0,t1):
            idx_blink.append(i)

    if doplot:
        fig, ax = plt.subplots(2, 1, figsize=(15,6), sharex=True)

        # upper plot
        ax[0].plot(x, '-ok', ms=5, lw=3, alpha=0.3, label='raw')
        ax[0].legend(loc=1, fontsize=16)
        ax0c = ax[0].twinx()
        ax0c.plot(dx, 'sb', ms=5, alpha=0.3, label='slope')
        ax0c.legend(loc=4, fontsize=16)
        #ax0c.plot(id_nan, '-r')
        #ax0c.plot(d_nan, 'oy', alpha=0.8)

        # plot preliminary ON/OFF points
        for t in ons_prelim:
            ax[0].axvline(t, color='r', linestyle=':')
        for t in offs_prelim:
            ax[0].axvline(t, color='g', linestyle=':')

        # plot final ON/OFF points
        for t in ons:
            ax[0].axvline(t, color='r', linestyle='-')
            ax[0].text(t, 0.2, "ON", color='r')
        for t in offs:
            ax[0].axvline(t, color='g', linestyle='-')
            ax[0].text(t, 0.2, "OFF", color='g')

        # lower plot
        ax[1].plot(x, '-k', lw=4, alpha=0.25, label='raw')
        ax[1].plot(xc, '-b', lw=1, alpha=1.0, label='processed')
        ax[1].legend(loc=1, fontsize=16)

        plt.tight_layout()
        plt.show()

    return idx_blink, xc