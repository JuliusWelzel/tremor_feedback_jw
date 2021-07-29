function waterfalloverview(all_trials,s)
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

    
    %% spectra average
    freqsAll    = all_trials(s).fs_freqs(1,:);
    specAvgVo   = mean(all_trials(s).fs_spec(idx_vo,:));
    specAvgAo   = mean(all_trials(s).fs_spec(idx_ao,:));
    specAvgAv   = mean(all_trials(s).fs_spec(idx_av,:));
    
    subplot(2,2,4)
    pVo = plot(freqsAll,specAvgVo)
    pVo.Color = color.cmap_vo(1,:);
    pVo.LineWidth = 1;
    hold on
    
    pAo = plot(freqsAll,specAvgAo)
    pAo.Color = color.cmap_ao(1,:);
    pAo.LineWidth = 1;
    hold on
    
    pAv = plot(freqsAll,specAvgAv)
    pAv.Color = color.cmap_av(1,:);
    pAv.LineWidth = 1;
    
    xlim([4 10])
    
    ylabel (['\SigmaBandpower [a.u.]'])
    xlabel ('Frequency [Hz]')
    legend('Visual','Auditiv','Audio-visual')
    legend boxoff
    
    
    %%

 
    %% FORCE SENSOR DATA
    foi_fs = all_trials(s).fs_freqs(1,:)>=4 & all_trials(s).fs_freqs(1,:)<= 12;

    % vo waterfall
    subplot(2,2,1)
    wvo = waterfall(all_trials(s).fs_freqs(1,:),1:sum(idx_vo),all_trials(s).fs_spec(idx_vo,:))
    wvo.FaceColor = 'flat';
    wvo.EdgeColor = 'w';
    wvo.FaceVertexCData =  winter(sum(idx_vo));
    axis tight
   
    xlim([4 12])
    zlim([0 max(all_trials(s).fs_spec(:,foi_fs),[],'all')])
    
    xlabel 'Frequency [Hz]'
    ylabel 'Trial [N]'
    zlabel (['Power [a.u./Hz]'])

    % av waterfall
    subplot(2,2,2)
    wav = waterfall(all_trials(s).fs_freqs(1,:),1:sum(idx_av),all_trials(s).fs_spec(idx_av,:))
    wav.FaceColor = 'flat';
    wav.EdgeColor = 'w';
    wav.FaceVertexCData =  summer(sum(idx_av));
    axis tight
    
    xlim([4 12])
    zlim([0 max(all_trials(s).fs_spec(:,foi_fs),[],'all')])
    
    xlabel 'Frequency [Hz]'
    ylabel 'Trial [N]'
    zlabel (['Power [a.u./Hz]'])

    % ao waterfall
    subplot(2,2,3)
    wao = waterfall(all_trials(s).fs_freqs(1,:),1:sum(idx_ao),all_trials(s).fs_spec(idx_ao,:))
    wao.FaceColor = 'flat';
    wao.EdgeColor = 'w';
    wao.FaceVertexCData =  cool(sum(idx_ao));
    axis tight
    
    xlim([4 12])
    zlim([0 max(all_trials(s).fs_spec(:,foi_fs),[],'all')])
    
    xlabel 'Frequency [Hz]'
    ylabel 'Trial [N]'
    zlabel (['Power [a.u./Hz]'])
   
end

