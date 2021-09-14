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

global subj s % set global for transfer in function

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
    
    %% Extract marker and max force
    idx_ep_all = find(contains(mrk_arch.time_series,'epoch'));
   
    % check if max force is correct and numeric
    idx_mrk_max_f = 7;
    if startsWith(mrk_arch.time_series{idx_mrk_max_f},max_force) && isnumeric(str2num(extractAfter(mrk_arch.time_series{idx_mrk_max_f},'max_force_')))
        max_f      = str2num(extractAfter(mrk_arch.time_series{idx_mrk_max_f},'max_force_'));
        display('Max force correct')
    else
        break
    end
    
    %start single subject structure to store all relevant derivitaves
    eps.ID = subj(s);
    eps.max_force = max_f;
    
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
        eps(e).num              = e;
        eps(e).fdbck_con        = string(extractBetween(mrk_arch.time_series{idx_ep_all(e)},'_','_'));
        eps(e).frc_con          = str2num(extractAfter(mrk_arch.time_series{idx_ep_all(e)+1},'sfc_'));        
        eps(e).AudioCondition   = "Loudness";

        if e <= n_ep_train;
            eps(e).block = "training";
        elseif e >= n_ep_vo & e < n_ep_av;
            eps(e).block = "vo";
        elseif e >= n_ep_av & e < n_ep_ao;
            eps(e).block = "av";
        elseif e > n_ep_ao;
            eps(e).block = "ao";  
        end
 
 
        
        %% Extract time series // idx_ep_all(e) is position of first marker per trial -> epoch_con_start
        
        % extract trial info and marker
        [eps(e).mrk_trial  eps(e).mrk_ts]   = tsBetweenMrks(mrk_arch,idx_ep_all(e),idx_ep_all(e)+2,mrk_arch);

        % extract per trial parts of force sensor
        [eps(e).fs_trial eps(e).fs_ts]      = tsBetweenMrks(fsr_arch,idx_ep_all(e)+1,idx_ep_all(e)+2,mrk_arch);
        
        % extract per trial parts of pupil labs
        [eps(e).ppl_trial eps(e).ppl_ts]    = tsBetweenMrks(ppl_arch,idx_ep_all(e),idx_ep_all(e)+2,mrk_arch);

        %% find idx when sub hit target (within 2 SD from last 2 seconds
        
        
        
        %% extract single trial values
        eps(e).rmse_raw = real(sqrt(mean(...
            eps(e).fs_trial(80:end) - eps(e).frc_con * eps(1).max_force ...
            / (eps(e).frc_con * eps(1).max_force).^2)));
        
        %% extract power values per trial 
        eps(e).pow03    = bandpower(eps(e).fs_trial / (eps(e).frc_con * eps(1).max_force),80,[0.1 3]);        
        eps(e).pow412   = bandpower(eps(e).fs_trial / (eps(e).frc_con * eps(1).max_force),80,[4 12]);

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
    save_fig(gcf,PATHOUT_plot,[subj{s} 'all_trials_raw']);

    % plot extra stuff and save
    close all
    eps = singleTrialPupil(eps);
    save_fig(gcf,PATHOUT_plot,[subj{s} 'pupil_data']);
 
    save([PATHOUT_prep subj{s} '_epData.mat'],'eps');
    
    
    %% transfer 
    [all_trials] = transfer2all(eps);
    
    waterfalloverview(all_trials,s);

    save_fig(gcf,PATHOUT_plot,[subj{s} 'specs']);

    display(['Done with ' subj{s}])

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































