function [a,b,c,d, sr] = load_trmr(name)

    load(name);
    n_vars = who;
    
    sr = PNSSamplingRate;
    a = eval(n_vars{contains(n_vars,'Flex')});
    b = eval(n_vars{contains(n_vars,'Extens')});
    c = eval(n_vars{contains(n_vars,'mffx')});
    d = eval(n_vars{contains(n_vars,'mffy')});
    
end

