function [sub,fdbck_con,frc_con,scl,...
            fs_pow_4_12,fs_spec,fs_freqs,...
            fs_rmse_raw,fs_rmse_03,fs_rmse_412,fs_pow_412] = interpSingleTrialData(nms_SUBJ)
%interpSingleTrialData Interpolate single trial data from EMG and store
%single trial info


    global PATHIN
    global eps
    
    % filter configs
    fs_srate = 50; % wanted srate force sensor
    
    filt_fs_03 = designfilt('bandpassfir','FilterOrder',20,...
                'CutoffFrequency1',0.1,'CutoffFrequency2',3,...
                'SampleRate',fs_srate);  
            
    filt_fs_412 = designfilt('bandpassfir','FilterOrder',20,...
    'CutoffFrequency1',4,'CutoffFrequency2',12,...
    'SampleRate',fs_srate);    

            

  
    % vars for loop
    for e = 1:numel(eps) % only extract data after training trials
       
        % interpolate force sensor
        tmp_dur                 = round(eps(e).mrk_ts(end)-eps(e).mrk_ts(end-1),0);
        fictiv_ts               = linspace(eps(e).fs_ts(1),eps(e).fs_ts(end),tmp_dur * fs_srate);        
        interp_trials_fs(:,e)   = interp1(eps(e).fs_ts,eps(e).fs_trial,fictiv_ts); 
                
        % calculate error
        fs_ts_raw    = double(interp_trials_fs(:,e)); % start after ~1 second
        fs_ts_03     = filtfilt(filt_fs_03,fs_ts_raw);
        fs_ts_412    = filtfilt(filt_fs_412,fs_ts_raw);
        
        rmse_raw    = sqrt(mean((fs_ts_raw - eps(e).frc_con*eps(1).max_force).^2));
        rmse_03     = sqrt(mean((fs_ts_03 - eps(e).frc_con*eps(1).max_force).^2));
        rmse_412    = sqrt(mean((fs_ts_412 - eps(e).frc_con*eps(1).max_force).^2));
        pow_412     = sum(abs(fs_ts_03));


 
        % compute power spectra
        [fs_spec_vec fs_freq_vec ]      = pwSpectFsr(...
                                        interp_trials_fs(:,e)',...
                                        fictiv_ts(:,e),...
                                        fs_srate);
                                    
        pow_fsr(:) = sum(abs(fs_spec_vec(fs_freq_vec >=4 & fs_freq_vec <=12)));

        
        
        % transfer info
        sub(c)         = str2num(nms_SUBJ(2:end));
        fdbck_con(e)   = eps(e).fdbck_con;        
        frc_con(e)     = eps(e).frc_con;
        scl(e)         = eps(e).scl;
        
        %% transfer output per entity per trial
                
        %FSR
        fs_pow_4_12(e)  = max(pow_fsr);
        fs_spec(e,:)    = fs_spec_vec;
        fs_freqs(e,:)   = fs_freq_vec; 
        
        % Error
        fs_rmse_raw(e)     = rmse_raw;
        fs_rmse_03 (e)     = rmse_03;
        fs_rmse_412(e)     = rmse_412;
        fs_pow_412(e)      = pow_412;
        
        
    end
    

end

