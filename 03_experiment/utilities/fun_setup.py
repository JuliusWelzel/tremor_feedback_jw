
###############################################################################
#
#           ADDITIONAL FUN
#
##############################################################################

# prep data to send to tcp port
def sent2PD(s_tcp,msg):
    tcp_str = str(msg)
    tcp_str += ';'
    str2sent = tcp_str.encode()
    s_tcp.send(str2sent)


# Update text on screen in psychopy
def presTextPsychoPy(txt):
    exp_text.text = txt
    exp_text.draw()
    win.flip()

def presGetMaxForce():
    

def presTrialVis(i):

    #transfer info for this trial from design mat
    SclFeedback     = design_mat[i,2]
    SclMaxForce     = 0.15

    #present trial intrsuctions
    out_marker.push_sample(['epoch_vo_start']) # send scaling factor
    presTextPsychoPy("Nur visuell")
    core.wait(dur_hint)

    # start baseline
    out_marker.push_sample(['baseline'])
    presTextPsychoPy(" ")
    core.wait(dur_bl)

    # reset trial timer
    timer.reset()
    countdownTimer = core.CountdownTimer(dur_trial)

    # draw fixation cross
    fixation.draw()
    win.flip()
    out_marker.push_sample(['fix_cross']) # output to lsl

    core.wait(DurJitter)

    tar_force = max_force * SclMaxForce

    # reset input buffer from serial port
    SerialArduino.reset_input_buffer()
    ArdBuff = []

    # send scaling factor to lsl
    out_marker.push_sample(['trial_start_sfb_{}_sfc_{}'.format(SclFeedback,SclMaxForce)]) # send scaling factor

    # update autodraw
    bar_force.autoDraw = True
    bar_target.autoDraw = True

    # init for LSL data
    start_time      = local_clock()
    sent_samples    = 0
    current_force   = 0

    c_flush = 0

    while countdownTimer.getTime() + DurJitter > 0: # add jitter to trial duration

        elapsed_time = local_clock() - start_time
        required_samples = int(60 * elapsed_time) - sent_samples # possible sampling rate of 80Hz

        if required_samples > 0:

            tmp = SerialArduino.readline().rstrip() # read from serial port

            if not tmp: # continue to next iteration if buffer is empty
                tmp = current_force
            else:
                try:
                    current_force = float(tmp)
                except ValueError:
                    current_force = current_force

            if c_flush % clr_buf == 0: # flush buffer every 10 runs for no overhead
                SerialArduino.reset_input_buffer()

            # now send it and wait for a bit
            lc_out.push_chunk([current_force])
            sent_samples += required_samples


            tmp_crs_pos = ((current_force - tar_force)/tar_force) * SclFeedback # offset inital bar placement, according to Archer ea., 2017
            bar_force.pos = (tmp_crs_pos,0)

            # update drawing of bars to automatic
            win.flip()

            # add to buffer for passive condition
            ArdBuff.append(current_force)
            c_flush += 1

    # stop autodraw
    bar_force.autoDraw = False
    bar_target.autoDraw = False

    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross

    TrialBuff[i] = ArdBuff


def presTrialAud(i):

    #transfer info for this trial from design mat
    SclFeedback     = design_mat[i,2]
    SclMaxForce     = design_mat[i,0]
    DurJitter       = design_mat[i,3]

    #present trial intrsuctions
    out_marker.push_sample(['epoch_ao_start']) # send scaling factor
    presTextPsychoPy("Nur auditiv")
    core.wait(dur_hint)

    # start baseline
    out_marker.push_sample(['baseline'])
    presTextPsychoPy(" ")
    core.wait(dur_bl)

    # reset trial timer
    timer.reset()
    countdownTimer = core.CountdownTimer(dur_trial)

    # draw fixation cross
    fixation.draw()
    win.flip()
    out_marker.push_sample(['fix_cross']) # output to lsl
    core.wait(DurJitter)

    tar_force = max_force * SclMaxForce

    # reset input buffer from serial port
    SerialArduino.reset_input_buffer()
    ArdBuff = []

    # send scaling factor to lsl
    out_marker.push_sample(['trial_start_sfb_{}_sfc_{}'.format(SclFeedback,SclMaxForce)]) # send scaling factor
    sent2PD(s_vol,1)
    sent2PD(s_pitch,0) # inital tone for PD

    # update autodraw
    bar_target.autoDraw = True

    # init for LSL data
    start_time      = local_clock()
    sent_samples    = 0
    current_force   = 0

    c_flush = 0

    while countdownTimer.getTime() + DurJitter > 0: # add jitter to trial duration

        elapsed_time = local_clock() - start_time
        required_samples = int(80 * elapsed_time) - sent_samples # possible sampling rate of 80Hz

        if required_samples > 0:

            tmp = SerialArduino.readline().rstrip() # read from serial port

            if not tmp: # continue to next iteration if buffer is empty
                tmp = current_force
            else:
                try:
                    current_force = float(tmp)
                except ValueError:
                    current_force = current_force

            if c_flush % clr_buf == 0: # flush buffer every 10 runs for no overhead
                SerialArduino.reset_input_buffer()

            # now send it and wait for a bit
            lc_out.push_chunk([current_force])
            sent_samples += required_samples

            tmp_x_pos = ((current_force-tar_force)/tar_force) * SclFeedback # offset inital bar placement, according to Archer ea., 2017
            sent2PD(s_pitch,tmp_x_pos)

            # update drawing of bars to automatic
            win.flip()

            # add to buffer for passive condition
            ArdBuff.append(current_force)
            c_flush += 1

    # stop autodraw
    bar_target.autoDraw = False

    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross
    # Turn of DSP in PD
    sent2PD(s_vol,0)

    TrialBuff[i] = ArdBuff


