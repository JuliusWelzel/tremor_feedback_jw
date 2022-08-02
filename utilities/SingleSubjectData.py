import datetime
import os
from pathlib import Path
from pandas import Int8Dtype, StringDtype
import pyxdf
import numpy as np

from utilities.utl import find_lsl_stream, find_nearest

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

    def prep_pupil(self):
        # find all exp epochs markers
        nms_mrk         = [nm_mrk for mrk_ in self.mrk["time_series"] for nm_mrk in mrk_]
        idx_exp_start   = nms_mrk.index("block1")
        idxs_eps_end    = [i for i,nm in enumerate(nms_mrk) if 'end_trial' in nm and i > idx_exp_start]
        idxs_eps_start  =[idx -1 for idx in idxs_eps_end]
        times_eps_start = self.mrk['time_stamps'][idxs_eps_start]
        times_eps_end   = self.mrk['time_stamps'][idxs_eps_end]

        # loop over epochs end markers to process full epochs
        idx_ep_start    = []
        idx_ep_end      = []
        for e_ts in times_eps_end:
            idx_ep_end.append(find_nearest(self.mrk["time_stamps"],e_ts))
            
            print(self.mrk["time_stamps"][idx_ep_end][-1]-self.mrk["time_stamps"][idx_ep_end[-1] - 2])
        



        
 
        
            
            

        


class Epochs:
    """Epochs object from numpy array.

    Parameters
    ----------
    data : array, shape (n_epochs, n_channels, n_times)
        The channels' time series for each epoch. See notes for proper units of
        measure.
    events : None | array of int, shape (n_events, 3)
        The events typically returned by the read_events function.
        If some events don't match the events of interest as specified
        by event_id, they will be marked as 'IGNORED' in the drop log.
        If None (default), all event values are set to 1 and event time-samples
        are set to range(n_epochs).
    tmin : float
        Start time before event. If nothing provided, defaults to 0.
    event_id : int | list of int | dict | None
        The id of the event to consider. If dict,
        the keys can later be used to access associated events. Example:
        dict(auditory=1, visual=3). If int, a dict will be created with
        the id as string. If a list, all events with the IDs specified
        in the list are used. If None, all events will be used with
        and a dict is created with string integer names corresponding
        to the event id integers.
    """

    def __init__(self, data, times, events=None, event_id=None):
        
        # prep inputs
        data    = np.asanyarray(data,dtype=np.float64)
        times   = np.asanyarray(times,dtype=np.float64)     

        if isinstance(events,list):
            nms_mrk     = [nm_mrk for mrk_ in events["time_series"] for nm_mrk in mrk_]

        ## check inputs
        # check input data
        if  times.shape[0] != data.shape[0]:
            raise ValueError('Data and times have different amount of samples')
        if data.ndim == 2 and events and not event_id:
            raise AttributeError('Specify events to epoch the data in event_id')
        if data.ndim != 3 and events:
            raise ValueError('Data must be a 3D array of shape (n_channels, '
                             'n_samples, n_epochs)')
        # check input events
        if not any(events.index(event_id)):
            raise AttributeError('Event for epoching not present in events')

        
    def epoch(self, event_id=None, tmin=-0.2, tmax=0.5):
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