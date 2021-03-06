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
from scipy.spatial.distance import pdist, squareform
from scipy.cluster.hierarchy import linkage, cut_tree
from collections import defaultdict
import glob, os
from generator.generator import seq_to_stim, seq_to_string, string_to_seq
from sklearn.metrics import silhouette_score
from scipy.stats import sem

def get_seq_types(type_file=None):
    """ 
    Reads the file with sequence type info. 
    """

    if type_file == None:
        type_file = "./scheduling/seq_types.csv"
    try:
        type_data = pd.read_csv(type_file, sep = ";")
    except IOError: 
        print("Error: Sequence type file is missing!")

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
        print("Error: Configuration file is missing!")
    
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
        print("Error: Texts file is missing!")
    
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
    MT = keytimes[-1] - keytimes[0]
    
    score = len(sequence)/MT
    return((accuracy, MT, score))


def calcmaxgroupscore(session, n_sessions, factor, baseline, maxscore):
    """ 
    Calculates the maxscore. 
    """    
    maxgroupscore = np.max(
            (baseline*np.exp(-session/n_sessions),
            maxscore*(1 + factor*np.exp(-2*session/n_sessions)))
            )
    return(maxgroupscore)


def startSession(opts):
    """ 
    Starts a new session.
    """    
    config = get_config(opts.config_file)
    texts = get_texts(config["LANGUAGE"])
        
    # get username and user group

    try:
        user_json = open("./config/user.json", "r")
        json_obj = json.load(user_json)
        if config["ASK_USER"] == 0:
            username = json_obj["USERNAME"]
            sched_table = json_obj["SCHEDULE_TABLE"]
        else:
            myDlg = gui.Dlg(title="Sequence training.")
            myDlg.addField("Enter your username:")
            myDlg.addField("Enter your schedule table: ", json_obj["SCHEDULE_TABLE"])
            myDlg.show()
            if myDlg.OK:  
                username = myDlg.data[0]
                sched_table = myDlg.data[1]
            else:
                username = 'test0000'
                sched_table = ''

        user_json.close()
    except IOError: 
        print("Error: User file is missing!")


    # override certain options if we are in fMRI mode
    if opts.run_fmri :
        config["MODE"] = "fmri"
    
    if config["MODE"] == "fmri":
        config["PRESHOW"] = 0
        config["TESTMEM"] = 0
        config["BREAKS"] = 0
        config["BUTTONBOX_KEYS"] = config["BUTTONBOX_KEYS_FMRI"]
        config["START_TIME"] = config["START_TIME_FMRI"]
        # larger letters in fMRI mode
        config["HEADING_TEXT_HEIGHT"] = 1.4*config["HEADING_TEXT_HEIGHT"]
        config["TEXT_HEIGHT"] = 1.4*config["TEXT_HEIGHT"]
    
    if opts.demo: # load demo schedule instead
        schedule_file = "./scheduling/schedules/schedule-demo.csv"
        sched_group = 0
        memofilename = "./data/memofile-demo.csv"
        keysfilename = "./data/keysfile-demo.csv"
        trialsfilename = "./data/trialsfile-demo.csv"
        # remove previous demo files
        for fl in glob.glob("./data/*-demo.csv"):
            os.remove(fl) 
    else:

        # get schedule
        if opts.schedule_file == None:
            try:
                schedule_table = pd.read_csv("./scheduling/tables/{}.csv".\
                format(sched_table), sep = ";")
                schedule_file = schedule_table.loc[ 
                        schedule_table["SUBJECT"] == username, 
                        "SCHEDULE_FILE"].values[0]
                sched_group = schedule_table.loc[ 
                        schedule_table["SUBJECT"] == username, 
                        "SCHEDULE_GROUP"].values[0]
            except IOError: 
                print("Error: Schedule table file is missing!")
            
            if config["MODE"] == "fmri":
                schedule_file = "./scheduling/schedules/{}_fmri.csv".\
            format(schedule_file)
            else:
                schedule_file = "./scheduling/schedules/{}.csv".\
            format(schedule_file)
                    
        else:
            schedule_file = opts.schedule_file
            sched_group = 0
            
        if config["MODE"] == "fmri": 
            memofilename = "./data/memofile-{}_fmri.csv".format(username)
            keysfilename = "./data/keysfile-{}_fmri.csv".format(username)
            trialsfilename = "./data/trialsfile-{}_fmri.csv".format(username) 
        else: 
            memofilename = "./data/memofile-{}.csv".format(username)
            keysfilename = "./data/keysfile-{}.csv".format(username)
            trialsfilename = "./data/trialsfile-{}.csv".format(username) 
        
    try:
        schedule = pd.read_csv(schedule_file, sep = ";")
        n_sess = np.max(schedule["sess_num"])
    except IOError: 
        print("Error: Schedule file is missing!")

    maxscore = defaultdict(float)
    maxgroupscore = defaultdict(lambda:config["MAXSCORE_BASELINE"], {})
   
    try:
        # proceed from where it was left before
        memofile = open(memofilename, "ab")
        keysfile = open(keysfilename, "ab")
        trialsfile = open(trialsfilename, "ab")
        trialstable = pd.read_csv(trialsfilename, sep=';')
        # get last session from session file    
        try:
            last_json = open("./config/last_session.json", "r")
            json_obj = json.load(last_json)
            if username in json_obj.keys():
                last_sess_num = json_obj[username]
            else: 
                last_sess_num = np.max(trialstable["sess_num"])
            last_json.close()
        except IOError: 
            print("Session file not found.")
            last_sess_num = np.max(trialstable["sess_num"]) 

        next_sess_num = last_sess_num + 1
        q = np.where(schedule["sess_num"] >= next_sess_num)
        # sess_num is zero if there are no more sessions left
        sess_num = schedule["sess_num"][np.min(q)] if q[0].size else 0

        if config["MODE"] == "fmri": 
            run = np.max(trialstable.loc[trialstable["sess_num"] == \
                                         last_sess_num, "run"]) + 1

            if run > config["N_RUNS"]: # we did the last run, move to next
                run = 1
            else:    
                sess_num = last_sess_num
                
        else:
            run = 1

        # override previous options
        if opts.run:
            run = opts.run
        if opts.session >= 0:
            sess_num = opts.session

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

        if np.isnan(sess_num):
            sess_num = 0

        if np.isnan(run):
            run = 1

        # check everything alright before moving on
        if config["ASK_USER"] == 1:
            myDlg = gui.Dlg(title="Confirm information.")
            myDlg.addText("Username: %s"%(username))
            myDlg.addText("Session: %d"%(sess_num))
            if config["MODE"] == "fmri":
                myDlg.addText("Run: %d"%(run)) 
            myDlg.show()
            if not myDlg.OK:
                exit()   

        # connect files with a csv writer
        memowriter = csv.writer(memofile, delimiter=";")
        keyswriter = csv.writer(keysfile, delimiter=";")
        trialswriter = csv.writer(trialsfile, delimiter=";")

    except pd.errors.EmptyDataError: 
        
        if opts.run:
            run = opts.run
        else:
            run = 1

        # create new session
        memofile = open(memofilename, "wb")
        keysfile = open(keysfilename, "wb")
        trialsfile = open(trialsfilename, "wb")
        sess_num = np.min(schedule["sess_num"])

        if config["ASK_USER"] == 1:
            myDlg = gui.Dlg(title="Confirm information.")
            myDlg.addText("Username: %s"%(username))
            myDlg.addText("Session: %d"%(sess_num))
            if config["MODE"] == "fmri":
                myDlg.addText("Run: %d"%(run)) 
            myDlg.show()
            if not myDlg.OK:
                exit()   
            
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
                "seq_train",
                "trial", 
                "true_sequence", 
                "obs_sequence", 
                "accuracy", 
                "RT",
                "global_clock",
                "run",
                "block"
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
                "clock_finished",
                "global_clock",
                "paced",
                "run",
                "block",
                "stretch"
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
                "clock_finished",
                "global_clock",
                "paced",
                "run",
                "block",
                "stretch"
        ])

    # select schedule for this session
    schedule_unique = schedule[["sequence_string", 
                                "seq_color","seq_train"]].drop_duplicates()
    schedule_unique = schedule_unique.query("seq_train !='unseen'")
     
    schedule = schedule.query('sess_num == %d and run == %d'%(sess_num, run))
    if config["MODE"] == "fmri":
        print("Username %s, session %d, run %d"%(username, sess_num, run))
        
    return(sched_group, sess_num, username, memowriter, keyswriter, 
           trialswriter, memofile, keysfile, trialsfile, maxscore, 
           maxgroupscore, config, texts, schedule, 
           schedule_unique, run)


