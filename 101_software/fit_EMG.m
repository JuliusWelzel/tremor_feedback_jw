function [mACC EMG_overall] = fit_EMG(emgdata,emg_check,t_BP_ms,t_emg_,cfg,sub)
%UNTITLED Summary of this function goes here
%   Detailed explanation goes here

%define variables
n_sub = 1;
n_trials = 96;

% take different trials into accoutnt
if str2num(emg_check(sub).ID)<50;    
    trials = [cfg.blck_idx{1}(1):cfg.blck_idx{3}(end) 249:256];
else
    trials = [cfg.blck_idx{1}(1):cfg.blck_idx{4}(end)];
end

c_a = 1; %counter accuracy


c1_all = zeros(n_sub,n_trials);
c2_all = zeros(n_sub,n_trials);
c1 = zeros(n_sub,n_trials);
c2 = zeros(n_sub,n_trials);
c = [];
cca = [];


    for t = 1:n_trials

        satt2 = movstd(emgdata{sub,trials(t)}(1,:),125); %125 sample windows, you can play around with this parameter and check in the loop above
        satt = std(emgdata{sub,trials(t)}(1,:)); %STD for right(1) channel
        c = find(satt2 >(t_emg_*satt)); % first exceed thresh STD

        %including button press rigth hand
        if ~isempty(c) 
            c1_all(1,t) = c(1); % BP sample
        end


        %indices without button press

        % right hand
        if ~isempty(c) && c(1) < size(emgdata{sub,trials(t)}(1,:),2)-t_BP_ms*(cfg.EMG.srate/1000)%<- threshold to account for the button press (750 ms), check if index is lower so that movement is not derived from button press
            c1(1,t) = c(1); % position where movavg exceeds std
        end

        %left hand // only when no movement in rigth hand
        if isempty(c)
            satt3 = movstd(emgdata{sub,trials(t)}(2,:),125);
            satt4 = std(emgdata{sub,trials(t)}(2,:));
            cca = find(satt3 >(satt4));

            if ~isempty(cca) 
                c2_all(1,t) = cca(1); % left hand only
            end

            if ~isempty(cca) && cca(1) < size(emgdata{sub,trials(t)}(2,:),2)-t_BP_ms*(cfg.EMG.srate/1000)%left hand without BP
                c2(1,t) = cca(1);
            end
        end

        %summed hands
        summed = emgdata{sub,trials(t)}(1,:)+emgdata{sub,trials(t)}(2,:);
        satt2 = movstd(summed,125);
        satt = std(summed);
        c = find(satt2 >t_emg_*satt);

        if ~isempty(c) && c(1) < size(emgdata{sub,trials(t)}(2,:),2)-t_BP_ms*(cfg.EMG.srate/1000)
            c1(1,t) = c(1); %-> stores all invalid trials
        end 

    end

    c1(c1==0) = NaN;
    c2(c2==0) = NaN;
    c1_all(c1_all==0) = NaN;
    c2_all(c2_all==0) = NaN;

    %% EMG validity plots without invalid ME trials (discard marble drop)

    EMG_overall = nan(1,n_trials);

    for t = 1:n_trials
       EMG_overall(1,t)  = emg_check(sub).trials_dur(t);
       if isnan(c1(1,t))  && ismember(t,cfg.blck_idx{1,:}) | ismember(t,cfg.blck_idx{4,:}) % movement blocks
           EMG_overall(1,t)  = NaN;
       elseif ~isnan(c1(1,t)) | emg_check(1).trials_valid(t) == 0 && ismember(t,cfg.blck_idx{2,:}) | ismember(t,cfg.blck_idx{3,:}) % imagery blocks
           EMG_overall(1,t)  = NaN;
       end
    end

    ACCs = 100*[NaN_acc(EMG_overall(:,cfg.blck_idx{1,:})) NaN_acc(EMG_overall(:,cfg.blck_idx{2,:})) NaN_acc(EMG_overall(:,cfg.blck_idx{3,:})) NaN_acc(EMG_overall(:,cfg.blck_idx{4,:}))];
    mACC = mean(ACCs);

end

