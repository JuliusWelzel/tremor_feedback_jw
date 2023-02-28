function make_fdbck_sound(tmp_A,tar_val)

amp         = 10; 
fs          = 8192;  % sampling frequency
duration    = 0.1;
freq        = 200 * 1/(abs(tar_val-tmp_A));
values      = 0:1/fs:duration;
dat_sound   = amp*sin(2*pi* freq*values);
sound(dat_sound)


end

