%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%                       Extract Epochs
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Extract epochs from paradigm and store in MatLab struct
% Data: Jos Becktepe, University of Kiel)
% Author: Julius Welzel (j.welzel@neurologie.uni-kiel.de)

% define paths
PATHIN_raw = [MAIN '04_Data' filesep '00_raw' filesep];
PATHOUT_prep = [MAIN '04_Data' filesep '01_prep' filesep];

if ~exist(PATHOUT_prep);mkdir(PATHOUT_prep);end

list = dir(fullfile([PATHIN_raw]));
list = list(contains({list.name},'_isometric_tremor_loud'));
SUBJ = extractBefore({list.name},'_isometric_tremor_loud');

nms_task = '_isometric_tremor_loud';
%% define config vars

cfg.filer.HP = 0.1;
cfg.filter.LP = 40;
cfg.exp.n_trials = 120;

save(cfg,[PATHOUT_prep 'cfg.mat']);

%% Loop over subs

for s = 1:numel(SUBJ)
    
    display(['Working in SUBJ ' SUBJ{s}])
    
    % load data
    tmp     = load_xdf([PATHIN_raw SUBJ{s} nms_task '.xdf']); %full xdf file

    ppl = findLslStream(tmp,'pupil_capture');
    fsr = findLslStream(tmp,'HX711');
    mrk = findLslStream(tmp,'PsychoPyMarkers');

    % preprocess data
    ppl_prep = prep_ppl_it(ppl); %Improve new_time vector in the future
    
    %% Extract marker and max force
    
    idx_ep_all = find(contains(mrk.time_series,'epoch'));
        
    max_f = str2num(extractAfter(mrk.time_series{1},'max_force_'));

    eps.ID = SUBJ(s);
    eps.max_force = max_f;
    %% Cut epochs and all infos and seave results
    
    for e = 1:numel(idx_ep_all)-1
        
        % fill struct with info 
        eps(e).num          = e;
        eps(e).fdbck_con    = string(extractBetween(mrk.time_series{idx_ep_all(e)},'_','_'));
        eps(e).frc_con      = str2num(extractAfter(mrk.time_series{idx_ep_all(e)+3},'sfc_'));
        eps(e).scl          = str2num(string(extractBetween(mrk.time_series{idx_ep_all(e)+3},'sfb_','_sfc')));
        
        
        %% Extract time series idx_ep_all(e) is position of first marker per trial (epoch_"con")
        
        % extract trial info and marker
        [eps(e).mrk_trial  eps(e).mrk_ts]   = tsBetweenMrks(mrk,idx_ep_all(e),idx_ep_all(e)+4,mrk);
        eps(e).len_trial = eps(e).mrk_ts(end)-eps(e).mrk_ts(1);

        % extract per trial parts of force sensor
        [eps(e).fs_trial eps(e).fs_ts]      = tsBetweenMrks(fsr,idx_ep_all(e)+3,idx_ep_all(e)+4,mrk);
        
        % extract per trial parts of pupil labs
        [eps(e).ppl_trial eps(e).ppl_ts]    = tsBetweenMrks(ppl_prep,idx_ep_all(e),idx_ep_all(e)+4,mrk);


    end
       

%     save([PATHOUT SUBJ{s} '_epData.mat'],'eps');
    
    

end


