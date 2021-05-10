% get max force from table
function max_f = GetMaxForce(prob_info,sSUBJ)

    idx_s = strcmp(prob_info.ID,sSUBJ);
    max_f = prob_info.Maximalkraft(idx_s);

end