def presTrialVisAud(i):

    #transfer info for this trial from design mat
    SclFeedback     = design_mat[i,2]
    SclMaxForce     = design_mat[i,0]
    DurJitter       = design_mat[i,3]

    #present trial intrsuctions
    out_marker.push_sample(['epoch_va_start']) # send scaling factor
    presTextPsychoPy("Visuell & auditiv")
    core.wait(dur_hint)

    # start baseline
    out_marker.push_sample(['baseline'])
    presTextPsychoPy(" ")
    core.wait(dur_bl)

    # reset trial timer
    timer.reset()
    countdownTimer = core.CountdownTimer(dur_trial)

    # draw fixation cross
    fixation.draw()
    win.flip()
    out_marker.push_sample(['fix_cross']) # output to lsl

    core.wait(DurJitter)

    tar_force = max_force * SclMaxForce

    # reset input buffer from serial port
    SerialArduino.reset_input_buffer()
    ArdBuff = []

    # send scaling factor to lsl
    out_marker.push_sample(['trial_start_sfb_{}_sfc_{}'.format(SclFeedback,SclMaxForce)]) # send scaling factor

    sent2PD(s_pitch,0) # inital tone for PD
    sent2PD(s_vol,1)

    # update autodraw
    bar_force.autoDraw = True
    bar_target.autoDraw = True

    # init for LSL data
    start_time      = local_clock()
    sent_samples    = 0
    current_force   = 0

    c_flush = 0

    while countdownTimer.getTime() + DurJitter > 0: # add jitter to trial duration

        elapsed_time = local_clock() - start_time
        required_samples = int(80 * elapsed_time) - sent_samples # possible sampling rate of 80Hz

        if required_samples > 0:

            tmp = SerialArduino.readline().rstrip() # read from serial port

            if not tmp: # continue to next iteration if buffer is empty
                tmp = current_force
            else:
                try:
                    current_force = float(tmp)
                except ValueError:
                    current_force = current_force

            if c_flush % clr_buf == 0: # flush buffer every 10 runs for no overhead
                SerialArduino.reset_input_buffer()

            # now send it and wait for a bit
            lc_out.push_chunk([current_force])
            sent_samples += required_samples


            tmp_crs_pos = ((current_force - tar_force)/tar_force) * SclFeedback # offset inital bar placement, according to Archer ea., 2017
            bar_force.pos = (tmp_crs_pos,0)
            sent2PD(s_pitch,tmp_crs_pos)

            win.flip()

            # add to buffer for passive condition
            ArdBuff.append(current_force)
            c_flush += 1


    # stop autodraw
    bar_force.autoDraw = False
    bar_target.autoDraw = False

    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross
    # Turn of DSP in PD
    sent2PD(s_vol,0)

    TrialBuff[i] = ArdBuff



# read force for 1 s and return mean of all values higher than the mean in this time window
def readMaxForce(SerialArduino):

    # reset input buffer from serial port
    SerialArduino.reset_input_buffer()

    # start CountdownTimer
    cd_max_f = core.CountdownTimer(1)

    # try to read data
    all_f = []
    while cd_max_f.getTime() >0:
        tmp = SerialArduino.readline().rstrip()

        try:
            all_f.append(float(tmp))

        except ValueError:
            continue

    if not all_f:
        print('No reading possible')

    m_force = np.asarray(all_f).mean()

    max_force = round(np.asarray(all_f)[np.asarray(all_f) >= m_force/2].mean(),0)
    print('The current max. Force is {}. Should be between 4000-12000.'.format(max_force))

    return max_force


def SetTrialDist():

    # Set experimental setup

    dist_screen     = 95 #in cm
    width_screen    = 52.2 #in cm

    view_angle_sml  = 0.0039
    view_angle_big  = 6.9

    scl_big         = dist_screen*np.tan(np.deg2rad(view_angle_big)) / (width_screen/2)
    scl_sml         = dist_screen*np.tan(np.deg2rad(view_angle_sml)) / (width_screen/2)

    DesignViewAng = np.array([scl_big,scl_big,scl_sml,scl_sml])
    np.random.shuffle(DesignViewAng)

    # add 2 training blocks
    DesignViewAng = np.concatenate((np.array([scl_big,scl_sml]),DesignViewAng))

    return DesignViewAng


def InitLslArduino():

    name        = 'HX711'
    type        = 'ForceSensor'
    n_channels  = 1
    srate       = 60

    info = StreamInfo(name, type, n_channels, srate, 'float32', 'IntTrmr1001')

    # append some meta-data
    info.desc().append_child_value("manufacturer", "Arduino")
    channel_names = ['ForceSensor']
    chns = info.desc().append_child("channels")
    for label in channel_names:
        ch = chns.append_child("channel")
        ch.append_child_value("label", label)
        ch.append_child_value("unit", "a.u.")
        ch.append_child_value("type", "Arduino")

    # next make an outlet; we set the transmission chunk size to 32 samples and
    # the outgoing buffer size to 360 seconds (max.)
    outlet = StreamOutlet(info, 60, 30)

    return outlet
