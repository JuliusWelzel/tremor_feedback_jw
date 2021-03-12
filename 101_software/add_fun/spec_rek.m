function [data spec] = spec_rek(path_data,dat_F,f_lims)

tp = 0;

% load and filter force data
cfg              = [];
cfg.dataset      = path_data;
cfg.channel      = 'all';
cfg.hpfilter     = 'yes';
cfg.hpfreq       = dat_F.HP;
% cfg.lpfilter     = 'yes';
% cfg.lpfilter     = dat_F.LP; 
% cfg.rectify      = 'yes';
% cfg.dftfilter    = 'yes';
% cfg.dftfreq      = [50];
data_raw = ft_preprocessing(cfg); 

cfg              = [];
cfg.channel      = {'optical_grip_force'};
data             = ft_selectdata(cfg, data_raw);

cfg = [];
cfg.resamplefs   = 250;
[data] = ft_resampledata(cfg, data)

cfg = []; 
cfg.length  = 5;
cfg.overlap = 0;
data = ft_redefinetrial(cfg, data)

cfg = [];
cfg.output     = 'pow'
cfg.method     = 'mtmfft'
cfg.taper      = 'hanning'
cfg.foilim     = f_lims;
cfg.keeptrials = 'yes'
spec = ft_freqanalysis(cfg, data)

% cfg = []
% cfg.channel = 'optical_grip_force';
% cfg.parameter   = 'powspctrm';
% cfg.channel     = [1];
% % cfg.title       = [nms_SUBS{s} ' ' nms_CONS_plot{c}];
% if tp
%     ft_singleplotER(cfg, spec);
%     xlabel 'Frequency [Hz]'
%     ylabel 'Power [V]'
% end
% 
end