# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 08:41:28 2018

@author: benjamin.garzon@gmail.com

Some functions for SeqLearn.
"""
import os, json, csv
import numpy as np
import pandas as pd
from psychopy import gui

def get_config(config_file=None):
    if config_file == None:
        config_file = "./config/config.json"
    try:
        config_json = open(config_file, "r")
        config = json.load(config_json)
        config_json.close()
    except IOError: 
        print "Error: Config_file is missing!"

    config["ALLOWED_KEYS"] = config["SEQ_KEYS"] + ["escape"]  
    
    return(config)

def showStimulus(window, stimulus):
    stimulus.draw()
    window.flip()

def scorePerformance(keys, RTs, sequence):
    """ 
    Returns accuracy and total movement time.
    """
    # accuracy
    correct = [keys[k][0] == s for k, s in enumerate(sequence)]
    accuracy = np.sum(correct) / len(sequence)

    # MT
    MT = np.sum(RTs[1:])
    score = 1/MT
    return((accuracy, MT, score))

def startSession():
    """ 
    Starts a new session.
    """
    # get username
    myDlg = gui.Dlg(title="Sequence training.")
    myDlg.addField('Enter your username:')
    ok_data = myDlg.show()
    if myDlg.OK:  
        username = myDlg.data[0]
    else:
        username = 'test0000'
        
    keysfilename = "./data/keysfile-{}.csv".format(username)
    trialsfilename = "./data/trialsfile-{}.csv".format(username) 
    
    try: #if os.path.exists(keysfilename) and os.path.exists(trialsfilename) :
        # proceed from where it was left before
        keysfile = open(keysfilename, "a")
        trialsfile = open(trialsfilename, "a")
        trialstable = pd.read_csv(trialsfilename, sep=';')
        sess_num = np.max(trialstable["sess_num"]) + 1
        maxscore = np.max(trialstable["score"])
        maxgroupscore = maxscore*1.2
        
        # connect files with a csv writer
        keyswriter = csv.writer(keysfile, delimiter=";")
        trialswriter = csv.writer(trialsfile, delimiter=";")

    except: # else
        # create new session
        keysfile = open(keysfilename, "wb")
        trialsfile = open(trialsfilename, "wb")
        sess_num = 1
        maxscore = 0
        maxgroupscore = 2
        
        # connect files with a csv writer
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
                "MT",
                "score"
        ])
        
    return(sess_num, username, keyswriter, trialswriter, keysfile, trialsfile,
           maxscore, maxgroupscore)


def filter_keys(keys):
    """ 
    Aggregate keypresses when they are close together (chords)
    """

    stimulus.draw()
    win.flip()