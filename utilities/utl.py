import numpy as np
from scipy import signal
from scipy.interpolate import interp1d


def moving_average_window(data, win_size):
    """Implementation of moving average rolling window

    Args:
        data (ndarray): Any ndarray which is converted to numpy
        win_size (int): Window size for average

    Returns:
        avg_data (ndarray): Data after moving average has been used
    """
    sample = 0
    avg_data = np.array([])
    while sample < len(data):
        ret = np.nanmean(data[sample:sample+win_size])
        avg_data = np.append(avg_data,ret)
        sample += (win_size + 1)
    return avg_data

def fill_nan(data2fill):
    """
    interpolate to fill nan values
    """
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
        _, Pxx_spec = signal.welch(int_data, 30, window='hamming',nperseg=60, scaling='spectrum')        
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
    """'
    Find stream in xdf file based on stream name
    """
    
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
    return idx
    
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
        npad, _     = divmod(2 ** (new_size // max(orig_shape)),2)
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
    """
    check array edges and pad with closest mean
    """
    ind = np.where(~np.isnan(a))[0]
    first, last = ind[0], ind[-1]
    a[:first] = a[first]
    a[last + 1:] = a[last]
    
    # interpolate nans in array not at edges
    nans    = np.isnan(a)
    x       = lambda z: z.nonzero()[0]
    a[nans]= np.interp(x(nans), x(~nans), a[~nans])
    
    return a


def get_channel_labels_ppl_xdf(ppl):
    """This function returns the labels from the PupilLabs Code LSL outlet as used in the XDF file.

    Args:
        ppl (dict): stream type from PupilLabsLSL capture outlet

    Returns:
        nms_ppl(list): label names from LSL outlet (gitRepo)[https://github.com/labstreaminglayer/App-PupilLabs/tree/master/pupil_capture]
    """

    ch_info = ppl["info"]["desc"][0]["channels"][0]
    len(ch_info["channel"])

    nms_ppl = []
    for i,ch in enumerate(ch_info["channel"]):
        nms_ppl.append(ch.get('label')[0])

    return nms_ppl

def axlines_with_text(ax, ax_position, str_label, axis='x'):

    if axis not in ['x','y']:
        raise ValueError('axis specification msut be x or y')

    ymin, ymax = ax.get_ylim()
    xmin, xmax = ax.get_xlim()

    if axis == 'x':
        ax.axvline(ax_position, c='k',ls = '--', lw = .5)
        ax.text(x=ax_position, y=(ymax + ymin) / 2, s=str_label, ha='center', va='center',rotation='vertical', backgroundcolor='white')
    elif axis == 'y':
        ax.axhline(ax_position, c='k',ls = '--', lw = .5)
        ax.text(x=(xmax + xmin) / 2, y=ax_position, s=str_label, ha='center', va='center',rotation='horizontal', backgroundcolor='white')


def polygon_under_graph(x, y):
    """
    Construct the vertex list which defines the polygon filling the space under
    the (x, y) line graph. This assumes x is in ascending order.
    """
    return [(x[0], 0.), *zip(x, y), (x[-1], 0.)]

def remove_outliers(df,columns,n_std):
    for col in columns:
        print('Working on column: {}'.format(col))
        
        mean = df[col].mean()
        sd = df[col].std()
        
        df = df[(df[col] <= mean+(n_std*sd))]
        
    return df