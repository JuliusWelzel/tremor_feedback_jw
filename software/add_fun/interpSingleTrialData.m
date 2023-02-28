function [fs_pow_4_12,fs_spec,fs_freqs] = interpSingleTrialData(eps)
%interpSingleTrialData Interpolate single trial data from EMG and store
%single trial info
    
    % filter configs
    fs_srate = 80; % wanted srate force sensor
                
    filt_fs_412 = designfilt('bandpassfir','FilterOrder',20,...
    'CutoffFrequency1',4,'CutoffFrequency2',12,...
    'SampleRate',fs_srate);    

            

  
    % vars for loop
    for e = 3:numel(eps) % only extract data after training trials
       
        % interpolate force sensor
        tmp_dur                 = round(eps(e).mrk_ts(end)-eps(e).mrk_ts(end-1),0);
        fictiv_ts               = linspace(eps(e).fs_ts(1),eps(e).fs_ts(end),tmp_dur * fs_srate);        
        interp_trials_fs(:,e)   = interp1(eps(e).fs_ts,eps(e).fs_trial,fictiv_ts); 
                
        % calculate error
        fs_ts_raw    = double(interp_trials_fs(:,e)); % start after ~1 second
        fs_ts_412    = filtfilt(filt_fs_412,fs_ts_raw);
        
        % compute power spectra
        [fs_spec_vec fs_freq_vec ]      = pwSpectFsr(...
                                        interp_trials_fs(:,e)',...
                                        fictiv_ts,...
                                        fs_srate);
                                    
        pow_fsr(:) = sum(abs(fs_spec_vec(fs_freq_vec >=4 & fs_freq_vec <=12)));

        
                
        %% transfer output per entity per trial
                
        %FSR
        fs_pow_4_12(e)  = pow_fsr;
        fs_spec(e,:)    = fs_spec_vec;
        fs_freqs(e,:)   = fs_freq_vec; 
        
        
        
    end
    

end

