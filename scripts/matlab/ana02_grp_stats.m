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
PATHIN_raw      = fullfile(MAIN,['04_data\00_raw']);
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

idx_empty = ismissing(nms_sub);

tab = table([all_trials.ID]',[all_trials.TrialNumber]',[all_trials.ForceCondition]',[all_trials.Scaling]',...
    [all_trials.FeedbackCondition]',[all_trials.AuditiveCondition]',...
    [all_trials.rmse]',[all_trials.out_rmse]',[all_trials.pow03]',[all_trials.pow412]',[all_trials.out_pow_412]',...
    [all_trials.ppl_sz_l]',[all_trials.out_ppl_sz_l]',[all_trials.ppl_sz_r]',[all_trials.out_ppl_sz_r]');

tab.Properties.VariableNames = {'ID','n','ForceCondition','Scaling','FeedbackCondition','AuditiveCondition',...
    'rmse','Outlier RMSE','Power [0-3 Hz]','Power [4-12 Hz]','Outlier Power',...
    'Pupilsize left','Outlier Ppl l','Pupilsize right','Outlier Ppl r'};

tab.ViewingAngle = atand((tab.Scaling * .24) / .95);
writetable(tab,[PATHOUT 'overview_all_trials.csv'])

%% add clinical data

fdbk = tab(:,{'ID','Scaling','rmse','Power [4-12 Hz]'});
varfun(@mean,fdbk,'InputVariables',{'ID','Scaling'},...
       'GroupingVariables',{'rmse','Power [4-12 Hz]'})
clinical = readtable(fullfile(PATHIN_raw,'trial2_provisional_demographics_and_score_data_21_08_02_mg.xlsx'))