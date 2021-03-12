% ms_wlt() - markus siegel wavelet transform 
%
% usage:
% [out, sf, st] = ms_wlt(foi,fsample,w)
%
% foi:      frequencies of interest
% fsample:  sampling rate
% w:        width of the wavelet (Q), 
%           given as vector of length(foi) 
%
% sf   standard veiation frequency
% st   standard deviation time
%
%

function [out, sf, st] = jt_ms_wlt(foi,fsample,w)
dt = 1/fsample;
for k=1:length(foi)
    sf = foi(k)/w(k);
    st = 1/(2*pi*sf);
    toi = -3*st:dt:3*st;
    A = 1/sqrt(st*sqrt(pi));
    out{k} = A*exp(-toi.^2/(2*st^2)) .* exp(1i*2*pi*foi(k).*toi); %#ok<AGROW>
end


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% plot(abs(out{1}))                     % gaussian
% plot(cos(angle(out{1})))              % sinus
% plot(cos(angle(out{1})).*abs(out{1})  % wavelet
