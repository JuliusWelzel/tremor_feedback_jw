function [all_trials] = transfer2all(eps)
%transfer2all transfers data from eps struct to a summary struct containing
%all data of all pariticipants. Transfers empty cell whenn no or corrupted
%data is avaliable.
%
% Input: 
%   - eps -> selfmade struct for intention tremor project
%
% Output:
%   - all_trials -> overview struct of all participants with fractions of
%   single subject data
%% import global vars
global SUBJ s prob_info

%% transfer 

    all_trials(s).ID                = repmat(string(SUBJ{s}),numel(eps),1)';
    all_trials(s).group             = repmat(string(prob_info.Gruppe{s}),numel(eps),1)';
    all_trials(s).TrialNumber       = [eps.num];
    all_trials(s).ForceCondition    = [eps.frc_con];
    all_trials(s).Scaling           = [eps.scl];
    all_trials(s).FeedbackCondition = [eps.fdbck_con];
    all_trials(s).ActivePassive     = [eps.block];
    all_trials(s).AuditiveCondition = [eps.AudioCondition];
    
    % sensor data
    all_trials(s).out_rmse          = isoutlier([eps.rmse_raw]);
    all_trials(s).RMSE              = [eps.rmse_raw];
    all_trials(s).out_pow           = isoutlier([eps.pow412]);
    
    pow03                           = [eps.pow03];
    pow03(isoutlier(pow03))         = NaN;
    all_trials(s).pow03             = nanzscore([pow03]);
    
    pow412                          = [eps.pow412];
    pow412(isoutlier(pow412))       = NaN;
    all_trials(s).pow412            = nanzscore([pow412]);

    try 
        % pupil data
        all_trials(s).ppl_sz_l          = [eps.ppl_sz_trl_l];
        all_trials(s).out_ppl_sz_l      = isoutlier([eps.ppl_sz_trl_l]);
        all_trials(s).ppl_sz_r          = [eps.ppl_sz_trl_r];
        all_trials(s).out_ppl_sz_r      = isoutlier([eps.ppl_sz_trl_r]);
    catch
        
        % pupil data
        all_trials(s).ppl_sz_l          = [];
        all_trials(s).out_ppl_sz_l      = [];
        all_trials(s).ppl_sz_r          = [];
        all_trials(s).out_ppl_sz_r      = [];
    end % in case of empty pupil data
    
    try
        [all_trials(s).fs_pow_4_12,all_trials(s).fs_spec,all_trials(s).fs_freqs,] = interpSingleTrialData(eps);
    catch
        all_trials(s).fs_pow_4_12   = [];
        all_trials(s).fs_spec       = [];
        all_trials(s).fs_freqs      = [];
    end
    
end

