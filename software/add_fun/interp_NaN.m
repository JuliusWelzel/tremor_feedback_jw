function inter_vec = interp_NaN(vec)


N = ~isnan(vec);
Y = cumsum(N-diff([1,N])/2);
inter_vec = interp1(1:nnz(N),vec(N),Y);

end

