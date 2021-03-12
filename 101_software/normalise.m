function data_norm = normalise(data)
% data_norm = normalise(data)
%
% This function calculates the deviation of each element from the mean,
% relative to the average deviation across the dataset.


% This metric doesn't care how the data are arranged, so we reshape to a
% vector
data_norm	= reshape(data, [1, numel(data)]);

% Subtract the mean from each element
data_norm	= data_norm - mean(data_norm);

% Divide by the root mean square deviation from the mean across elements
data_norm	= data_norm ./ sqrt(mean(data_norm.^2));

for idx = find(isnan(data_norm))
    data_norm(idx) = 0;
end

end