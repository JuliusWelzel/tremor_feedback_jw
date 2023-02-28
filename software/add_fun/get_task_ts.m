function [ts_task t_vec] = get_task_ts(pl,mrk,nm_task)
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
t_fc = 2;
t_task = 35-2;

% time vector
t_vec = linspace((t_bl+t_fc)*-1,t_task,(t_bl+t_fc+t_task)*pl_srate+1);

% extract data for cog load
idx_task = find(contains(mrk.time_series,nm_task));

% time series per task 
idx_start   = dsearchn(pl.time_stamps',mrk.time_stamps(idx_task));
ts_task     = pl.time_series(chan_pd,idx_start-(t_bl+t_fc)*pl_srate:idx_start+t_task*pl_srate);

% baseline corrected
m_bl = nanmean(pl.time_series(chan_pd,idx_start-6*pl_srate:idx_start-1*pl_srate),2);
ts_task = ts_task-m_bl;

end

