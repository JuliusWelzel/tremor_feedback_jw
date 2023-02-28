function [ts_resam time_vec] = tsFullResam(ts,mrk1,mrk2,mk)
%tsBetweenMrks: return full resampled time series of force sensor data
%
%Input:
%           ts     = full input time series
%           mk     = LSL recorded marker structure from XDF
%
% OUTPUT:
%           ts_cut      = multichannel times series cut between two markers
%           time_vec = corresponding timesstamps
%
% Author: Julius Welzel, University of Kiel, September 2020
% Contact: j.welzel@nurologie.uni-kiel.de //
% https://github.com/JuliusWelzel/int_trmr_eeg


    % find positoin of first and last marker in timeseries
    [neg idx_start] = min((ts.time_stamps - mk.time_stamps(mrk1)).^2);
    [neg idx_end] = min((ts.time_stamps - mk.time_stamps(mrk2)).^2);

    if size(ts.time_series,1) < size(ts.time_series,2)
        ts_resam = ts.time_series(:,idx_start:idx_end);
        time_vec = ts.time_stamps(:,idx_start:idx_end);
    elseif size(ts.time_series,1) > size(ts.time_series,2)
        ts_resam = ts.time_series(idx_start:idx_end,:);
        time_vec = ts.time_stamps(idx_start:idx_end,:);

    end
    
end

