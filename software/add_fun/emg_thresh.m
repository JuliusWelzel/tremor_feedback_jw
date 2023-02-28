function [fs_m fs_sd] = fs_thresh(eps)

for e = 15:numel(eps)
    
    ts_trial_start = eps(e).mrk_ts(contains(eps(e).mrk_trial,'trial_start'));
    [neg idx_start] = min((ts_trial_start - eps(e).fs_ts).^2);


    fs_trial(:,:,e) = eps(e).fs_trial(3:4,idx_start + 2 * 80:idx_start + 3.5 * 80); % check middle 3.5 seconds
    
end

fs_sd = mean(std(fs_trial,[],2),'all');
fs_m = mean(mean(fs_trial,2),'all');


end

