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
from db.python_mysql_dbconfig import read_db_config
from sqlalchemy import create_engine, exc

# start session

sess_date = str(datetime.now().date())
sess_time = str(datetime.now().time())
sess_num, username, keyswriter, trialswriter, keysfile, trialsfile, maxscore, \
maxgroupscore, config, texts, schedule, schedule_unique = startSession()

win = visual.Window(config["SCREEN_RES"], fullscr=False, monitor="testMonitor", 
                    units="cm")

# define stimuli
buzzer = sound.Sound(config["BUZZER_FILE"])
intro_message = visual.TextStim(win, 
                                text=texts["TEXT_INTRO"].format(username, 
                                           sess_num), 
                                           height = \
                                           config["HEADING_TEXT_HEIGHT"], 
                                           alignHoriz='center') 
instructions1_message = visual.TextStim(win, 
                                       text=texts["TEXT_INSTRUCT1"].format(
                                               config["MAX_WAIT"], 
                                               config["TOTAL_TRIALS"]), 
                                       height = config["TEXT_HEIGHT"], 
                                       alignHoriz='center') 

instructions2_message = visual.TextStim(win, 
                                       text=texts["TEXT_INSTRUCT2"], 
                                       height = config["TEXT_HEIGHT"], 
                                       alignHoriz='center') 

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
                              image=config["HAND_FILE"])
 
late_message = visual.TextStim(win, 
                                text=texts["TEXT_LATE"], 
                                alignHoriz="center", 
                                pos = (0, -3))  
miss_message = visual.TextStim(win, 
                                text=texts["TEXT_MISS"], 
                                alignHoriz="center")

new_message = visual.TextStim(win, 
                                text=texts["TEXT_NEW"], 
                                alignHoriz="center", pos = (0, 5), 
                                color="yellow")  

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
showStimulus(win, [instructions1_message])
event.waitKeys() 
showStimulus(win, [instructions2_message])
event.waitKeys() 

if config["PRESHOW"]==1:
   
    for row in schedule_unique.itertuples():    
        squares = seq_to_stim(row.sequence_string, row.seq_color, win, 
                          config["SQUARE_SIZE"])
        showStimulus(win, squares)
        event.waitKeys()
    
for row in schedule.itertuples():
    sess_num, sess_type, n_trials, seq_keys, seq_type, \
    sequence_string, seq_train, seq_color = row.sess_num, row.sess_type, \
    row.n_trials, row.seq_keys.split(" "), row.seq_type, row.sequence_string, \
    row.seq_train, row.seq_color 
    
    trialStimulus = []
 #   textStimuli = []
    squareStimuli = []
    
    sequence = string_to_seq(sequence_string)
    squares = seq_to_stim(sequence_string, seq_color, win, config["SQUARE_SIZE"])

    # turn the text strings into stimuli
    for iTrial in range(n_trials):                
        texttrial = texts["TEXT_TRIAL"].format(iTrial+1)
#        text = config["TEXT_DO_SEQ"].format(sequence_string.replace("-", "\n"))
        trialStimulus.append(visual.TextStim(win, 
                                             height=config["TEXT_HEIGHT"],
                                             text=texttrial, pos = (-9, 9)))

#        textStimuli.append(visual.TextStim(win, text=text, 
#                                           height=config["TEXT_HEIGHT"]*2,
#                                           color = "red")) 
        squareStimuli.append(squares)
        
    cum_trial = 1 
    trial = 1
    misses = 0
#    maxwait = config["MAX_WAIT"]
    maxwait = len(sequence)*config["MAX_WAIT_PER_KEYPRESS"]
    while (trial <= n_trials):
        # present fixation
        showStimulus(win, [fixation])
        core.wait(config["FIXATION_TIME"])     
        
#        textStimuli[trial-1].draw()
#        if cum_trial == 1:
#            showStimulus(win, [new_message, textStimuli[trial-1]])    
#        else:
        showStimulus(win, [trialStimulus[trial-1]] + squareStimuli[trial-1])    

#        core.wait(config["PRESENTATION_TIME"])     

#        hand_sign.draw()
        event.clearEvents()
        trialClock.reset()
#        win.flip()

        core.wait(maxwait, hogCPUperiod=maxwait)
        
        keypresses = event.getKeys(keyList=seq_keys, 
                                   timeStamped = trialClock)
        print keypresses
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
#            continue

        else:
            misses = 0
            keys, keytimes, RTs = filter_keys(keypresses, 
                                              config["MAX_CHORD_INTERVAL"], 
                                              len(sequence))
            trial_type = "done"
#        print keys
#        print keytimes
#        print RTs
        
    #    if len(keys) >= config["SEQ_LENGTH"]:
    #        break
    #        if key=="escape":
    #            break
    

                
            accuracy, MT, score  = scorePerformance(keys, RTs, sequence)
            if accuracy < 1:
                showStimulus(win, [error_message, error_sign])
                if config["BUZZER_ON"] == 1:
                    buzzer.play()
                core.wait(config["ERROR_TIME"])        
                score = 0
            else:
                print score
                #feedback
                maxscore[sequence_string] = np.maximum(score, 
                        maxscore[sequence_string])
    
                max_height = maxscore[sequence_string]*config["BAR_HEIGHT"]/\
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
        
                group_best_bar = visual.Rect(win, height=config["BAR_HEIGHT"], 
                                       width=config["BAR_WIDTH"], 
                                       lineWidth=0, 
                                       fillColor="yellow",
                                       pos=(3*config["BAR_WIDTH"], 
                                            0.5*config["BAR_HEIGHT"] - 2)
                                       )
    
                showStimulus(win, [last_bar, last_label, best_bar, best_label, 
                                   group_best_bar, group_best_label])
                core.wait(config["FEEDBACK_TIME"])
            
                trial = trial + 1
    
        # write result to data file

        key_from = ["0"]

        for keystroke in range(len(keys)):
            
            key_to = keys[keystroke]
            RT = RTs[keystroke]
            # write result to data file    
            keyswriter.writerow([
                username,
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
            keytime0 = keytimes[keystroke]


        trialswriter.writerow([
                username,
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
    
        cum_trial = cum_trial + 1    
        core.wait(config["FIXATION_TIME"]) 

# synchronize local file and database
keysfile.close()
trialsfile.close()

mykeys = pd.read_table(keysfile.name, sep = ';')
mytrials = pd.read_table(trialsfile.name, sep = ';')

# update only what we did in the current session
mykeys = mykeys.loc[mykeys['sess_num'] == sess_num]
mytrials= mytrials.loc[mytrials['sess_num'] == sess_num]

try:
    db_config = read_db_config()
    engine_string = 'mysql://%s:%s@%s/%s'%(db_config['user'], 
                                           db_config['password'], 
                                           db_config['host'], 
                                           db_config['database'])
    engine = create_engine(engine_string)
    mykeys.to_sql('keys_table', engine, if_exists = 'append') 
    mytrials.to_sql('trials_table', engine, if_exists = 'append')
    print('Synced with database.')
except exc.SQLAlchemyError as e:
    print('Error:', e)
 
#finally:

 
## Closing Section
win.close()
core.quit()

