%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%         Plot group level data
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Intention tremor behavioural
% Data: int_trmr_eeg (Jos Becktepe, University of Kiel)
% Author: Julius Welzel, j.welzel@neurologie.uni-kiel.de

%% Plot POWER error FSR

idx_trmr = [1,3,4,6,8,9];
for s= 1:numel(idx_trmr)
    z_pow{s} = zscore(all_trials(idx_trmr(s)).pow_412);
end
pow_4_12    = [z_pow{:}];
scl         = [all_trials(idx_trmr).scl]; 
idx_vo      = strcmp([all_trials(idx_trmr).fdbck_con],'vo');   
idx_ao      = strcmp([all_trials(idx_trmr).fdbck_con],'ao');   
idx_va      = strcmp([all_trials(idx_trmr).fdbck_con],'va');   

close all
figure
subplot(1,3,1)
% visual only
s_vo                    = scatter(scl(idx_vo),pow_4_12(idx_vo))
s_vo.MarkerFaceColor    = color.c_vo;
s_vo.MarkerEdgeAlpha    = 0;
s_vo.SizeData           = 10;

hold on

% visual audio
s_va                    = scatter(scl(idx_va),pow_4_12(idx_va))
s_va.MarkerFaceColor    = color.c_av;
s_va.MarkerEdgeAlpha    = 0;
s_va.SizeData           = 10;


%audio only
s_ao                    = scatter(scl(idx_ao),pow_4_12(idx_ao))
s_ao.MarkerFaceColor    = color.c_ao;
s_ao.MarkerEdgeAlpha    = 0;
s_ao.SizeData           = 10;

hold on


xlabel ('Normalised scaling factor [a.u.]')
ylabel ('\SigmaPower 4-12 [Hz]')

reg_l = lsline;
reg_l(1).Color = color.c_vo;
reg_l(1).LineWidth = 2;
reg_l(2).Color = color.c_av;
reg_l(2).LineWidth = 2;
reg_l(3).Color = color.c_ao;
reg_l(3).LineWidth = 2;
legend([s_vo,s_va,s_ao],{'Visual only','Visual-Audio','Audio only'})


subplot(1,3,2)
singleBoxplot({pow_4_12(idx_vo),pow_4_12(idx_va),pow_4_12(idx_ao)})
tune_BP([color.c_ao; color.c_av;color.c_vo])
xticklabels({'Visual only','Visual-Audio','Audio only'})
ylabel ('\SigmaPower 4-12 [Hz]')

% plot max force
idx_20      = [all_trials(idx_trmr).frc_con] == .2;   
idx_30      = [all_trials(idx_trmr).frc_con] == .3;   
idx_40      = [all_trials(idx_trmr).frc_con] == .4;   

subplot(1,3,3)
singleBoxplot({pow_4_12(idx_20),pow_4_12(idx_30),pow_4_12(idx_40)})
tune_BP([[.2 .2 .2];[.5 .5 .5]; [.8 .8 .8]])
xticklabels({'20%','30%','40%'})
ylabel ('\SigmaPower 4-12 [Hz]')

save_fig(gcf,PATHOUT_plots,'pilot_force_sensor_tremor')

%% Plot ERROR emg

idx_trmr = [1:9];
for s= 1:numel(idx_trmr)
    z_pow{s} = zscore(all_trials(idx_trmr(s)).emg_pow_4_12);
end
pow_4_12    = [z_pow{:}];
scl         = [all_trials(idx_trmr).scl]; 
idx_vo      = strcmp([all_trials(idx_trmr).fdbck_con],'vo');   
idx_ao      = strcmp([all_trials(idx_trmr).fdbck_con],'ao');   
idx_va      = strcmp([all_trials(idx_trmr).fdbck_con],'va');   

close all
figure
subplot(1,3,1)
% visual only
s_vo                    = scatter(scl(idx_vo),pow_4_12(idx_vo))
s_vo.MarkerFaceColor    = color.c_vo;
s_vo.MarkerEdgeAlpha    = 0;
s_vo.SizeData           = 10;

hold on

% visual audio
s_va                    = scatter(scl(idx_va),pow_4_12(idx_va))
s_va.MarkerFaceColor    = color.c_av;
s_va.MarkerEdgeAlpha    = 0;
s_va.SizeData           = 10;


%audio only
s_ao                    = scatter(scl(idx_ao),pow_4_12(idx_ao))
s_ao.MarkerFaceColor    = color.c_ao;
s_ao.MarkerEdgeAlpha    = 0;
s_ao.SizeData           = 10;

