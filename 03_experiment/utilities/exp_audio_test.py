#######################################
#
#      Create int_trmr experiment using PsychoPy
#
#######################################
#
# Author: Julius Welzel (Neurogeriatrie, UKSH Kiel,University of Kiel)
# Contact: j.welzel@neurologie.uni-kiel.de
# Version: 1.0 // setting up default (15.07.2020)
# -*- coding: utf-8 -*-

#import standard packages
from psychopy import visual, core, event
import numpy as np
from pylsl import StreamInlet, resolve_stream, StreamOutlet, StreamInfo, local_clock, StreamInlet
import socket
import serial
import random

# self written fun
from modules.fun_startup import readMaxForce, SetTrialDist, InitLslArduino


def main_experiment():


        ## ################    Setup Streams     ####################

        # Create trigger stream:
        # create LSL trigger outlet
        info_marker_stream = StreamInfo('PsychoPyMarkers','Marker',1,0,'string')
        global out_marker
        out_marker = StreamOutlet(info_marker_stream)

        # create LSL arduino outlet
        global SerialArduino, SerialSRate
        SerialArduino   = serial.Serial(port = 'COM4', baudrate = 115200)
        SerialSRate     = 80
        # set LSL outlet for load cell
        global lc_out, clr_buf
        lc_out      = InitLslArduino()
        # buffer clearance for serial property
        clr_buf = 20

        # setup TCP to PD
        global s_pitch, s_vol
        s_pitch = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_pitch.connect(('localhost', 1000))

        s_vol = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_vol.connect(('localhost',1001))

        global schweb_pitch, schweb_vol
        schweb_pitch = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        schweb_pitch.connect(('localhost', 1002))

        schweb_vol = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        schweb_vol.connect(('localhost',1003))


        ## ################   Get Max Force   ##################
        global max_force
        chunk_      = []
        max_force   = []
        input ("Now ask for max force and press enter")

        # get max force
        for i in range(1):
            core.wait(1)
            print ('Now')
            chunk_ = readMaxForce(SerialArduino)
            max_force.insert(i,chunk_)
            print ('Done')

            if i == 2:
                continue
            input("Again ask for max. force")

        print("Max force is {} Unit\n".format(max(max_force)))
        max_force = max(max_force)
        input("Start LabRecorder, press any key to continue")
        out_marker.push_sample(['max_force_{}'.format(max_force)]) # output to lsl



        ## ################    Setup Psychopy     ####################

        # Set window and remove mouse during experiment:
        win_size = (1200,800)
        global win
        win = visual.Window(size = win_size, fullscr = False, allowGUI = False,
                            monitor='testMonitor', units='norm',color = [-1,-1,-1])

        # Experimental settings
        global design_mat, trial_num
        trial_num       = 5
        design_mat, trial_num = SetTrialDist( trial_num )

        global dur_hint, dur_bl, dur_fc, dur_trial
        dur_hint        = 1;
        dur_bl          = 1.5;
        dur_fc          = (10,15); # in deci seconds
        dur_trial       = 6;
        # total 1 + 1.5 + 1.25 + 6 = 9.75 s per trial (40 trials -> 6,5 min)

        # stimulus settings
        global wdth_bar, hght_bar, scaling_factor, tar_pos, c_red, c_green
        wdth_bar = 0.01
        hght_bar = 1
        scaling_factor = 1
        tar_pos = 0 # change scaling factor if different arduino setup

        c_red   = [115,38,38]


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
                                  width = wdth_bar , height = hght_bar + 2 * wdth_bar,
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


        # init some vars for passive condition
        global ArdBuff, TsBuff, TrialBuff
        ArdBuff = []
        TsBuff  = []
        TrialBuff = [None] * len(design_mat)

        ####################  TRAINING BLOCK ###################################
        # INTRO
        txt = "Block Lautstärke"
        presTextPsychoPy(txt)
        event.waitKeys()
        out_marker.push_sample(['blockLaut']) # output to lsl


        for i in range(trial_num):
            presTrialAud(i)

        txt = "Block Schwebung"
        presTextPsychoPy(txt)
        event.waitKeys()
        out_marker.push_sample(['blockSchweb']) # output to lsl


        for i in range(trial_num):
            presTrialAudSchweb(i)

        ####################  BLOCK 3 ###################################
        # INTRO
        txt = "Block 3 (ca 6 min)"
        presTextPsychoPy(txt)
        event.waitKeys()
        out_marker.push_sample(['block3']) # output to lsl

        # explain task 1
        txt = "Passiver Block"
        presTextPsychoPy(txt)
        event.waitKeys()

        for i in range(trial_num):

            if design_mat[i,1] == 1:
                presTrialVisPas(i)

            if design_mat[i,1] == 2:
                presTrialVisAudPas(i)

            if design_mat[i,1] == 3:
                presTrialAudPas(i)

        # end task 1
        txt = "Geschafft"
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



def presTrialVis(i):

    #transfer info for this trial from design mat
    SclFeedback     = design_mat[i,2]
    SclMaxForce     = design_mat[i,0]
    DurJitter       = design_mat[i,3]

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
    bar_target.autoDraw = True
    bar_force.autoDraw = True

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

            # update drawing of bars to automatic
            win.flip()

            # add to buffer for passive condition
            ArdBuff.append(current_force)
            c_flush += 1

    # stop autodraw
    bar_target.autoDraw = False
    bar_force.autoDraw = False

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
    bar_target.autoDraw = True
    bar_force.autoDraw = True

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
    bar_target.autoDraw = False
    bar_force.autoDraw = False

    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross
    # Turn of DSP in PD
    sent2PD(s_vol,0)

    TrialBuff[i] = ArdBuff


