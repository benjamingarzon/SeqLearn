#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 08:41:28 2018

@author: benjamin.garzon@gmail.com

Training tool for discrete sequence production
"""

from __future__ import division
from psychopy import core, visual, event, prefs
import csv, time
from datetime import datetime
from lib.utils import showStimulus, scorePerformance, Configurator
from generator.generator import Generator
prefs.general['audioLib'] = ['pygame']
from psychopy import sound


config = Configurator().get()

sess_date = str(datetime.now().date())
sess_time = str(datetime.now().time())
sess_num = 1

buzzer = sound.Sound(config.BUZZER_FILE)

## Setup Section
win = visual.Window(config.SCREEN_RES, fullscr=False, monitor="testMonitor", units="cm")

intro_message = visual.TextStim(win, text=config.TEXT_INTRO) 
error_message = visual.TextStim(win, text=config.TEXT_ERROR) #pos=[0,+3], 
error_box = visual.Rect(win, height=5, width=5, lineWidth=3, lineColor="red") 
# turn the text strings into stimuli
textStimuli = []
sequence = Generator(set=config.SEQ_KEYS, size=config.SEQ_LENGTH).random()

for iTrial in range(config.TOTAL_STIMULI):
    text = config.TEXT_DO_SEQ.format(iTrial, " - ".join(sequence))
    textStimuli.append(visual.TextStim(win, text=text)) 
  
# fixation cross
fixation = visual.ShapeStim(win, 
    vertices=((0, -0.5), (0, 0.5), (0,0), (-0.5,0), (0.5, 0)),
    lineWidth=5,
    closeShape=False,
    lineColor="white"
)
 
# open data output file
keysfile = open("./data/keysfile.csv", "wb")
trialsfile = open("./data/trialsfile.csv", "wb")

# connect it with a csv writer
keyswriter = csv.writer(keysfile, delimiter=";")
trialswriter = csv.writer(trialsfile, delimiter=";")
# create output file header
keyswriter.writerow([
    "sess_num",
    "sess_date",    
    "sess_time",    
    "cumulative_trial", 
    "trial", 
    "keystroke",
    "key_from",
    "key_to", 
    "RT"
    ])
trialswriter.writerow([
    "sess_num",
    "sess_date",    
    "sess_time",    
    "cumulative_trial", 
    "trial", 
    "true_sequence", 
    "obs_sequence", 
    "accuracy", 
    "RT",
    "MT"
    ])
    
## Experiment Section

#display instructions and wait
showStimulus(win, intro_message)

#check for a keypress
event.waitKeys()

n = len(textStimuli)
cum_trial = 0
trial = 0
while (trial < n):
    # present fixation
    showStimulus(win, fixation)
    core.wait(config.FIXATION_TIME) # note how the real time will be very close to a multiple of the refresh time
     
    # present stimulus text and wait a maximum of 2 second for a response
    showStimulus(win, textStimuli[trial])    
    mytime0 = time.time()
    key_from = ["0"]
    keys = []
    RTs = []
    for keystroke in range(config.SEQ_LENGTH):
        key_to = event.waitKeys(keyList=config.ALLOWED_KEYS, )
        mytime = time.time()
        RT =  mytime - mytime0
        mytime0 = mytime
        keys.append(key_to)
        RTs.append(RT)
        if key_to=="escape":
            break
#        print(key)
#        print(RT)
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

    accuracy, MT  = scorePerformance(keys, RTs, sequence)
    if accuracy < 1:
        showStimulus(win, error_box)
        buzzer.play()
        core.wait(config.ERROR_TIME)
        showStimulus(win, error_message)
        core.wait(config.ERROR_TIME)
    else:
        #feedback and next
        showStimulus(win, visual.TextStim(win, text="{:.3f}".format(MT)))
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
    ])

    cum_trial = cum_trial + 1    
    core.wait(config.FIXATION_TIME) 
#    if key==None:
#        key=[]
#        key.append("no key")
keysfile.close()
trialsfile.close()
 
## Closing Section
win.close()
core.quit()
