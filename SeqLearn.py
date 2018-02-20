#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 08:41:28 2018

@author: benjamin.garzon@gmail.com

Training tool for discrete sequence production
"""

# give feedback on what they did
# github
# ask for username
# change cumulative trials 
# if keys come together, count as chords
# open session

from __future__ import division
from psychopy import core, visual, event
import csv, random, time
import numpy as np
from datetime import datetime

TEXT_DO_SEQ="Trial {}\nTry this sequence:\n {}"
TEXT_ERROR="You made a mistake!\nTry again."
TEXT_INTRO="Reproduce the sequence that will be shown next.\nPress a key when ready."
SEQ_KEYS=["a", "s", "d", "f"]
ALLOWED_KEYS=SEQ_KEYS + ["escape"]
TOTAL_STIMULI=20
SEQ_LENGTH=7
FIXATION_TIME=1.0
ERROR_TIME=1
ERROR_BOX_TIME=0.3

def showStimulus(stimulus):
    stimulus.draw()
    win.flip()

def computePerformance(keys, RTs, sequence):
    # returns accuracy and total movement time
    # accuracy
    correct = [keys[k][0] == s for k, s in enumerate(sequence)]
    accuracy = np.sum(correct) / len(sequence)

    # MT
    MT = np.sum(RTs[1:])
    return((accuracy, MT))

sess_date = str(datetime.now().date())
sess_time = str(datetime.now().time())
sess_num = 1

## Setup Section
win = visual.Window([800,600], fullscr=False, monitor="testMonitor", units="cm")

intro_message = visual.TextStim(win, text=TEXT_INTRO) 
error_message = visual.TextStim(win, text=TEXT_ERROR) #pos=[0,+3], 
error_box = visual.Rect(win, height=5, width=5, lineWidth=3, lineColor='red') 
# turn the text strings into stimuli
textStimuli = []
sequence = np.random.choice(SEQ_KEYS, size=SEQ_LENGTH, replace=True)

for iTrial in range(TOTAL_STIMULI):
    text = TEXT_DO_SEQ.format(iTrial, ' - '.join(sequence))
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
    "response", 
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
showStimulus(intro_message)

#check for a keypress
event.waitKeys()

n = len(textStimuli)
cum_trial = 0
trial = 0
while (trial < n):
    # present fixation
    showStimulus(fixation)
    core.wait(FIXATION_TIME) # note how the real time will be very close to a multiple of the refresh time
     
    # present stimulus text and wait a maximum of 2 second for a response
    showStimulus(textStimuli[trial])    
    mytime0 = time.time()
    keys = []
    RTs = []
    for keystroke in range(SEQ_LENGTH):
        key = event.waitKeys(keyList=ALLOWED_KEYS)
        mytime = time.time()
        RT =  mytime - mytime0
        mytime0 = mytime
        keys.append(key)
        RTs.append(RT)
        if key=="escape":
            break
        print(key)
        print(RT)
        # write result to data file    
        keyswriter.writerow([
            sess_num,
            sess_date,    
            sess_time,
            cum_trial, 
            trial, 
            keystroke, 
            key, 
            "{:.3f}".format(RT),
        ])

    accuracy, MT  = computePerformance(keys, RTs, sequence)
    if accuracy < 1:
        showStimulus(error_box)
        core.wait(ERROR_TIME)
        showStimulus(error_message)
        core.wait(ERROR_TIME)
    else:
        #feedback and next
        showStimulus(visual.TextStim(win, text="{:.3f}".format(MT)))
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
    core.wait(FIXATION_TIME) 
#    if key==None:
#        key=[]
#        key.append("no key")
keysfile.close()
trialsfile.close()
 
## Closing Section
win.close()
core.quit()
