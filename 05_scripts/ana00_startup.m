%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%
%                       Setup envir
%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% tremor feedback
% Data: Jos Becktepe, University of Kiel
% Author: Julius Welzel (j.welzel@neurologie.uni-kiel.de)

clc; clear all; close all;

MAIN = [fileparts(pwd) '\'];
addpath(genpath(MAIN));
addpath([userpath '\toolboxes\eeglab2021.0\']);
addpath([userpath '\toolboxes\fieldtrip-20201023\']);
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