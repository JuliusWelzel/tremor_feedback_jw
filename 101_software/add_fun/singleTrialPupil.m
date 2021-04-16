function eps = singleTrialPupil(s,eps)
% singleTrialPupil: Function to  extract pupil diameter from preprocessed pupilabs data
% and detect blink onsets
%     
% INPUT: 
%     eps: single epochs from int_trmr_eeg
%     (https://github.com/JuliusWelzel/int_trmr_eeg) containing data for
%     from force sensor, emg, and pupil labs including markers per epoch


% OUTPUT:
%    bls: vector containing single baseline averages puil size,
%       corrected
%    trls: vector containing single trial averages puil size,
%       corrected
% 
% Author: (Julius Welzel, University of Kiel, 2021)

%% Loop over every epoch and correct blinks

for e = 1:numel(eps) % only start after training epoch
    
    % prep data
    eps(e).ppl_trial(21,eps(e).ppl_trial(1,:) < 0.5) = NaN
    eps(e).ppl_trial(21,:) = hampel(eps(e).ppl_trial(21,:),4,2);

    
    eps(e).ppl_trial(22,eps(e).ppl_trial(1,:) < 0.5) = NaN
    eps(e).ppl_trial(22,:) = hampel(eps(e).ppl_trial(22,:),4,2);
    
    clear blinks
    idx_blink_onset     = find(diff(eps(e).ppl_trial(1,:))< -0.45); %sudden drop in confidence of more than 0.45
    
    c = 1;
    for b = 1:numel(idx_blink_onset)
        
        clear tmp_conf
        tmp_conf = eps(e).ppl_trial(1,:);
        idx_norm_conf = find(tmp_conf(idx_blink_onset(b)+1:end)     >=  tmp_conf(idx_blink_onset(b)+1)+0.45,1); % find idx when confidence returns to normal
        
        if idx_norm_conf < 10  % blink must be longer than 10 samples, @120Hz srate ~ 80ms
            continue
        elseif isempty(idx_norm_conf)
            idx_norm_conf = length(eps(e).ppl_trial(1,:));
        end
        
        idx_tmp_offset = idx_blink_onset(b) + idx_norm_conf;
        
            
        blinks(c).onset = idx_blink_onset(b) - 2;
        blinks(c).offset = idx_tmp_offset + 2;
        c = c+1;
    end
    
    %% interpolate
    if exist('blinks','var') == 0
        % add information about blink occurence 
        eps(e).ppl_blink_n      = NaN;
        eps(e).ppl_blink_perc   = NaN;
        continue
    end
    
    
    for b = 1:numel(blinks)
       
        try
            
            % do it for one channels
            tmp_blink_length    = abs(blinks(b).onset-blinks(b).offset) * 2;
            tmp_ts_raw          = eps(e).ppl_trial(21,blinks(b).onset-tmp_blink_length:blinks(b).offset+tmp_blink_length);
            tmp_ts_clean        = tmp_ts_raw;
            tmp_ts_clean(tmp_blink_length/2 : tmp_blink_length*2) = NaN;

            tmp_interp = fillmissing(tmp_ts_clean,'makima'); % actually do the interpolation

            % spline interpolate around blink
            eps(e).ppl_trial(21,blinks(b).onset-tmp_blink_length:blinks(b).offset+tmp_blink_length) = ...  
                tmp_interp;
        
            %% do it for the other channel
            tmp_blink_length    = abs(blinks(b).onset-blinks(b).offset) * 2;
            tmp_ts_raw          = eps(e).ppl_trial(22,blinks(b).onset-tmp_blink_length:blinks(b).offset+tmp_blink_length);
            tmp_ts_clean        = tmp_ts_raw;
            tmp_ts_clean(tmp_blink_length/2 : tmp_blink_length*2) = NaN;

            tmp_interp = fillmissing(tmp_ts_clean,'makima'); % actually do the interpolation

            % spline interpolate around blink
            eps(e).ppl_trial(22,blinks(b).onset-tmp_blink_length:blinks(b).offset+tmp_blink_length) = ...  
                tmp_interp;

        catch % catch if not possible
            continue
        end
    end
    
    % add information about blink occurence 
    eps(e).ppl_blink_n      = numel(blinks);
    eps(e).ppl_blink_perc   = sum(abs([blinks.onset]-[blinks.offset]))/length(eps(e).ppl_ts);
    eps(e).ppl_blinks       = blinks;
    
    
end % epoch loop


% extract data from all trials

c = 1;
for e = 1:numel(eps)

    % find fix cross and take previous 120 sample ~0.5 s
    idx_bl              = find(contains(eps(e).mrk_trial,'fix_cross'));
    [neg bl_idx_end]    = min((eps(e).ppl_ts - eps(e).mrk_ts(idx_bl)).^2);

    % find trial end and take previous 120 sample ~0.5 s
    idx_trl              = find(contains(eps(e).mrk_trial,'trial_start'));
    [neg trl_idx_end]    = min((eps(e).ppl_ts - eps(e).mrk_ts(idx_bl)).^2);

    % extract ts
    sz_bls(e,:)   = nanmean(eps(e).ppl_trial(21:22,bl_idx_end + 120:bl_idx_end + 240),2);
    sz_trl(e,:)   = nanmean(eps(e).ppl_trial(21:22,trl_idx_end + 120:end) - sz_bls(e,:)',2);  
    
    %% store data for long table
    eps(e).ppl_sz_bl_l        = sz_bls(e,1);
    eps(e).ppl_sz_trl_l       = sz_trl(e,1);

    eps(e).ppl_sz_bl_r        = sz_bls(e,2);
    eps(e).ppl_sz_trl_r       = sz_trl(e,2);

end


    
end % fun

%% 
%{
close all
figure
subplot(2,1,1)
plot(eps(e).ppl_ts, eps(e).ppl_trial(22,:))
vline(eps(e).mrk_ts,'k',eps(e).mrk_trial)
vline(eps(e).ppl_ts([blinks.onset]),'r')
vline(eps(e).ppl_ts([blinks.offset]),'g')
subplot(2,1,2)
plot(eps(e).ppl_ts,eps(e).ppl_trial(1,:))
vline(eps(e).ppl_ts([blinks.onset]),'r')
vline(eps(e).ppl_ts([blinks.offset]),'g')
%}
