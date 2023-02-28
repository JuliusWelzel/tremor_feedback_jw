function outlet = createLSL

% instantiate LSL
lib = lsl_loadlib();

% make a new stream outlet
info = lsl_streaminfo(lib,'Delsys','EMG',4,0,'cf_float32');
outlet = lsl_outlet(info); 

end

