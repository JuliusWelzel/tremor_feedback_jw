function b = interpNaN(a)
%interpNaN - Interpolates NaN values in a vector
%
% Author: MVP Jan, MatLab, https://www.mathworks.com/matlabcentral/answers/408164-how-to-interpolate-at-nan-values

v        = ~isnan(a);
G        = griddedInterpolant(find(v), a(v), 'previous');
idx      = find(~v);
bp       = G(idx);
G.Method = 'next';
bn       = G(idx);
b        = a;
b(idx)   = (bp + bn) / 2;

end

