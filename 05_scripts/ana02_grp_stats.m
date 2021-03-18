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
PATHIN          = [MAIN '04_data\01_prep\'];
PATHOUT         = [MAIN '04_data\02_grp_stats\'];
PATHOUT_plots   = [MAIN '05_plots\01_single_subject\'];

if ~isdir(PATHOUT); mkdir(PATHOUT); end
if ~isdir(PATHOUT_plots); mkdir(PATHOUT_plots); end

list = dir(fullfile([PATHIN]));
list = list(contains({list.name},'epData'));
SUBJ = extractBefore({list.name},'_');


%% Loop over subs

for s = 1:numel(SUBJ)
    
    display(['Working in SUBJ ' SUBJ{s}])

    clear eps
    global eps
    load([PATHIN SUBJ{s} '_epData.mat']);
    
    global all_trials
eeg     
    waterfALL(s);
    save_fig(gcf,PATHOUT_plots,[SUBJ{s} '_ss_fft'],'fontsize',12,'figsize',[0 0 50 30]);
end


save([PATHOUT 'all_part_all_trials.mat'],'all_trials')
