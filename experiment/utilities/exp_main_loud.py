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
        clr_buf = 20


        # setup TCP to PD
        global s_pitch, s_vol
        s_pitch = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_pitch.connect(('localhost', 1000))

        s_vol = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s_vol.connect(('localhost',1001))


        ## ################   Get Max Force   ##################
        global max_force
        chunk_      = []
        max_force   = []
        input ("Now ask for max force and press enter")

        # get max force
        for i in range(3):
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
        win_size = (1920,1080)
        global win
        win = visual.Window(size = win_size, fullscr = True, allowGUI = False,
                            monitor='testMonitor', units='norm',color = [-1,-1,-1])

        # Experimental settings
        global design_mat, trial_num
        trial_num       = 40
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


        # init some vars for passive condition
        global ArdBuff,  TrialBuff
        ArdBuff = []
        TrialBuff = [None] * len(design_mat)

        ####################  TRAINING BLOCK ###################################
        # INTRO
        num_training = 5
        txt = "Trainingsblock"
        presTextPsychoPy(txt)
        event.waitKeys()
        out_marker.push_sample(['block0']) # output to lsl

        # explain task 1
        txt = "Drücken Sie so fest, dass sich die beiden vertikalen Balken überlappen und halten Sie diese Kraft."
        presTextPsychoPy(txt)
        event.waitKeys()

        for i in range(num_training):
            presTrialVis(i)

        # explain task 2
        txt = "Üben Sie wieder Druck aus bis sich die Balken überlappen. Sie bekommen einen zusätzlichen Ton als Rückmeldung."
        presTextPsychoPy(txt)
        event.waitKeys()

        for i in range(num_training):
            presTrialVisAud(i)

        audio_train = True
        while audio_train:
            # explain task 2 repeat if nesecary
            event.clearEvents()
            txt = "Drücken Sie erneut den Sensor. Allerdings bekommen Sie jetzt kein visuelles Feedback sondern nur ein auditives."
            presTextPsychoPy(txt)
            event.waitKeys()

            for i in range(num_training):
                presTrialAud(i)

            txt = "Auditive Bedingung verstanden? Drücke r zum Wiederholen und c zum Fortsetzen"
            presTextPsychoPy(txt)
            key = event.waitKeys()

            if key == ['r']:
                audio_train = True
            elif key == ['c']:
                audio_train = False



        ####################  BLOCK 1 ###################################

        # INTRO
        event.clearEvents()
        txt = "Block 1 (ca 6 min)"
        presTextPsychoPy(txt)
        event.waitKeys()
        out_marker.push_sample(['block1']) # output to lsl

        # explain task 1
        txt = "Steuern Sie das Ziel so schnell wie möglich an."
        presTextPsychoPy(txt)
        event.waitKeys()

        for i in range(trial_num*0,trial_num*1-1):

            if design_mat[i,1] == 1:
                presTrialVis(i)

            if design_mat[i,1] == 2:
                presTrialVisAud(i)

            if design_mat[i,1] == 3:
                presTrialAud(i)

        # end task 1
        txt = "Geschafft"
        presTextPsychoPy(txt)
        event.waitKeys()

        ####################  BLOCK 2 ###################################
        # INTRO
        txt = "Block 2 (ca 6 min)"
        presTextPsychoPy(txt)
        event.waitKeys()
        out_marker.push_sample(['block2']) # output to lsl

        # explain task 1
        txt = "Steuern Sie das Ziel so schnell wie möglich an."
        presTextPsychoPy(txt)
        event.waitKeys()

        for i in range(trial_num*1,trial_num*2-1):

            if design_mat[i,1] == 1:
                presTrialVis(i)

            if design_mat[i,1] == 2:
                presTrialVisAud(i)

            if design_mat[i,1] == 3:
                presTrialAud(i)

        # end task 1
        txt = "Geschafft"
        presTextPsychoPy(txt)
        event.waitKeys()

        ####################  BLOCK 3 ###################################
        # INTRO
        txt = "Block Passiv (ca 6 min)"
        presTextPsychoPy(txt)
        event.waitKeys()
        out_marker.push_sample(['block3']) # output to lsl

        # explain task 1
        txt = "Jetzt brauchen Sie nicht drücken"
        presTextPsychoPy(txt)
        event.waitKeys()

        for i in range(trial_num*0,trial_num*1-1):

            if design_mat[i,1] == 1:
                presTrialVisPas(i)

            if design_mat[i,1] == 2:
                presTrialVisAudPas(i)

            if design_mat[i,1] == 3:
                presTrialAudPas(i)

        # end task 1
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
    bar_force.autoDraw = True
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

            # now send it and wait for a bit
            lc_out.push_chunk([current_force])
            sent_samples += required_samples


            tmp_crs_pos = ((current_force - tar_force)/tar_force) * SclFeedback # offset inital bar placement, according to Archer ea., 2017
            bar_force.pos = (tmp_crs_pos,0)

            # update drawing of bars to automatic
            win.flip()

            # add to buffer for passive condition
            ArdBuff.append(current_force)

    # stop autodraw
    bar_force.autoDraw = False
    bar_target.autoDraw = False

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

            # now send it and wait for a bit
            lc_out.push_chunk([current_force])
            sent_samples += required_samples

            tmp_x_pos = ((current_force-tar_force)/tar_force) * SclFeedback # offset inital bar placement, according to Archer ea., 2017
            sent2PD(s_pitch,tmp_x_pos)

            # update drawing of bars to automatic
            win.flip()

            # add to buffer for passive condition
            ArdBuff.append(current_force)

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
    bar_force.autoDraw = True
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

            # now send it and wait for a bit
            lc_out.push_chunk([current_force])
            sent_samples += required_samples


            tmp_crs_pos = ((current_force - tar_force)/tar_force) * SclFeedback # offset inital bar placement, according to Archer ea., 2017
            bar_force.pos = (tmp_crs_pos,0)
            sent2PD(s_pitch,tmp_crs_pos)

            win.flip()

            # add to buffer for passive condition
            ArdBuff.append(current_force)


    # stop autodraw
    bar_force.autoDraw = False
    bar_target.autoDraw = False

    out_marker.push_sample(['end_trial']) # send 1 for start of fixation cross
    # Turn of DSP in PD
    sent2PD(s_vol,0)


