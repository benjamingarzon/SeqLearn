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

# start session

sess_date = str(datetime.now().date())
sess_time = str(datetime.now().time())
sess_num, username, keyswriter, trialswriter, keysfile, trialsfile, maxscore, \
maxgroupscore, config, schedule = startSession()

win = visual.Window(config["SCREEN_RES"], fullscr=False, monitor="testMonitor", 
                    units="cm")

# define stimuli
buzzer = sound.Sound(config["BUZZER_FILE"])
intro_message = visual.TextStim(win, 
                                text=config["TEXT_INTRO"].format(username, 
                                           sess_num), 
                                           height = \
                                           config["HEADING_TEXT_HEIGHT"], 
                                           alignHoriz='center') 
instructions1_message = visual.TextStim(win, 
                                       text=config["TEXT_INSTRUCT1"].format(
                                               config["MAX_WAIT"], 
                                               config["TOTAL_TRIALS"]), 
                                       height = config["TEXT_HEIGHT"], 
                                       alignHoriz='center') 

instructions2_message = visual.TextStim(win, 
                                       text=config["TEXT_INSTRUCT2"], 
                                       height = config["TEXT_HEIGHT"], 
                                       alignHoriz='center') 


last_label = visual.TextStim(win, 
                                text=config["LAST_LABEL"], 
                                height = config["TEXT_HEIGHT"], 
                                pos = (-3*config["BAR_WIDTH"], 
                                       -0.5*config["BAR_HEIGHT"] - 2),
                                alignHoriz='center') 
best_label = visual.TextStim(win, 
                             text=config["BEST_LABEL"], 
                             height = config["TEXT_HEIGHT"],
                             pos = (0, 
                                    -0.5*config["BAR_HEIGHT"] - 2),
                             alignHoriz='center') 

group_best_label = visual.TextStim(win, 
                             text=config["GROUP_BEST_LABEL"], 
                             height = config["TEXT_HEIGHT"],
                             pos = (3*config["BAR_WIDTH"], 
                                    -0.5*config["BAR_HEIGHT"] - 2),
                             alignHoriz='center') 
error_message = visual.TextStim(win, 
                                text=config["TEXT_ERROR"], 
                                alignHoriz="center", 
                                pos = (0, -3))  
error_sign = visual.ImageStim(win, 
                              image=config["WRONG_FILE"],
                              pos = (0, 2))

hand_sign = visual.ImageStim(win, 
                              image=config["HAND_FILE"])
 
late_message = visual.TextStim(win, 
                                text=config["TEXT_LATE"], 
                                alignHoriz="center", 
                                pos = (0, -3))  
miss_message = visual.TextStim(win, 
                                text=config["TEXT_MISS"], 
                                alignHoriz="center")

new_message = visual.TextStim(win, 
                                text=config["TEXT_NEW"], 
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

         
for row in schedule.itertuples():
    sess_num, sess_type, n_trials, seq_keys, seq_type, \
    sequence_string, seq_train, seq_color = row.sess_num, row.sess_type, \
    row.n_trials, row.seq_keys.split(" "), row.seq_type, row.sequence_string, \
    row.seq_train, row.seq_color 
    
    trialStimulus = []
 #   textStimuli = []
    squareStimuli = []
    
    sequence = string_to_seq(sequence_string)
    # turn the text strings into stimuli
    for iTrial in range(n_trials):                
        texttrial = config["TEXT_TRIAL"].format(iTrial+1)
        squares = seq_to_stim(sequence_string, seq_color, win, 
                              config["SQUARE_SIZE"])
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

        core.wait(config["MAX_WAIT"], hogCPUperiod=config["MAX_WAIT"])
        
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

keysfile.close()
trialsfile.close()

# synchronize local file and database

 
## Closing Section
win.close()
core.quit()

