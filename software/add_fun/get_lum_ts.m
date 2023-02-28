function [ts_task t_vec t_mrk] = get_lum_ts(pl,mrk,nm_task)
%get_task_ts - extract task time series
%   INPUTS:
%       pl = pupil labs lsl struct 
%       mrk = marker lsl struct
%       nm_task = name of experimental task
% 
%   OUTPUTS:
%       ts_task = time series of given task

% cfg
pl_srate    = 200;
chan_pd     = [21 22]; % 21 & 22 for pupil size in mm per eye
chan_CI     = 1; % ch with CI intervall for measurement 

% times of task parts
t_bl = 5;
t_task = 20*12;

% time vector
t_vec = linspace((t_bl)*-1,t_task,(t_bl+t_task)*pl_srate+1);

% extract data for cog load
idx_task = find(contains(mrk.time_series,nm_task));

% time series per task 
idx_start   = dsearchn(pl.time_stamps',mrk.time_stamps(idx_task));
ts_task     = pl.time_series(chan_pd,idx_start-(t_bl)*pl_srate:idx_start+t_task*pl_srate);

end

