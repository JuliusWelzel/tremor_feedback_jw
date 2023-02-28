#######################################
#
#      Recreate Archer ea., experiment using PsychoPy
#
#######################################
#
# Author: Julius Welzel (Neurogeriatrie, UKSH Kiel,University of Kiel)
# Contact: j.welzel@neurologie.uni-kiel.de
# Version: 1.0 // setting up default (01.08.2021)
# -*- coding: utf-8 -*-

#import standard packages
from psychopy import visual, core, event
import numpy as np
from pylsl import StreamInlet, resolve_stream, StreamOutlet, StreamInfo, local_clock, StreamInlet
import socket
import serial



def main_experiment():


    ## ################    Setup Streams     ####################
    
    # Create trigger stream:
    # create LSL trigger outlet
    info_marker_stream = StreamInfo('PsychoPyMarkers','Marker',1,0,'string')
    global out_marker
    out_marker = StreamOutlet(info_marker_stream)
    
    # create LSL arduino outlet
    global SerialArduino, SerialSRate
    SerialArduino   = serial.Serial(port = 'COM5', baudrate = 115200)
    SerialSRate     = 80
    # set LSL outlet for load cell
    global lc_out, clr_buf
    lc_out      = InitLslArduino()
    clr_buf     = 20
    
    
    # setup TCP to PD
    global s_pitch, s_vol
    s_pitch = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_pitch.connect(('localhost', 1000))
    
    s_vol = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s_vol.connect(('localhost',1001))

    ## ################    Setup Psychopy     ####################

    # Set window and remove mouse during experiment:
    win_size = (400,400)
    global win
    win = visual.Window(size = win_size, fullscr = False, allowGUI = False,
                        monitor='testMonitor', units='norm',color = [-1,-1,-1])


    # Experimental settings
    global design_mat, trial_num
    trial_num       = 40
    design_mat = SetTrialDist()
    

    global dur_wait, dur_trial
    dur_wait    = 30    
    dur_trial   = 30;

    # stimulus settings
    global wdth_bar, hght_bar, tar_pos, c_red, c_green
    wdth_bar = 0.01
    hght_bar = 1
    tar_pos = 0 # change scaling factor if different arduino setup

    c_red   = [115,38,38]
    c_green = [38,115,77]




    ## ################    Stimuli Psychopy    #################

    ## intro
    global exp_text
    exp_text = visual.TextStim(win,
                                 pos=[0,0],
                                 color = (1,1,1)
                                 )

    ## main trial components
    global fixation
    fixation =  visual.TextStim(win,
                                pos=[0,0],
                                text = '+',
                                height = 0.7,
                                color = (0,0,0)
                                )

    global bar_target
    bar_target  = visual.Rect(win,
                              width = wdth_bar , height = hght_bar + 8 * wdth_bar,
                              pos=[tar_pos,0],
                              fillColor = 'grey', lineColor = 'black',
                              )

    global bar_force
    bar_force   = visual.Rect(win,
                              width = wdth_bar * 4, height = hght_bar,
                              pos=[0,0],
                              fillColor = c_red, lineColor = c_red, fillColorSpace='rgb255',lineColorSpace='rgb255',
                              autoDraw=False
                              )




    #Set timer
    global timer
    timer = core.Clock()


    
    
    ## ################   Get Max Force   ##################
    # init some vars for passive condition
    check_max_force = True
    while check_max_force:
        mf = presGetMaxForce()
        max_force = round(np.array(mf).mean(),0)
        presTextPsychoPy("Max. Kraft gesamt: {}".format(max_force))
        
        key = event.waitKeys()
        
        txt = "Maximalkraft korrekt? Drücke r zum Wiederholen und c zum Fortsetzen"
        presTextPsychoPy(txt)
        key = event.waitKeys()
        
        if key == ['r']:
            check_max_force = True
        elif key == ['c']:
            check_max_force = False
            
    # get max force
    out_marker.push_sample(['max_force_{}'.format(max_force)]) # output to lsl

    
    ####################  TRAINING BLOCK ###################################
    # INTRO
    txt = "Trainingsblock"
    presTextPsychoPy(txt)
    event.waitKeys()
    out_marker.push_sample(['block0']) # output to lsl

    # explain task 1
    txt = "Sobald der Balken Grün wird drücken Sie so fest, dass sich die beiden vertikalen Balken überlappen und halten Sie diese Kraft."
    presTextPsychoPy(txt)
    event.waitKeys()

    presRest(0,3)
    presTrialVis(0,5)

    # explain task 2
    txt = "Üben Sie wieder Druck aus bis sich die Balken überlappen."
    presTextPsychoPy(txt)
    event.waitKeys()

    presRest(1,3)
    presTrialVis(1,5)


    ####################  BLOCK VIS ###################################

    # INTRO
    event.clearEvents()
    txt = "Block 1 (ca 6 min)"
    presTextPsychoPy(txt)
    event.waitKeys()
    out_marker.push_sample(['block1']) # output to lsl

    # explain task 1
    txt = "Steuern Sie das Ziel so schnell wie möglich an und halten sie die Balken genau übereinander."
    presTextPsychoPy(txt)
    event.waitKeys()

    for i in range(2,6):

        presRest(i,dur_trial)
        presTrialVis(i,dur_trial)

    presRest(i,dur_trial)

        
    ####################  BLOCK AUDVIS ###################################

    # INTRO
    event.clearEvents()
    txt = "Block 2 (ca 6 min)"
    presTextPsychoPy(txt)
    event.waitKeys()
    out_marker.push_sample(['block1']) # output to lsl

    # explain task 1
    txt = "Steuern Sie das Ziel so schnell wie möglich an und halten sie die Balken genau übereinander. Jetzt hören Sie einen zusätzlichen Ton."
    presTextPsychoPy(txt)
    event.waitKeys()

    presRest(i,dur_trial)
    
    for i in range(2,6):

        presRest(i,dur_trial)
        presTrialVisAud(i,dur_trial)
        
    presRest(i,dur_trial)

        
    ####################  BLOCK AUD ###################################

    # INTRO
    event.clearEvents()
    txt = "Block 3 (ca 6 min)"
    presTextPsychoPy(txt)
    event.waitKeys()
    out_marker.push_sample(['block1']) # output to lsl

    # explain task 1
    txt = "Steuern Sie das Ziel so schnell wie möglich an und halten sie die Balken genau übereinander. Jetzt hören Sie einen zusätzlichen Ton."
    presTextPsychoPy(txt)
    event.waitKeys()

    presRest(i,dur_trial)
    
    for i in range(2,6):

        presRest(i,dur_trial)
        presTrialVisAud(i,dur_trial)
        
    presRest(i,dur_trial)

    # end task 
    txt = "Geschafft. Beende die Aufnahme"
    presTextPsychoPy(txt)
    event.waitKeys()


    ## ################    FINISH UP     ####################

    # Cleanup (always!)
    win.close()
    core.quit()
    print ("DONE")



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
    global max_force
    chunk       = []
    max_force_trials   = [None] * 3
    
    # make bar red again
    bar_force.fillColor = c_red
    bar_force.lineColor = c_red

    for i in range(3):
    
        dur_get_max_force = 3
        out_marker.push_sample(['start_get_max_force_{}'.format(i)]) # send scaling factor
        presTextPsychoPy("Sie sehen gleich einen grünen Balken. Sobald der Balken rot wird, drücken Sie so FEST wie möglich.")
        event.waitKeys()
        
        
        # reset input buffer from serial port
        SerialArduino.reset_input_buffer()
        ard_buffer = []
        max_force = np.array([])
        
        # draw red bar and wait for 1 s
        bar_force.draw()
        win.flip()
        core.wait(1)
        
        # init for LSL data
        start_time      = local_clock()
        sent_samples    = 0
        current_force   = 0
    
        c_flush = 0
    
        # reset trial timer
        timer.reset()
        countdownTimer = core.CountdownTimer(dur_get_max_force)
    
        # update bar to green    
        bar_force.fillColor = c_green
        bar_force.lineColor = c_green
        bar_force.draw()
        win.flip()
    
        max_force, ard_buffer = readMaxForce()                
        lc_out.push_chunk([ard_buffer])
        out_marker.push_sample(['end_max_force_block_{}'.format(i)]) # send marker to LSL
        
        # make bar red again
        bar_force.fillColor = c_red
        bar_force.lineColor = c_red
    
        # save force from 3s trial to np array
        max_force_trials[i] = np.array(max_force)
    
    presTextPsychoPy("Geschafft!")
    return max_force_trials

    

