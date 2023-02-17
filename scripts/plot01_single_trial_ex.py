%reload_ext autoreload
%autoreload 2

import os
import numpy as np
import pandas as pd
from pathlib import Path
from scipy.signal import medfilt, butter, sosfilt
import matplotlib.pyplot as plt
from matplotlib.collections import PolyCollection
from matplotlib.gridspec import GridSpec
from matplotlib import patches
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
    cfg_mov_win_oi
)

# import relevant dirs
from src.config import dir_rawdata, dir_prep, dir_plots
from src.utl import get_channel_labels_ppl_xdf, axlines_with_text
import src.pupil_prep as pp

print(f"Data imported from {dir_rawdata}")

# Increase the resolution of all the plots below
bundles.beamer_moml()
plt.rcParams.update(
    {"figure.dpi": 200, "figure.facecolor": "w", "figure.figsize": (15, 10)}
)

# set params for epoch processing and plotting for force data
cfg_pupil_plot_colors = plt.cm.viridis(np.linspace(0, 1, 3))
cfg_plot_lw = 1.5
cfg_idx_eye = 21

# pupil preprocessing
cfg_conv_kernel_sz = 100  # samples
cfg_kernel_smoothing = Gaussian1DKernel(stddev=cfg_conv_kernel_sz)

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
per_bad_samples = []
ppl_size = []
bl_sizes = []

