
close all
for e = 1:numel(eps.ppl);
sig     = eps.ppl(e).trial(21,:);
sig_out = isoutlier(sig,'movmean',60);
sig_    = smoothdata(sig,'rlowess',120);
std_ci = median(eps.ppl(e).trial(1,:)) * 0.95;
idx_oi = eps.ppl(e).trial(1,:) > std_ci & ~sig_out; 
sig_(~idx_oi) = NaN;
pd = fitdist(sig_','normal');
sig_((sig_ > pd.mean + pd.sigma) | (sig_ < pd.mean - 2*pd.sigma) ) = NaN;
ts = eps.ppl(e).ts - eps.ppl(e).ts(1);

subplot(4,4,e)
plot(ts,sig_)
hold on
plot(ts,eps.ppl(e).trial(1,:))
hold on
vline(30)
axis tight
hline(std_ci)
title([num2str(round(pd.sigma/pd.mean,4))])


end
