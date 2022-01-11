function plot_psd(dat,varargin)
% plot_psd: Function to plot the times/indices/... on a zero vector and
% estimate psd with it and plot
%     
% INPUT: 
%       dat: vector of data points
%       PATHOUT: string to where figure should be saved
%       NAME: Name as string under which figure should be saved
% 
% DEFAULTS: 
%       format is .png as default, can be changed to any type
% 
% 
% Author: (Julius Welzel & Mareike Daeglau, University of Oldenburg, 2018)


% check for name value pairs
% Parse inputs: 
p = inputParser;
defaultKernelwidth = 100; 
addParameter(p,'Kernelwidth',defaultKernelwidth,@isnumeric);
defaultColor = [0 0 0]; 
addParameter(p,'Color',defaultColor,@isnumeric);

parse(p,varargin{:});
KernelWidth = p.Results.Kernelwidth;
color       = p.Results.Color;

% do actual plotting
ms_sam = 1000/80; % ms per sample

% estimate probability density function 
[pd vec_pdf] = ksdensity(dat,'Bandwidth',KernelWidth);


plot(dat,zeros(size(dat)),'|','MarkerSize',20,'MarkerFaceColor',color,'MarkerEdgeColor',color)

% plot densitys
hold on
plot(vec_pdf,pd,'Color',color)

box off
ylabel 'Density'
xlabel 'Time [ms]'
ylim([-max(pd)*.1 max(pd)])
hline(0,':k')



end

