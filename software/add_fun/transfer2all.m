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
global subj s all_trials

%% transfer 

    all_trials(s).ID                = repmat(string(subj{s}),numel(eps.fs),1)';
    all_trials(s).TrialNumber       = [eps.n_epoch];
    all_trials(s).ForceCondition    = [eps.con_frc];
    all_trials(s).Scaling           = [eps.con_scl];
    all_trials(s).FeedbackCondition = [eps.con_fdbck];
    all_trials(s).Block             = [eps.blk];
    all_trials(s).AuditiveCondition = [eps.con_audio];
    
    % sensor data
    all_trials(s).out_rmse          = isoutlier([eps.frc_rmse]);
    all_trials(s).rmse              = [eps.frc_rmse];
    all_trials(s).out_pow_412       = isoutlier([eps.frc_bp412]);
    
    pow03                           = [eps.frc_bp03];
%     pow03(isoutlier(pow03))         = NaN;
    all_trials(s).pow03             = nanzscore([pow03]);
    
    pow412                          = [eps.frc_bp412];
%     pow412(isoutlier(pow412))       = NaN;
    all_trials(s).pow412            = nanzscore([pow412]);

    try 
        % pupil data
        all_trials(s).ppl_sz_l          = [eps.ppl.ppl_sz_trl_l];
        all_trials(s).out_ppl_sz_l      = isoutlier([eps.ppl.ppl_sz_trl_l]);
        all_trials(s).ppl_sz_r          = [eps.ppl.ppl_sz_trl_r];
        all_trials(s).out_ppl_sz_r      = isoutlier([eps.ppl.ppl_sz_trl_r]);
    
    catch    
        % pupil data
        all_trials(s).ppl_sz_l          = [];
        all_trials(s).out_ppl_sz_l      = [];
        all_trials(s).ppl_sz_r          = [];
        all_trials(s).out_ppl_sz_r      = [];
    end % in case of empty pupil data
    
    
end

