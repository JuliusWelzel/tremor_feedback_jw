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
PATHOUT_plot = [MAIN '06_plots' filesep '01_single_trial' filesep];

if ~exist(PATHOUT_prep);mkdir(PATHOUT_prep);end
if ~exist(PATHOUT_plot);mkdir(PATHOUT_plot);end

global subj s all_trials % set global for transfer in function

% find all datasets which did the replication experiment ("_archer_")
list = dir(fullfile([PATHIN_raw]));
list_s = list(contains({list.name},'_archer_'));
subj = extractBefore({list_s.name},'_archer_');

%% Loop over subs
 
for s = 1:numel(subj) % all 
    
    clear eps
    display(['Working on subject ' subj{s}])
     
    % load data from first paradigm
    tmp_loud     = load_xdf([PATHIN_raw subj{s} '_archer_replicate.xdf']); %full xdf file

    ppl_arch = findLslStream(tmp_loud,'pupil_capture');
    fsr_arch = findLslStream(tmp_loud,'HX711');
    mrk_arch = findLslStream(tmp_loud,'PsychoPyMarkers');
    
    % initalize epoch class 
    eps = SingleSubjectDataArcherRep;
    eps.id = subj{s};
    
    % get ppl sampling rate
    eps.ppl_srate = round(str2num(ppl_arch.info.sample_count)/(ppl_arch.time_stamps(end)-ppl_arch.time_stamps(1)),0);

    %% Extract marker and max force
    idx_ep_all = find(contains(mrk_arch.time_series,'epoch'));
   
    % check if max force is correct and numeric
    idx_mrk_max_f = startsWith(mrk_arch.time_series,'max_force_');
    if startsWith(mrk_arch.time_series{idx_mrk_max_f},'max_force_') && isnumeric(str2num(extractAfter(mrk_arch.time_series{idx_mrk_max_f},'max_force_')))
        eps.frc_max     = str2num(extractAfter(mrk_arch.time_series{idx_mrk_max_f},'max_force_'));
        display(['Max force correct: ' num2str(eps.frc_max)])
    else
        eps.frc_max = NaN;
        display(['Invalid Max force for ' subj{s}])
        break
    end
    
    % find start of blocks
    idx_blk     = find(contains(mrk_arch.time_series,'block1'));
    idx_blk_vo  = idx_blk(1);
    idx_blk_av  = idx_blk(2);
    idx_blk_ao  = idx_blk(3);
    
    % find number oftrials per condition
    n_ep_train  = 2;
    n_ep_vo     = sum(strcmp(mrk_arch.time_series(idx_blk_vo:idx_blk_av-1),'end_trial')); 
    n_ep_av     = sum(strcmp(mrk_arch.time_series(idx_blk_av:idx_blk_ao-1),'end_trial')); 
    n_ep_ao     = sum(strcmp(mrk_arch.time_series(idx_blk_ao:end),'end_trial')); 

    % preprocess fsr timeseries
    fsr_arch.time_series = hampel(fsr_arch.time_series,2,5);

    %% Cut epochs and all infos and save results
    
    for e = 1:numel(idx_ep_all)
        
        % fill struct with info 
        eps.n_epoch(e)          = e;
        eps.con_fdbck(e)        = string(extractBetween(mrk_arch.time_series{idx_ep_all(e)},'_','_'));
        eps.con_frc(e)          = str2num(extractAfter(mrk_arch.time_series{idx_ep_all(e)+1},'sfc_'));  
        eps.con_scl(e)          = round(str2num(string(extractBetween(mrk_arch.time_series{idx_ep_all(e)+1},'sfb_','_sfc_'))),3);
        eps.con_audio(e)        = "beat_tone";

        if e <= n_ep_train;
            eps.blk(e)  = "training";
        elseif e > n_ep_train
            eps.blk(e)  = "experiment";
        end
        
        %% Extract time series // idx_ep_all(e) is position of first marker per trial -> epoch_con_start
        
        % extract trial info and marker
        [eps.mrk(e).trial  eps.mrk(e).ts]   = tsBetweenMrks(mrk_arch,idx_ep_all(e),idx_ep_all(e)+2,mrk_arch);

        % extract per trial parts of force sensor
        [eps.fs(e).frc eps.fs(e).ts]        = tsBetweenMrks(fsr_arch,idx_ep_all(e)+1,idx_ep_all(e)+2,mrk_arch);
        
        % extract per trial parts of pupil labs
        [eps.ppl(e).trial eps.ppl(e).ts]    = tsBetweenMrks(ppl_arch,idx_ep_all(e)-1,idx_ep_all(e)+2,mrk_arch);


    end
    
    %% find idx when sub hit target (within 3 SD from last middle third)
        
    eps = eps.PrepForceSensor;
    eps = eps.TransferScl2deg; % change viewing angle to degree
    
    %% plot all trials per participant

    color.cmap_vo = winter(numel(eps.fs));
    color.cmap_av = summer(numel(eps.fs));
	color.cmap_ao = cool(numel(eps.fs));
        
    figure
    for p = 1:numel(eps.fs)
        hold on
        switch eps.con_fdbck(p)
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
        
        
        plot(eps.fs(p).ts - eps.fs(p).ts(1), eps.fs(p).frc/(eps.con_frc(p) * eps.frc_max),'Color',tmp_cc)
        hold on
        hline(1,'--k')
        xlim([0 inf])
        ylim([0 inf])
    end
    save_fig(gcf,PATHOUT_plot,[subj{s} 'all_trials_raw']);

    % plot extra stuff and save
    close all
%     eps = singleTrialPupil(eps);

[valOut,speedFiltData,devFiltData] ...
    = rawDataFilter(t_ms,diaSamples,rawFiltSettings)
tmp = genMeanDiaSamples(ts_l_dia,r_dia,l_valid,r_valid)

    save_fig(gcf,PATHOUT_plot,[subj{s} 'pupil_data']);
 
    save([PATHOUT_prep subj{s} '_epData.mat'],'eps');
    
    
    %% transfer 
    [all_trials] = transfer2all(eps);
    
    waterfalloverview(eps);

    save_fig(gcf,PATHOUT_plot,[subj{s} 'specs']);

    display(['Done with ' subj{s}])

end

%%
save([PATHOUT_prep 'all_trials'],'all_trials')


tab = table([all_trials.ID]',[all_trials.TrialNumber]',[all_trials.ForceCondition]',[all_trials.Scaling]',...
    [all_trials.FeedbackCondition]',[all_trials.Block]',[all_trials.AuditiveCondition]',...
    [all_trials.rmse]',[all_trials.out_rmse]',[all_trials.pow03]',[all_trials.pow412]',[all_trials.out_pow_412]',...
    [all_trials.ppl_sz_l]',[all_trials.out_ppl_sz_l]',[all_trials.ppl_sz_r]',[all_trials.out_ppl_sz_r]');

tab.Properties.VariableNames = {'ID','n','ForceCondition','Scaling','FeedbackCondition','Block','AuditiveCondition',...
    'RMSE','Outlier RMSE','Power [0-3 Hz]','Power [4-12 Hz]','Outlier Power',...
    'Pupilsize left','Outlier Ppl l','Pupilsize right','Outlier Ppl r'};

writetable(tab,[PATHOUT_prep 'overview_all_trials_archer_rep.csv'])































