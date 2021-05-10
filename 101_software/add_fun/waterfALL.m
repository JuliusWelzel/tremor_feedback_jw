function waterfALL(all_trials,s)
%waterfALL: Plot EMG emg_spectrum of all trials 
%
%Input:
%           s                   = subject number
%           (global) all_trials = derived from ana02_grp_stats
% OUTPUT:
%           waterfall plot with overview and per condition plots
%
% Author: Julius Welzel, University of Kiel, September 2020
% Contact: j.welzel@nurologie.uni-kiel.de //
% https://github.com/JuliusWelzel/int_trmr_eeg

%% get info per trial

    global color
    
    n_trials = numel(all_trials(s).ID);
    idx_vo = strcmp(all_trials(s).FeedbackCondition,'vo');
    idx_av = strcmp(all_trials(s).FeedbackCondition,'va');
    idx_ao = strcmp(all_trials(s).FeedbackCondition,'ao');

    
    %% boxplot overview
   subplot(2,3,[1:3])
   singleBoxplot({all_trials(s).fs_pow_4_12(idx_vo),all_trials(s).fs_pow_4_12(idx_av),all_trials(s).fs_pow_4_12(idx_ao)})
   tune_BP([color.c_ao;color.c_av;color.c_vo])
   ylabel (['\SigmaBandpower [a.u.]'])
   xticklabels({'VO','AV','AO'})

    %% FORCE SENSOR DATA
    foi_fs = all_trials(s).fs_freqs(1,:)>=4 & all_trials(s).fs_freqs(1,:)<= 12;

    % vo waterfall
    subplot(2,3,4)
    wvo = waterfall(all_trials(s).fs_freqs(1,:),1:sum(idx_vo),all_trials(s).fs_spec(idx_vo,:))
    wvo.FaceColor = 'flat';
    wvo.EdgeColor = 'w';
    wvo.FaceVertexCData =  repmat(color.c_vo,sum(idx_vo),1);
    axis tight
   
    xlim([4 12])
    zlim([0 max(all_trials(s).fs_spec(:,foi_fs),[],'all')])
    
    xlabel 'Frequency [Hz]'
    ylabel 'Trial [N]'
    zlabel (['PSD [a.u./Hz]'])

    % av waterfall
    subplot(2,3,5)
    wav = waterfall(all_trials(s).fs_freqs(1,:),1:sum(idx_av),all_trials(s).fs_spec(idx_av,:))
    wav.FaceColor = 'flat';
    wav.EdgeColor = 'w';
    wav.FaceVertexCData =  repmat(color.c_av,sum(idx_av),1);
    axis tight
    
    xlim([4 12])
    zlim([0 max(all_trials(s).fs_spec(:,foi_fs),[],'all')])
    
    xlabel 'Frequency [Hz]'
    ylabel 'Trial [N]'
    zlabel (['PSD [a.u./Hz]'])

    % ao waterfall
    subplot(2,3,6)
    wao = waterfall(all_trials(s).fs_freqs(1,:),1:sum(idx_ao),all_trials(s).fs_spec(idx_ao,:))
    wao.FaceColor = 'flat';
    wao.EdgeColor = 'w';
    wao.FaceVertexCData =  repmat(color.c_ao,sum(idx_ao),1);
    axis tight
    
    xlim([4 12])
    zlim([0 max(all_trials(s).fs_spec(:,foi_fs),[],'all')])
    
    xlabel 'Frequency [Hz]'
    ylabel 'Trial [N]'
    zlabel (['PSD [a.u./Hz]'])
   
end

