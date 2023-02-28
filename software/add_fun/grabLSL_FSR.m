function dat_force = grabLSL_FSR(inlet)

% Create buffer 
tmp_buf = [];

while length(tmp_buf) < 5
    
        tmp_buf     = inlet.pull_chunk();
        dat_force = mean(sscanf(char(tmp_buf),'%f'));

%         idx_start   = find(tmp_buf == 10,1);
%         idx_end     = find(tmp_buf == 13,1,'last');
%         tmp_buf     = tmp_buf(idx_start:idx_end);
%         tmp_buf     = reshape(tmp_buf,6,length(tmp_buf)/6); 
%         
%         tmp_buf = tmp_buf([2:5],:);
%         
%         dat_force = mean(sscanf(char(tmp_buf),'%f'));


end

end