def presTrialVisPas(i):

    #transfer info for this trial from design mat
    SclFeedback     = design_mat[i,2]
    SclMaxForce     = design_mat[i,0]
    DurJitter       = design_mat[i,3]

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
    c = 0

    # send scaling factor to lsl
    out_marker.push_sample(['trial_start_sfb_{}_sfc_{}'.format(SclFeedback,SclMaxForce)]) # send scaling factor

    # update autodraw
    bar_target.autoDraw = True
    bar_force.autoDraw = True

    # init for LSL data
    start_time      = local_clock()
    sent_samples    = 0
    current_force   = 0

    while countdownTimer.getTime() + DurJitter > 0 : # add jitter to trial duration

        elapsed_time = local_clock() - start_time
        required_samples = int(80 * elapsed_time) - sent_samples # possible sampling rate of 80Hz

        if required_samples > 0:

            # add from buffer
            current_force = TrialBuff[i][c]
            c +=1

            # get a time stamp in seconds and add hardware time difference 5ms
            stamp = local_clock() - 0.005
            # now send it and wait for a bit
            lc_out.push_chunk([current_force])
            sent_samples += required_samples


            tmp_crs_pos = ((current_force - tar_force)/tar_force) * SclFeedback # offset inital bar placement, according to Archer ea., 2017
            bar_force.pos = (tmp_crs_pos,0)

            # update drawing of bars to automatic
            win.flip()

            # add to buffer for passive condition
            ArdBuff.append(current_force)
            TsBuff.append(stamp)

    # stop autodraw
    bar_target.autoDraw = False
    bar_force.autoDraw = False

    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross



def presTrialAudPas(i):

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
    c = 0

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

    while countdownTimer.getTime() + DurJitter > 0: # add jitter to trial duration

        elapsed_time = local_clock() - start_time
        required_samples = int(80 * elapsed_time) - sent_samples # possible sampling rate of 80Hz

        if required_samples > 0:

            # add from buffer
            current_force = TrialBuff[i][c]
            c +=1

            # get a time stamp in seconds and add hardware time difference 5ms
            stamp = local_clock() - 0.005
            # now send it and wait for a bit
            lc_out.push_chunk([current_force])
            sent_samples += required_samples

            tmp_x_pos = ((current_force-tar_force)/tar_force) * SclFeedback # offset inital bar placement, according to Archer ea., 2017
            sent2PD(s_pitch,tmp_x_pos)

            # update drawing of bars to automatic
            win.flip()

            # add to buffer for passive condition
            ArdBuff.append(current_force)
            TsBuff.append(stamp)

    # stop autodraw
    bar_target.autoDraw = False

    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross
    # Turn of DSP in PD
    sent2PD(s_vol,0)



def presTrialVisAudPas(i):

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
    c = 0

    # send scaling factor to lsl
    out_marker.push_sample(['trial_start_sfb_{}_sfc_{}'.format(SclFeedback,SclMaxForce)]) # send scaling factor

    sent2PD(s_pitch,0) # inital tone for PD
    sent2PD(s_vol,1)

    # update autodraw
    bar_target.autoDraw = True
    bar_force.autoDraw = True

    # init for LSL data
    start_time      = local_clock()
    sent_samples    = 0
    current_force   = 0


    while countdownTimer.getTime() + DurJitter > 0: # add jitter to trial duration

        elapsed_time = local_clock() - start_time
        required_samples = int(80 * elapsed_time) - sent_samples # possible sampling rate of 80Hz

        if required_samples > 0:

            # add from buffer
            current_force = TrialBuff[i][c]
            c +=1

            # get a time stamp in seconds and add hardware time difference 5ms
            stamp = local_clock() - 0.005
            # now send it and wait for a bit
            lc_out.push_chunk([current_force], stamp)
            sent_samples += required_samples


            tmp_crs_pos = ((current_force - tar_force)/tar_force) * SclFeedback # offset inital bar placement, according to Archer ea., 2017
            bar_force.pos = (tmp_crs_pos,0)
            sent2PD(s_pitch,tmp_crs_pos)

            win.flip()

            # add to buffer for passive condition
            ArdBuff.append(current_force)
            TsBuff.append(stamp)


    # stop autodraw
    bar_target.autoDraw = False
    bar_force.autoDraw = False

    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross
    # Turn of DSP in PD
    sent2PD(s_vol,0)


def endExp():
    key = event.getKeys
    if key == 'q':
        win.close
        core.quit

def is_ascii(c):
    return len(c) == len(c.encode())


def presTrialAudSchweb(i):

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
    sent2PD(schweb_vol,1)
    sent2PD(schweb_pitch,0) # inital tone for PD

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

            # get a time stamp in seconds and add hardware time difference 5ms
            stamp = local_clock() - 0.005
            # now send it and wait for a bit
            lc_out.push_chunk([current_force])
            sent_samples += required_samples

            tmp_x_pos = ((current_force-tar_force)/tar_force) * SclFeedback # offset inital bar placement, according to Archer ea., 2017
            sent2PD(schweb_pitch,tmp_x_pos)

            # update drawing of bars to automatic
            win.flip()

            # add to buffer for passive condition
            ArdBuff.append(current_force)
            TsBuff.append(stamp)

            c_flush += 1

    # stop autodraw
    bar_target.autoDraw = False

    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross
    # Turn of DSP in PD
    sent2PD(schweb_vol,0)

    TrialBuff[i] = ArdBuff
