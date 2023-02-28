function [ tfSpec, windowVec, freqVec ] = tfana( data, srate, winLength, TT ,varargin )
% myTF preprocesses data for a time-frequency plot
%
% Inputs to the function :
%     Data -> [1*sample]
%     Sampling rate 
%     Window length in seconds
% 
% Name value pairs:
%     Overlap in percent
%     Which window function to use. (implement Hanning, Hamming, and the standard Tukey window, Rect for default)
%     The option to plot the TF spectrum
% 
% Outputs of the function :
%     tfSpec -> The 2D time-frequency spectrum (size: frequencies ◊ number of windows)
%     windowVec -> The ìwindow vectorî which is the center timepoints of each window
%     ferqVec -> The frequency vector
%
% Author: Benedikt Kretzmeyer, Rahel Franke ,Julius Welzel & Jo·o Voﬂkuhl

for i = 1:2:length(varargin)

    if strcmpi(varargin{i},'whichWin')
        if strcmpi(varargin{i+1},'hanning')
            win = hann(winLength*srate); 
            whichWin = varargin{i+1};
            warning(['Amplitudes might be decreased due to window "' whichWin,'"'])
        elseif strcmpi(varargin{i+1},'hamming')
            win = hamming(winLength*srate);
            whichWin = varargin{i+1};
            warning(['Amplitudes might be decreased due to window "' whichWin,'"'])
        elseif strcmpi(varargin{i+1},'tukey')
            win = tukeywin(winLength*srate);
            whichWin = varargin{i+1};
            warning(['Amplitudes might be decreased due to window "' whichWin,'"'])
        else
            whichWin = 'rect';
            win = rectwin(winLength*srate);
            warning(['Window ', whichWin, ' not possible in this function. Window set to "rectangular" instead'])
        end
        
    elseif strcmpi(varargin{i},'overlap')
        overlap = varargin{i+1};
        
    elseif strcmpi(varargin{i},'plot')
        plotout = varargin{i+1};
    end

    
    
end

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

if plotout

imagesc(windowVec,freqVec,tfSpec)
ylim([0,1]);          % cut of the frequencies to only show frequencies which are 8 times oversampled.    
                            % you can also just limit the y-axis to 0 to 100. 
axis xy                     % flip the y-axis
c = colorbar;
c.Label.String = 'Amplitude [\muV]';
% caxis([0 1])               
xlabel('Time [Sec]')
ylabel('Frequency [Hz]')
stepX = round(length(windowVec)/sqrt(length(windowVec)));
set(gca,'xTick',windowVec(1:stepX:length(windowVec)))  % Put the labels to the correct places (center of column)
title (TT);
% Enlarge figure to full screen.
set(gcf, 'Units', 'Normalized', 'OuterPosition', [0 0 1 1]);



end

end

