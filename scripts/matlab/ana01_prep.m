%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%                       Extract Epochs
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Extract epochs from paradigm and store in MatLab struct
% Data: Jos Becktepe, University of Kiel)
% Author: Julius Welzel (j.welzel@neurologie.uni-kiel.de)

% define paths
PATHIN_raw = fullfile(MAIN,'04_Data','00_raw');
PATHOUT_prep = fullfile(MAIN,'04_Data','01_prep');
PATHOUT_plot = fullfile(MAIN,'06_plots','01_single_trial');

if ~exist(PATHOUT_prep);mkdir(PATHOUT_prep);end
if ~exist(PATHOUT_plot);mkdir(PATHOUT_plot);end

global SUBJ s prob_info % set global for transfer in function

list = dir(fullfile([PATHIN_raw]));
list_s = list(contains({list.name},'_isometric_tremor_loud'));
SUBJ = extractBefore({list_s.name},'_isometric_tremor_loud');

prob_info = readtable([PATHIN_raw list(contains({list.name},'rekrutierung')).name]);

load([PATHOUT_prep 'all_trials.mat'])

%% Loop over subs
 
for s = 1:numel(SUBJ)
    
    clear eps
    display(['Working on SUBJ ' SUBJ{s}])
    
    if contains(SUBJ{s},{'p110','p111','p115','p117'});continue;end  
    
    % load data from first paradigm
    tmp_loud     = load_xdf([PATHIN_raw SUBJ{s} '_isometric_tremor_loud.xdf']); %full xdf file

    ppl_loud = findLslStream(tmp_loud,'pupil_capture');
    fsr_loud = findLslStream(tmp_loud,'HX711');
    mrk_loud = findLslStream(tmp_loud,'PsychoPyMarkers');
    
    %% Extract marker and max force
    fsr_loud.time_series = hampel(fsr_loud.time_series,1);
    idx_ep_all = find(contains(mrk_loud.time_series,'epoch'));
        
    max_f = str2num(extractAfter(mrk_loud.time_series{1},'max_force_'));
    if isempty(max_f)
        max_f = GetMaxForce(prob_info,SUBJ{s});
    end
    
    eps.ID = SUBJ(s);
    eps.max_force = max_f;
    
    idx_blk_act     =  find(contains(mrk_loud.time_series,'block1'));
    idx_blk_pas     =  find(contains(mrk_loud.time_series,'block3'));
    if isempty(idx_blk_pas);idx_blk_pas = numel(mrk_loud.time_series);end

    n_ep_train      = sum(strcmp(mrk_loud.time_series(1:idx_blk_act),'end_trial')); 
    n_ep_activ      = sum(strcmp(mrk_loud.time_series(idx_blk_act:idx_blk_pas),'end_trial')); 

    %% Cut epochs and all infos and save results
    
    for e = 1:numel(idx_ep_all)-1
        
        % fill struct with info 
        eps(e).num          = e;
        eps(e).fdbck_con    = string(extractBetween(mrk_loud.time_series{idx_ep_all(e)},'_','_'));
        eps(e).frc_con      = str2num(extractAfter(mrk_loud.time_series{idx_ep_all(e)+3},'sfc_'));
        eps(e).scl          = str2num(string(extractBetween(mrk_loud.time_series{idx_ep_all(e)+3},'sfb_','_sfc')));
        
        
        if e <= n_ep_train;
            eps(e).block = "training";
        elseif e > n_ep_train & e <= n_ep_activ;
            eps(e).block = "active";
        elseif e > n_ep_activ;
            eps(e).block = "passive";  
        end
 
 
        
        %% Extract time series idx_ep_all(e) is position of first marker per trial (epoch_"con")
        
        % extract trial info and marker
        [eps(e).mrk_trial  eps(e).mrk_ts]   = tsBetweenMrks(mrk_loud,idx_ep_all(e),idx_ep_all(e)+4,mrk_loud);
        eps(e).len_trial = eps(e).mrk_ts(end)-eps(e).mrk_ts(end-1);

        % extract per trial parts of force sensor
        [eps(e).fs_trial eps(e).fs_ts]      = tsBetweenMrks(fsr_loud,idx_ep_all(e)+3,idx_ep_all(e)+4,mrk_loud);
        
        % extract per trial parts of pupil labs
        [eps(e).ppl_trial eps(e).ppl_ts]    = tsBetweenMrks(ppl_loud,idx_ep_all(e),idx_ep_all(e)+4,mrk_loud);

        
        %% extract single trial values
        eps(e).rmse_raw = real(sqrt(mean(...
            eps(e).fs_trial(80:end) - eps(e).frc_con * eps(1).max_force ...
            / (eps(e).frc_con * eps(1).max_force).^2)));
        eps(e).AudioCondition = 'Loudness';
        
        %% extract power values per trial 
        eps(e).pow03    = bandpower(eps(e).fs_trial / (eps(e).frc_con * eps(1).max_force),80,[0.1 3]);        
        eps(e).pow412   = bandpower(eps(e).fs_trial / (eps(e).frc_con * eps(1).max_force),80,[4 12]);

    end
       
    %% load data from second paradigm
    
    tmp_fly     = load_xdf([PATHIN_raw SUBJ{s} '_isometric_tremor_fly.xdf']); %full xdf file

    ppl_fly = findLslStream(tmp_fly,'pupil_capture');
    fsr_fly = findLslStream(tmp_fly,'HX711');
    mrk_fly = findLslStream(tmp_fly,'PsychoPyMarkers');

    %% Prep fsr signal
    fsr_fly.time_series = hampel(fsr_fly.time_series,1);
    idx_ep_all = find(contains(mrk_fly.time_series,'epoch'));
    cont_e = numel(eps) + 1;
    
    for e = 1:numel(idx_ep_all)
        
        % fill struct with info 
        eps(cont_e).num          = e;
        eps(cont_e).fdbck_con    = string(extractBetween(mrk_fly.time_series{idx_ep_all(e)},'_','_'));
        eps(cont_e).frc_con      = str2num(extractAfter(mrk_fly.time_series{idx_ep_all(e)+3},'sfc_'));
        eps(cont_e).scl          = str2num(string(extractBetween(mrk_fly.time_series{idx_ep_all(e)+3},'sfb_','_sfc')));
        
        idx_blk_act     =  find(contains(mrk_loud.time_series,'block1'));
        idx_blk_pas     =  find(contains(mrk_loud.time_series,'block3'));
        if isempty(idx_blk_pas);idx_blk_pas = numel(mrk_loud.time_series);end;

        n_ep_train      = sum(strcmp(mrk_loud.time_series(1:idx_blk_act),'end_trial')); 
        n_ep_activ      = sum(strcmp(mrk_loud.time_series(idx_blk_act:idx_blk_pas),'end_trial')); 

        if e <= n_ep_train;
            eps(cont_e).block = "training";
        elseif e > n_ep_train & e <= n_ep_activ;
            eps(cont_e).block = "active";
        elseif e > n_ep_activ;
            eps(cont_e).block = "passive";  
        end
 
 
        
        %% Extract time series idx_ep_all(e) is position of first marker per trial (epoch_"con")
        
        % extract trial info and marker
        [eps(cont_e).mrk_trial  eps(cont_e).mrk_ts]   = tsBetweenMrks(mrk_fly,idx_ep_all(e),idx_ep_all(e)+4,mrk_fly);
        eps(cont_e).len_trial = eps(cont_e).mrk_ts(end)-eps(cont_e).mrk_ts(end-1);

        % extract per trial parts of force sensor
        [eps(cont_e).fs_trial eps(cont_e).fs_ts]      = tsBetweenMrks(fsr_fly,idx_ep_all(e)+3,idx_ep_all(e)+4,mrk_fly);
        
        % extract per trial parts of pupil labs
        [eps(cont_e).ppl_trial eps(cont_e).ppl_ts]    = tsBetweenMrks(ppl_fly,idx_ep_all(e),idx_ep_all(e)+4,mrk_fly);

        
        %% extract single trial values after 1,5 second of onset
        eps(cont_e).rmse_raw = real(sqrt(mean(...
            eps(cont_e).fs_trial(80:end) - eps(cont_e).frc_con * eps(1).max_force ...
            / (eps(e).frc_con * eps(1).max_force).^2)));
        eps(cont_e).AudioCondition = "Schwebung";
        
        %% extract power values per trial 
        eps(cont_e).pow03   = bandpower(eps(cont_e).fs_trial / (eps(e).frc_con * eps(1).max_force),80,[0.1 3]);        
        eps(cont_e).pow412  = bandpower(eps(cont_e).fs_trial / (eps(e).frc_con * eps(1).max_force),80,[4 12]);
        
        cont_e = cont_e +1;

    end
    
    %% plot all trials per participant

    color.cmap_vo = winter(numel(eps));
    color.cmap_av = summer(numel(eps));
	color.cmap_ao = cool(numel(eps));
        
    figure
    for p = 1:numel(eps)
        hold on
        switch eps(p).fdbck_con
            case "vo"
                tmp_cc = color.cmap_vo(p,:);
                subplot(1,3,1)
                ylabel 'Normalised targetforce [a.u.]'
                title 'Visual'

            case "va"
                tmp_cc = color.cmap_av(p,:);
                subplot(1,3,2)
                xlabel 'Time [s]'
                title 'Audio-visual'

                
            case "ao"
                tmp_cc = color.cmap_ao(p,:);
                subplot(1,3,3)
                xlabel 'Time [s]'
                title 'Audio'
        end
        
        
        plot(eps(p).fs_ts - eps(p).fs_ts(1), eps(p).fs_trial/(eps(p).frc_con * eps(1).max_force),'Color',tmp_cc)
        hold on
        hline(1,'--k')
        xlim([0 inf])
        ylim([0 inf])
    end
    save_fig(gcf,PATHOUT_plot,[SUBJ{s} 'all_trials_raw']);

    % plot extra stuff and save
    close all
    eps = singleTrialPupil(eps);
    save_fig(gcf,PATHOUT_plot,[SUBJ{s} 'pupil_data']);
 
    save([PATHOUT_prep SUBJ{s} '_epData.mat'],'eps');
    
    
    %% transfer 
    [all_trials] = transfer2all(eps);
    
    waterfalloverview(all_trials,s);

    save_fig(gcf,PATHOUT_plot,[SUBJ{s} 'specs']);

    display(['Done with ' SUBJ{s}])

end

save([PATHOUT_prep 'all_trials'],'all_trials')


tab = table([all_trials.ID]',[all_trials.group]',[all_trials.TrialNumber]',[all_trials.ForceCondition]',[all_trials.Scaling]',...
    [all_trials.FeedbackCondition]',[all_trials.ActivePassive]',[all_trials.AuditiveCondition]',...
    [all_trials.RMSE]',[all_trials.out_rmse]',[all_trials.pow03]',[all_trials.pow412]',[all_trials.out_pow]',...
    [all_trials.ppl_sz_l]',[all_trials.out_ppl_sz_l]',[all_trials.ppl_sz_r]',[all_trials.out_ppl_sz_r]');

tab.Properties.VariableNames = {'ID','Group','n','ForceCondition','Scaling','FeedbackCondition','ActivePassive','AuditiveCondition',...
    'RMSE','Outlier RMSE','Power [0-3 Hz]','Power [4-12 Hz]','Outlier Power',...
    'Pupilsize left','Outlier Ppl l','Pupilsize right','Outlier Ppl r'};

writetable(tab,[PATHOUT_prep 'overview_all_trials.csv'])