def presTrialVis(i,dur_trial):
    
    #transfer info for this trial from design mat
    SclFeedback     = design_mat[i]
    SclMaxForce     = 0.15
    
    #present trial intrsuctions
    out_marker.push_sample(['epoch_vo_start']) # send scaling factor
    
    
    # reset trial timer
    timer.reset()
    countdownTimer = core.CountdownTimer(dur_trial)
    
    
    tar_force = max_force * SclMaxForce
    
    # reset input buffer from serial port
    SerialArduino.reset_input_buffer()
    ard_buffer = []
    
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
    
    while countdownTimer.getTime() > 0: 
        
        elapsed_time = local_clock() - start_time
        required_samples = int(SerialSRate * elapsed_time) - sent_samples # possible sampling rate of 80Hz
        
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
            ard_buffer.append(current_force)
            c_flush += 1
    
    # stop autodraw
    bar_force.autoDraw = False
    bar_target.autoDraw = False
    
    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross


def presTrialAud(i,dur_trial):

    #transfer info for this trial from design mat
    SclFeedback     = design_mat[i]
    SclMaxForce     = 0.15

    #present trial intrsuctions
    out_marker.push_sample(['epoch_ao_start']) # send scaling factor

    # reset trial timer
    timer.reset()
    countdownTimer = core.CountdownTimer(dur_trial)


    tar_force = max_force * SclMaxForce

    # reset input buffer from serial port
    SerialArduino.reset_input_buffer()
    ard_buffer = []

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

    while countdownTimer.getTime() > 0: # add jitter to trial duration

        elapsed_time = local_clock() - start_time
        required_samples = int(SerialSRate * elapsed_time) - sent_samples # possible sampling rate of 80Hz

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
            ard_buffer.append(current_force)
            c_flush += 1

    # stop autodraw
    bar_target.autoDraw = False

    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross
    # Turn of DSP in PD
    sent2PD(s_vol,0)


