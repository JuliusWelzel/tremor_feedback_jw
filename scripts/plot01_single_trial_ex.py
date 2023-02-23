import os
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.signal import medfilt, butter, sosfilt
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.gridspec import GridSpec
from matplotlib import patches
import pickle
from tueplots import bundles
from astropy.convolution import convolve_fft, Gaussian1DKernel
from mne import set_log_level
from mne.time_frequency import psd_array_welch
import seaborn as sns

from src.SingleSubjectData import SubjectData, Epochs


######################################################################
# import config variables
from src.utl import axlines_with_text, polygon_under_graph
from src.config import (
    cfg_time_bl,
    cfg_time_trial,
    cfg_time_ep_pupil,
    cfg_bandpass_freq,
    cfg_bandpass_order,
    cfg_trmr_win_oi,
    cfg_mov_win_oi,
    cfg_colors
)

# import relevant dirs
from src.config import dir_prep, dir_plots
from src.utl import get_channel_labels_ppl_xdf
import src.pupil_prep as pp

print(f"Data imported from {dir_prep}")

# Increase the resolution of all the plots below
bundles.beamer_moml()
plt.rcParams.update(
    {"figure.dpi": 200, "figure.facecolor": "w", "figure.figsize": (15, 10)}
)

# set params for epoch processing and plotting for force data
cfg_pupil_plot_colors = cfg_colors["condotion_colros"]
cfg_plot_lw = 1.5
cfg_idx_eye = 21

# find all relevant files
f_list_pupil = os.listdir(dir_prep)
str_match = "clean_pupil"
fnms_pupil = [s for s in f_list_pupil if str_match in s]

# find all relevant files
f_list_fsr = os.listdir(dir_prep)
str_match = "clean_fsr"
fnms_fsr = [s for s in f_list_fsr if str_match in s]

fnms_fsr[0]

for f in fnms_fsr:
    tmp_fname_fsr = Path.joinpath(dir_prep,f)
    with open(tmp_fname_fsr, 'rb') as handle_mocap:
        eps = pickle.load(handle_mocap)

    tmp_view_angle = eps.events["value"][eps.events["value"].str.contains('sfb') ].str.split('_').str[3].astype(float).round(2)

    fig, axd = plt.subplots(figsize=[18,6])

    # prep single trial pupil data
    for i in range(eps.data.shape[2]):

        if 0 <= i < 4:
            tmp_color = cfg_pupil_plot_colors[0]
            tmp_label = 'visual'
        elif 4 <= i < 8:
            tmp_color = cfg_pupil_plot_colors[1]
            tmp_label = 'auditiv-visual'
        elif 8 <= i <12:
            tmp_color = cfg_pupil_plot_colors[2]
            tmp_label = 'auditiv'

        epoch_timevec = np.linspace(min(eps.times),max(eps.times),len(eps.times))

        if tmp_view_angle.iloc[i] == .02:
            ls = 'dotted'
        elif tmp_view_angle.iloc[i] == .44:
            ls = 'solid'

        if i in [0,4,8]:
            axd.plot(epoch_timevec,eps.data[0,:,i],color=tmp_color,linewidth=cfg_plot_lw, alpha=.5, linestyle = ls, label=tmp_label)
        else:
            axd.plot(epoch_timevec,eps.data[0,:,i],color=tmp_color,linewidth=cfg_plot_lw, alpha=.5, linestyle = ls)


    # plot all trials and histograms of BL and Pupil size
    ymin, ymax = axd.get_ylim()
    xmin, xmax = axd.get_xlim()
    cfg_patch_trial = patches.Rectangle((cfg_time_trial[0],ymin),np.diff(cfg_time_trial),(ymax + np.abs(ymin)),alpha = .1, color = 'grey')

    axd.axvline(0,c='k')
    axd.add_patch(cfg_patch_trial)
    axd.annotate("Trial average", (np.sum(cfg_time_trial) * .5, ymax * .9), color='Black', weight='bold', fontsize=10, ha='center', va='top')
    axd.set_xlabel('Time[s]')
    axd.set_ylabel('Force [au]')
    axd.set_title(f"{f.split('_')[0]} force epochs")
    axd.set_xlim([0,30])
    axd.legend(loc = 2) # set legend upper left

    fig.tight_layout()
    fig.savefig(Path.joinpath(dir_plots,f"{f.split('_')[0]}_fsr_epochs.png"))
    fig.clf()
