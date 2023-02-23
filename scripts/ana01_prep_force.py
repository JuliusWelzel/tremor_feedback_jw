import os
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.signal import medfilt, butter, sosfilt
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.gridspec import GridSpec
import pickle
from tueplots import bundles
from mne import set_log_level
from mne.time_frequency import psd_array_welch

from src.SingleSubjectData import SubjectData, Epochs


######################################################################
# import config variables
from src.utl import axlines_with_text, polygon_under_graph
from src.config import (
    cfg_time_trial,
    cfg_time_ep_fsr,
    cfg_bandpass_freq,
    cfg_bandpass_order,
    cfg_trmr_win_oi,
    cfg_mov_win_oi,
    cfg_colors
)

# import relevant dirs
from src.config import dir_rawdata, dir_prep, dir_plots


print(f"Data imported from {dir_rawdata}")

set_log_level("WARNING")

# Increase the resolution of all the plots below
bundles.beamer_moml()
plt.rcParams.update(
    {"figure.dpi": 200, "figure.facecolor": "w", "figure.figsize": (15, 10)}
)

# set params for epoch processing and plotting for force data
cfg_fsr_plot_colors = cfg_colors["condition_colors"]
cfg_plot_lw = 1.5

# find all relevant files
f_list = os.listdir(dir_rawdata)
str_match = "archer"
fnms = [s for s in f_list if str_match in s]


# prelocate variables
tmp_fnms = fnms.copy()

id = []
n_trial = []
con_view_ang = []
con_feedback = []
all_m_psds_trmr = []
all_m_psds_mov = []
all_psds_trmr = []