def presTrialVisAud(i,dur_trial):

    #transfer info for this trial from design mat
    SclFeedback     = design_mat[i]
    SclMaxForce     = 0.15

    #present trial intrsuctions
    out_marker.push_sample(['epoch_va_start']) # send scaling factor


    # reset trial timer
    timer.reset()
    countdownTimer = core.CountdownTimer(dur_trial)


    tar_force = max_force * SclMaxForce

    # reset input buffer from serial port
    SerialArduino.reset_input_buffer()
    ard_buffer = []

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

    while countdownTimer.getTime() > 0: # add jitter to trial duration

        elapsed_time = local_clock() - start_time
        required_samples = int(SerialSRate * elapsed_time) - sent_samples # possible sampling rate of 80Hz

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
            ard_buffer.append(current_force)
            c_flush += 1


    # stop autodraw
    bar_force.autoDraw = False
    bar_target.autoDraw = False

    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross
    # Turn of DSP in PD
    sent2PD(s_vol,0)


def presRest(i,dur_wait):
    # update bar to green and center
    bar_force.pos = (-design_mat[i],0)
    bar_force.fillColor = c_red
    bar_force.lineColor = c_red
    bar_force.draw()
    win.flip()
    core.wait(dur_wait)
    
    bar_force.fillColor = c_green
    bar_force.lineColor = c_green



# read force for 3 s and return mean of all values 
def readMaxForce():
    
    # reset input buffer from serial port
    SerialArduino.reset_input_buffer()
    
    # start CountdownTimer
    cd_max_f = core.CountdownTimer(3)
    
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
    max_force = round(np.asarray(all_f).mean(),0)
    
    return max_force, all_f


def SetTrialDist():

    # Set experimental setup

    dist_screen     = 95 #in cm
    width_screen    = 52.2 #in cm

    view_angle_sml  = 0.39
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
    srate       = SerialSRate

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
    outlet = StreamOutlet(info, SerialSRate, 30)

    return outlet
