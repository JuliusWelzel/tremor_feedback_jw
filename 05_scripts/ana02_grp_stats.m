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
PATHIN          = [MAIN '04_data\01_prep\'];
PATHOUT         = [MAIN '04_data\02_grp_stats\'];
PATHOUT_plots   = [MAIN '06_plots\01_single_trial\'];

if ~isdir(PATHOUT); mkdir(PATHOUT); end
if ~isdir(PATHOUT_plots); mkdir(PATHOUT_plots); end

list = dir(fullfile([PATHIN]));
list = list(contains({list.name},'epData'));
SUBJ = extractBefore({list.name},'_');


%% Loop over subs

for s = 1:numel(SUBJ)
    
    display(['Working in SUBJ ' SUBJ{s}])

    clear eps
    load([PATHIN SUBJ{s} '_epData.mat']);
    
%     get appropriate epochs here 
    
    figure
    for p = 1:numel(eps)
        hold on
        
        switch eps(p).fdbck_con
            
            case "vo"
                tmp_cc = color.c_vo;
                
                % force sensor
                subplot(3,3,1)
                ylabel 'Normalised targetforce [a.u.]'
                title 'Visual'
                plot(eps(p).fs_ts - eps(p).fs_ts(1), eps(p).fs_trial/(eps(p).frc_con * eps(1).max_force),'Color',tmp_cc)
                hline(1,'--k')

                % pupil data
                subplot(3,3,4)
                ylabel 'BL_corrected pupil size [mm³]'
                title 'Visual'
                plot(eps(p).ppl_ts - eps(p).ppl_ts(1), hampel(eps(p).ppl_trial(22,:),20),'Color',tmp_cc)
                hold on
                plot(eps(p).ppl_ts - eps(p).ppl_ts(1), eps(p).ppl_trial(22,:))



            case "va"
                tmp_cc = color.c_av;
                subplot(1,3,2)
                xlabel 'Time [s]'
                title 'Audio-visual'

                
            case "ao"
                tmp_cc = color.c_ao;
                subplot(1,3,3)
                xlabel 'Time [s]'
                title 'Audio'
        end
        
        
    end
    
    % force sensor
    subplot(3,3,7)
    ylabel 'Scale [a.u.]'
    title 'Visual'

    
    waterfALL(s);
    save_fig(gcf,PATHOUT_plots,[SUBJ{s} '_ss_fft'],'fontsize',12,'figsize',[0 0 50 30]);
end


save([PATHOUT 'all_part_all_trials.mat'],'all_trials')
