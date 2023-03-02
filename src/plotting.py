import matplotlib.pyplot as plt
from matplotlib import patches
from matplotlib.collections import PolyCollection
from matplotlib import ticker
from mne.time_frequency import psd_array_welch
import numpy as np
from pathlib import Path
import seaborn as sns
from scipy.signal import butter, sosfilt

# import config variables
from src.utl import polygon_under_graph
from src.config import (
    cfg_time_trial,
    cfg_bandpass_freq,
    cfg_bandpass_order,
    cfg_trmr_win_oi,
    cfg_colors,
    dir_single_trial_plots,
)

plt.rcParams.update(
    {"figure.facecolor": "w"}
)

def single_trial_force_raw(eps,id):
    """Create single trial plots from all force trials per subject.

    Args:
        eps (class): epoch class from force data
        id (string): subject id
    """

    # set params for epoch processing and plotting for force data
    cfg_pupil_plot_colors = cfg_colors["condition_colors"]
    cfg_plot_lw = 1.5

    # single trial information
    idx_solid = [] # find index of high angle trials
    tmp_view_angle = eps.events["value"][eps.events["value"].str.contains('sfb') ].str.split('_').str[3].astype(float).round(2)

    # initate plot
    fig, axd = plt.subplots(figsize=[13,6], dpi= 300)

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
            idx_solid.append(i)

        axd.plot(epoch_timevec,eps.data[0,:,i],color=tmp_color,linewidth=cfg_plot_lw, alpha=.5, linestyle = ls)

    # plot all trials
    axd.set_xlim([0,30])
    axd.set_ylim([0,np.max(eps.data) * 1.1])

    ymin, ymax = axd.get_ylim()
    cfg_patch_trial = patches.Rectangle((cfg_time_trial[0],ymin),np.diff(cfg_time_trial),(ymax + np.abs(ymin)),alpha = .05, color = 'grey')

    axd.add_patch(cfg_patch_trial)
    axd.annotate("Trial average", (np.sum(cfg_time_trial) * .5, ymax * .9), color='Black', weight='bold', fontsize=10, ha='center', va='top')
    axd.set_xlabel('Time[s]')
    axd.set_ylabel('Force [a.u.]')

    # setup two level legend
    # dummy lines with NO entries, just to create the black style legend
    dummy_lines = []
    linestyles = ['solid','dotted']
    for style in linestyles:
        dummy_lines.append(axd.plot([],[], c="black", ls = style)[0])

    lines = axd.get_lines()
    legend1 = plt.legend([lines[i] for i in idx_solid[::2]], ["visual", "auditiv-visual","auditiv"], loc = 2)
    legend2 = axd.legend([dummy_lines[i] for i in [0,1]], ["high", "low"], loc = 1)
    axd.add_artist(legend1)

    fig.tight_layout()
    sns.despine(fig=fig)
    fig.savefig(Path.joinpath(dir_single_trial_plots,f"{id}_fsr_epochs.png"))
    fig.clf()


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

    fig.savefig(Path.joinpath(dir_single_trial_plots, f"{id}_single_trial_trmr.png"))