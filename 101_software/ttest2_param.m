function [all] = ttest2_param(group_1,group_2)

    [h_t p_t ci_t s] = ttest2(group_1,group_2);
    
    %t-val
    all.t_val = s.tstat;
    
    %df
    all.df = s.df;
    
    %group MEAN
    all.M(1) = mean(group_1);
    all.M(2) = mean(group_2);
    
    %group MEAN
    all.SD(1) = std(group_1);
    all.SD(2) = std(group_2);
    
    all.p = p_t
    
end

