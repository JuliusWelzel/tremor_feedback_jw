    %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%               Get tremor boundries with Mike X Cohens approach
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% Intention tremor behave
% Data: int_trmr_eeg (Jos Becktepe, University of Kiel)
% Author: Julius Welzel, j.welzel@neurologie.uni-kiel.de

%% Set envir

PATHIN      = [MAIN '04_data\00_main_pilot\'];
PATHOUT     = [MAIN '04_data\01_prep_pilot\'];

if ~isdir(PATHOUT); mkdir(PATHOUT); end

list = dir(fullfile([PATHIN]));
list = list(contains({list.name},'pilot'));
SUBJ = extractBetween({list.name},'_','_iso');

nms_task = '_isometric_tremor';


%% Loop over subs

s = 1; % only one for now
tmp     = load_xdf([PATHIN 'pilot_' SUBJ{s} nms_task '.xdf']); %full xdf file
emg = findLslStream(tmp,'Delsys');
srate = str2num(emg.info.sample_count)/(emg.time_stamps(end)-emg.time_stamps(1));

dat_fs  = emg.time_series;
pnts    = length(dat_fs);
nbchan  = size(dat_fs,1);

% filter dat_fs
filt_fs = designfilt('bandpassfir','FilterOrder',100,...
    'CutoffFrequency1',0.1,'CutoffFrequency2',30,...
    'SampleRate',srate);

for n = 1:nbchan
    dat_fs(n,:) = filtfilt(filt_fs,double(dat_fs(n,:)));
end

%% simulation parameters
freqbands = getBounds_JW(dat_fs,srate,[3 12])

% plot spectrum
vec_spec = pwSpectFsr(emg.time_series,emg.time_stamps,emg_srate);
