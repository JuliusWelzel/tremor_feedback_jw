"""
===========
Config file
===========

Configuration parameters for the study.
"""

import os
from socket import getfqdn
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

def define_dir(root, name):
    """define_dir create path handle and creates dir if not existend.

    Args:
        root (str): root to directory of interest
        name (str): name of directory

    Returns:
        pathlib.Path: Pathlib handle of dir
    """
    dir_oi = Path.joinpath(root, name)  # create path
    Path.mkdir(dir_oi, parents=False, exist_ok=True)
    return dir_oi


###############################################################################
# Determine which user is running the scripts on which machine and set the path
# where the data is stored and how many CPU cores to use.

user = os.getlogin()  # Username of the user running the scripts
host = getfqdn()  # Hostname of the machine running the scripts

if user == "User":
    # Julius Workstation
    dir_proj = Path(r"C:\Users\User\Desktop\kiel\tremor_feedback_jw")
elif: user == 'juliu'
    # Julius Laptop
    dir_proj = Path(r"C:\Users\juliu\Desktop\kiel\tremor_feedback_jw")
else:
    raise RuntimeError(
        "Please edit src/config.py and set the dir_proj "
        "variable to point to the location where the data "
        "should be stored."
    )

###############################################################################
# These are relevant directories which are used in the analysis.

# (import) helper functions
dir_proj = Path(r"C:\Users\User\Desktop\kiel\tremor_feedback_jw\src").parent.absolute()
dir_rawdata = define_dir(Path.joinpath(dir_proj, "data"), "00_raw")
dir_prep = define_dir(Path.joinpath(dir_proj, "data"), "01_prep")
dir_stats = define_dir(Path.joinpath(dir_proj, "data"), "02_stats")
dir_plots_single_trial = define_dir(Path.joinpath(dir_proj, "plots"), "01_single_trial")
dir_plots_group_cmpr = define_dir(Path.joinpath(dir_proj, "plots"), "02_group_comparisons")

###############################################################################
# These are all the relevant parameters for the analysis.

# Band-pass filter limits.
cfg_bandpass_freq = [0.1, 12]  # Hz
cfg_bandpass_order = 5  # filter order

# Frequency window of interest for tremor data
cfg_trmr_win_oi = [4, 12]  # Hz

# Frequency window of interest for volentary movement data
cfg_mov_win_oi = [0.1, 3]  # Hz

# times for baseline (bl) and epoch (ep)
cfg_time_bl = [-10, -2]  # s
cfg_time_trial = [5, 20]  # s
cfg_time_ep_fsr = [0, 30]  # s
cfg_time_ep_pupil = [-12, 30]  # s

###############################################################################
# These are all the relevant colors settings for the analysis


condition_colors = plt.cm.viridis(np.linspace(0, 1, 8))
condition_colors = condition_colors[[0,4,7],:]
#trial_colors = plt.cm.viridis(np.linspace(0, 1, 12))
trial_colors = condition_colors.repeat(4,0)
group_colors = plt.cm.magma(np.linspace(0, 1, 4))[[1,2],:]

cfg_colors = {"condition_colors": condition_colors, "trial_colors": trial_colors, "group_colors": group_colors}