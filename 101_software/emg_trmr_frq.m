function [elfr,elco,elcotf] = emg_trmr_frq(data,sr,ws,fl,fh,vfl,vfh)
% emg_trmr_frq filter emg data
%
% Inputs to the function :
%     data      -> raw emg signal
%     sr        -> Sampling rate 
%     fl & fh   -> lower & higher frequency
%     vfl & vfh -> which frequencies to show
% 
%
% Author: Julius Welzel, 06/2019 (Uni Kiel, Germany)

EEG        = eeg_emptyset();
EEG.data   = data;
EEG.times  = linspace(1,length(EEG.data)/sr,length(EEG.data));
EEG.xmin   = EEG.times(1);
EEG.xmax   = EEG.times(end);
EEG.srate  = round(1/((EEG.xmax-EEG.xmin)/length(EEG.times))); % Rounded actual sampling rate. Note that the unit of the time must be in second.
EEG.nbchan = size(EEG.data,1);
EEG.pnts   = size(EEG.data,2);
[EEG h f] = pop_eegfiltnew(EEG,fl,fh);

%rektify
EEG.data_rek = abs(EEG.data - mean(EEG.data));
data = EEG.data_rek;

% 3 Power Spectrum
[elfr,elco,elcotf]=spec_m(EEG.data_rek,sr,ws,vfl,vfh);


end

