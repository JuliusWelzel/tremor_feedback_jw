function [totalarea ca] = cont_area(C,Xgrid,Ygrid,Z_group)
%cont_area Calculates area inside conture lines


    % Extract the x- and y-locations from the contour matrix C.
    ca.xL = C(1, :);
    ca.yL = C(2, :);
    % Interpolate on the first surface to find z-locations for the intersection
    % line.
    ca.zL = interp2(Xgrid, Ygrid, Z_group, ca.xL, ca.yL);
        
    %find curves
    n(1) = 1;         %n: indices where the certain curves start
    d(1) = C(2,1);  %d: distance to the next index
    ii = 1;
    while true

           n(ii+1) = n(ii)+d(ii)+1;    %calculate index of next startpoint

           if n(ii+1) > numel(ca.xL)   %breaking condition
               n(end) = [];            %delete breaking point
               break
           end

           d(ii+1) = ca.yL(n(ii+1));   %get next distance
           ii = ii+1; 
    end

    %which contourlevel to calculate?
    value = 0;             %must be member of clevels
    sel = find(ismember(ca.xL(n),value));
    idx = n(sel);          %indices belonging to choice
    L = ca.yL( n(sel) );   %length of curve array

    % calculate area and plot all contours of the same level
    for ii = 1:numel(idx)
        x{ii} = ca.xL(idx(ii)+1:idx(ii)+L(ii));
        y{ii} = ca.yL(idx(ii)+1:idx(ii)+L(ii));

        %partial areas of all contours of the same plot
        areas(ii) = polyarea(x{ii},y{ii});   

    end

    % calculate total area of all contours of same level
    totalarea = sum(areas);


end

