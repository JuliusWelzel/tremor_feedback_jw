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

pad_samples = 160;

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
        
        % trial derivitaves
        info.t_mean(ct)     = mean(eps.fs(e).pad_fs_dev( 2 * eps.frc_srate:end)); % mean corrected force after 2 seconds (estimated mean hitting)
        info.t_std (ct)     = std(eps.fs(e).pad_fs_dev( 2 * eps.frc_srate:end)); % mean corrected force after 2 seconds (estimated mean hitting)
        
        info.idx_hit(ct)    = find(eps.fs(e).pad_fs_dev > info.t_mean(ct) - info.t_std(ct),1) - pad_samples;
        info.raw(ct,:)      = eps.fs(e).pad_fs_dev;
        
        ct = ct+1;
        
    end
        

end

n_sec_pad   = 2;
dur_ep      = 30;
target_force    = ones(1,length(eps.fs(3).frc));
target_force    = zeroPadData(target_force,n_sec_pad * eps.frc_srate);
time_pad        = linspace(-n_sec_pad,dur_ep + n_sec_pad,(dur_ep + (2*n_sec_pad)) *  eps.frc_srate);

trials(trials < 0 ) = 0;

%% plot

idx_low     = info.scl == min(info.scl);
idx_high    = info.scl == max(info.scl);
idx_vo      = strcmp(info.mod,"vo");

% single trials
plot(time_pad,trials(idx_low & idx_vo,:) - target_force,'Color',shadeColor(color.c_vo),'LineWidth',0.001,'LineStyle',':')
hold on
plot(time_pad,trials(idx_high & idx_vo,:) - target_force,'Color',shadeColor(color.c_ao),'LineWidth',0.001,'LineStyle',':')
hold on

% means
m(1) = plot(time_pad,mean(trials(idx_low & idx_vo,:),1) - target_force,'Color',color.c_vo,'LineWidth',2)
hold on
m(2) = plot(time_pad,mean(trials(idx_high & idx_vo,:),1) - target_force,'Color',color.c_ao,'LineWidth',2)
hold on

hline(0,':k')
hline(-1,':k')

legend(m(1:2),'low','high')
xlim([-1 5])
ylim([-1.1 .2])
box off
ylabel 'Deviation from target force [a.u.]'
xlabel 'Time [s]'

%%
figure
stdshade(trials(idx_high & idx_vo,:) - target_force,0.3,color.c_vo * 1.7,time_pad)
hold on
stdshade(trials(idx_low & idx_vo,:) - target_force,0.3,color.c_vo,time_pad)
hline(0,':k')
hline(-1,':k')

xlabel 'Time [s]'
ylabel 'Deviation from target force [a.u.]'
xlim ([-2 15])

legend('','low','','high')


%% estimate when hitting the target point
pad_samples = n_sec_pad * eps.frc_srate;
trials_clean = trials;
% prep bad trials
idx_bad_eps = sum(trials(:,pad_samples:end-pad_samples) < 0,2) > .5 *eps.frc_srate | ... % bad if half a sec lower than 0 (error in FSR)
    trials(:,pad_samples +1) > 1; % Bad if participant already pressed FSR before start of epoch
trials_clean(idx_bad_eps,:) = [];
info(idx_bad_eps,:) = [];

%% plot

idx_low     = info.scl == min(info.scl);
idx_high    = info.scl == max(info.scl);
idx_vo      = strcmp(info.mod,"vo");

% single trials
plot(time_pad,trials_clean(idx_low & idx_vo,:) - target_force,'Color',shadeColor(color.c_vo * 1.7),'LineWidth',0.001,'LineStyle',':')
hold on
plot(time_pad,trials_clean(idx_high & idx_vo,:) - target_force,'Color',shadeColor(color.c_vo),'LineWidth',0.001,'LineStyle',':')
hold on

% means
m(1) = plot(time_pad,mean(trials_clean(idx_low & idx_vo,:),1) - target_force,'Color',color.c_vo * 1.7,'LineWidth',2)
hold on
m(2) = plot(time_pad,mean(trials_clean(idx_high & idx_vo,:),1) - target_force,'Color',color.c_vo,'LineWidth',2)
hold on

hline(0,':k')
hline(-1,':k')

legend(m(1:2),'low','high')
xlim([-1 5])
ylim([-1.1 .2])
box off
ylabel 'Deviation from target force [a.u.]'
xlabel 'Time [s]'


%% plots hits 
ms_sam = 1000/80;
low_hit     = info.idx_hit(idx_low & info.idx_hit > 10) * ms_sam;
high_hit    = info.idx_hit(idx_high & info.idx_hit > 10) * ms_sam;

figure
plot_psd(low_hit,'Color',color.c_vo * 1.7,'Kernelwidth',200)
hold on
plot_psd(high_hit,'Color',color.c_vo,'Kernelwidth',200)

legend('','low','','high')
legend boxoff
xlim([0 3000])
