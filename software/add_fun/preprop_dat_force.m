function [data] = preprop_dat_force(data,dat_F)

%select force data only
data = pop_select( data, 'channel',{'optical_grip_force' 'optical_hub_force'});

%filter
data = pop_eegfiltnew(data, [],dat_F.LP,[],0,[],0);
%resample
data = pop_resample( data,dat_F.resample);
%filter
data = pop_eegfiltnew(data, [],dat_F.HP,[],0,[],0);

%clean line noise
data = pop_cleanline(data, 'bandwidth',8,'chanlist',[1 2] ,'computepower',1,'linefreqs',50,'normSpectrum',0,'p',0.01,'pad',2,'plotfigures',0,'scanforlines',1,'sigtype','Channels','tau',100,'verb',1,'winsize',4,'winstep',1);

end

