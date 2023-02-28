function  EEG  = renameEvents_table(EEG)


for e = 1:length(EEG.event)
    
    %rename Eventmarker
     if~isempty(strfind(EEG.event(e).type, '>opaque<'))
        EEG.event(e).type = 'opaque';
  
     elseif   ~isempty(strfind(EEG.event(e).type, '>transp<'))
                EEG.event(e).type = 'transp';  
                    
     elseif   ~isempty(strfind(EEG.event(e).type, '>NZ:1 (Korrekte SP)<'))
                EEG.event(e).type = 'StartKorrekt';
                
     elseif   ~isempty(strfind(EEG.event(e).type, '>NZ:2 (Block auf Start)<'))
                EEG.event(e).type = 'Release';
                
     elseif   ~isempty(strfind(EEG.event(e).type, '>NZ:3 (Alle Inaktiv)<'))
                EEG.event(e).type = 'GraspDone';
                
     elseif   ~isempty(strfind(EEG.event(e).type, '>NZ:4 (Block am Ziel)<'))
                EEG.event(e).type = 'TransportDone';
                                             
     elseif   ~isempty(strfind(EEG.event(e).type, '>NZ:6 (Ende)<'))
                EEG.event(e).type = 'End';
                
    %rename valid and invalid trials
                
     elseif   ~isempty(strfind(EEG.event(e).type, '>Text Input<'))
         
                if ~isempty(strfind(EEG.event(e).type, '>1<'))
                EEG.event(e).type = 'valid'; 
                elseif ~isempty(strfind(EEG.event(e).type, '>2<'));
                EEG.event(e).type = 'invalid';
                end
                
    %rename orientations
     elseif   ~isempty(strfind(EEG.event(e).type, '>Sound<'))
         
                if ~isempty(strfind(EEG.event(e).type, '>0-Start-1')) 
                EEG.event(e).type = '0-Start-1'; 
                elseif ~isempty(strfind(EEG.event(e).type, '>0-Start-2'))
                EEG.event(e).type = '0-Start-2';
                elseif ~isempty(strfind(EEG.event(e).type, '>0-Start-3')) 
                EEG.event(e).type = '0-Start-3';
                elseif ~isempty(strfind(EEG.event(e).type, '>0-Start-4')) 
                EEG.event(e).type = '0-Start-4';
                end
     elseif strcmp(EEG.event(e).type,'1')
         EEG.event(e).del = [];
     else
         EEG.event(e).del = 1;
    
    %Back-up other markers; irrelevant at this time
                
%     elseif   ~isempty(strfind(EEG.event(e).type, '>NZ:5 (Block am Ziel + SB)<'))
%                 EEG.event(e).type = '';
%     elseif   ~isempty(strfind(EEG.event(e).type, '>NZ:7 (Nur SB)<'))
%                 EEG.event(e).type = '';
% 
%      
     end
     
end

for e = length(EEG.event):-1:1
    if EEG.event(e).del == 1
        EEG.event(e) = [];
    end
end
    


    
end