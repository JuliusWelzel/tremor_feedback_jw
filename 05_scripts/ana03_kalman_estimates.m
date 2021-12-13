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
PATHIN          = fullfile(MAIN,'04_data','01_prep');
PATHOUT         = fullfile(MAIN,'04_data','03_kalman_estimates');
PATHOUT_plots   = fullfile(MAIN,'06_plots','03_kalman_estimates');

if ~isdir(PATHOUT); mkdir(PATHOUT); end
if ~isdir(PATHOUT_plots); mkdir(PATHOUT_plots); end

list = dir(fullfile([PATHIN]));
list = list(contains({list.name},'epData'));
SUBJ = extractBefore({list.name},'_');

info    = table;
trials  = [];
ct      = 1;


% loop over participants
for s = 1:numel(SUBJ)
    if ~contains(SUBJ{s},{'p2','p3'})
        continue
    end
    
    load(fullfile(PATHIN,[SUBJ{s} '_epData.mat']));
    

    idx_exp = find(strcmp(eps.blk,"experiment"));
    
    for e = idx_exp
    
        % participant specific
        info.id(ct) =  string(SUBJ{s});
        
        % trial specific
        trials(ct,:) = eps.fs(e).pad_fs_dev;
        
        info.blk(ct) = eps.blk(e);
        info.mod(ct) = eps.con_fdbck(e);
        info.scl(ct) = eps.con_scl(e);
        
        ct = ct+1;
        
    end
        

end

%% plot

idx_low     = info.scl == min(info.scl);
idx_high    = info.scl == max(info.scl);
idx_vo      = strcmp(info.mod,"vo");

plot(mean(trials(idx_low & idx_vo,:),1),'Color',color.c_vo)
hold on
plot(mean(trials(idx_high & idx_vo,:),1),'Color',color.c_ao)
legend('low','high')