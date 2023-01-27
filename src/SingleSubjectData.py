import datetime
import os
from pathlib import Path
from scipy import signal
import pandas as pd
import pyxdf
import numpy as np

from src.utl import find_lsl_stream, find_nearest

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
        
        # find max force if avaliable
        try:
            nms_mrk = [nm_mrk for mrk_ in self.mrk["time_series"] for nm_mrk in mrk_]
            self.max_force = float([nm for nm in nms_mrk if nm.startswith('max_force')][0].split('_')[2])
            print(f"Max force is {self.max_force:.0f} something for {self.id}")
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

    def __init__(self, subject, data, times, events=None, event_id=None, srate = None, max_force = None,):
        
        if not subject.eye:
            time_0_eye = np.nan
        else:
            time_0_eye = min(subject.eye["time_stamps"])     
        
        time_0 = np.nanmin([time_0_eye,min(subject.fsr["time_stamps"])])
        self.srate = srate
        self.max_force = max_force

        # prep inputs
        if data.ndim == 1:
            data = data[:,None]
        self.data    = np.transpose(np.asanyarray(data,dtype=np.float64))
        self.times   = np.asanyarray(times - time_0,dtype=np.float64)  # first sample is time 0

        # sort according to timestamps
        idx_ts = np.argsort(self.times)
        self.data = self.data[:,idx_ts]   
        self.times = self.times[idx_ts]

        # translate events from xdf to pd
        events_value    = [nm_mrk for mrk_ in events["time_series"] for nm_mrk in mrk_]
        events_time     = events["time_stamps"] - time_0 # relate events to start at 0

        self.events = pd.DataFrame(list(zip(events_value, events_time)),
                columns =['value', 'time'])

        # check output data
        if  times.shape[0] != data.shape[0]:
            raise ValueError('Data and times have different amount of samples')
        if data.ndim == 2 and events and event_id:
            print('Data will be epoched to ' + event_id)
        if data.ndim != 3 and events and event_id:
            raise ValueError('Data must be a 3D array of shape (n_channels, '
                            'n_samples, n_epochs)')
        if not srate:
            raise AttributeError('Sampling rate must be spcified')
        
    def epoch(self, event_id, idx_start = 0, tmin=-0.2, tmax=0.5, resample_epochs = False, time_offset = 0):

        if self.data.ndim == 3:
            raise ValueError('Data has already been epoched')

        if not event_id:
            raise AttributeError('Specify event_id for epoching')
    
        self.events = self.events.iloc[idx_start:]
        # extract times for mathcing events
        idx_event_id = self.events[self.events["value"].str.match(event_id)].index
        if not idx_event_id.any():
            raise ValueError ('No matching event value found')

        # find time stamps closest to events_oi in data times
        ts_ep_events = self.events["time"][idx_event_id]

        idx_event_id_match = []
        for ts in ts_ep_events:
            idx = find_nearest(self.times,ts)
            idx_event_id_match.append(idx)

        # cfgs for epoching
        n_epochs = len(idx_event_id_match)
        ep_win_to_start = int(tmin * self.srate)
        ep_win_to_end = int(tmax * self.srate)
        n_samples_epoch = abs(ep_win_to_start) + ep_win_to_end
        data_epoched = np.ones(shape=(self.data.shape[0], int(n_samples_epoch ), n_epochs))

        # specify time vector for epoch 
        self.times = np.linspace(0, int(n_samples_epoch / self.srate), n_samples_epoch ) + time_offset

        # do the actual epoching
        for i,idx in enumerate(idx_event_id_match):
            tmp_epoch = []
            tmp_epoch = self.data[:,idx + ep_win_to_start:idx + ep_win_to_end]

            if resample_epochs:
                tmp_epoch = signal.resample(tmp_epoch,n_samples_epoch, axis = 1)
            data_epoched[:,:,i] = tmp_epoch

        self.data = data_epoched
        

        

        