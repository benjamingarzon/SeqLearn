#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 08:41:28 2018

@author: benjamin.garzon@gmail.com

Training tool for discrete sequence production.
"""

from __future__ import division
from psychopy import visual, core, event, prefs
from datetime import datetime
from lib.utils import showStimulus, scorePerformance, startSession, filter_keys
from generator.generator import string_to_seq, seq_to_string, seq_to_stim
prefs.general['audioLib'] = ['pygame']
from psychopy import sound
import numpy as np
import pandas as pd
import os, glob, json
from argparse import ArgumentParser
from sqlalchemy import create_engine, exc
from sshtunnel import SSHTunnelForwarder

def SeqLearn(opts):

    # start session
    if opts.restart: # remove previous files
        for fl in glob.glob("./data/*.csv"):
            os.remove(fl)    
    
    sess_date = str(datetime.now().date())
    sess_time = str(datetime.now().time())
    sched_group, sess_num, username, keyswriter, trialswriter, keysfile, \
    trialsfile, maxscore, maxgroupscore, config, texts, schedule, \
    schedule_unique = \
    startSession(opts)
    
    win = visual.Window(config["SCREEN_RES"],
                        fullscr=False, 
                        monitor="testMonitor", 
                        units="cm")
    
    # define window and stimuli
    buzzer = sound.Sound(config["BUZZER_FILE"])
    intro_message = visual.TextStim(win, 
                                    text=texts["TEXT_INTRO"].format(username, 
                                               sess_num), 
                                               height = \
                                               config["HEADING_TEXT_HEIGHT"], 
                                               alignHoriz='center') 
    
    instructionspre1_message = visual.TextStim(win, 
                                           text=texts["TEXT_INSTRUCTPRE1"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz='center',
                                           pos = (-5, 0), 
                                           wrapWidth = 11 ) 

    instructionspre2_message = visual.TextStim(win, 
                                           text=texts["TEXT_INSTRUCTPRE2"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz='center')
    
    instructions1_message = visual.TextStim(win, 
                                           text=texts["TEXT_INSTRUCT1"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz='center',
                                           pos = (-5, 0), 
                                           wrapWidth = 11) 
    
    instructions2_message = visual.TextStim(win, 
                                           text=texts["TEXT_INSTRUCT2"].format(
                                                   config["MAX_WAIT"], 
                                                   config["TOTAL_TRIALS"]), 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz='center') 
    
    instructions3_message = visual.TextStim(win, 
                                           text=texts["TEXT_INSTRUCT3"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz='center') 
    
    instructions4_message = visual.TextStim(win, 
                                           text=texts["TEXT_INSTRUCT4"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz='center',
                                           color='red') 
    
    last_label = visual.TextStim(win, 
                                    text=texts["LAST_LABEL"], 
                                    height = config["TEXT_HEIGHT"], 
                                    pos = (-3*config["BAR_WIDTH"], 
                                           -0.5*config["BAR_HEIGHT"] - 2),
                                    alignHoriz='center') 

    best_label = visual.TextStim(win, 
                                 text=texts["BEST_LABEL"], 
                                 height = config["TEXT_HEIGHT"],
                                 pos = (0, 
                                        -0.5*config["BAR_HEIGHT"] - 2),
                                 alignHoriz='center') 
    
    group_best_label = visual.TextStim(win, 
                                 text=texts["GROUP_BEST_LABEL"], 
                                 height = config["TEXT_HEIGHT"],
                                 pos = (3*config["BAR_WIDTH"], 
                                        -0.5*config["BAR_HEIGHT"] - 2),
                                 alignHoriz='center') 
                                 
    error_message = visual.TextStim(win, 
                                    text=texts["TEXT_ERROR"], 
                                    alignHoriz="center", 
                                    pos = (0, -3))  
    error_sign = visual.ImageStim(win, 
                                  image=config["WRONG_FILE"],
                                  pos = (0, 2))
    
    hand_sign = visual.ImageStim(win, 
                                  image=config["HAND_FILE"],
                                  pos = (6, 0))
     
    late_message = visual.TextStim(win, 
                                    text=texts["TEXT_LATE"], 
                                    alignHoriz="center", 
                                    pos = (0, -3))  

    miss_message = visual.TextStim(win, 
                                    text=texts["TEXT_MISS"], 
                                    alignHoriz="center")
        
    # fixation cross
    fixation = visual.ShapeStim(win, 
        vertices=((0, -0.5), (0, 0.5), (0,0), (-0.5,0), (0.5, 0)),
        lineWidth=5,
        closeShape=False,
        lineColor="white"
    )
    
    trialClock = core.Clock()
    
    ## Experiment Section
    
    #display instructions and wait
    showStimulus(win, [intro_message])
    core.wait(config["INTRO_TIME"])
    
    if config["PRESHOW"]==1:
    
        showStimulus(win, [instructionspre1_message, hand_sign])
        event.waitKeys(keyList = ['space']) 

        showStimulus(win, [instructionspre2_message])
        event.waitKeys(keyList = ['space']) 

        #mouse.isPressedIn(shape, buttons=[0]): 
        for row in schedule_unique.itertuples():    
            squares = seq_to_stim(row.sequence_string, row.seq_color, win, 
                              config["SQUARE_SIZE"])
            showStimulus(win, squares)
            event.waitKeys()
    
    showStimulus(win, [instructions1_message, hand_sign])
    event.waitKeys(keyList = ['space']) 
    
    showStimulus(win, [instructions2_message])
    event.waitKeys(keyList = ['space']) 
    
    showStimulus(win, [instructions3_message])
    event.waitKeys(keyList = ['space']) 
    
    showStimulus(win, [instructions4_message])
    event.waitKeys(keyList = ['space']) 
    
    for row in schedule.itertuples():
        sess_num, sess_type, n_trials, seq_keys =\
        row.sess_num, row.sess_type, row.n_trials, row.seq_keys.split(" ") 
        
        sequence_string, seq_train, seq_color, seq_type =\
        row.sequence_string, row.seq_train, row.seq_color, row.seq_type         
        
        trialStimulus = []
        squareStimuli = []
        
        sequence = string_to_seq(sequence_string)
        squares = seq_to_stim(sequence_string, 
                              seq_color, 
                              win, 
                              config["SQUARE_SIZE"])
    
        # turn the text strings into stimuli
        for iTrial in range(n_trials):                
            texttrial = texts["TEXT_TRIAL"].format(iTrial+1)

            trialStimulus.append(
                    visual.TextStim(win, 
                                    height=config["TEXT_HEIGHT"],
                                    text=texttrial, pos = (-9, 9)))
    
            squareStimuli.append(squares)
            
        cum_trial = 1 
        trial = 1
        misses = 0
        exiting = False
        maxwait = len(sequence)*config["MAX_WAIT_PER_KEYPRESS"]
        while (trial <= n_trials):

            # present fixation
            showStimulus(win, [fixation])
            core.wait(config["FIXATION_TIME"])     
            
            showStimulus(win, 
                         [trialStimulus[trial-1]] + squareStimuli[trial-1])    
        
            event.clearEvents()
            trialClock.reset()    
            core.wait(maxwait, hogCPUperiod=maxwait)
            
            keypresses = event.getKeys(keyList=seq_keys + 
                                       [config["ESCAPE_KEY"]], 
                                       timeStamped = trialClock)
            
            trialincrease = 0

            if len(keypresses) <= 1:
                showStimulus(win, [late_message, error_sign])
                if config["BUZZER_ON"] == 1:
                    buzzer.play()
                core.wait(config["ERROR_TIME"])
                misses = misses + 1
                
                accuracy = 0
                score = 0
                MT = 0
                keys = ["0"]
                keytimes = [0]
                RTs = [config["MAX_WAIT"]]
                trial_type = "missed"
    
                if misses > config["MAX_MISSES"]:
                    showStimulus(win, [miss_message])
                    core.wait(config["ERROR_TIME"])
                if misses > config["MAX_TOTAL_MISSES"]:
                    exit()    

            else:
                misses = 0
                keys, keytimes, RTs = filter_keys(keypresses, 
                                                  config["MAX_CHORD_INTERVAL"], 
                                                  len(sequence))
                trial_type = "done"
                    
                accuracy, MT, score  = scorePerformance(keys, RTs, sequence, 
                                                        keytimes)

                if [config["ESCAPE_KEY"]] in keys:
                    
                    if np.sum([key == [config["ESCAPE_KEY"]] 
                        for key in keys]) > 1:
                        exiting = True
                        break
                
                if accuracy < 1:
                    showStimulus(win, [error_message, error_sign])
                    if config["BUZZER_ON"] == 1:
                        buzzer.play()
                    core.wait(config["ERROR_TIME"])        
                    score = 0
                else:

                    #print score

                    #feedback
                    maxscore[sequence_string] = np.maximum(score, 
                            maxscore[sequence_string])
        
                    max_height = \
                    maxscore[sequence_string]*config["BAR_HEIGHT"]/\
                    maxgroupscore[sequence_string]
                    
                    last_height = score*config["BAR_HEIGHT"]/\
                    maxgroupscore[sequence_string]
                    
                    last_bar = visual.Rect(win, height=last_height, 
                                              width=config["BAR_WIDTH"], 
                                              lineWidth=0, 
                                              fillColor="blue", 
                                              pos=(-3*config["BAR_WIDTH"], 
                                                   0.5*last_height - 2)
                                              ) 
                    best_bar = visual.Rect(win, height=max_height, 
                                           width=config["BAR_WIDTH"], 
                                           lineWidth=0, 
                                           fillColor="green",
                                           pos=(0, 
                                                0.5*max_height - 2)
                                           )
            
                    group_best_bar = \
                    visual.Rect(win, 
                    height=config["BAR_HEIGHT"], 
                    width=config["BAR_WIDTH"], 
                    lineWidth=0, 
                    fillColor="yellow",
                    pos=(3*config["BAR_WIDTH"],
                         0.5*config["BAR_HEIGHT"] - 2)
                    )
        
                    showStimulus(win, [last_bar, last_label, best_bar, 
                                       best_label, group_best_bar, 
                                       group_best_label])
                    core.wait(config["FEEDBACK_TIME"])

                    trialincrease = 1
                        
            # write result to data file
    
            key_from = ["0"]
            
            for keystroke in range(len(keys)):
                
                key_to = keys[keystroke]
                RT = RTs[keystroke]
                # write result to data file    
                keyswriter.writerow([
                    username,
                    sched_group,
                    sess_num,
                    sess_date,    
                    sess_time,
                    seq_type,
                    sess_type,
                    seq_train,
                    seq_to_string(sequence),
                    seq_to_string(keys),
                    accuracy, 
                    score,
                    cum_trial, 
                    trial,
                    trial_type,
                    keystroke, 
                    " ".join(key_from), 
                    " ".join(key_to), 
                    "{:.3f}".format(RT*1000),
                ])
                key_from = key_to
                #keytime0 = keytimes[keystroke]
    
    
            trialswriter.writerow([
                    username,
                    sched_group,
                    sess_num,
                    sess_date,    
                    sess_time,
                    seq_type,
                    sess_type,
                    seq_train,
                    cum_trial,
                    trial, 
                    trial_type,
                    seq_to_string(sequence),
                    seq_to_string(keys),
                    accuracy, 
                    "{:.3f}".format(RTs[0]*1000),
                    "{:.3f}".format(MT*1000),
                    "{:.3f}".format(score)
            ])
        
            trial = trial + trialincrease
            cum_trial = cum_trial + 1    
            core.wait(config["FIXATION_TIME"]) 
    
        if exiting:
            print "Session has been interrupted. Bye!"
            break
            
    # synchronize local file and database
    keysfile.close()
    trialsfile.close()
    
    mykeys = pd.read_table(keysfile.name, sep = ';')
    mytrials = pd.read_table(trialsfile.name, sep = ';')
    
    # update only what we did in the current session
    mykeys = mykeys.loc[mykeys['sess_num'] == sess_num]
    mytrials= mytrials.loc[mytrials['sess_num'] == sess_num]
    
    if not opts.demo:
        try:
            db_config_json = open("./db/db_config.json", "r")
            db_config = json.load(db_config_json)
            db_config_json.close()
    
            with SSHTunnelForwarder(
                    (db_config['REMOTEHOST'], 
                    int(db_config['REMOTEPORT'])),
                    ssh_username = db_config['SSH_USER'],
                    ssh_password = db_config['SSH_PASS'],
                    ssh_pkey = os.path.abspath(db_config['KEY']),
                    remote_bind_address = (db_config['LOCALHOST'], 
                                           int(db_config['LOCALPORT']))
                ) as server:
                    port = server.local_bind_port
                    try:
                        engine_string = 'mysql://%s:%s@%s:%d/%s'%(username, 
                                                       db_config['DB_PASS'], 
                                                       db_config['LOCALHOST'],
                                                       port,
                                                       db_config['DATABASE'])
        
                        engine = create_engine(engine_string)
                        mykeys.to_sql('keys_table', engine, 
                                      if_exists = 'append') 
                        mytrials.to_sql('trials_table', engine, 
                                        if_exists = 'append')
                        print('Synced with database.')
                    except exc.SQLAlchemyError as e:
                        print('Error:', e)
    
        except:
            print('Could not connect to database!')
         
        #finally:

    ## Closing Section
    win.close()
    core.quit()


def build_parser():
    parser = ArgumentParser()

    parser.add_argument('--schedule_file', 
                        type = str,
                        dest = 'schedule_file', 
                        help = 'Enter schedule file.',
                        required = False)

    parser.add_argument('--config_file', 
                        type = str,
                        dest = 'config_file', 
                        help = 'Enter configuration file.',
                        required = False)
    
    parser.add_argument('--restart', 
                        dest='restart', 
                        help='Remove previous data and start from session 1.',
                        action='store_true',
                        required = False)

    parser.add_argument('--demo', 
                        dest='demo', 
                        help='Do a demo, no saving.',
                        action='store_true',
                        required = False)

    return(parser)


def main():

    parser = build_parser()
    opts = parser.parse_args()
    SeqLearn(opts)
    
if __name__== "__main__":
  main()

