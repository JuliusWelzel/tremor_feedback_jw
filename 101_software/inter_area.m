%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%                       inter_area (fun)
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% This function calucate the area of intersection of a 3D topographie and
% and plane in z-axis

% Input Variables: - chanlocs: Standard EEGLab chanlocs format with x,y,z
%                             coordinates of channel locations
%                 - map: Vector [1 *length(chanlocs)] with value of
%                        topographie
%                 - lvl_inter: Vector of position of z-level of
%                              intersection 
% 
% 
% Output Variables: - area_inter: Vector with area for every intersection
%                     level [1 *length(lvl_inter)]



% Author: Julius Welzel, Mareike Daeglau, University of Oldenburg 
% Contact: julius.welzel@gmail.com
% Version: 1.0 // 11.03.19 // inital setup 



function area_inter = inter_area(chanlocs, map, n_inter, ID, PATHOUT,c_map, FB)

% Calculate and interpolate X & Y coordinates from chanlocs
p_interp = 200; % points to interpolate (should be higher for less channels

% get cartesian coordinates by MIKE X COHEN :D and grid data
[elocsX,elocsY] = pol2cart(pi/180*[chanlocs.theta],[chanlocs.radius]);
elocsX = elocsX*-1; %swap left/ right
xlin = linspace(min(elocsX),max(elocsX),p_interp);
ylin = linspace(min(elocsY),max(elocsY),p_interp);
[Xgrid, Ygrid] = meshgrid(xlin,ylin);

%% Get 3D representation of indv map
   
min_z = min(min(map));
max_z = max(max(map));
lvl_inter = linspace(max_z,min_z,n_inter);

Z = griddata(elocsX,elocsY,map,Xgrid,Ygrid,'cubic'); % estimate Z values for map_st
area_inter = NaN(1,length(lvl_inter));

p = numSubplots(length(lvl_inter)); % for subplot config

figure
for i = 1:length(lvl_inter)
    
    try
        ax = subplot(p(1),p(2),i);
        mesh(Xgrid,Ygrid,Z) % plot map 3D
        colormap(ax,c_map)
        hold on
        surf(Xgrid,Ygrid,lvl_inter(i)*ones(size(Z)),'FaceColor','k','FaceAlpha',0.08,'EdgeColor','none')
        hold on
        zlabel 'z-Score [\sigma]'
    set(gca,'YTickLabel',[]);
    set(gca,'XTickLabel',[]);

        % Take the difference between the two surface heights and find the contour
        % where that surface is zero.
        zdiff = Z - (lvl_inter(i)*ones(size(Z)));
        C = contours(Xgrid, Ygrid, zdiff,[0,0]);
        
        %claculate the intersection area
        [a, ca] = cont_area(C,Xgrid,Ygrid,Z);

        % Visualize the line.
        cl = line(ca.xL, ca.yL, ca.zL, 'Color', 'k', 'LineWidth', 3);
        title(['A^2 : ' num2str(round(a,2)) ' // z : ' num2str(round(lvl_inter(i),2))]);
        
        area_inter(i) = a;
    catch
        area_inter(i) = 0;
    end

end


sgtitle (['Subj ' num2str(ID)])
save_fig(gcf,PATHOUT,['SurfArea_subj_' FB '_' num2str(ID)],'figtype','.png','figsize',[0 0 35 25],'fontsize',10)

end

