function ppl = prep_ppl_it(ppl)
%prep_ppl_it Preprocesses pupil labs LSL time Series,

%% reorder new time vector
new_times = linspace(ppl.time_stamps(1),ppl.time_stamps(end),numel(ppl.time_stamps));
ppl.time_stamps = new_times;

for ch = [21,22]
    clear tmp
    tmp = smoothdata(ppl.time_series(ch,:),'omitnan');
    ppl.time_series(ch,:) = interp1(new_times(~isnan(tmp)),tmp(~isnan(tmp)),new_times); %interpolate NaNs in data 

end

display ('PPL prep done')

end