####################################################
# prep every participant
for f in tmp_fnms:
    sub = SubjectData()
    sub.load_data(dir_rawdata,f)

    if not sub.eye:
        print(f'No pupil data found for {sub.id}')
        continue

    # skip participant if more than 25% of pupil data is artifact (Murphy, 2014)
    per_bad_diff = np.sum(np.diff(sub.eye["time_series"][:,cfg_idx_eye]) > 0.075) / len(sub.eye["time_series"][:,0]) 
    per_bad_dia = np.sum(sub.eye["time_series"][:,cfg_idx_eye] < 1.5) / len(sub.eye["time_series"][:,0])  
    if per_bad_diff > 0.25 or per_bad_dia > 0.25:
        flag_dataset_artifact = True

    # extract ppl chn names
    nms_ppl = get_channel_labels_ppl_xdf(sub.eye)

    # epoch data
    eps = Epochs(sub,sub.eye["time_series"],times=sub.eye["time_stamps"], events=sub.mrk, srate = sub.srate_ppl)
    idx_exp_start   = eps.events[eps.events["value"].str.match('block1')].index[0]
    eps.epoch('end_trial', idx_start=idx_exp_start,tmin=cfg_time_ep_pupil[0],tmax=cfg_time_ep_pupil[1], time_offset=cfg_time_ep_pupil[0])
    eps.data[eps.data == 0] = np.nan

    # cfgs for epoched data
    ch_oi = ['diameter1_3d']
    idx_ch_oi = [nms_ppl.index(key) for key in ch_oi]   

    tmp_view_angle = eps.events["value"][eps.events["value"].str.contains('sfb') ].str.split('_').str[3].astype(float).round(2)

    fig, axd = plt.subplot_mosaic([['top', 'top'],['left', 'right']],
                                constrained_layout=True)
    # prep single trial pupil data
    for i in range(eps.data.shape[2]):
            
        data_median  =  np.nanmedian(eps.data[idx_ch_oi,:,i])
        data_std     = np.nanstd(eps.data[idx_ch_oi,:,i])
        lower_thresh = data_std * -1.5
        upper_thresh = data_std * 1.5

        if 0 <= i < 4:
            tmp_color = cfg_pupil_plot_colors[0]
            tmp_label = 'visual'
        elif 4 <= i < 8:
            tmp_color = cfg_pupil_plot_colors[1] 
            tmp_label = 'auditiv-visual'
        elif 8 <= i <12:
            tmp_color = cfg_pupil_plot_colors[2]
            tmp_label = 'auditiv'      
        
        id.append(sub.id)
        n_trial.append(i)

        diameter = np.squeeze(eps.data[idx_ch_oi,:,i] - data_median)

        idx_outlier = np.logical_or(diameter < lower_thresh, diameter > upper_thresh)
        idx_low_conf = eps.data[0,:,i] < 0.5

        per_bad_diff_ep = np.sum(np.diff(eps.data[cfg_idx_eye,:,i]) > 0.075) / len(eps.data[:,:,i]) 
        per_bad_dia_ep = np.sum(eps.data[cfg_idx_eye,:,i] < 1.5) / len(eps.data[:,:,i]) 
        per_bad_conf_ep = np.sum([idx_low_conf,idx_outlier]) / len(idx_low_conf)
        per_bad_samples.append(max(per_bad_diff_ep, per_bad_dia_ep, per_bad_conf_ep))

        sparse_diam = np.where(np.logical_or(idx_outlier,idx_low_conf),np.nan,diameter)

        # use kernel for convolution and interpolate NaNs
        smooth = convolve_fft(sparse_diam.T,cfg_kernel_smoothing,nan_treatment = 'interpolate', boundary = 'wrap')

        # do baseline correction
        bl_diam = np.nanmedian(sparse_diam[np.logical_and(eps.times > cfg_time_bl[0],eps.times < cfg_time_bl[1])])
        bl_sizes.append(bl_diam)
        smooth = smooth - bl_diam
        tmp_pupil_size = np.mean(smooth[np.logical_and(eps.times > cfg_time_trial[0],eps.times < cfg_time_trial[1])])
        ppl_size.append(tmp_pupil_size)

        epoch_timevec = np.linspace(min(eps.times),max(eps.times),len(eps.times))

        if tmp_view_angle.iloc[i] == .02:
            ls = 'dotted'
        elif tmp_view_angle.iloc[i] == .44:
            ls = 'solid'

        if i in [0,4,8]:
            axd["top"].plot(epoch_timevec,smooth,color=tmp_color,linewidth=cfg_plot_lw, alpha=.5, linestyle = ls, label=tmp_label)
        else:
            axd["top"].plot(epoch_timevec,smooth,color=tmp_color,linewidth=cfg_plot_lw, alpha=.5, linestyle = ls)


    # info per epoch
    con_view_ang.extend(tmp_view_angle)
    con_feedback.extend(eps.events["value"][eps.events["value"].str.contains('epoch') ].str.split('_').str[1])

    sub_trials = pd.DataFrame()
    sub_trials["ppl_size"] = ppl_size[-11:]
    sub_trials["feedback_condition"] = con_feedback[-11:]
    sub_trials["bl_sizes"] = bl_sizes[-11:]

    # plot all trials and histograms of BL and Pupil size
    ymin, ymax = axd["top"].get_ylim()
    xmin, xmax = axd["top"].get_xlim()
    cfg_patch_trial = patches.Rectangle((cfg_time_trial[0],ymin),np.diff(cfg_time_trial),(ymax + np.abs(ymin)),alpha = .1, color = 'grey')
    
    axd["top"].axvline(0,c='k')
    axd["top"].add_patch(cfg_patch_trial)
    axd["top"].annotate("Trial average", (np.sum(cfg_time_trial) * .5, ymax * .9), color='Black', weight='bold', fontsize=10, ha='center', va='top')
    axlines_with_text(axd["top"],cfg_time_bl[0], 'BL start', axis='x')
    axlines_with_text(axd["top"],cfg_time_bl[1], 'BL end', axis='x')
    axd["top"].set_xlabel('Time[s]')
    axd["top"].set_ylabel('Baseline corrected diameter [mm^2]')
    axd["top"].set_title(f"{sub.id} pupil epochs")
    axd["top"].set_xlim([cfg_time_ep_pupil[0] - 1, cfg_time_ep_pupil[1]])
    axd["top"].legend(loc = 2) # set legend upper left 
    
    
    sns.kdeplot(data = sub_trials, x = "bl_sizes", hue= "feedback_condition", ax = axd["left"], fill=True, common_norm=False, palette=cfg_pupil_plot_colors,alpha=.5, linewidth=0)
    axd["left"].set_title('Baseline sizes')
    

    sns.kdeplot(data = sub_trials, x = "ppl_size", hue= "feedback_condition", ax = axd["right"], fill=True, common_norm=False, palette=cfg_pupil_plot_colors,alpha=.5, linewidth=0)
    axd["right"].set_title('Pupil sizes')
    
    fig.tight_layout()
    fig.savefig(Path.joinpath(dir_plots,f"{sub.id}_pupil_epochs.png"))
    fig.clf()

