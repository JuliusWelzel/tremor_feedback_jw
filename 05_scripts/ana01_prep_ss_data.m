%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%                       Extract behavioural data from pilot
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Intention tremor behave
% Data: int_trmr_eeg (Jos Becktepe, University of Kiel)
% Author: Julius Welzel, j.welzel@neurologie.uni-kiel.de

%% Set envir

PATHIN      = [MAIN '04_data\00_main_pilot\'];
PATHOUT     = [MAIN '04_data\01_prep_pilot\'];

if ~isdir(PATHOUT); mkdir(PATHOUT); end

list = dir(fullfile([PATHIN]));
list = list(contains({list.name},'_isometric_'));
SUBJ = extractBetween({list.name},'_','_iso');

nms_task = '_isometric_tremor';

%% Loop over subs

for s = [11,12]%1:numel(SUBJ)
    
    clear eps
    display(['Working in SUBJ ' SUBJ{s}])
    if strcmp(SUBJ{s},'p004') % skip corrupted datasets
        continue;
    end
    
    % load data
    tmp     = load_xdf([PATHIN 'pilot_' SUBJ{s} nms_task '.xdf']); %full xdf file

    emg = findLslStream(tmp,'Delsys');
    ppl = findLslStream(tmp,'pupil_capture');
    fsr = findLslStream(tmp,'HX711');
    mrk = findLslStream(tmp,'PsychoPyMarkers');

    % preprocess data
%     emg = prep_emg_it(emg);
%     ppl_prep = prep_ppl_it(ppl); %Improve new_time vector in the future
    
    %% Extract marker and max force
    
    idx_ep_all = find(contains(mrk.time_series,'epoch'));
        
    max_f = str2num(extractAfter(mrk.time_series{1},'max_force_'));
    if strcmp(SUBJ(s),'p001'); max_f = 7262; idx_ep_all(end) = [];  end


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
%         [eps(e).ppl_trial eps(e).ppl_ts]    = tsBetweenMrks(ppl_prep,idx_ep_all(e),idx_ep_all(e)+4,mrk);

        % extract per trial parts of emg
%         [eps(e).emg_trial eps(e).emg_ts]    = tsBetweenMrks(emg,idx_ep_all(e),idx_ep_all(e)+4,mrk);

    end
       

    save([PATHOUT SUBJ{s} '_epData.mat'],'eps');
    
    

end


