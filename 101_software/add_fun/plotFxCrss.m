function  plotFxCrss(LW,xl,yl)

ca = gca;

% Get the centre coordinate of the window
xCenter = [ca.XLim(1)+ca.XLim(2)]/2;
yCenter = [ca.YLim(1)+ca.YLim(2)]/2;

% Here we set the size of the arms of our fixation cross
LW = 5;
LS_y = 0.075;
LS_x = 1;


plot([xCenter xCenter],[yCenter-LS_y yCenter+LS_y],'w','LineWidth',LW)
hold on
plot([xCenter-LS_x xCenter+LS_x],[yCenter yCenter],'w','LineWidth',LW)

% set axs
xlim (xl)
ylim (yl)

axis off

end

