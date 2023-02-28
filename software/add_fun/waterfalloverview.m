function waterfalloverview(eps)
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
    
    % delete training trials
    eps.fs(1:2) = [];
    n_trials = numel(eps.fs);
    idx_vo = strcmp(eps.con_fdbck(3:end),'vo') ;
    idx_av = strcmp(eps.con_fdbck(3:end),'va');
    idx_ao = strcmp(eps.con_fdbck(3:end),'ao');

    
    %% spectra average
    freqsAll    = eps.fs(1).freq_vec;
    specsAll    = vertcat(eps.fs.spec_vec);
    specAvgVo   = mean(specsAll(idx_vo,:));
    specAvgAo   = mean(specsAll(idx_ao,:));
    specAvgAv   = mean(specsAll(idx_av,:));
    
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
    foi_fs = freqsAll >=4 & freqsAll <= 12;

    % vo waterfall
    subplot(2,2,1)
    wvo = waterfall(freqsAll,1:sum(idx_vo),specsAll(idx_vo,:))
    wvo.FaceColor = 'flat';
    wvo.EdgeColor = 'w';
    wvo.FaceVertexCData =  winter(sum(idx_vo));
    axis tight
   
    xlim([4 12])
    zlim([0 max(specsAll(:,foi_fs),[],'all')])
    
    xlabel 'Frequency [Hz]'
    ylabel 'Trial [N]'
    zlabel (['Power [a.u./Hz]'])

    % av waterfall
    subplot(2,2,2)
    wav = waterfall(freqsAll,1:sum(idx_av),specsAll(idx_av,:))
    wav.FaceColor = 'flat';
    wav.EdgeColor = 'w';
    wav.FaceVertexCData =  summer(sum(idx_av));
    axis tight
    
    xlim([4 12])
    zlim([0 max(specsAll(:,foi_fs),[],'all')])
    
    xlabel 'Frequency [Hz]'
    ylabel 'Trial [N]'
    zlabel (['Power [a.u./Hz]'])

    % ao waterfall
    subplot(2,2,3)
    wao = waterfall(freqsAll,1:sum(idx_ao),specsAll(idx_ao,:))
    wao.FaceColor = 'flat';
    wao.EdgeColor = 'w';
    wao.FaceVertexCData =  cool(sum(idx_ao));
    axis tight
    
    xlim([4 12])
    zlim([0 max(specsAll(:,foi_fs),[],'all')])
    
    xlabel 'Frequency [Hz]'
    ylabel 'Trial [N]'
    zlabel (['Power [a.u./Hz]'])
   
end

