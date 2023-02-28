function tune_BP(color)

h = findobj(gca,'Tag','Box');

if size(color,1) == length(h)
    
    h = findobj(gca,'Tag','Box');
    hm = findobj(gca,'Tag','Median');

     for j=1:length(h)
        patch(get(h(j),'XData'),get(h(j),'YData'),color(j,:),'FaceAlpha',.5);
        set(hm(j),'Color',color(j,:))
        set(hm(j),'LineWidth',2)

     end

    
else
    h = findobj(gca,'Tag','Box');
     for j=1:length(h)
        patch(get(h(j),'XData'),get(h(j),'YData'),color,'FaceAlpha',.5);
     end

    h = findobj(gca,'Tag','Median');
    set(h,'Color',color)
    set(h,'LineWidth',2)

end
