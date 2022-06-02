%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%                       Setup envir
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% tremor feedback
% Data: Jos Becktepe, University of Kiel
% Author: Julius Welzel (j.welzel@neurologie.uni-kiel.de)

clc; clear all; close all;
filepath = fileparts(mfilename('fullpath'));
cd (filepath)

MAIN = fullfile(fileparts(pwd));
addpath(genpath(MAIN));
addpath(fullfile(userpath,'\toolboxes\xdf-Matlab-master'));
addpath(fullfile(userpath,'\toolboxes\eeglab2021.0\'));
addpath(fullfile(userpath,'\toolboxes\fieldtrip-20220104\'));
ft_defaults

%Change MatLab defaults
set(0,'defaultfigurecolor',[1 1 1]);

%colors
global color
color.c_vo = hex2rgb('#5e3f5d');
color.c_av = hex2rgb('#cd4c31');
color.c_ao = hex2rgb('#f7a51e');

color.shade = 0.3;

% ana01_prep