####################################################
# prep every participant
for f in tmp_fnms:

    sub = SubjectData()
    sub.load_data(dir_rawdata, f)

    if not sub.fsr:
        print(f"No fsr data found for {sub.id}")
        continue

    # prep raw
    tmp_dat = medfilt(sub.fsr["time_series"][:, 0], 3)

    # epoch data
    eps = Epochs(
        sub,
        tmp_dat,
        times=sub.fsr["time_stamps"],
        events=sub.mrk,
        srate=80,
        max_force=sub.max_force,
    )
    eps.data = eps.data / eps.max_force

    # do epoching of data
    idx_exp_start = eps.events[eps.events["value"].str.match("block1")].index[0]
    eps.epoch(
        "trial_start*",
        idx_start=idx_exp_start,
        tmin=cfg_time_ep_fsr[0],
        tmax=cfg_time_ep_fsr[1],
        resample_epochs=True,
    )

    # create a binary pickle file to store normalised epochs of fsr data per subject
    tmp_fname = Path.joinpath(dir_prep,sub.id + "_clean_fsr_eps.pkl")

    with open(tmp_fname, 'wb') as handle:
        pickle.dump(eps, handle, protocol=pickle.HIGHEST_PROTOCOL)

    # define cfgs from loaded epochs
    cfg_filter = butter(
        cfg_bandpass_order, cfg_bandpass_freq, "bp", fs=eps.srate, output="sos"
    )
    cfg_epoch_timevec = eps.times
    cfg_fsr_psd_colors = cfg_colors["trial_colors"]

    # zscore per condition
    # extract viewing angle from epoch object
    tmp_view_angle = (
        eps.events["value"][eps.events["value"].str.contains("sfb")]
        .str.split("_")
        .str[3]
        .astype(float)
        .round(2)
    )
    psds_trmr = []
    psds_mov = []

    # prep figure
    fig = plt.figure(constrained_layout=True)
    gs = GridSpec(3, 2, figure=fig)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[1, 0])
    ax3 = fig.add_subplot(gs[2, 0])
    ax5 = fig.add_subplot(gs[:, 1], projection="3d")

    # prep single trial force data
    for i in range(eps.data.shape[2]):

        # append for overview
        id.append(sub.id)
        n_trial.append(i)

        # set plotting style for each epoch conditions
        if tmp_view_angle.iloc[i] == 0.02:
            ls = "dotted"
        elif tmp_view_angle.iloc[i] == 0.44:
            ls = "solid"

        if 0 <= i < 4:
            tmp_color = cfg_fsr_plot_colors[0]
            tmp_label = "visual"
            ax1.plot(
                cfg_epoch_timevec,
                eps.data[0, :, i],
                color=tmp_color,
                linewidth=cfg_plot_lw,
                alpha=0.5,
                linestyle=ls,
            )
        elif 4 <= i < 8:
            tmp_color = cfg_fsr_plot_colors[1]
            tmp_label = "auditiv-visual"
            ax2.plot(
                cfg_epoch_timevec,
                eps.data[0, :, i],
                color=tmp_color,
                linewidth=cfg_plot_lw,
                alpha=0.5,
                linestyle=ls,
            )
        elif 8 <= i < 12:
            tmp_color = cfg_fsr_plot_colors[2]
            tmp_label = "auditiv"
            ax3.plot(
                cfg_epoch_timevec,
                eps.data[0, :, i],
                color=tmp_color,
                linewidth=cfg_plot_lw,
                alpha=0.5,
                linestyle=ls,
            )

        idx_times_oi = np.logical_and(
            eps.times >= cfg_time_ep_fsr[0], eps.times <= cfg_time_ep_fsr[1]
        )
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
        tmp_psd_mov, freqs_mov = psd_array_welch(
            filt_trmr,
            eps.srate,
            fmin=cfg_mov_win_oi[0],
            fmax=cfg_mov_win_oi[1],
            n_fft=eps.srate * 3,
            n_per_seg=eps.srate * 3,
            n_overlap=eps.srate,
        )
        psds_trmr.append(tmp_psd_trmr)
        psds_mov.append(tmp_psd_mov)
        ax5.plot(
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
    poly = PolyCollection(verts, facecolors=cfg_fsr_psd_colors, alpha=0.7)
    ax5.add_collection3d(poly, zs=ep_range, zdir="y")

    # plot distribution and scatter
    m_psds_trmr = [
        np.mean(
            p.T[
                np.logical_and(
                    (freqs_trmr >= cfg_trmr_win_oi[0]),
                    (freqs_trmr <= cfg_trmr_win_oi[1]),
                )
            ]
        )
        for p in psds_trmr
    ]
    m_psds_mov = [
        np.mean(
            p.T[
                np.logical_and(
                    (freqs_mov >= cfg_mov_win_oi[0]), (freqs_mov <= cfg_mov_win_oi[1])
                )
            ]
        )
        for p in psds_mov
    ]

    # set line for raw force data
    axlines_with_text(ax1, 0.15, "Target force", axis="y")
    axlines_with_text(ax2, 0.15, "Target force", axis="y")
    axlines_with_text(ax3, 0.15, "Target force", axis="y")

    ax1.set_ylabel("Raw force [a.u.]")
    ax2.set_ylabel("Raw force [a.u.]")
    ax3.set_ylabel("Raw force [a.u.]")

    ax3.set_xlabel("Time[s]")
    ax2.sharex(ax3)
    ax1.sharex(ax3)
    ax1.set_xlim(cfg_time_trial)
    ax2.set_xlim(cfg_time_trial)
    ax3.set_xlim(cfg_time_trial)
    ax1.autoscale(enable=True, axis="y", tight=True)
    ax2.autoscale(enable=True, axis="y", tight=True)
    ax3.autoscale(enable=True, axis="y", tight=True)

    ax5.set_xlim(2, 14)
    ax5.view_init(35, -80)
    ax5.set_xlabel("Frequency [Hz]")
    ax5.set_zlabel(r"PSD [$\dfrac{V^2}{Hz}$]")
    ax5.set_ylabel("Trial number")

    fig.savefig(Path.joinpath(dir_plots, f"{sub.id}_fsr_all.png"))
    fig.clf()
    plt.close("all")

    # info per epoch
    con_view_ang.extend(tmp_view_angle)
    con_feedback.extend(
        eps.events["value"][eps.events["value"].str.contains("epoch")]
        .str.split("_")
        .str[1]
    )
    all_m_psds_trmr.extend(m_psds_trmr)
    all_m_psds_mov.extend(m_psds_mov)
    all_psds_trmr.extend(psds_trmr)

####################################################
# move to overview table
all_trials = {
    "ID": id,
    "Trial n": n_trial,
    "Feedback type": con_feedback,
    "Feedback angle": con_view_ang,
    "Power [4-12]": all_m_psds_trmr,
    "Power [1-3]": all_m_psds_mov,
}

all_trials = pd.DataFrame(all_trials)

# convert float to categorical
all_trials["Feedback angle"] = (
    all_trials["Feedback angle"].astype(str).map({"0.02": "low", "0.44": "high"})
)
all_trials["Group"] = all_trials["ID"].str[0]
fname = "all_trials_fsr.csv"

# delete file before saving
if Path.joinpath(dir_prep, fname).is_file():
    Path.joinpath(dir_prep, fname).unlink()
all_trials.to_csv(Path.joinpath(dir_prep, fname), index=False, index_label=False)

fname = "all_trials_fsr.csv"
all_trials = pd.read_csv(Path.joinpath(dir_prep, fname))
