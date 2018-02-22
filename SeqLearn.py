#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 08:41:28 2018

@author: benjamin.garzon@gmail.com

Training tool for discrete sequence production.
"""

from __future__ import division
from psychopy import core, visual, event, prefs
from datetime import datetime
from lib.utils import showStimulus, scorePerformance, get_config, \
startSession, filter_keys
from generator.generator import Generator
prefs.general['audioLib'] = ['pygame']
from psychopy import sound
import numpy as np

# start session
config = get_config()

sess_date = str(datetime.now().date())
sess_time = str(datetime.now().time())
sess_num, username, keyswriter, trialswriter, keysfile, trialsfile, maxscore, \
maxgroupscore = startSession()

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
instructions_message = visual.TextStim(win, 
                                       text=config["TEXT_INSTRUCT"].format(
                                               config["MAX_WAIT"], 
                                               config["TOTAL_TRIALS"]), 
                                       height = config["TEXT_HEIGHT"], 
                                       alignHoriz='center') 
last_label = visual.TextStim(win, 
                                text=config["LAST_LABEL"], 
                                height = config["TEXT_HEIGHT"], 
                                pos = (-3*config["BAR_WIDTH"], 
                                       -0.5*config["BAR_HEIGHT"]),
                                alignHoriz='center') 
best_label = visual.TextStim(win, 
                             text=config["BEST_LABEL"], 
                             height = config["TEXT_HEIGHT"],
                             pos = (0, 
                                    -0.5*config["BAR_HEIGHT"]),
                             alignHoriz='center') 

group_best_label = visual.TextStim(win, 
                             text=config["GROUP_BEST_LABEL"], 
                             height = config["TEXT_HEIGHT"],
                             pos = (3*config["BAR_WIDTH"], 
                                    -0.5*config["BAR_HEIGHT"]),
                             alignHoriz='center') 
error_message = visual.TextStim(win, 
                                text=config["TEXT_ERROR"], 
                                alignHoriz="center")  
error_sign = visual.ImageStim(win, 
                              image=config["WRONG_FILE"]) 
late_message = visual.TextStim(win, 
                                text=config["TEXT_LATE"], 
                                alignHoriz="center")

textStimuli = []
sequence, sequence_string = Generator(set=config["SEQ_KEYS"], 
                     size=config["SEQ_LENGTH"],
                     maxchordsize=config["MAX_CHORD_SIZE"]).random()

# turn the text strings into stimuli
for iTrial in range(config["TOTAL_TRIALS"]):
    text = config["TEXT_DO_SEQ"].format(iTrial+1, sequence_string)
    textStimuli.append(visual.TextStim(win, text=text, 
                                       height=config["TEXT_HEIGHT"])) 

# fixation cross
fixation = visual.ShapeStim(win, 
    vertices=((0, -0.5), (0, 0.5), (0,0), (-0.5,0), (0.5, 0)),
    lineWidth=5,
    closeShape=False,
    lineColor="white"
)
     

## Experiment Section

#display instructions and wait
#showStimulus(win, intro_message)
#core.wait(config["INTRO_TIME"])
#showStimulus(win, instructions_message)

#check for a keypress
event.waitKeys()

n = len(textStimuli)
cum_trial = 1 
trial = 1
while (trial <= n):

#    keys = []
#    keytimes = []

    # present fixation
    showStimulus(win, fixation)
    core.wait(config["FIXATION_TIME"])     
    
    # present stimulus text and wait a maximum of 2 second for a response
    event.clearEvents()
    showStimulus(win, textStimuli[trial-1])    
#    
#    core.wait(5)
     
#    keys = event.getKeys(#maxWait=config["MAX_WAIT"], 
#                                keyList=config["ALLOWED_KEYS"], 
#                                timeStamped = timer)
    
#    print(keys)
#    print(keys)
#    timer = core.Clock()
#    for keystroke in range(config["SEQ_LENGTH"]):

    keytime0 = core.getTime() 
#    while True:
#        core.wait(5.0)
    core.wait(config["MAX_WAIT"])
    keypresses = event.getKeys(#maxWait=config["MAX_WAIT"], 
                           keyList=config["ALLOWED_KEYS"], 
                           timeStamped = True)

#    print(keypresses)
    if len(keypresses) == 0:
        showStimulus(win, error_sign)
        #buzzer.play()
        core.wait(config["ERROR_TIME"])
        showStimulus(win, late_message)
        core.wait(config["ERROR_TIME"])

        continue
    else:
#        print core.getTime()
        keys, keytimes, RTs = filter_keys(keypresses, config["MAX_CHORD_INTERVAL"], 
                                keytime0)#, keys, keytimes)
#        print core.getTime()

    print keys
    print keytimes
    print RTs
    
#    if len(keys) >= config["SEQ_LENGTH"]:
#        break
#        if key=="escape":
#            break

       
    # print out the data
    key_from = ["0"]
        
    for keystroke in range(len(keys)):
        
        key_to = keys[keystroke]
        RT = RTs[keystroke]
        # write result to data file    
        keyswriter.writerow([
            sess_num,
            sess_date,    
            sess_time,
            cum_trial, 
            trial, 
            keystroke, 
            key_from, 
            key_to, 
            "{:.3f}".format(RT),
        ])
        key_from = key_to
        keytime0 = keytimes[keystroke]

    accuracy, MT, score  = scorePerformance(keys, RTs, sequence)
    
    if accuracy < 1:
        showStimulus(win, error_sign)
        #buzzer.play()
        core.wait(config["ERROR_TIME"])
        showStimulus(win, error_message)
        core.wait(config["ERROR_TIME"])
    else:
        #feedback
        maxscore = np.maximum(score, maxscore)
        showStimulus(win, visual.TextStim(win, text="{:.3f}".format(MT)))
        max_height = maxscore*config["BAR_HEIGHT"]/maxgroupscore
        last_height = score*config["BAR_HEIGHT"]/maxgroupscore
        
        last_bar = visual.Rect(win, height=last_height, 
                                  width=config["BAR_WIDTH"], 
                                  lineWidth=0, 
                                  fillColor="blue", 
                                  pos=(-3*config["BAR_WIDTH"], 
                                       0.5*last_height)
                                  ) 
        best_bar = visual.Rect(win, height=max_height, 
                               width=config["BAR_WIDTH"], 
                               lineWidth=0, 
                               fillColor="green",
                               pos=(0, 
                                    0.5*max_height)
                               )

        group_best_bar = visual.Rect(win, height=config["BAR_HEIGHT"], 
                               width=config["BAR_WIDTH"], 
                               lineWidth=0, 
                               fillColor="yellow",
                               pos=(3*config["BAR_WIDTH"], 
                                    0.5*config["BAR_HEIGHT"])
                               )

        last_bar.draw()
        last_label.draw()
        
        best_bar.draw()
        best_label.draw()
        
        group_best_bar.draw()
        group_best_label.draw()
        
        win.flip()
        core.wait(config["FEEDBACK_TIME"])

#        best_group_bar = visual.Rect(win, height=5, width=config.BAR_WIDTH, 
#                                  lineWidth=3, lineColor="blue")         
        config["ALLOWED_KEYS"]
        trial = trial + 1

    # write result to data file
    trialswriter.writerow([
            sess_num,
            sess_date,    
            sess_time,
            cum_trial,
            trial, 
            sequence,
            keys,
            accuracy, 
            "{:.3f}".format(RTs[0]),
            "{:.3f}".format(MT),
            "{:.3f}".format(score)
    ])

    cum_trial = cum_trial + 1    
    core.wait(config["FIXATION_TIME"]) 
#    if key==None:
#        key=[]
#        key.append("no key")
keysfile.close()
trialsfile.close()
 
## Closing Section
win.close()
core.quit()
