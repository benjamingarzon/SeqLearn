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
from lib.utils import showStimulus, scorePerformance, startSession, \
filter_keys, test_sequence, update_table
from generator.generator import string_to_seq, seq_to_string, seq_to_stim
prefs.general["audioLib"] = ["pygame"]
from psychopy import sound
import numpy as np
import pandas as pd
import os, glob, json
from argparse import ArgumentParser
from sqlalchemy import create_engine, exc
from sshtunnel import SSHTunnelForwarder
from stimuli.stimuli import define_stimuli

def SeqLearn(opts):

############################ 
## Start session
############################ 
    
    if opts.restart: # remove previous files
        for fl in glob.glob("./data/*.csv"):
            os.remove(fl)    
    
    sess_date = str(datetime.now().date())
    sess_time = str(datetime.now().time())
    sched_group, sess_num, username, memowriter, keyswriter, trialswriter, \
    memofile, keysfile, trialsfile, maxscore, maxgroupscore, config, texts, \
    schedule, schedule_unique, total_trials, seq_length = \
    startSession(opts)

############################ 
## Define window and stimuli
############################ 
    
    win = visual.Window(config["SCREEN_RES"],
                        fullscr=False, 
                        monitor="testMonitor", 
                        units="cm")    
    
    
    stimuli = define_stimuli(win, username, config, texts, sess_num, 
                             seq_length, total_trials)
        
    buzzer = stimuli["buzzer"]
    beat = stimuli["beat"]
    intro_message = stimuli["intro_message"]
    instructions_space = stimuli["instructions_space"]
    instructions_select = stimuli["instructions_select"]
    instructionspre1_message = stimuli["instructionspre1_message"]
    instructionspre2_message = stimuli["instructionspre2_message"]
    instructions1_message = stimuli["instructions1_message"]    
    instructions2_message = stimuli["instructions2_message"]
    instructions3_message = stimuli["instructions3_message"]
    instructions4_message = stimuli["instructions4_message"]
    instructions4_space = stimuli["instructions4_space"]
    instructionspaced1_message = stimuli["instructionspaced1_message"]    
    last_label = stimuli["last_label"]
    best_label = stimuli["best_label"]
    group_best_label = stimuli["group_best_label"]
    bottomline = stimuli["bottomline"]
    error_message = stimuli["error_message"]
    error_sign = stimuli["error_sign"]
    hand_sign = stimuli["hand_sign"]
    bars_sign = stimuli["bars_sign"]
    late_message = stimuli["late_message"]
    miss_message = stimuli["miss_message"]
    fixation = stimuli["fixation"]
    bye_message = stimuli["bye_message"]
    trialClock = core.Clock()

############################ 
## Experiment Section
############################ 
    
############################ 
## Memorization
############################ 

    showStimulus(win, [intro_message])
    core.wait(config["INTRO_TIME"])

    if config["PRESHOW"]==1:
        
        showStimulus(win, [instructionspre1_message, hand_sign])
        event.waitKeys(keyList = ["space"]) 

        showStimulus(win, [instructionspre2_message])
        event.waitKeys(keyList = ["space"]) 

        for row in schedule_unique.itertuples():    
            squares = seq_to_stim(row.sequence_string, row.seq_color, win, 
                                  config["SQUARE_SIZE"])
            
            showStimulus(win, squares + [instructions_space])
            event.waitKeys(keyList = ["space"])        
  
            if config["TEST_MEM"] == 1:
                test_sequence(row.sequence_string, win, config, row.seq_color, 
                texts, instructions_space, instructions_select, error_message, 
                error_sign, buzzer, memowriter, username, sched_group, 
                sess_num, sess_date, sess_time, row.seq_train)
                
    memofile.close()

