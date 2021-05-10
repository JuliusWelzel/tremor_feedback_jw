%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%         Extract single subject data for data quality 
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Intention tremor behavioural
% Data: int_trmr_eeg (Jos Becktepe, University of Kiel)
% Author: Julius Welzel, j.welzel@neurologie.uni-kiel.de

%% Set envir
global PATHIN
PATHIN          = [MAIN '04_data\01_prep\'];
PATHOUT         = [MAIN '04_data\02_grp_stats\'];
PATHOUT_plots   = [MAIN '06_plots\01_single_trial\'];

if ~isdir(PATHOUT); mkdir(PATHOUT); end
if ~isdir(PATHOUT_plots); mkdir(PATHOUT_plots); end

list = dir(fullfile([PATHIN]));
list = list(contains({list.name},'epData'));
SUBJ = extractBefore({list.name},'_');

load([PATHIN 'all_trials.mat'])
for i = 1:numel(all_trials)
   try
        nms_sub(i) = all_trials(i).ID(1);
   end
end

idx_empty = isempty({all_trials.ID})
%% Loop over subs

for s = 1:numel(SUBJ)
    
    display(['Working in SUBJ ' SUBJ{s}])

    clear eps
    load([PATHIN SUBJ{s} '_epData.mat']);
    
    eps = singleTrialPupil(s,eps);
%     get appropriate epochs here 
    
    figure
    for p = 1:numel(eps)
        
        hold on
        % pupil data
        ylabel 'BL_corrected pupil size [mm³]'
        
        %%
        close all
        plot(eps(p).ppl_trial(21,:))
        hold on 
        
        windowSize = 20; 
        b = (1/windowSize)*ones(1,windowSize);
        a = 1;
        y = filter(b,a,eps(p).ppl_trial(21,:));
        y(eps(e).ppl_trial(1,:) < 0.8) = NaN;
        plot(y)
        hold on 
        y_ = hampel(y,48,1);
        plot(y_)
        hold on
        plot(eps(p).ppl_trial(1,:))

%%

    end
        
        
    end
    
    % force sensor
    subplot(3,3,7)
    ylabel 'Scale [a.u.]'
    title 'Visual'
    save_fig(gcf,PATHOUT_plots,[SUBJ{s} '_pupil_data'],'fontsize',12,'figsize',[0 0 50 30]);


    waterfALL(all_trials,s);
    save_fig(gcf,PATHOUT_plots,[SUBJ{s} '_ss_fft'],'fontsize',12,'figsize',[0 0 50 30]);
end


save([PATHOUT 'all_part_all_trials.mat'],'all_trials')
