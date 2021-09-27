classdef SingleSubjectDataArcherRep
    %SingleSubjectData contains all data in various forms of the
    %replication of the archer ea., 2016 experiment (doi: 10.1093/brain/awx338).
    
    properties
        % Subject specific
        id          = "";
        frc_max     = []; % max force from 3 trials of 1 s
        frc_srate   = 80;
        ppl_srate    
        
        % Epoch specific
        n_epoch     = []; % running epoch number
        blk         = ""; % training or experimental
        con_fdbck   = ""; % feedback condition vo,av,ao
        con_frc     = []; % percentage of max_force [15,20,25%]
        con_scl     = []; % scale used for feedback [0-1]
        con_audio   = ""; % audiofeedback contition [fly, loudness]
        
        % Per epoch
        mrk     = struct('trial',[],'ts',[]); % mrk per epoch and LSL timestamps
        
        fs      = struct('frc',[],'ts',[],'spec_vec',[],'freq_vec',[]); % force sensor per epoch and LSL timestamps
        
        ppl     = struct('trial',[],'ts',[]); % EyeTracking (pupil labs) output (22 chans) per epoch and LSL timestamps
        
        
        % Derivitves
        frc_rmse    = []; % RMSE per epoch
        frc_bp03    = []; % bandpower(fun) derived power 0-3 Hz
        frc_bp412   = []; % bandpower(fun) derived power 4-12 Hz
        frc_pow412  = []; % FF derived power 4-12 Hz
        
    end
    
    methods
        %% TransferScl2deg
        
        function obj = TransferScl2deg(obj)
            %TransferScl2deg - Transfer sclaed output from feedback used in
            %psychopy to viewing angle in degree. 95 cm distance to
            %monitor, which is 26.1 cm wide.
            obj.con_scl = atand((26.1 * obj.con_scl) / 95);
        end
        
        %% ResampleForceSensor
        
        function obj = PrepForceSensor(obj)
            %ResampleForceSensor - Resample output from force sensor to 80.
            %Prior to resampling deal with missing values from arduino
            %malfunction.
            
            % filter configs
            filt_fs_412 = designfilt('bandpassfir','FilterOrder',20,...
            'CutoffFrequency1',4,'CutoffFrequency2',12,...
            'SampleRate',obj.frc_srate);    

            % vars for loop
            for e = 1:numel(obj.fs) % only extract data after training trials

                % interpolate force sensor
                tmp_dur                 = round(obj.mrk(e).ts(end)-obj.mrk(e).ts(end-1),0);
                fictiv_ts               = linspace(obj.fs(e).ts(1),obj.fs(e).ts(end),tmp_dur * obj.frc_srate);        
                obj.fs(e).frc           = interp1(obj.fs(e).ts,obj.fs(e).frc,fictiv_ts,'spline'); 
                obj.fs(e).ts            = fictiv_ts;
                
                % find idx when sub hit target (within 3 SD from last middle third)
        
                idx_hit = FindTargetHitFrc(obj,e);
                if isempty(idx_hit);continue;end % break script if no hit from participant is found

                % extract single trial values of RMSE
                obj.frc_rmse(e) = real(sqrt(mean(...
                    obj.fs(e).frc(idx_hit:end) - obj.con_frc(e) * obj.frc_max ...
                    / (obj.con_frc(e) * obj.frc_max).^2)));

                % extract power values per trial using bandpower function
                obj.frc_bp03(e)    = bandpower(obj.fs(e).frc(idx_hit:end) / (obj.con_frc(e) * obj.frc_max),obj.frc_srate,[0.1 3]);        
                obj.frc_bp412(e)   = bandpower(obj.fs(e).frc(idx_hit:end) / (obj.con_frc(e) * obj.frc_max),obj.frc_srate,[4 12]);
                
                % compute single trial power spectra
                [obj.fs(e).spec_vec obj.fs(e).freq_vec ]      = pwSpectFsr(...
                                                                obj.fs(e).frc,...
                                                                fictiv_ts,...
                                                                obj.frc_srate);
                                    
                obj.frc_pow412(e) = sum(abs(obj.fs(e).freq_vec(obj.fs(e).freq_vec >=4 & obj.fs(e).freq_vec <=12)));

            end            
        end
        
        %%
        
    end % methods
end % class

