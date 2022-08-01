# Script to check data format validity from tremor feedback paradigm

import pyxdf
import os
import numpy as np
from scipy import stats
from pathlib import Path
import sys
import datetime

from utilities.utl import find_lsl_stream, find_nearest
from utilities.pupil_prep import *
from utilities.SingleSubjectData import SingleSubjectArcherRep


# (import) helper functions
MAINPATH = Path(__file__).parent.absolute()
DATARAWPATH = Path.joinpath(MAINPATH, "04_data","00_raw")

f_list = os.listdir(DATARAWPATH)
str_match = 'archer'
fnms = [s for s in f_list if str_match in s]
f = fnms[12]

sub = SingleSubjectArcherRep()
sub.load_data(DATARAWPATH,f)
#for ix,f in enumerate(fnms):
    # load xdf file
    
streams, _ = pyxdf.load_xdf(os.path.join(DATARAWPATH,f))
fsr  = find_lsl_stream(streams, 'HX711')
mrk = find_lsl_stream(streams, 'PsychoPyMarkers')
eye = find_lsl_stream(streams, 'pupil_capture')


sub_id = f.split('_')[0]
fname = f
date = datetime.datetime.fromtimestamp(int(float(Path(os.path.join(DATARAWPATH,f)).stat().st_ctime))).date()
time = datetime.datetime.fromtimestamp(int(float(Path(os.path.join(DATARAWPATH,f)).stat().st_ctime))).time()

try:
    nms_mrk = [nm_mrk for mrk_ in mrk["time_series"] for nm_mrk in mrk_]
    max_f = float([nm for nm in nms_mrk if nm.startswith('max_force')][0].split('_')[2])
except:
    max_f = 0
    print("No max force found")
    
        
# epoch data
idxs_eps_end = [i for i,nm in enumerate(nms_mrk) if 'end_trial' in nm]
times_eps_end = mrk['time_stamps'][idxs_eps_end]

# eye tracking data
nms_label_pupillab =[nm_lb['label'][0] for nm_lb in eye['info']['desc'][0]['channels'][0]['channel']]

idx_diam0_3d =  nms_label_pupillab.index('diameter0_3d')
idx_diam1_3d =  nms_label_pupillab.index('diameter1_3d')
idx_conf =  nms_label_pupillab.index('confidence')

# (1) confidence threshold
idx_conf, _ = confidence_threshold(eye['time_series'][:,idx_diam0_3d], eye['time_series'][:,idx_conf], thr=0.5, doplot=False)
# (2) delete diameter velocity outliers
idx_vout, _ = delete_velocity_outliers(eye['time_series'][:,idx_diam0_3d], whsize=10, n_mad=3, doplot=False)
# (3) eyeblink detection (Hershman et al.)
idx_blinks, _ = blink_detection(eye['time_series'][:,idx_diam0_3d], w_smooth=9, doplot=False)

# apply all deletions
diam = eye['time_series'][:,idx_diam0_3d]
diam_corr = diam.copy()
idx_corr = list(idx_conf) + list(idx_vout) + list(idx_blinks)
idx_corr = list(set(idx_corr))
diam_corr[idx_corr] = np.nan
p_corr = 1.*len(idx_corr)/len(diam)
print(f"Total proportion of deleted (NaN) data points: {p_corr:.3f}")

plt.figure(figsize=(18,6),dpi = 300)
plt.plot(diam, '-k', lw=1, alpha=0.3, label='raw data')
plt.plot(diam_corr, '-b', lw=.5, alpha=1.0, label='clean data')
plt.title("All corrections applied")
plt.axvline(nms_mrk.index('block1'))
plt.legend(loc=1, fontsize=18)
plt.tight_layout()
plt.show()