def filter_keys(keypresses, n_chords, key_code):
    """ 
    Aggregate keypresses when they are close together (chords)
    """
    allkeys = [key_code[x[0]] for x in keypresses]
    allkeytimes = np.array([x[1] for x in keypresses])
    
    # cluster the sequence in chords
    d = pdist(np.reshape(allkeytimes, (-1, 1))) # can be done faster 
    Z = linkage(d, 'complete')
    
    #clusters = np.array([ x[0] for x in cut_tree(Z, n_clusters = n_chords)])
    n_keys = len(keypresses)
    ##### different clusters
    solutions = []
    for n_clusters in range(2, np.min((n_chords + 2, n_keys))):
        clusters = np.array([ x[0] for x in cut_tree(Z, n_clusters = n_clusters)])
        ss = silhouette_score(squareform(d), clusters, metric='precomputed')
        solutions.append((n_clusters, clusters, ss))
    # get best one
    if len(solutions) > 0:
        maxsolution = max(solutions, key=lambda x:x[2])
        clusters = maxsolution[1]
    else:
        clusters = n_keys*[0]
    #####
    
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

    return(keys, keytimes, RTs, allkeys)        


def test_sequence(mystring, win, config, mycolor, texts, instructions_space,
                  instructions_select, error_message, error_sign, buzzer, 
                  memowriter, username, sched_group, sess_num, sess_date, 
                  sess_time, seq_train, globalClock, run):
    """ 
    Test that the subject has memorized the sequence.
    """
    
    mouse = event.Mouse(visible=True, win=win)

    myseq = string_to_seq(mystring)
    full_seq = [config["SEQ_KEYS"] for i, _ in enumerate(myseq)]
    full_string = seq_to_string(full_seq)
    squares = seq_to_stim(mystring, mycolor, win, 
                                    config["SQUARE_SIZE"])

    attempts = 1
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
            showStimulus(win, [error_message, error_sign])
            if config["BUZZER_ON"] == 1:
                buzzer.play()
            core.wait(config["FEEDBACK_TIME"])        
            showStimulus(win, squares + [instructions_space])
            event.waitKeys(keyList = ["space"])
            
        memowriter.writerow([
                    username,
                    sched_group,
                    sess_num,
                    sess_date,    
                    sess_time,
                    seq_train,
                    attempts,
                    mystring,
                    mypressedstring, 
                    1.0 if iscorrect else 0.0, # just check if correct
                    timer.getTime(),
                    globalClock.getTime(), 
                    run                    
                ])
            
        attempts = attempts + 1

    

