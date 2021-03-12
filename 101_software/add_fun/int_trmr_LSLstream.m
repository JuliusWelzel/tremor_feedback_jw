function outlet = int_trmr_LSLstream(lib,Name,Type,nChan)



info = lsl_streaminfo(lib,Name,Type,nChan,100,'cf_double64','arduinoUNO');

outlet = lsl_outlet(info);



end

