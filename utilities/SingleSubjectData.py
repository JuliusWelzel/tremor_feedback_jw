import datetime
import os
from pathlib import Path
from pandas import Int8Dtype, StringDtype
import pyxdf
import numpy as np

from utilities.utl import find_lsl_stream

class SubjectData:
    
    def __init__(self):
        # when the mediapipe is first started, it detects the hands. After that it tries to track the hands
        # as detecting is more time consuming than tracking. If the tracking confidence goes down than the
        # specified value then again it switches back to detection

        # generic infos
        self.id = None
        self.date = None
        self.time = None
        self.fname = None
        # exp infos
        self.max_force = None
        self.n_epochs = None
        self.n_trigger = None
        # hardware infos
        self.srate_fsr = None
        self.srate_ppl = None
        self.n_blinks = None
        self.per_bad_eye = None
        self.freq_tremor = None
        
    def load_data(self,datapath,fname):
        # extract generic infos from file
        self.id = fname.split('_')[0]
        self.date = datetime.datetime.fromtimestamp(int(float(Path(os.path.join(datapath,fname)).stat().st_mtime))).date()
        self.time = datetime.datetime.fromtimestamp(int(float(Path(os.path.join(datapath,fname)).stat().st_mtime))).time()
        self.fname = fname

        # load xdf file
        streams, _ = pyxdf.load_xdf(os.path.join(datapath,fname))
        self.fsr  = find_lsl_stream(streams, 'HX711')
        self.mrk = find_lsl_stream(streams, 'PsychoPyMarkers')
        self.eye = find_lsl_stream(streams, 'pupil_capture')
        
        # find amx force if avaliable
        try:
            nms_mrk = [nm_mrk for mrk_ in self.mrk["time_series"] for nm_mrk in mrk_]
            self.max_force = float([nm for nm in nms_mrk if nm.startswith('max_force')][0].split('_')[2])
            print(f"Max force is {self.max_force:.0f} something")
        except:
            self.max_force = np.nan
            print("No max force found")

        # exp infos
        idxs_eps_end = [i for i,nm in enumerate(nms_mrk) if 'end_trial' in nm]
        times_eps_end = self.mrk['time_stamps'][idxs_eps_end]
        self.n_epochs = len(idxs_eps_end)
        self.n_trigger = len(self.mrk["time_series"])

        # hardware infos ppl
        if self.eye:
            self.srate_ppl = len(self.eye["time_stamps"])/(self.eye["time_stamps"][-1]-self.eye["time_stamps"][0])
            self.per_bad_eye = round((sum(self.eye["time_series"][:,0]<.5) / len(self.eye["time_series"][:,0])) * 100 ,3)
        elif not self.eye:
            self.srate_ppl = np.nan
            self.per_bad_eye = np.nan

    def epoch(self):
        print(f"{self.n_epochs:.0f} full epochs found")



        
 
        
            
            

        


class TrialData:
    
    def __init__(self):
        # when the mediapipe is first started, it detects the hands. After that it tries to track the hands
        # as detecting is more time consuming than tracking. If the tracking confidence goes down than the
        # specified value then again it switches back to detection

        # generic infos
        self.id = None
        self.date = None
        self.time = None
        self.id = None
        self.scale = None
        self.feedback_con = None
        self.rmse = None
        self.pow_0_3 = None
        self.pow_4_12 = None
        self.ppl_sz_l = None
        self.ppl_sz_r = None
        
    def load_data(self,datapath,fname):
        # extract meta data from fname
        self.id = fname.split('_')[0]
        self.date = datetime.datetime.fromtimestamp(int(float(Path(os.path.join(datapath,fname)).stat().st_ctime))).date()
        self.time = datetime.datetime.fromtimestamp(int(float(Path(os.path.join(datapath,fname)).stat().st_ctime))).time()

        streams, _ = pyxdf.load_xdf(os.path.join(datapath,fname))
        fsr  = find_lsl_stream(streams, 'HX711')
        mrk = find_lsl_stream(streams, 'PsychoPyMarkers')
        eye = find_lsl_stream(streams, 'pupil_capture')
        
        try:
            nms_mrk = [nm_mrk for mrk_ in mrk["time_series"] for nm_mrk in mrk_]
            max_f = float([nm for nm in nms_mrk if nm.startswith('max_force')][0].split('_')[2])
            print(f"Max force is {max_f:.0f} something")
        except:
            max_f = np.nan
            print("No max force found")