import numpy as np

from scipy import signal
from scipy.interpolate import interp1d


def moving_average_window(data, frames_per_angle) :
    s = 0
    avg_data = np.array([])
    while s < len(data):
        ret = np.nanmean(data[s:s+frames_per_angle])
        avg_data = np.append(avg_data,ret)
        s += (frames_per_angle + 1)
    return avg_data

def fill_nan(data2fill):
    '''
    interpolate to fill nan values
    '''
    inds = np.arange(data2fill.shape[0])
    good = np.where(np.isfinite(data2fill))
    if len(good[0]) > 1:        
        tmp_int = interp1d(inds[good], data2fill[good],bounds_error=False)
        dat_int = np.where(np.isfinite(data2fill),data2fill,tmp_int(inds))
    else:
        dat_int = np.zeros(data2fill.shape[0])
    return dat_int

def amp_per_angle(data,frames_per_angle,chn_idx):
    s = 1
    epoch_max_amp = np.array([])
    while s < len(data) - 1:
        tmp_data = data[s:s+frames_per_angle,chn_idx]
        int_data = fill_nan(tmp_data)
        f, Pxx_spec = signal.welch(int_data, 30, window='hamming',nperseg=60, scaling='spectrum')        
        epoch_max_amp = np.append(epoch_max_amp,Pxx_spec[0:4].sum())
        s += frames_per_angle
    return epoch_max_amp


def remove_outliers(an_array, std_dev):
    mean = np.mean(an_array)
    standard_deviation = np.std(an_array)
    distance_from_mean = abs(an_array - mean)
    max_deviations = std_dev
    outlier = distance_from_mean > max_deviations * standard_deviation
    an_array[outlier] = mean
    
    return an_array
 
    
def find_lsl_stream(streams,name):
    ''''
    Find stream in xdf file based on stream name
    '''
    
    stream_check = False
    for n in range(0,len(streams)):
        if len(streams[n]["time_series"]) > 0 and streams[n]["info"]["name"][0] == name:
            stream_oi = streams[n]
            stream_check = True

    if not stream_check:
        stream_oi = []
        print('Stream {} not found'.format(name))
            
                
    return stream_oi
    
def find_nearest(array, value):
    array = np.asarray(array)
    idx = (np.abs(array - value)).argmin()
    return int(np.where(array[idx] == array)[0])
    
###############################################################################
# implement padding for resampling
###############################################################################


def resample_mp_pos(pos_data, new_size, pad = False):
    """
    Resample mediapipe hand position channels, carefully.
    Parameters
    ----------
    pos_data : array, shape (n_samples,) or (n_stim_channels, n_samples)
        Position channels to resample.
    new_size : float
        Length of desired signal to be resampled to
    pad : boolean 
        Determine padding should be applied before resampling  
    Returns
    -------
    pos_resampled : array, shape (n_stim_channels, n_samples_resampled)
        The resampled position channels.
    """
    
    # check array dimensions
    orig_shape = pos_data.shape
    if orig_shape[0] > orig_shape[1]:
        pos_data = pos_data.T
    elif len(orig_shape) > 2:
        raise ValueError('Array should be 2 dimensional')
    
    # pad nan edges with closest value and interpoalte nan
    pos_data = fill_nan_edges(pos_data)
    
    npad  = 0
    # add padding if wanted
    if pad:
        npad, extra     = divmod(2 ** (new_size // max(orig_shape)),2)
        pos_data        = np.pad(pos_data,((0,0), (npad,npad)), mode = 'edge') 
        
    # calculate resampling factor (including padding)
    fac_resam       = new_size / max(orig_shape)
    npad_resam      = int(np.ceil(fac_resam * npad))
    new_size_pad    = new_size + (npad_resam * 2)
    
    
    # resample
    pos_resampled   = signal.resample(pos_data, new_size_pad, axis = 1)
    if not npad_resam == 0:
        pos_resampled   = pos_resampled[:,npad_resam:-npad_resam]      
    
    return pos_resampled
    
    

def fill_nan_edges(a):
    '''
    check array edges and pad with closest mean
    '''
    ind = np.where(~np.isnan(a))[0]
    first, last = ind[0], ind[-1]
    a[:first] = a[first]
    a[last + 1:] = a[last]
    
    '''
    interpolate nans in array not at edges
    '''
    nans    = np.isnan(a)
    x       = lambda z: z.nonzero()[0]
    a[nans]= np.interp(x(nans), x(~nans), a[~nans])
    
    return a