def endExp():
    key = event.getKeys
    if key == 'q':
        win.close
        core.quit


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



def SetTrialDist(NumBlock):

    # num_block is the amount of trials per block

    num_frc = 3 # 3 target conditions
    num_con = 3 # 3 feedback conditions
    blocks  = 5 # n blocks in total

    NTrialsCon  = NumBlock // num_con # rounded number of trials for each condition with equal distribution
    NTrialsBlk  = NTrialsCon * num_con
    
    DesignMatExp = np.array([]).reshape(0,4) #prelocate

    for b in range(blocks):

        # define conditions (1 = visual only, 2 = audio-visual, 3 = audio only)
        con_vo  = np.ones(NTrialsCon) * 1
        con_av  = np.ones(NTrialsCon) * 2
        con_ao  = np.ones(NTrialsCon) * 3

        con_blk = np.concatenate((con_vo,con_av,con_ao), axis = None)


        # define target forces
        frc_20  = np.ones(NTrialsCon) * 0.20
        frc_25  = np.ones(NTrialsCon) * 0.25
        frc_30  = np.ones(NTrialsCon) * 0.30

        frc_blk = np.concatenate((frc_20,frc_25,frc_30), axis = None)
        np.random.shuffle(frc_blk)


        # define scale forin range 0.1-0.9
        scl_blk = np.random.randint(10,90,NTrialsBlk)/100

        # define jitter times for fix cross 1-1.5 s
        jit_blk = np.random.randint(10,15,NTrialsBlk)/10

        
        # stack different options, transpose them and shuffle
        blk_all = np.vstack((frc_blk,con_blk,scl_blk,jit_blk))
        blk_all = np.transpose(blk_all)
        np.random.shuffle(blk_all)

        # prep output
        DesignMatExp   = np.vstack((DesignMatExp,blk_all))

    return DesignMatExp, NTrialsBlk 


def InitLslArduino():
    
    name        = 'HX711'
    type        = 'ForceSensor'
    n_channels  = 1
    srate       = 80
    
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
    outlet = StreamOutlet(info, 80, 30)
    
    return outlet

