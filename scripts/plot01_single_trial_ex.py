from pathlib import Path
import pickle
import os

# import config variables
from src.plotting import single_trial_specs, single_trial_force_raw
from src.config import dir_prep

print(f"Data imported from {dir_prep}")

# find all relevant files
f_list_pupil = os.listdir(dir_prep)
str_match = "clean_pupil"
fnms_pupil = [s for s in f_list_pupil if str_match in s]

# find all relevant files
f_list_fsr = os.listdir(dir_prep)
str_match = "clean_fsr"
fnms_fsr = [s for s in f_list_fsr if str_match in s]
fnms_fsr = fnms_fsr[0:2]

# loop over all participants
for f in fnms_fsr:

    tmp_fname_fsr = Path.joinpath(dir_prep, f)
    with open(tmp_fname_fsr, 'rb') as handle_mocap:
        eps = pickle.load(handle_mocap)

    single_trial_force_raw(eps, f.split('_')[0]) # plot raw force trials
    single_trial_specs(eps, f.split('_')[0]) # plot specs of force data per trial