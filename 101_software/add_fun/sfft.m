function [windowVec,freqVec,tfSpec] = sfft(data,srate,winLength,overlap)

win = hann(winLength*srate); % define window
windowStep = winLength*(srate-((overlap/100)*srate));    % calculation of the number of samples the window has to be moved

% This time the windows, or pieces are not cut out before we enter the
% loop. Instead now the window is extracted from the data inside of a while
% loop and in the same loop iteration the fft is calculated and stored.

samp = 0;           % start value for the samples
count = 1;          % counter to store the resulting spectra

% A while loop that starts at 0 and terminates when the window exceeds the
% last sample in the data minus the window length. After that sample, no
% full window can be extracted anymore.
while samp <= size(data,2)-winLength*srate
    
    sig = data(samp+1:samp+winLength*srate).*win'; % extraction of the window
    
    % application of fft
    fftDat = fft(sig);
    amp = abs(fftDat);
    amp = amp/length(sig);
    amp = amp(1:length(amp)/2);
    amp(2:end) = amp(2:end) * 2;
    
    tfSpec(:,count) = amp;  % store the amplitude spectrum in a 2D array
    
    samp = samp+windowStep; % Update the index variable. "push the windos to the right"
    count = count+1;        % Update counter to store the next spectrum
end

% The idea is to have a timevec that keeps the center values for each
% window. With overlapping windows, this is a bit more complicated than
% without.
% The start value is half the window size (center of the first window)
% The stepsize is windowstep (how far the window is pushed to the right) in seconds
% The end value is the length of the data in seconds minus half the window
% size. The center value of the last window cannot be later than that value.

windowVec = winLength/2:windowStep/srate:(size(data,2)/srate)-(winLength/2);

freqVec = 0:1/winLength:srate/2-(1/winLength);    % you should know this line :)

tfSpec = mean(tfSpec,2);

end

