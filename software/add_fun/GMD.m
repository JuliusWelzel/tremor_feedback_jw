function GMD = GMD(map1,map2)
%GMD This function returns the global map dissimilarity of two maps.
% 
% The global map dissimilarity (GMD) is a measure of two topographies. In this
% case the function takes EEG topoplots to return the value. Values can
% range between 0 (if maps are identical) and 2 (if maps are inverse).
% GMD is jsut the normalized global field potential (GFP).
% Lehmann ea., 1980, doi.org/10.1016/0013-4694(80)90419-8 

% Author: Julius Welzel & Mareike Daeglau, University of Oldenburg
% Version 1.0 // initial setup // Janurary 2019

% Inputs:
%       map1           vector containing the first dataset.
%       map2           vector containing the second dataset (must be 
%                       the same size as data1).
%   Outputs:
%       GMD             Map Dissimilarity Index value.
%
%
% -------------------------------------------------------------------------
    
% Check input variables to ensure dimensions match
if ~all(size(map1) == size(map2))
    error('Error: The dimensions of map1 and map2 are different');
end


std_m1 = std(map1);
std_m2 = std(map2);

m1 = mean(map1);
m2 = mean(map2);

GMD = sqrt(((map1-m1)/std_m1)-((map2-m2)/std_m2).^2);

% Calculate the deviation of each element in each dataset from the mean,
% relative to the average deviation across the dataset
data1_norm	= normalise(map1);
data2_norm	= normalise(map2);

% Take the root mean square (rms) difference between the two conditions
SDI = sqrt(mean((data1_norm - data2_norm).^2));

% Print the value
fprintf('\nGlobal Map Dissimilarity = %.3f\n', SDI);

end


end

