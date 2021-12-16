function s_color = shadeColor(color,varargin)
% This function return britgher shade of color.
% INPUT: 
%     color: any color in rRGB
%     alpha: how much brighter you want it

%Author: Julius Welzel, 2021

% check for name value pairs
% Parse inputs: 
p = inputParser;
defaultAlpha = 1.4; 
addParameter(p,'alpha',defaultAlpha,@isnumeric);
parse(p,varargin{:});
alpha = p.Results.alpha;

s_color = color * alpha;
idx_cor = s_color > 1;
s_color(idx_cor) = 1;

end

