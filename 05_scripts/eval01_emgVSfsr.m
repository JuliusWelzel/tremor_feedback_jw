filt_emg = designfilt('bandpassfir','FilterOrder',1000,...
'CutoffFrequency1',1,'CutoffFrequency2',40,...
'SampleRate',emg_srate);    

time_vec_emg = linspace(emg.time_stamps(1),emg.time_stamps(end),numel(emg.time_stamps));

emg_unfilt = resample(emg.time_series(3,:),time_vec_emg,'spline');
emg_filt = filtfilt(filt_emg,emg_unfilt);


%%
close all
figure
subplot(1,2,1)
plot(time_vec_emg,zscore(emg_unfilt))
hold on
plot(fsr.time_stamps,zscore(fsr.time_series))
xlim([6300 6310])
ylim([-5 5])

subplot(1,2,2)
plot(time_vec_emg,zscore(emg_filt))
hold on
plot(fsr.time_stamps,zscore(fsr.time_series))
xlim([6300 6310])
ylim([-5 5])

plot(fsr.time_stamps,zscore(fsr.time_series))
hold on
plot(ppl.time_stamps,ppl.time_series(22,:))
xlim([6300 6310])
ylim([-5 5])
