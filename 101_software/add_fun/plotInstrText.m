function  plotInstTxt(txt,fSize,xl,yl)

ca = gca;

% Get the centre coordinate of the window
xCenter = [ca.XLim(1)+ca.XLim(2)]/2;
yCenter = [ca.YLim(1)+ca.YLim(2)]/2;

% set text
text(xCenter-4,yCenter,txt,'FontSize',fSize,'Color','white')

% set axs
xlim (xl)
ylim (yl)

axis off

end

