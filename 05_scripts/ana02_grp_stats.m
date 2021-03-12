%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%         Extract single subject data for group level stats
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Intention tremor behavioural
% Data: int_trmr_eeg (Jos Becktepe, University of Kiel)
% Author: Julius Welzel, j.welzel@neurologie.uni-kiel.de

%% Set envir
global PATHIN
PATHIN          = [MAIN '04_data\01_prep_pilot\'];
PATHOUT         = [MAIN '04_data\02_grp_stats\'];
PATHOUT_plots   = [MAIN '05_plots\01_all_pilot\'];

if ~isdir(PATHOUT); mkdir(PATHOUT); end
if ~isdir(PATHOUT_plots); mkdir(PATHOUT_plots); end

list = dir(fullfile([PATHIN]));
list = list(contains({list.name},'epData'));
SUBJ = extractBefore({list.name},'_');

%% set config for analysis
global cfg
cfg.EMG.BP = [30 200];


%% Loop over subs

for s = [10,11]%1:numel(SUBJ)
    
    display(['Working in SUBJ ' SUBJ{s}])

    clear eps
    global eps
    load([PATHIN SUBJ{s} '_epData.mat']);
    
    global all_trials
    [all_trials(s).sub,all_trials(s).fdbck_con,all_trials(s).frc_con,all_trials(s).scl,...
        all_trials(s).emg_pow_4_12,all_trials(s).emg_spec, all_trials(s).emg_freqs,...
        all_trials(s).fs_pow_4_12,all_trials(s).fs_spec,all_trials(s).fs_freqs,...
        all_trials(s).rmse_raw,all_trials(s).rmse_03,all_trials(s).rmse_412,all_trials(s).pow_412] = interpSingleTrialData(SUBJ{s});    
     
    waterfALL(s);
    save_fig(gcf,PATHOUT_plots,[SUBJ{s} '_ss_fft'],'fontsize',12,'figsize',[0 0 50 30]);
end


save([PATHOUT 'all_part_all_trials.mat'],'all_trials')
