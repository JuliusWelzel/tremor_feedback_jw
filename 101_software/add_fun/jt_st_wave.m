% jt_st_wave() - wavelet transform 
% 
% USAGE:
% [tfr, foi] = st_wave(data, fsample, foi, qmin, qmax, times)
%
% IN:
%  data     	data vector
%  fsample  	sampling rate, e.g., EEG.srate    
%  foi      	frequencies of interest
%  qmin         minimum wavelet width at min frequency
%  qmax         maximum wavelet width at max frequency.
%				For qmax > qmin, wavelet width is being increased
%				for higher frequencies.	Set min=max for running 
%				standard wavelet transform
%  times	    time stamps vector, e.g., EEG.times
%
% OUT
%  trf        	complex time frequency array
%  foi	     	frequencies of interest
%
% st_wave() needs ms_wlt() markus siegel



function [tfr, fres, tres, foi] = jt_st_wave(data, fsample, foi, qmin, qmax, times) 

w = linspace(qmin,qmax,length(foi));  
data=data(:)';

wl = jt_ms_wlt(foi,fsample,w);  % create wavelet family
tfr = zeros(length(foi), length(data));  % hurry-up 

% wavelet transform
for ifr = 1:length(foi)
    tfr(ifr,:) = conv2(data,wl{ifr},'same');
%       tfr(ifr,1:ceil(length(wl{ifr})/2)) = NaN;    
%       tfr(ifr,end-ceil(length(wl{ifr})/2):end) = NaN; 
    fres(ifr) = foi(ifr)/w(ifr); %#ok<AGROW>
    tres(ifr) = 1/(2*pi*fres(ifr)); %#ok<AGROW>
end


end

