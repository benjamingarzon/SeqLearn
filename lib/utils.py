# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 08:41:28 2018

@author: benjamin.garzon@gmail.com

Some functions for SeqLearn.
"""
import os, json
import numpy as np

class Configurator:
    """ Create a config."""

    def __init__(self, config_file=None):
        
        if config_file == None:
            config_file = "./config/config.json"
        try:
            config_json = open(config_file, "r")
            config_data = json.load(config_json)
            config_json.close()
        except IOError: 
            print "Error: Config_file is missing!"

        self.TEXT_DO_SEQ = config_data["TEXT_DO_SEQ"]
        self.TEXT_ERROR = config_data["TEXT_ERROR"]
        self.TEXT_INTRO = config_data["TEXT_INTRO"]
        self.SEQ_KEYS = config_data["SEQ_KEYS"]
        self.TOTAL_STIMULI = config_data["TOTAL_STIMULI"]
        self.SEQ_LENGTH = config_data["SEQ_LENGTH"]
        self.FIXATION_TIME = config_data["FIXATION_TIME"]
        self.ERROR_TIME = config_data["ERROR_TIME"]
        self.ERROR_BOX_TIME = config_data["ERROR_BOX_TIME"]
        self.ALLOWED_KEYS = self.SEQ_KEYS + ["escape"]  
        self.BUZZER_FILE = config_data["BUZZER_FILE"]
        self.SCREEN_RES = config_data["SCREEN_RES"]
        

    def get(self):           
        return(self) 

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
    return((accuracy, MT))

def startSession(username):
    """ 
    Starts a new session.
    """
    keysfilename = "./data/keysfile-{}.csv".format(username)
    trialsfilename = "./data/trialsfile-{}.csv".format(username) 
    
    if os.path.exists(keysfilename) and os.path.exists(trialsfilename) :
        keysfile = open(keysfilename, "a")
        trialsfile = open(trialsfilename, "a")
    else:
        keysfile = open(keysfilename, "wb")
        trialsfile = open(trialsfilename, "wb")
        
    return(sess_num, keysfile, trialsfile)


def filter_keys(keys):
    """ 
    Aggregate keypresses when they are close together (chords)
    """

    stimulus.draw()
    win.flip()


