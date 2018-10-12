# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 08:41:28 2018

@author: benjamin.garzon@gmail.com

Some functions for SeqLearn.
"""
from __future__ import division
import json, csv
import numpy as np
import pandas as pd
from psychopy import gui, event, core
from scipy.spatial.distance import pdist #, squareform
from scipy.cluster.hierarchy import linkage, cut_tree
from collections import defaultdict
import glob, os
from generator.generator import seq_to_stim, seq_to_string, string_to_seq

def get_seq_types(type_file=None):
    """ 
    Reads the file with sequence type info. 
    """

    if type_file == None:
        type_file = "./scheduling/seq_types.csv"
    try:
        type_data = pd.read_csv(type_file, sep = ";")
    except IOError: 
        print "Error: Sequence type file is missing!"

    return(type_data)


def get_config(config_file=None):
    """ 
    Reads the configuration file.
    """

    if config_file == None:
        config_file = "./config/config.json"
    try:
        config_json = open(config_file, "r")
        config = json.load(config_json)
        config_json.close()
    except IOError: 
        print "Error: Configuration file is missing!"
    
    return(config)
    

def get_texts(language):
    """ 
    Reads the file all texts.
    """

    # select language here
    if language == None:
        texts_file = "./config/texts.json"
    else:
        texts_file = "./config/texts_%s.json"%language
    try:
        texts_json = open(texts_file, "r")
        texts = json.load(texts_json)
        texts_json.close()
    except IOError: 
        print "Error: Texts file is missing!"
    
    return(texts)
    

def showStimulus(window, stimuli):
    """ 
    Shows a stimulus or a list of stimuli. 
    """
    for stimulus in stimuli:
        stimulus.draw()
    window.flip()


def scorePerformance(keys, RTs, sequence, keytimes):
    """ 
    Returns accuracy and total movement time.
    """
    # accuracy
    correct = np.array([1.0*(keys[k] == s) for k, s in enumerate(sequence) \
                        if k < len(keys)])
    accuracy = np.sum(correct) / len(sequence)

    # MT
    #MT = np.sum(RTs[1:])
    MT = keytimes[-1] - keytimes[0]
    
    score = len(sequence)/MT
    return((accuracy, MT, score))


def calcmaxgroupscore(session, n_sessions, factor, baseline, maxscore):
    """ 
    Calculates the maxscore. 
    """    
    maxgroupscore = np.max(
            (baseline*np.exp(-(session-1)/n_sessions),
            maxscore*(1 + factor*np.exp(-(session-1)/n_sessions)))
            )
    return(maxgroupscore)


def startSession(opts):
    """ 
    Starts a new session.
    """    
    config = get_config(opts.config_file)
    texts = get_texts(config["LANGUAGE"])
        
    # get username and user group
    if config["ASK_USER"] == 0:
        try:
            user_json = open("./config/user.json", "r")
            json_obj = json.load(user_json)
            username = json_obj["USERNAME"]
            sched_table = json_obj["SCHEDULE_TABLE"]
            user_json.close()
        except IOError: 
            print "Error: User file is missing!"
        
    else:
        myDlg = gui.Dlg(title="Sequence training.")
        myDlg.addField("Enter your username:")
        myDlg.addField("Enter your schedule table:")
        myDlg.show()
        if myDlg.OK:  
            username = myDlg.data[0]
            sched_table = myDlg.data[1]
        else:
            username = 'test0000'
            sched_table = ''
    
    
    if opts.demo: # load demo schedule instead
        schedule_file = "./scheduling/schedules/schedule-demo.csv"
        sched_group = 0
        memofilename = "./data/memofile-demo.csv"
        keysfilename = "./data/keysfile-demo.csv"
        trialsfilename = "./data/trialsfile-demo.csv"
        # remove previous demo files
        for fl in glob.glob("./data/*-demo.csv"):
            os.remove(fl)    
        total_trials = config["TOTAL_TRIALS_DEMO"]
        seq_length = config["SEQ_LENGTH_DEMO"]
    else:

        # get schedule

        if opts.schedule_file == None:
            try:
                schedule_table = pd.read_csv("./scheduling/tables/{}.csv".\
                format(sched_table), sep = ";")
                schedule_file = schedule_table.loc[ 
                        schedule_table["SUBJECT"] == username, "SCHEDULE_FILE"].values[0]
                sched_group = schedule_table.loc[ 
                        schedule_table["SUBJECT"] == username, "SCHEDULE_GROUP"].values[0]
            except IOError: 
                print "Error: Schedule table file is missing!"

    # override certain options if we are in fMRI mode
            if opts.run_fmri :
                config["MODE"] = "fmri"
            
            if config["MODE"] == "fmri":
                config["PRESHOW"] = 0
                config["TESTMEM"] = 0
                schedule_file = "./scheduling/schedules/{}_fmri.csv".\
            format(schedule_file)
            else:
                schedule_file = "./scheduling/schedules/{}.csv".\
            format(schedule_file)
                    
        else:
            schedule_file = opts.schedule_file
            sched_group = 0
            
        #print(schedule_file)    
        memofilename = "./data/memofile-{}.csv".format(username)
        keysfilename = "./data/keysfile-{}.csv".format(username)
        trialsfilename = "./data/trialsfile-{}.csv".format(username) 

        total_trials = config["TOTAL_TRIALS"]
        seq_length = config["SEQ_LENGTH"]
        
    try:
        schedule = pd.read_csv(schedule_file, sep = ";")
        n_sess = np.max(schedule["sess_num"])

    except IOError: 
        print "Error: Schedule file is missing!"
   
    try:
        # proceed from where it was left before
        memofile = open(memofilename, "ab")
        keysfile = open(keysfilename, "ab")
        trialsfile = open(trialsfilename, "ab")
        trialstable = pd.read_csv(trialsfilename, sep=';')

        if opts.session >= 0:
            sess_num = opts.session
        else:
            # take the next session that is in the schedule
            next_sess_num = np.max(trialstable["sess_num"]) + 1
            q = np.where(schedule["sess_num"] >= next_sess_num)
            sess_num = schedule["sess_num"][np.min(q)] if len(q) > 0 else 0
            
        maxscore = defaultdict(float)
        maxgroupscore = defaultdict(float)
        for seq in np.unique(trialstable["true_sequence"]):
            maxscore[seq] = np.max(
                    trialstable.loc[trialstable["true_sequence"] == seq, 
                                    "score"])
            maxgroupscore[seq] = calcmaxgroupscore(
                    sess_num, 
                    n_sess, 
                    config["MAXSCORE_FACTOR"], 
                    config["MAXSCORE_BASELINE"], 
                    maxscore[seq]
                    )

        # connect files with a csv writer
        memowriter = csv.writer(memofile, delimiter=";")
        keyswriter = csv.writer(keysfile, delimiter=";")
        trialswriter = csv.writer(trialsfile, delimiter=";")

    except pd.errors.EmptyDataError: 
        # create new session
        memofile = open(memofilename, "wb")
        keysfile = open(keysfilename, "wb")
        trialsfile = open(trialsfilename, "wb")
        sess_num = np.min(schedule["sess_num"])
        maxscore = defaultdict(float)
        maxgroupscore = defaultdict(lambda:config["MAXSCORE_BASELINE"], {})

        # connect files with a csv writer
        memowriter = csv.writer(memofile, delimiter=";")
        keyswriter = csv.writer(keysfile, delimiter=";")
        trialswriter = csv.writer(trialsfile, delimiter=";")

        # create output file header
        memowriter.writerow([
                "username",
                "sched_group",
                "sess_num",
                "sess_date",    
                "sess_time",    
        #        "seq_type",
        #        "sess_type",
                "seq_train",
                "trial", 
                "true_sequence", 
                "obs_sequence", 
                "accuracy", 
                "RT"

        ])

        keyswriter.writerow([
                "username",
                "sched_group",
                "sess_num",
                "sess_date",    
                "sess_time",    
                "seq_type",
                "sess_type",
                "seq_train",
                "true_sequence",
                "obs_sequence", 
                "accuracy", 
                "score",
                "cumulative_trial", 
                "trial", 
                "trial_type",
                "keystroke",
                "key_from",
                "key_to", 
                "RT",
                "clock_fixation", 
                "clock_execution",
                "clock_feedback",
                "paced"
        ])
    
        trialswriter.writerow([
                "username",
                "sched_group",
                "sess_num",
                "sess_date",    
                "sess_time",    
                "seq_type",
                "sess_type",
                "seq_train",
                "cumulative_trial", 
                "trial", 
                "trial_type",
                "true_sequence", 
                "obs_sequence", 
                "accuracy", 
                "RT",
                "MT",
                "score",
                "clock_fixation", 
                "clock_execution",
                "clock_feedback",
                "paced"
        ])

    # select schedule for this session
    schedule_unique = schedule[["sequence_string", 
                                "seq_color","seq_train"]].drop_duplicates()     
    schedule = schedule.query('sess_num == %d'%(sess_num))
    
    return(sched_group, sess_num, username, memowriter, keyswriter, 
           trialswriter, memofile, keysfile, trialsfile, maxscore, 
           maxgroupscore, config, texts, schedule, 
           schedule_unique, total_trials, seq_length)


def filter_keys(keypresses, max_chord_interval, n_chords):#, keys, keytimes):
    """ 
    Aggregate keypresses when they are close together (chords)
    """
    allkeys = [x[0] for x in keypresses]
    allkeytimes = np.array([x[1] for x in keypresses])
    
    # cluster the sequence in chords
    d = pdist(np.reshape(allkeytimes, (-1, 1))) # can be done faster 
    Z = linkage(d, 'complete')
    clusters = np.array([ x[0] for x in cut_tree(Z, n_clusters = n_chords)])
# clusters = np.array([ x[0] for x in cut_tree(Z, height= max_chord_interval)])

    keys = []
    keytimes = []

    indices = np.unique(clusters, return_index=True)[1]
    myclusters = [clusters[index] for index in sorted(indices)]
    for c in myclusters:
        keys.append(sorted([allkeys[i] for i, cluster in enumerate(clusters) 
        if cluster == c]))
        keytimes.append(np.mean(allkeytimes[np.where(clusters == c)]))
    RTs = np.append(keytimes[0], np.diff(keytimes)).tolist()
#    from matplotlib import pyplot as plt
#    from scipy.cluster.hierarchy import dendrogram
#    plt.figure(figsize=(25, 10))
#    plt.title('Hierarchical Clustering Dendrogram')
#    plt.xlabel('key')
#    plt.ylabel('distance')
#
#
#    print allkeys
#    print allkeytimes
#    print clusters
#    
#
#    dendrogram(
#            Z,
#            leaf_rotation=90.,  # rotates the x axis labels
#            leaf_font_size=8.,  # font size for the x axis labels
#            )
#    plt.show()

    return(keys, keytimes, RTs)        


def test_sequence(mystring, win, config, mycolor, texts, instructions_space,
                  instructions_select, error_message, error_sign, buzzer, 
                  memowriter, username, sched_group, sess_num, sess_date, 
                  sess_time, seq_train):
    """ 
    Test that the subject has memorized the sequence.
    """
    
    mouse = event.Mouse(visible=True, win=win)

    myseq = string_to_seq(mystring)
    full_seq = [config["SEQ_KEYS"] for i, _ in enumerate(myseq)]
    full_string = seq_to_string(full_seq)
    squares = seq_to_stim(mystring, mycolor, win, 
                                    config["SQUARE_SIZE"])

    attempts = 0
    iscorrect = False
    timer = core.Clock()

    while not iscorrect:
        squares_shown = seq_to_stim(full_string, config["BGCOLOR"], win, 
                                    config["SQUARE_SIZE"])

        
        showStimulus(win, squares_shown + [instructions_select])
        running = True
        timer.reset()
        while running:
            if any(mouse.getPressed()):
                for square in squares_shown:
                    if mouse.isPressedIn(square, buttons=[0]):
                        while mouse.isPressedIn(square, buttons=[0]):
                            pass
                        break
        
                if square.fillColor == mycolor:
                    square.fillColor = config["BGCOLOR"]
                else:
                    square.fillColor = mycolor
                showStimulus(win, squares_shown + [instructions_select])
            if event.getKeys("space"):
                running = False
        
        j = 0
        pressed_indices = [ i for i, square in enumerate(squares_shown) \
                           if square.fillColor == mycolor ]
        pressed_seq = []
        for row in full_seq:
            chord = []
            for key in row:
                if j in pressed_indices:
                    chord.append(key)
                j = j + 1    
                    
            pressed_seq.append(chord)
        mypressedstring = seq_to_string(pressed_seq)
        if mystring == mypressedstring:
            iscorrect = True
            
        else:
            attempts = attempts + 1
            showStimulus(win, [error_message, error_sign])
            if config["BUZZER_ON"] == 1:
                buzzer.play()
            core.wait(config["ERROR_TIME"])        
            showStimulus(win, squares + [instructions_space])
            event.waitKeys(keyList = ["space"])
            
        memowriter.writerow([
                    username,
                    sched_group,
                    sess_num,
                    sess_date,    
                    sess_time,
                    seq_train,
                    attempts + 1,
                    mystring,
                    mypressedstring, 
                    1.0 if iscorrect else 0.0, # just check if correct
                    timer.getTime()                    
                ])
            
    

def SetUsername():
    """ 
    Opens a dialogue to set the username and schedule table.
    """

    myDlg = gui.Dlg(title="Sequence training configuration.")
    myDlg.addField("Enter username:")
    myDlg.addField("Enter schedule table:", "kip1_schedule_table")
    
    myDlg.show()
    
    if myDlg.OK:  
        username = myDlg.data[0]
        sched_table = int(myDlg.data[1])
    else:
        username = ''
        sched_table = ''
        print("Cancelled.")
        
    print("Username: {}".format(username))
    print("Schedule table: {}".format(sched_table))
    
    json_obj = {"USERNAME": username, 
                "SCHEDULE_TABLE": sched_table}
    
    with open("./config/user.json", "w") as outfile:
        json.dump(json_obj, outfile)
        

def update_table(engine, table_name, mytable):
    """ 
    Insert in the database only new rows.
    """
    cols = list(set(mytable.columns) - set(["MT", "accuracy", "RT", "score"]))
    
    if not engine.dialect.has_table(engine, table_name):
        mytable.to_sql(table_name, engine, 
                      if_exists = 'fail')
    else:        
        myoldtable = pd.read_sql_table(table_name, engine)[cols]
        mytable = mytable[~mytable[cols].isin(myoldtable).all(1)]
        mytable.to_sql(table_name, engine, if_exists = 'append') 

def wait_clock_old(t):
    """ 
    Just waits.
    """

    core.wait(t, hogCPUperiod = t)
    

def wait_clock(myclock, t):
    """ 
    Just waits.
    """
    mytime = myclock.getTime()
    while (myclock.getTime() < mytime + t):
        pass
    return(mytime)