def SetUsername():
    """ 
    Opens a dialogue to set the username and schedule table.
    """
    myDlg = gui.Dlg(title="Sequence training configuration.")
    myDlg.addField("Enter username:")
    myDlg.addField("Enter schedule table:", "lue1_schedule_table")
    
    myDlg.show()
    
    if myDlg.OK:  
        username = myDlg.data[0]
        sched_table = myDlg.data[1]
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
        

def update_table(engine, table_name, mytable, username):
    """ 
    Insert in the database only new rows.
    """
    cols = list(set(mytable.columns) - set(["MT", "accuracy", "RT", 
                "score", "index", "global_clock", "clock_fixation", 
                "clock_execution", "clock_feedback"]))
    
    if not engine.dialect.has_table(engine, table_name):
        mytable.to_sql(table_name, engine, 
                      if_exists = 'fail')
    else:        
        query = "select {} from {} where username = '{}'".format(
                ", ".join(cols),
                table_name, 
                username)
#        myoldtable = pd.read_sql_table(table_name, engine)[cols]  
        myoldtable = pd.read_sql_query(query, engine)[cols]
        mynewtable = mytable[~mytable[cols].isin(myoldtable).all(1)]
        mynewtable.to_sql(table_name, engine, if_exists = 'append', 
                          index = False) 


def wait_clock_old(t):
    """ 
    Just waits.
    """

    core.wait(t, hogCPUperiod = t)
    

def wait_clock(myclock, t, rel = True):
    """ 
    Just waits.
    """
    if rel:  # wait for a time t 
        mytime = myclock.getTime()
        while (myclock.getTime() < mytime + t):
            pass
    else: # wait until clock is t      
        while (myclock.getTime() < t):
            pass
        mytime = myclock.getTime()
    return(mytime)
    
def generate_ITIs(itimean, itirange, ititype):
    Nitis = 10000

    if ititype == 'exp':
        # truncated exponential
        ITIs = np.random.exponential(itimean, Nitis)
  
        maxiti = itimean*np.exp(itirange)
        miniti = itimean/np.exp(itirange)
        ITIs[ITIs > maxiti] = maxiti
        ITIs[ITIs < miniti] = miniti
        print("ITI: (min = %.1f, mean = %.1f, max = %.1f, diff = %.1f, sem = %.2f)"%(miniti, 
                                                      np.mean(ITIs),
                                                      maxiti, 
                                                      maxiti-miniti,
                                                      sem(ITIs)))
    else:
        ITIs = list(np.random.uniform(itimean + itirange, 
                       itimean + itirange, 
                       size=Nitis))
    return(ITIs)
    
def end_session(username, sess_num):
    try:
        with open('./config/last_session.json') as f:
            json_obj = json.load(f)

        json_obj[username] = sess_num
    
        with open('./config/last_session.json', 'w') as f:
            json.dump(json_obj, f)    
                
    except IOError: 
        print("Session file not found; a new one will be created.")
        json_obj = {username: sess_num}
        with open('./config/last_session.json', 'w') as f:
            json.dump(json_obj, f)    
