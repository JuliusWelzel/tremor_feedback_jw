function [ spec_vec freq_vec ]= pwSpectFsr(ts_trial,time_vec,srate)
%pwSpectFsr: Get spectrum output plot form single trial data
%markers
%
%Input:
%           ts_trial    = full input time series
%           time_vec    = vector with timestamps
%
% OUTPUT:
%           spec_vec    = spectrum
%           freq_vec    = frequency corresponding to spectrum
%
% Author: Julius Welzel, University of Kiel, September 2020
% Contact: j.welzel@nurologie.uni-kiel.de //
% https://github.com/JuliusWelzel/int_trmr_eeg

Fs      = srate;           % Sampling frequency                    
T       = 1/Fs;         % Sampling period       
L       = linspace(time_vec(1)-time_vec(1),time_vec(end)-time_vec(1),numel(time_vec));   % Length of signal
nbpnts  = numel(L);
t       = (0:nbpnts-1)*T;    % Time vector

% get number of channels
nbchan = min(size(ts_trial));
    
for ch = 1:nbchan    
    
    fft_out = fft(ts_trial(nbchan,:));

    P2 = abs(fft_out/nbpnts);
    P1 = P2(1:nbpnts/2+1);
    P1(2:end-1) = 2*P1(2:end-1);
    spec_vec(nbchan,:) = P1;

end

freq_vec = linspace(0,srate/2,size(spec_vec,2));


end

