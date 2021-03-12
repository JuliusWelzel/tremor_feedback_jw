function [sub,fdbck_con,frc_con,scl,...
            emg_pow_4_12,emg_spec,emg_freqs,...
            fs_pow_4_12,fs_spec,fs_freqs,...
            fs_rmse_raw,fs_rmse_03,fs_rmse_412,fs_pow_412] = interpSingleTrialData(nms_SUBJ)
%interpSingleTrialData Interpolate single trial data from EMG and store
%single trial info


    global PATHIN
    global eps
    
    % filter configs
    fs_srate = 80; % wanted srate force sensor
    emg_srate = 2000; % wanted srate force sensor
    
    filt_fs_03 = designfilt('bandpassfir','FilterOrder',100,...
                'CutoffFrequency1',0.1,'CutoffFrequency2',3,...
                'SampleRate',fs_srate);  
            
    filt_fs_412 = designfilt('bandpassfir','FilterOrder',100,...
    'CutoffFrequency1',4,'CutoffFrequency2',12,...
    'SampleRate',fs_srate);    

            

  
    % vars for loop
    c = 1;
    for e = 15:numel(eps) % only extract data after training trials
       
        % interpolate force sensor
        tmp_dur                 = round(eps(e).mrk_ts(end)-eps(e).mrk_ts(end-1),0);
        fictiv_ts               = linspace(eps(e).fs_ts(1),eps(e).fs_ts(end),tmp_dur * fs_srate);        
        interp_trials_fs(:,c)         = interp1(eps(e).fs_ts,eps(e).fs_trial,fictiv_ts); 
        interp_trials_fs(1,c)         = interp_trials_fs(2,c);
        interp_trials_fs(end,c)       = interp_trials_fs(end-1,c);
        
        % get time when threshold is exceeded
        fs_mean_trial       = mean(interp_trials_fs(3 * fs_srate:5 * fs_srate,c));
        fs_std_trial        = std(interp_trials_fs(3 * fs_srate:5 * fs_srate,c));
        idx_target_hit_fs   = find(interp_trials_fs(:,c) < fs_mean_trial+fs_std_trial &...
                                interp_trials_fs(:,c) > fs_mean_trial-fs_std_trial,1);
        if isempty(idx_target_hit_fs); idx_target_hit_fs = 1; end % dirty hack for when thresh not working
        [neg idx_target_hit_emg]  = min((fictiv_ts(idx_target_hit_fs) - eps(e).emg_ts).^2);
        
        % calculate error
        fs_ts_raw    = double(interp_trials_fs(80:end,c)); % start after 1 second
        fs_ts_03     = filtfilt(filt_fs_03,fs_ts_raw);
        fs_ts_412    = filtfilt(filt_fs_412,fs_ts_raw);
        
        rmse_raw    = sqrt(mean((fs_ts_raw - eps(e).frc_con*eps(1).max_force).^2));
        rmse_03     = sqrt(mean((fs_ts_03 - eps(e).frc_con*eps(1).max_force).^2));
        rmse_412    = sqrt(mean((fs_ts_412 - eps(e).frc_con*eps(1).max_force).^2));
        pow_412     = sum(abs(fs_ts_03));

        % extract data from EMG    
        clear rec_ep
        for ch_emg = 3:size(eps(e).emg_trial,1)

            %filter and bandpower
            rec_ep(ch_emg,:) = abs(eps(e).emg_trial(ch_emg,:)); % rectify
        
        end
        
        m_rec_ep = mean(rec_ep(3:4,:));
 
        % compute power spectra
        [emg_spec_vec emg_freq_vec ]    = pwSpectFsr(...
                                        m_rec_ep(idx_target_hit_emg:idx_target_hit_emg+emg_srate * 2.5),...
                                        eps(e).emg_ts(idx_target_hit_emg:idx_target_hit_emg+emg_srate * 2.5),...
                                        emg_srate);
                                    
        pow_emg(:) = sum(emg_spec_vec(emg_freq_vec >=4 & emg_freq_vec <=12));

                                    
        [fs_spec_vec fs_freq_vec ]      = pwSpectFsr(...
                                        interp_trials_fs(idx_target_hit_fs:idx_target_hit_fs+fs_srate * 2.5,c)',...
                                        fictiv_ts(idx_target_hit_fs:idx_target_hit_fs+fs_srate * 2.5),...
                                        fs_srate);
                                    
        pow_fsr(:) = sum(abs(fs_spec_vec(fs_freq_vec >=4 & fs_freq_vec <=12)));

        
        
        % transfer info
        sub(c)         = str2num(nms_SUBJ(2:end));
        fdbck_con(c)   = eps(e).fdbck_con;        
        frc_con(c)     = eps(e).frc_con;
        scl(c)         = eps(e).scl;
        
        %% transfer output per entity per trial
        
        %EMG
        emg_pow_4_12(c) = max(pow_emg);
        emg_spec(c,:)   = emg_spec_vec;
        emg_freqs(c,:)  = emg_freq_vec; 
        
        %FSR
        fs_pow_4_12(c)  = max(pow_fsr);
        fs_spec(c,:)    = fs_spec_vec;
        fs_freqs(c,:)   = fs_freq_vec; 
        
        % Error
        fs_rmse_raw(c)     = rmse_raw;
        fs_rmse_03 (c)     = rmse_03;
        fs_rmse_412(c)     = rmse_412;
        fs_pow_412(c)      = pow_412;

        
        c = c+1;
        
        
    end
    

end