####################################################
# move to overview table
all_trials = {"ID": id, "Trial n": n_trial, "Feedback type": con_feedback, "Feedback angle": con_view_ang, "Pupil size": ppl_size, "Percentage bad pupil samples": per_bad_samples}
all_trials = pd.DataFrame(all_trials)

all_trials["Feedback angle"] = all_trials["Feedback angle"].astype(str).map({'0.02': 'low', '0.44': 'high'})
all_trials["Group"] = all_trials["ID"].str[0]
all_trials.head()

all_trials = {"ID": id, "Trial n": n_trial, "Feedback type": con_feedback, "Feedback angle": con_view_ang, "Pupil size": ppl_size, "Percentage bad pupil samples": per_bad_samples}
all_trials = pd.DataFrame(all_trials)

# convert float to categorical

all_trials["Feedback angle"] = all_trials["Feedback angle"].astype(str).map({'0.02': 'low', '0.44': 'high'})
all_trials["Group"] = all_trials["ID"].str[0]
fname = "all_trials_pupil.csv"

# delete file before saving
if Path.joinpath(dir_prep,fname).is_file():
    Path.joinpath(dir_prep,fname).unlink()
all_trials.to_csv(Path.joinpath(dir_prep,fname), index=False, index_label=False)


from scipy.stats import ttest_ind
from scipy import stats
df = all_trials
ppl_z = np.abs(stats.zscore(df['Pupil size']))
df = df[ppl_z <  3]
df_stats = df[df["Percentage bad pupil samples"] > 0.5]


####################################################
# check diffs
low_vo = df_stats[np.logical_and(df_stats["Feedback angle"]=='low',df_stats["Feedback type"]=='vo')]
high_vo = df_stats[np.logical_and(df_stats["Feedback angle"]=='high',df_stats["Feedback type"]=='vo')]
low_av = df_stats[np.logical_and(df_stats["Feedback angle"]=='low',df_stats["Feedback type"]=='va')]
high_av = df_stats[np.logical_and(df_stats["Feedback angle"]=='high',df_stats["Feedback type"]=='va')]
low_ao = df_stats[np.logical_and(df_stats["Feedback angle"]=='low',df_stats["Feedback type"]=='ao')]
high_ao = df_stats[np.logical_and(df_stats["Feedback angle"]=='high',df_stats["Feedback type"]=='ao')]

#perform independent two sample t-test
t_vo, p_vo = ttest_ind(low_vo['Pupil size'],high_vo['Pupil size'])
t_av, p_av = ttest_ind(low_av['Pupil size'],high_av['Pupil size'])
t_ao, p_ao = ttest_ind(low_ao['Pupil size'],high_ao['Pupil size'])

print(f'Differences for group deltas in visual only for pupil size is t={t_vo:.2f}, p:{p_vo:.3f}')
print(f'Differences for group deltas in auditiv-visual only for pupil size is t={t_av:.2f}, p:{p_av:.3f}')
print(f'Differences for group deltas in auditiv only for pupil size is t={t_ao:.2f}, p:{p_ao:.3f}')

print(len(low_ao) + len(high_ao))
