import datetime
import os
from pathlib import Path
import pyxdf

from utilities.utl import find_lsl_stream

class SingleSubjectArcherRep:
    
    def __init__(self):
        # when the mediapipe is first started, it detects the hands. After that it tries to track the hands
        # as detecting is more time consuming than tracking. If the tracking confidence goes down than the
        # specified value then again it switches back to detection

        # generic infos
        self.id = None
        self.date = None
        self.time = None
        self.st_id = None
        self.st_ep_n = None
        self.st_scale = None
        self.st_feedback_con = None
        self.st_rmse = None
        self.st_pow_0_3 = None
        self.st_pow_4_12 = None
        self.st_ppl_sz_l = None
        self.st_ppl_sz_r = None
        
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
            max_f = 0
            print("No max force found")