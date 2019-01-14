#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 08:41:28 2018

@author: benjamin.garzon@gmail.com

Training tool for discrete sequence production.
"""

from __future__ import division
from psychopy import visual, core, event, prefs, logging
from datetime import datetime
from lib.utils import showStimulus, scorePerformance, startSession, \
filter_keys, test_sequence, update_table, wait_clock
from generator.generator import string_to_seq, seq_to_string, seq_to_stim
prefs.general["audioLib"] = ["pygame"]
import numpy as np
import pandas as pd
import os, glob, json
from argparse import ArgumentParser
from sqlalchemy import create_engine, exc
import sshtunnel
from stimuli.stimuli import define_stimuli
from shutil import copyfile


sshtunnel.SSH_TIMEOUT = 20.0
sshtunnel.TUNNEL_TIMEOUT = 20.0

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
    schedule, schedule_unique, run = \
    startSession(opts)

############################ 
## Define window and stimuli
############################ 
    
    win = visual.Window(
            config["SCREEN_RES"],
            winType = "pyglet", 
            fullscr = True if config["FULL_SCREEN"] == 1 else False, 
            monitor = "testMonitor", 
            units = "cm")    
    
    stimuli = define_stimuli(win, username, config, texts, sess_num)
        
    buzzer = stimuli["buzzer"]
    tick = stimuli["tick"]
    tock = stimuli["tock"]
    intro_message = stimuli["intro_message"]
    instructions_space = stimuli["instructions_space"]
    instructions_select = stimuli["instructions_select"]
    instructionspre1_message = stimuli["instructionspre1_message"]
    instructionspre2_message = stimuli["instructionspre2_message"]
    instructions1_message = stimuli["instructions1_message"]   
    instructions3_message = stimuli["instructions3_message"]
    instructions4_message = stimuli["instructions4_message"]
    instructions4_space = stimuli["instructions4_space"]
    instructionspaced1_message = stimuli["instructionspaced1_message"]    
    instructionsfmri1_message = stimuli["instructionsfmri1_message"]
    instructionsfmripaced1_message = stimuli["instructionsfmripaced1_message"]    
    instructionsbreak_message = stimuli["instructionsbreak_message"]    
    instructionsstretch_message = stimuli["instructionsstretch_message"]
    instructionsbreakseq_message = stimuli["instructionsbreaksequence_message"]
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
    fixation_alt = stimuli["fixation_alt"]
    bye_message = stimuli["bye_message"]
    ok_message = stimuli["ok_message"]
    ok_sign = stimuli["ok_sign"]

############################ 
## Clocks and logging
############################ 
    
    trialClock = core.Clock()
    globalClock = core.Clock()
    globalClock.reset()
        
    logging.LogFile(f=config["LOG_FILE"], filemode='w')
#    logging.setDefaultClock(globalClock)
    np.random.seed(config["RND_SEED"])
    
    
    if config["MODE"] == "fmri":
        itimean = config["ITIMEAN_FMRI"]
        itirange = config["ITIRANGE_FMRI"]
    else:
        itimean = config["ITIMEAN"]
        itirange = config["ITIRANGE"]
    
    ITI = list(np.random.uniform(itimean + itirange, 
                           itimean + itirange, 
                           size=100000))
    
############################ 
## Experiment Section
############################ 
    
############################ 
## Memorization
############################ 
    if sess_num > 0 :
        showStimulus(win, [intro_message])
        wait_clock(globalClock, config["INTRO_TIME"])

        if not config["MODE"] == "fmri": # home mode                       
            showStimulus(win, [instructionspre1_message, hand_sign])
            event.waitKeys(keyList = ["space"]) 
        
        if config["PRESHOW"] == 1:           
    
            showStimulus(win, [instructionspre2_message])
            event.waitKeys(keyList = ["space"]) 
    
            for row in schedule_unique.itertuples():    
                squares = seq_to_stim(row.sequence_string, row.seq_color, win, 
                                      config["SQUARE_SIZE"])
                
                showStimulus(win, squares + [instructions_space])
                #event.waitKeys(keyList = ["space"])        
                mykey = event.waitKeys(keyList = ["space", 
                                                  config["ESCAPE_KEY"]])
    
                if  any(config["ESCAPE_KEY"] in s for s in mykey):
                    break  
                if config["TEST_MEM"] == 1:
                    test_sequence(row.sequence_string, win, config, 
                    row.seq_color, texts, instructions_space, 
                    instructions_select, error_message, error_sign, buzzer, 
                    memowriter, username, sched_group, sess_num, sess_date, 
                    sess_time, row.seq_train, globalClock, run)
                

############################ 
## Free execution
############################ 
    
        if not config["MODE"] == "fmri": # home mode                       
            showStimulus(win, [instructions1_message, hand_sign])
            event.waitKeys(keyList = ["space"]) 

    memofile.close()
    mystart = 0
    stretch_trial = 1
    
    for rowindex, row in  enumerate(schedule.itertuples()):
        sess_num, sess_type, n_trials, seq_keys =\
        row.sess_num, row.sess_type, row.n_trials, row.seq_keys.split(" ") 
        
        sequence_string, seq_train, seq_color, seq_type, paced, instruct, \
        block = row.sequence_string, row.seq_train, row.seq_color, \
        row.seq_type, row.paced, row.instruct, row.block

        sequence = string_to_seq(sequence_string)

        if config["USE_BUTTONBOX"]: 
            # when using the button box translate if necessary
            key_code = {key: value for (key, value) in zip(
                    config["BUTTONBOX_KEYS"], seq_keys
                    )}
            seq_keys = config["BUTTONBOX_KEYS"]
        else:        
            key_code = {key: value for (key, value) in zip(seq_keys, 
                             seq_keys)}

        mystart = mystart + 1
            
        # add instructions if required
        if instruct == 1:

            if paced == 0:
            
                if not config["MODE"] == "fmri": # home mode  
                    
                    instructions2_message = visual.TextStim(win, 
                                    text = texts["TEXT_INSTRUCT2"].format(
                                    len(sequence)*\
                                    config["MAX_WAIT_PER_KEYPRESS"], 
                                    n_trials), 
                                    height = config["TEXT_HEIGHT"], 
                                    alignHoriz="center") 
                    
                    showStimulus(win, [instructions2_message])
                    event.waitKeys(keyList = ["space"]) 
                
                    showStimulus(win, [instructions3_message, bars_sign])
                    event.waitKeys(keyList = ["space"]) 
                
                    showStimulus(win, [instructions4_message, \
                                       instructions4_space])
                    event.waitKeys(keyList = ["space"]) 
#                else: # does not happen
#                    showStimulus(win, [instructionsfmri1_message])
#                    event.waitKeys(keyList = [config["FMRI_TRIGGER"]])  

            else:            
                if not config["MODE"] == "fmri": # home mode                    
                    showStimulus(win, [instructionspaced1_message, 
                                       instructions4_space])
                    event.waitKeys(keyList = ["space"]) 
                else: # fmri presentation
                    showStimulus(win, [instructionsfmripaced1_message])
                    event.waitKeys(keyList = [config["FMRI_TRIGGER"]])  
            
        else: # no instructions
            # ask for a break
            if config["BREAKS"] == 1: 
                showStimulus(win, [instructionsbreakseq_message])
                event.waitKeys(keyList = ["space"])  
        if mystart == 1: # only first time we pass
            start_time = globalClock.getTime()
            target_time = start_time + config["START_TIME"]
        else:
            if not config["MODE"] == "fmri": # home mode                    
                target_time = globalClock.getTime() + config["BUFFER_TIME"]
             
        trialStimulus = []
        squareStimuli = []
        
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
        if config["MODE"] == "fmri":
            print("Sequence: %s (%s)"%(sequence_string, seq_train))

        maxwait = len(sequence)*config["MAX_WAIT_PER_KEYPRESS"]
        nbeats = len(sequence) + config["EXTRA_BEATS"]
        char_list = range(config["EXTRA_BEATS"]) + range(len(sequence))
        label_list = config["EXTRA_BEATS"]*["WAIT: "] + \
        len(sequence)*["PRESS: "]
        color_list = (config["EXTRA_BEATS"]-1)*["red"] + \
        ["yellow"] + len(sequence)*["green"]
        number_list = [ visual.TextStim(win,     
                        text = x + str(y + 1),
                        color = z,
                        alignHoriz="center", 
                        pos = (0, 7)) for x, y, z in zip(label_list, 
                              char_list, 
                              color_list) ] 

        execution_duration = config["BEAT_INTERVAL"]*nbeats + \
        config["BUFFER_TIME"] 
        while (trial <= n_trials):
            
            # prepare stimuli
            if config["MODE"] == "fmri":
                current_stimuli = squareStimuli[trial-1]

                # stretch time
                if stretch_trial == config["STRETCH_TRIALS"]:
                    clock_stretch = wait_clock(globalClock, target_time, 
                                            rel = False)
                    showStimulus(win, [instructionsstretch_message])
                    target_time = clock_stretch + config["STRETCH_TIME"]
                    print("Stretching...")
                    stretch_trial = 1
                else:
                    stretch_trial = stretch_trial + 1

            else:
                current_stimuli = [trialStimulus[trial-1]] + \
                squareStimuli[trial-1]
 
            # present fixation
            clock_fixation = wait_clock(globalClock, target_time, 
                                            rel = False)
         
            if config["MODE"] == "fmri":                 
                if config["TRIGGER_FIXATION"] == 1:                 
                    event.waitKeys(keyList = [config["FMRI_TRIGGER"]])  
                clock_fixation = globalClock.getTime()
                print("Block %d, trial %d of %d"%(block, trial, n_trials))
                
            target_time = clock_fixation + config["FIXATION_TIME"]


            if trial == 1:
                showStimulus(win, [fixation_alt])
            else:
                showStimulus(win, [fixation])
            
                       
            # present sequence and read keypresses             
            clock_execution = wait_clock(globalClock, target_time, rel = False)
            showStimulus(win, current_stimuli)    
            
            if paced == 1:
                target_time = clock_execution + execution_duration                  
             
                keypresses = []
                trialClock.reset()    
    
                for nbeat in range(nbeats):                    
                    event.clearEvents()
                    showStimulus(win, current_stimuli + [number_list[nbeat]])
                    if nbeat == config["EXTRA_BEATS"]-1:
                        tick.play()
                    else:
                        tock.play()                                
                    
                    core.wait(config["BEAT_INTERVAL"], 
                              hogCPUperiod=config["BEAT_INTERVAL"])
                    
                    partial_keypresses = event.getKeys(
                            keyList = seq_keys + 
                            [config["ESCAPE_KEY"]], 
                            timeStamped = trialClock)

                    if nbeat >= config["EXTRA_BEATS"]:   
                        keypresses.extend(partial_keypresses)

            else: # unpaced
                target_time = target_time + maxwait + config["BUFFER_TIME"]                  

                event.clearEvents()
                trialClock.reset()                

                core.wait(maxwait, hogCPUperiod=maxwait)
                
                keypresses = event.getKeys(keyList=seq_keys + 
                                           [config["ESCAPE_KEY"]], 
                                           timeStamped = trialClock)
                
            trialincrease = 1 if config["MODE"] == "fmri" else 0

            if len(keypresses) <= 1:
                clock_feedback = wait_clock(globalClock, 
                                            target_time, 
                                            rel = False) if paced == 1 \
                                            else globalClock.getTime()

                if config["MODE"] != "fmri":    
                    showStimulus(win, [late_message, error_sign])
                    if config["BUZZER_ON"] == 1:
                        buzzer.play()
                
                misses = misses + 1
                
                accuracy = 0
                score = 0
                MT = 0
                keys = ["0"]
                keytimes = [0]
                RTs = [maxwait]
                trial_type = "missed"

                # OBS!: may break the target time                    
                if misses > config["MAX_MISSES"]:
                    showStimulus(win, [miss_message])
                    wait_clock(globalClock, config["FEEDBACK_TIME"])
                    target_time = clock_feedback + config["FEEDBACK_TIME"]

                if misses > config["MAX_TOTAL_MISSES"]:
                    exit()    

            else:
                misses = 0
                keys, keytimes, RTs = filter_keys(keypresses, 
                                                  len(sequence),
                                                  key_code)
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
                    clock_feedback = wait_clock(globalClock, 
                                                target_time, 
                                                rel = False) if paced == 1 \
                                                else globalClock.getTime()

                    if config["MODE"] != "fmri":
                        showStimulus(win, [error_message, error_sign])

                        if config["BUZZER_ON"] == 1:
                            buzzer.play()
                
                    score = 0
                    
                else:

                    trialincrease = 1
                    
                    if paced == 1:
                        clock_feedback = wait_clock(globalClock, target_time, 
                                                    rel = False)
                        if config["MODE"] != "fmri":
                            showStimulus(win, [ok_sign, ok_message])
                        
                    else:    
                        # feedback
                        pastmaxscore = maxscore[sequence_string] \
                        if sequence_string in maxscore.keys() else score                    
                                
                        max_height = \
                        pastmaxscore*config["BAR_HEIGHT"]/\
                        maxgroupscore[sequence_string]

                        maxscore[sequence_string] = np.maximum(score, 
                                pastmaxscore)
                       
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
                        
                        clock_feedback = globalClock.getTime()                                                                    
                        showStimulus(win, [last_bar, last_label, best_bar, 
                                           best_label, group_best_bar, 
                                           group_best_label, bottomline])
            
            if config["MODE"] != "fmri":        
                wait_clock(globalClock, config["FEEDBACK_TIME"])                                                       
                if config["BREAKS"] == 1 and \
                cum_trial%config["BREAK_TRIALS"] == 1: 
                    showStimulus(win, [instructionsbreak_message])
                    event.waitKeys(keyList = ["space"]) 
                    target_time = globalClock.getTime() + config["BUFFER_TIME"]                  
    
                else: 
                    target_time = clock_feedback + config["FEEDBACK_TIME"] + \
                config["BUFFER_TIME"]
            else:

                #decide do stretching when necessary
                print("Accuracy: %f"%(accuracy))
                                
            clock_finished = wait_clock(globalClock, 
                        target_time, 
                        rel = False)
            
#            showStimulus(win, [fixation_alt])
            target_time = clock_finished + ITI.pop()
 
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
                    "{:.3f}".format(clock_fixation - start_time), 
                    "{:.3f}".format(clock_execution - start_time),
                    "{:.3f}".format(clock_feedback - start_time),
                    "{:.3f}".format(clock_finished - start_time),
                    "{:.3f}".format(globalClock.getTime()), 
                    paced,
                    run,
                    block
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
                    "{:.3f}".format(score),
                    "{:.3f}".format(clock_fixation - start_time), 
                    "{:.3f}".format(clock_execution - start_time),
                    "{:.3f}".format(clock_feedback - start_time),
                    "{:.3f}".format(clock_finished - start_time),
                    "{:.3f}".format(globalClock.getTime()), 
                    paced,
                    run, 
                    block
            ])

            trial = trial + trialincrease
            cum_trial = cum_trial + 1    
            #wait_clock(globalClock, config["FIXATION_TIME"]) 

            
        if exiting:
            print("Session has been interrupted. Bye!")
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
    
    # make a local backup
    now = datetime.now()
    timestring = now.strftime('%Y%m%d_%H%M')

    copyfile(memofile.name, now.strftime(
            './data/backup/memofile-%s-%s.csv'%(username, timestring)))
    copyfile(keysfile.name, now.strftime(
            './data/backup/keysfile-%s-%s.csv'%(username, timestring)))
    copyfile(trialsfile.name, now.strftime(
            './data/backup/trialsfile-%s-%s.csv'%(username, timestring)))
    
    if not opts.demo and not opts.no_upload:
        try:
            db_config_json = open("./db/db_config.json", "r")
            db_config = json.load(db_config_json)
            db_config_json.close()
            #print(db_config)
    
            with sshtunnel.SSHTunnelForwarder(
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
                            update_table(engine, "memo_table", mymemo, 
                                         username) 
                        update_table(engine, "keys_table", mykeys, 
                                     username) 
                        update_table(engine, "trials_table", mytrials, 
                                     username)
                        engine.dispose()
                        print("Synced with database.")
                    except exc.SQLAlchemyError as e:
                        print("Error:", e)
    
        except:
            print("Could not connect to database!")
            
        #finally:

############################ 
## Quit
############################ 
    wait_clock(globalClock, config["FIXATION_TIME"])

    win.close()
    core.quit()


def build_parser():

    parser = ArgumentParser()

    parser.add_argument("--schedule_file", 
                        type = str,
                        dest = "schedule_file", 
                        help = "Enter schedule file (with extension).",
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

    parser.add_argument("--session", 
                        type = int,
                        dest = "session", 
                        help = "Run only this session. Incompatible with " + 
                        "--restart",
                        required = False)

    parser.add_argument("--run", 
                        type = int,
                        dest = "run", 
                        help = "Run only this run. Incompatible with " + 
                        "--restart",
                        required = False)


    parser.add_argument("--fmri", 
                        dest = "run_fmri", 
                        help = "Run in fMRI mode.",
                        action="store_true",
                        required = False)

    parser.add_argument("--no_upload", 
                        dest = "no_upload", 
                        help = "Do not upload the data to the database.",
                        action="store_true",
                        required = False)

    return(parser)

def main():

    parser = build_parser()
    opts = parser.parse_args()
    SeqLearn(opts)
    
if __name__== "__main__":
  main()

