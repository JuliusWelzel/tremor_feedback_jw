%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%         Extract pupil size data
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Intention tremor behavioural
% Data: int_trmr_eeg (Jos Becktepe, University of Kiel)
% Author: Julius Welzel, j.welzel@neurologie.uni-kiel.de

%% Set envir
global PATHIN
PATHIN          = [MAIN '04_data\01_prep_pilot\'];
PATHOUT         = [MAIN '04_data\02_ppl\'];
PATHOUT_plots   = [MAIN '05_plots\02_ppl\'];

if ~isdir(PATHOUT); mkdir(PATHOUT); end
if ~isdir(PATHOUT_plots); mkdir(PATHOUT_plots); end

list = dir(fullfile([PATHIN]));
list = list(contains({list.name},'epData'));
SUBJ = extractBefore({list.name},'_');

%% set config for analysis
global cfg
cfg.ppl = [];

tp = 0;
%% Loop over subs

for s = [6 7]%1:numel(SUBJ)
    
    display(['Working in SUBJ ' SUBJ{s}])

    clear eps
    clear ppl
    global eps
    global ppl
    load([PATHIN SUBJ{s} '_epData.mat']);
    
    singleTrialPupil(s); % only extract data after training trials
    

    
    %% plot overview of paritcipant
    [n idx_min_blink]   = min([eps.ppl_blink_n]);
    idx_min_blink       = idx_min_blink(1) + 14 ;
    [n idx_max_blink]   = max([eps.ppl_blink_n]);
    idx_max_blink       = idx_max_blink(1) + 14;

    nms_mrk = strrep(eps(idx_min_blink).mrk_trial,'_',' ');
    
    if tp 
        figure
        subplot(4,4,[1 2])
        plot(eps(idx_min_blink).ppl_ts,eps(idx_min_blink).ppl_trial(22,:),'Color',color.c_schweiz)
        vline(eps(idx_min_blink).mrk_ts,'k',nms_mrk)
        title 'Minimal blinks'
            ylabel 'Pupil size [mm²]'


        subplot(4,4,[5 6])
        plot(eps(idx_min_blink).ppl_ts,eps(idx_min_blink).ppl_trial(1,:),'Color',color.c_schweiz)
        vline(eps(idx_min_blink).mrk_ts,'k',nms_mrk)
        vline(eps(idx_min_blink).ppl_ts([eps(idx_min_blink).ppl_blinks.onset]),'r')
            ylabel 'Confidence score [a.u.]'
            xlabel 'Time [s]'


        subplot(4,4,[3 4])
        plot(eps(idx_max_blink).ppl_ts,eps(idx_max_blink).ppl_trial(22,:),'Color',color.c_schweiz)
        vline(eps(idx_max_blink).mrk_ts,'k',nms_mrk)
            title 'Maximal blinks'

        subplot(4,4,[7 8])
        plot(eps(idx_max_blink).ppl_ts,eps(idx_max_blink).ppl_trial(1,:),'Color',color.c_schweiz)
        vline(eps(idx_max_blink).mrk_ts,'k',nms_mrk)
        vline(eps(idx_max_blink).ppl_ts([eps(idx_max_blink).ppl_blinks.onset]),'r')
            xlabel 'Time [s]'
            ylabel 'Pupil size [mm²]'

        subplot(4,4,[9 10 13 14])
        sc = scatter([ppl(s).scl],[ppl(s).sz_trl])
        sc.MarkerFaceAlpha = 1;
        sc.MarkerFaceColor = color.c_schweiz;
        sc.MarkerEdgeAlpha = 0;
        lsline
            xlabel 'Scale [a.u.]'
            ylabel 'Norm ppl size [z-score]'

        subplot(4,4,[11 12])
        hst = histogram(ppl(s).sz_bl)
        hst.FaceColor = color.c_schweiz * 0.8
          xlabel 'BL ppl size [mm²]'

        subplot(4,4,[15 16])
        hst2 = histogram(ppl(s).sz_trl)
        hst2.FaceColor = color.c_schweiz
            xlabel 'Trial ppl size [z-score]'

        save_fig(gcf,PATHOUT_plots,['ppl_qual_' SUBJ{s}],'figsize',[0 0 60 40]);
    end
end

save([PATHOUT 'all_ppl_sz.mat'],'ppl')

%% construct table for stats
dat_trmr_ppl = table;
tmp_id = [ppl.id];
dat_trmr_ppl.id         = string(tmp_id)';
dat_trmr_ppl.scale      = [ppl.scl]';
tmp_con = [ppl.fdbck_con];
dat_trmr_ppl.condition  = string(tmp_con)';
dat_trmr_ppl.f_level    = [ppl.frc_con]';
dat_trmr_ppl.ppl_size   =[ppl.sz_trl]';

idx_id = contains(dat_trmr_ppl.id,{'p007','p008'});
dat_trmr_ppl(~idx_id,:) = [];

writetable(dat_trmr_ppl,[PATHOUT 'ppl_stats.csv']);

%% Plot group level data
dtp = dat_trmr_ppl;

idx_vo      = contains(dat_trmr_ppl.condition,'vo');   
idx_ao      = contains(dat_trmr_ppl.condition,'ao');   
idx_va      = contains(dat_trmr_ppl.condition,'va');   

close all
figure
% visual only
s_vo                    = scatter(dtp.scale(idx_vo),dtp.ppl_size(idx_vo))
s_vo.MarkerFaceColor    = color.c_vo;
s_vo.MarkerEdgeAlpha    = 0;
s_vo.SizeData           = 10;

hold on

% visual audio
s_va                    = scatter(dtp.scale(idx_va),dtp.ppl_size(idx_va))
s_va.MarkerFaceColor    = color.c_av;
s_va.MarkerEdgeAlpha    = 0;
s_va.SizeData           = 10;


%audio only
s_ao                    = scatter(dtp.scale(idx_ao),dtp.ppl_size(idx_ao))
s_ao.MarkerFaceColor    = color.c_ao;
s_ao.MarkerEdgeAlpha    = 0;
s_ao.SizeData           = 10;

hold on


xlabel ('Normalised scaling factor [a.u.]')
ylabel ('Pupil Size [z-score]')

reg_l = lsline;
reg_l(3).Color = color.c_vo;
reg_l(3).LineWidth = 2;
reg_l(2).Color = color.c_av;
reg_l(2).LineWidth = 2;
reg_l(1).Color = color.c_ao;
reg_l(1).LineWidth = 2;

[corr_vo p_vo] = corr(dtp.scale(idx_vo),dtp.ppl_size(idx_vo),'Rows','pairwise');
[corr_vo p_av] = corr(dtp.scale(idx_va),dtp.ppl_size(idx_va),'Rows','pairwise');
[corr_vo p_ao] = corr(dtp.scale(idx_ao),dtp.ppl_size(idx_ao),'Rows','pairwise');

legend([s_vo,s_va,s_ao],{['Visual only, p: ' num2str(round(p_vo,3))]...
                        ['Audio-visual, p: ' num2str(round(p_av,3))]...
                        ['Audio only, p: ' num2str(round(p_ao,3))]});
                    
save_fig(gcf,PATHOUT_plots,'overview_ppl_sz_scl');
                    


























































