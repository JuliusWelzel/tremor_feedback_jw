function [ts_cut samples_cut] = tsBetweenMrks(ts,mrk1,mrk2,mk)
%tsBetweenMrks: Extract time series of multiple channels between two given
%markers
%
%Input:
%           ts     = full input time series
%           mrk1   = first marker position in mk struct (starting point)
%           mrk2   = second marker position in mk struct (end point)
%           mk     = LSL recorded marker structure from XDF
%
% OUTPUT:
%           ts_cut      = multichannel times series cut between two markers
%           samples_cut = corresponding timesstamps
%
% Author: Julius Welzel, University of Kiel, September 2020
% Contact: j.welzel@nurologie.uni-kiel.de //
% https://github.com/JuliusWelzel/int_trmr_eeg


    % check if overlapping time points are present
    if mk.time_stamps(1) > ts.time_stamps(end) | mk.time_stamps(end) < mk.time_stamps(1)
        display('No overlapping time stamps')
        return
    end

    % find positoin of first and second marker in timeseries
    [neg idx_start] = min((ts.time_stamps - mk.time_stamps(mrk1)).^2);
    [neg idx_end] = min((ts.time_stamps - mk.time_stamps(mrk2)).^2);

    if size(ts.time_series,1) < size(ts.time_series,2)
        ts_cut = ts.time_series(:,idx_start:idx_end);
        samples_cut = ts.time_stamps(:,idx_start:idx_end);
    elseif size(ts.time_series,1) > size(ts.time_series,2)
        ts_cut = ts.time_series(idx_start:idx_end,:);
        samples_cut = ts.time_stamps(idx_start:idx_end,:);

    end
    
end

