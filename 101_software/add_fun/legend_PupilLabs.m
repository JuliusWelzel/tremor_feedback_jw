function  legend_PupilLabs

    xlabel 'time [s]'
    axis tight
    box off
    ylabel 'Pupil size [mm²]'
    
    % Add all our previous improvements:
    ax = gca();
    ax.XAxisLocation = 'origin';
    box off;
    
    vline([-5 -1],'--k')
    vline(0,'k')
    
end

