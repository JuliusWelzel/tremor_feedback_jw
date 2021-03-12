%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%                       Extract Epochs
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Extract epochs from paradigm and store in MatLab struct
% Data: Jos Becktepe, University of Kiel)
% Author: Julius Welzel (j.welzel@neurologie.uni-kiel.de)

% define paths
PATHIN_raw = [path_data '00_raw' filesep];
PATHOUT_pre = [MAIN '04_Data' filesep '01_prep' filesep];

if ~exist(PATHOUT_pre)
  mkdir(PATHOUT_pre);
end

%% define config vars

cfg.filer.HP = 0.1;
cfg.filter.LP = 40;
cfg.exp.n_trials = 120;

save(cfg,[PATHOUT_pre 'cfg.mat']);
