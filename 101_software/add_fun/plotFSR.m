function plotFSR(a,tp,nsam_ma)

%plotFSR plot live FSR data from arduino for n tps

win_movavg = zeros(1,nsam_ma);

if isempty(a)
    a = arduino;
end

x = 0;
for k = 1:tp
    b = readVoltage(a, 'A0');   
    win_movavg = [win_movavg(2:end) b];
    b_ma = mean(win_movavg);
    x = [x, b_ma];
    plot (x);
    grid;
    drawnow;
    
end


end


