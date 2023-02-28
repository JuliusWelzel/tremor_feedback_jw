import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib import ticker
from mne.time_frequency import psd_array_welch
import numpy as np
from pathlib import Path
from scipy.signal import butter, sosfilt

# import config variables
from src.utl import axlines_with_text, polygon_under_graph
from src.config import (
    cfg_time_trial,
    cfg_time_ep_fsr,
    cfg_bandpass_freq,
    cfg_bandpass_order,
    cfg_trmr_win_oi,
    cfg_mov_win_oi,
    cfg_colors,
    dir_plots,
)

def single_trial_specs(eps, id):
    """Create 3d projected spectra from all force data.

    Args:
        eps (class): epoch class from force data
        id (string): subject id
    """

    # define cfgs from loaded epochs
    cfg_filter = butter(
        cfg_bandpass_order, cfg_bandpass_freq, "bp", fs=eps.srate, output="sos"
    )
    cfg_fsr_psd_colors = cfg_colors["trial_colors"]

    psds_trmr = []

    # prep figure
    fig = plt.figure(dpi = 300, figsize=[8,6])
    ax = plt.axes(projection='3d')

    # prep single trial force data
    for i in range(eps.data.shape[2]):

        idx_times_oi = np.logical_and(eps.times >= cfg_time_trial[0], eps.times <= cfg_time_trial[1])
        filt_trmr = sosfilt(cfg_filter, eps.data[0, idx_times_oi, i])
        tmp_psd_trmr, freqs_trmr = psd_array_welch(
            filt_trmr,
            eps.srate,
            fmin=cfg_trmr_win_oi[0],
            fmax=cfg_trmr_win_oi[1],
            n_fft=eps.srate * 3,
            n_per_seg=eps.srate * 3,
            n_overlap=eps.srate,
        )

        psds_trmr.append(tmp_psd_trmr)

        ax.plot(
            freqs_trmr,
            tmp_psd_trmr.T,
            zs=i,
            zdir="y",
            lw=2,
            color=cfg_fsr_psd_colors[i],
            alpha=1,
        )

    ep_range = range(len(psds_trmr))
    verts = [polygon_under_graph(freqs_trmr, psd.T) for psd in psds_trmr]
    poly = PolyCollection(verts, facecolors=cfg_fsr_psd_colors, alpha=0.5)
    ax.add_collection3d(poly, zs=ep_range, zdir="y")

    # set line for raw force data
    ax.set_xlim(cfg_trmr_win_oi)
    ax.view_init(25, -65)
    ax.set_xlabel("Frequency [Hz]")
    ax.set_zlabel(r"PSD [$\dfrac{Force}{Hz}$]")
    ax.set_ylabel("Trial number")
    formatter = ticker.ScalarFormatter(useMathText=True)
    formatter.set_scientific(True)
    formatter.set_powerlimits((-1,1))
    ax.zaxis.set_major_formatter(formatter)

    fig.savefig(Path.joinpath(dir_plots, f"{id}_single_trial_trmr.png"))