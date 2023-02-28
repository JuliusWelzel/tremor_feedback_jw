function idx_hit = FindTargetHitFrc(eps,e)
% FindTargetHitFrc: Function to find when participant hit target and is
% within target range of +-3SD for 0.5 seconds. SD is derived from the epoch middle third (10 s) of each epoch. 
% Function is currently hard coded for a sampling rate of force sensor of 80Hz.
%     
% INPUT: 
%     eps:  Epoch strucure from project
%     e:    Epoch number
% OUTPUT:
%     idx_hit: sample index when target is "hit"
% 
% Author: (Julius Welzel, Universty of Kiel, 2021)

%% transfer from main script
frc     = eps.fs(e).frc;
time    = eps.fs(e).ts - eps.fs(e).ts;    
mf      = eps.frc_max;
con     = eps.con_frc(e);
frc_tar = mf*con;

%% get SD for threshold (CI intervall 3SD) from middle thirs (10 s) of epoch
n_sam = length(frc);

frc_sd      = std(frc(n_sam/3:(2*n_sam)/3)); 
sd_mltp     = 3;

%% loop window over timeseries
win_sz      = 40;
win_stp     = 5;
i           = 1;

idx_hit = [];
while length(frc) > i + win_sz
    flag_range = (frc(i:i+win_sz) < frc_tar + sd_mltp * frc_sd) & (frc(i:i+win_sz) > frc_tar - sd_mltp * frc_sd);
    i = i + win_stp;

    if sum(flag_range) == length(flag_range)
        idx_hit = i;
        break
    end
    
end

% if sliding window approach fails, use start of 2nd third as index 
if isempty(idx_hit);idx_hit = n_sam/3; end

%% Plot epoch with SDs and target window

% close all
% plot(time,frc)
% hline(frc_tar,'-k')
% 
% ylabel 'Force[a.u.]'
% xlabel 'Time[s]'
% 
% hline(frc_tar + sd_mltp * frc_sd,'--k')
% hline(frc_tar - sd_mltp * frc_sd,'--k')
% 
% vline(time(i))
% vline(time(i+win_sz))

end
