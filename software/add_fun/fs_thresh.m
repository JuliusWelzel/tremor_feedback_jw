function [fs_m fs_sd] = fs_thresh(eps)

for e = 15:numel(eps)
    
    fs_trial(:,e) = eps(e).fs_trial(:,2 * 80:5.5 * 80); % check middle 3.5 seconds
    
end

fs_sd = mean(std(fs_trial,[],2),'all');
fs_m = mean(mean(fs_trial,2),'all');


end