############################ 
## Free execution
############################ 
    
    showStimulus(win, [instructions1_message, hand_sign])
    event.waitKeys(keyList = ["space"]) 
        
    for row in schedule.itertuples():
        sess_num, sess_type, n_trials, seq_keys =\
        row.sess_num, row.sess_type, row.n_trials, row.seq_keys.split(" ") 
        
        sequence_string, seq_train, seq_color, seq_type, paced, instruct =\
        row.sequence_string, row.seq_train, row.seq_color, row.seq_type, \
        row.paced, row.instruct         

        # add instructions if required
        if instruct == 1:
            
            if paced == 0:
            
                showStimulus(win, [instructions2_message])
                event.waitKeys(keyList = ["space"]) 
            
                showStimulus(win, [instructions3_message, bars_sign])
                event.waitKeys(keyList = ["space"]) 
                
                showStimulus(win, [instructions4_message, instructions4_space])
                event.waitKeys(keyList = ["space"]) 

            else:            
                showStimulus(win, [instructionspaced1_message, 
                                   instructions4_space])
                event.waitKeys(keyList = ["space"]) 
                    
        trialStimulus = []
        squareStimuli = []
        
        sequence = string_to_seq(sequence_string)
        squares = seq_to_stim(sequence_string, 
                              seq_color, 
                              win, 
                              config["SQUARE_SIZE"])
    
        # turn the text strings into stimuli
        for iTrial in range(n_trials):                
            texttrial = texts["TEXT_TRIAL"].format(iTrial, n_trials)

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

            current_stimuli = [trialStimulus[trial-1]] + squareStimuli[trial-1]
            
            # present fixation
            showStimulus(win, [fixation])
            core.wait(config["FIXATION_TIME"])     
    
            # present sequence and read keypresses          
            showStimulus(win, current_stimuli)    
            
            if paced == 1:

                nbeats = len(sequence) + config["EXTRA_BEATS"]
                char_list = range(config["EXTRA_BEATS"]) + range(len(sequence))
                label_list = config["EXTRA_BEATS"]*["WAIT: "] + \
                len(sequence)*["PRESS: "]
                number_list = [ visual.TextStim(win,     
                                text=x + str(y + 1), 
                                alignHoriz="center", 
                                pos = (0, 5)) 
            for x, y in zip(label_list, char_list) ] 

                keypresses = []
                trialClock.reset()    
                
                for nbeat in range(nbeats):
                    event.clearEvents()
                    showStimulus(win, squares + [number_list[nbeat]])
                    beat.play()
                    core.wait(config["BEAT_INTERVAL"], 
                              hogCPUperiod=config["BEAT_INTERVAL"])
                    partial_keypresses = event.getKeys(
                            keyList = seq_keys + 
                            [config["ESCAPE_KEY"]], 
                            timeStamped = trialClock)
                    if nbeat >= config["EXTRA_BEATS"]:   
                        keypresses.extend(partial_keypresses)

            else:
            
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
                RTs = [maxwait]
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
                    # wrong
                    showStimulus(win, [error_message, error_sign])
                    if config["BUZZER_ON"] == 1:
                        buzzer.play()
                    core.wait(config["ERROR_TIME"])        
                    score = 0
                else:

                    trialincrease = 1
                    
                    if paced == 0:

                        # feedback
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
                                                       0.5*last_height - 3))
                        
                        best_bar = visual.Rect(win, height=max_height, 
                                               width=config["BAR_WIDTH"], 
                                               lineWidth=0, 
                                               fillColor="green",
                                               pos=(0, 
                                                    0.5*max_height - 3))
                
                        group_best_bar = \
                        visual.Rect(win, 
                                    height=config["BAR_HEIGHT"], 
                                    width=config["BAR_WIDTH"], 
                                    lineWidth=0, 
                                    fillColor="yellow",
                                    pos=(3*config["BAR_WIDTH"],
                                    0.5*config["BAR_HEIGHT"] - 3))
                        
                        showStimulus(win, [last_bar, last_label, best_bar, 
                                           best_label, group_best_bar, 
                                           group_best_label, bottomline])
                        
                        core.wait(config["FEEDBACK_TIME"])
                        
            # write results to files
            key_from = ["0"]
            
            for keystroke in range(len(keys)):
                
                key_to = keys[keystroke]
                RT = RTs[keystroke]

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

############################ 
## Sync local files with database
############################ 

    showStimulus(win, [bye_message]) 
        
    keysfile.close()
    trialsfile.close()
    
    mymemo = pd.read_table(memofile.name, sep = ";")
    mykeys = pd.read_table(keysfile.name, sep = ";")
    mytrials = pd.read_table(trialsfile.name, sep = ";")
    
    # update only what we did in the current session
#    mymemo = mymemo.loc[mymemo["sess_num"] == sess_num]
#    mykeys = mykeys.loc[mykeys["sess_num"] == sess_num]
#    mytrials= mytrials.loc[mytrials["sess_num"] == sess_num]
    
    if not opts.demo:
        try:
            db_config_json = open("./db/db_config.json", "r")
            db_config = json.load(db_config_json)
            db_config_json.close()
            #print db_config
    
            with SSHTunnelForwarder(
                    (db_config["REMOTEHOST"], 
                    int(db_config["REMOTEPORT"])),
                    ssh_username = db_config["SSH_USER"],
                    ssh_password = db_config["SSH_PASS"],
                    ssh_pkey = os.path.abspath(db_config["KEY"]),
                    remote_bind_address = (db_config["LOCALHOST"], 
                                           int(db_config["LOCALPORT"]))
                ) as server:
                    port = server.local_bind_port
                    try:
                        engine_string = "mysql://%s:%s@%s:%d/%s"%(username, 
                                                       db_config["DB_PASS"], 
                                                       db_config["LOCALHOST"],
                                                       port,
                                                       db_config["DATABASE"])
        
                        engine = create_engine(engine_string)
                        if config["TEST_MEM"] == 1 and config["PRESHOW"] == 1:
                            update_table(engine, "memo_table", mymemo) 
                        update_table(engine, "keys_table", mykeys) 
                        update_table(engine, "trials_table", mytrials)
                        
                        print("Synced with database.")
                    except exc.SQLAlchemyError as e:
                        print("Error:", e)
    
        except:
            print("Could not connect to database!")
            
        #finally:

############################ 
## Quit
############################ 
    core.wait(config["FIXATION_TIME"])
    win.close()
    core.quit()


def build_parser():

    parser = ArgumentParser()

    parser.add_argument("--schedule_file", 
                        type = str,
                        dest = "schedule_file", 
                        help = "Enter schedule file.",
                        required = False)

    parser.add_argument("--config_file", 
                        type = str,
                        dest = "config_file", 
                        help = "Enter configuration file.",
                        required = False)
    
    parser.add_argument("--restart", 
                        dest="restart", 
                        help="Remove previous data and start from session 1.",
                        action="store_true",
                        required = False)

    parser.add_argument("--demo", 
                        dest="demo", 
                        help="Do a demo, no saving.",
                        action="store_true",
                        required = False)

    return(parser)


def main():

    parser = build_parser()
    opts = parser.parse_args()
    SeqLearn(opts)
    
if __name__== "__main__":
  main()

