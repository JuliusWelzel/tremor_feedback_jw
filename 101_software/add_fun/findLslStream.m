function data_stream = findLslStream(data_all,stream_name)
%findLslStream - returns data from .xdf according to stream name
%
% INPUT:
%           data_all    = inital .xdf file
%           name    	= name of desired stream as string
%
% OUTPUT:
%           data_stream = single stream from .xdf file
%
% Author: Julius Welzel, University of Kiel, August 2020
% Contact: j.welzel@nurologie.uni-kiel.de // https://github.com/JuliusWelzel/VR_PD

% Prep output
data_stream = [];

for s = 1:numel(data_all)

    if strcmp(data_all{1,s}.info.name,stream_name)

        data_stream = data_all{1,s};

    end % if stream name

end % for streams


if isempty(data_stream)

    display(['No stream named ' stream_name ' in .xdf']);

end

end
