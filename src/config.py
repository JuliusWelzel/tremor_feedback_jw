"""
===========
Config file
===========

Configuration parameters for the study.
"""

import os
from socket import getfqdn
from pathlib import Path


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
else:
    raise RuntimeError(
        "Please edit src/config.py and set the dir_proj "
        "variable to point to the location where the data "
        "should be stored."
    )

###############################################################################
# These are relevant directories which are used in the analysis.

# (import) helper functions
dir_proj = Path("__file__").parent.absolute()
dir_rawdata = define_dir(Path.joinpath(dir_proj, "data"), "00_raw")
dir_prep = define_dir(Path.joinpath(dir_proj, "data"), "01_prep")
dir_stats = define_dir(Path.joinpath(dir_proj, "data"), "02_stats")

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
cfg_time_ep = [0, 30]  # s

# pupil preprocessing
cfg_conv_kernel_sz = 120  # samples
