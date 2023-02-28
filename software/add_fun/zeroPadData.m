function pad_data = zeroPadData(data,n_samples)
%zeroPadData - This function zeropads the data in the first diemnsion with
%a specific number of samples
%
% Author: Julius Welzel

sz_data = size(data);
pad_data = [zeros(sz_data(1),n_samples) data zeros(sz_data(1),n_samples)];

end