hold on


xlabel ('Normalised scaling factor [a.u.]')
ylabel ('Emg Power 4-12 [Hz]')

reg_l = lsline;
reg_l(1).Color = color.c_vo;
reg_l(1).LineWidth = 2;
reg_l(2).Color = color.c_av;
reg_l(2).LineWidth = 2;
reg_l(3).Color = color.c_ao;
reg_l(3).LineWidth = 2;

legend([s_vo,s_va,s_ao],{'Visual only','Visual-Audio','Audio only'})


subplot(1,3,2)
singleBoxplot({pow_4_12(idx_vo),pow_4_12(idx_va),pow_4_12(idx_ao)})
tune_BP([color.c_ao; color.c_av;color.c_vo])
xticklabels({'Visual only','Visual-Audio','Audio only'})
ylabel ('Emg Power 4-12 [Hz]')

% plot max force
idx_20      = [all_trials(idx_trmr).frc_con] == .2;   
idx_30      = [all_trials(idx_trmr).frc_con] == .3;   
idx_40      = [all_trials(idx_trmr).frc_con] == .4;   

subplot(1,3,3)
singleBoxplot({pow_4_12(idx_20),pow_4_12(idx_30),pow_4_12(idx_40)})
tune_BP([[.2 .2 .2];[.5 .5 .5]; [.8 .8 .8]])
xticklabels({'20%','30%','40%'})
ylabel ('Emg Power 4-12 [Hz]')

save_fig(gcf,PATHOUT_plots,'pilot_emg')


%% Plot error over time

idx_trmr = [1:9];
for s= 1:numel(idx_trmr)
    z_pow{s} = zscore(all_trials(idx_trmr(s)).emg_pow_4_12);
    n_trial_all{s} = [1:numel(all_trials(idx_trmr(s)).emg_pow_4_12)];
end
pow_4_12    = [z_pow{:}];
n_trial     = [n_trial_all{:}];
idx_vo      = strcmp([all_trials(idx_trmr).fdbck_con],'vo');   
idx_ao      = strcmp([all_trials(idx_trmr).fdbck_con],'ao');   
idx_va      = strcmp([all_trials(idx_trmr).fdbck_con],'va');   


close all
figure
% visual only
s_vo                    = scatter(n_trial(idx_vo),pow_4_12(idx_vo))
s_vo.MarkerFaceColor    = color.c_vo;
s_vo.MarkerEdgeAlpha    = 0;
s_vo.SizeData           = 10;
hold on

% visual audio
s_va                    = scatter(n_trial(idx_va),pow_4_12(idx_va))
s_va.MarkerFaceColor    = color.c_av;
s_va.MarkerEdgeAlpha    = 0;
s_va.SizeData           = 10;
hold on

%audio only
s_ao                    = scatter(n_trial(idx_ao),pow_4_12(idx_ao))
s_ao.MarkerFaceColor    = color.c_ao;
s_ao.MarkerEdgeAlpha    = 0;
s_ao.SizeData           = 10;
hold on


xlabel ('Trial number')
ylabel ('\SigmaPower 4-12 [Hz]')

reg_l = lsline;
reg_l(1).Color = color.c_vo;
reg_l(1).LineWidth = 2;
reg_l(2).Color = color.c_av;
reg_l(2).LineWidth = 2;
reg_l(3).Color = color.c_ao;
reg_l(3).LineWidth = 2;


legend([s_vo,s_va,s_ao],{'Visual only','Visual-Audio','Audio only'})



save_fig(gcf,PATHOUT_plots,'trial_oder')

%% ERROR per condition

idx_trmr = [2,5,7];
for s= 1:numel(idx_trmr)
    z_rmse{s} = zscore(all_trials(idx_trmr(s)).rmse_03);
end
raw_rmse    = [z_rmse{:}];
scl         = [all_trials(idx_trmr).scl]; 
idx_vo      = strcmp([all_trials(idx_trmr).fdbck_con],'vo');   
idx_ao      = strcmp([all_trials(idx_trmr).fdbck_con],'ao');   
idx_va      = strcmp([all_trials(idx_trmr).fdbck_con],'va');   


singleBoxplot({raw_rmse(idx_vo),raw_rmse(idx_va),raw_rmse(idx_ao)})
tune_BP([color.c_ao; color.c_av;color.c_vo])
xticklabels({'Visual only','Visual-Audio','Audio only'})
ylabel ('zscored RMSE [0-3 Hz]')



save_fig(gcf,PATHOUT_plots,'rmse_03_con')

