# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 08:41:28 2018

@author: benjamin.garzon@gmail.com

Some functions for SeqLearn.
"""
import json, csv
import numpy as np
import pandas as pd
from psychopy import gui
from scipy.spatial.distance import pdist #, squareform
from scipy.cluster.hierarchy import linkage, cut_tree
from collections import defaultdict

def get_seq_types(type_file=None):
    if type_file == None:
        type_file = "./scheduling/seq_types.csv"
    try:
        type_data = pd.read_csv(type_file, sep = ";")
    except IOError: 
        print "Error: Sequence type file is missing!"

    return(type_data)


def get_config(config_file=None):
    if config_file == None:
        config_file = "./config/config.json"
    try:
        config_json = open(config_file, "r")
        config = json.load(config_json)
        config_json.close()
    except IOError: 
        print "Error: Configuration file is missing!"

    config["ALLOWED_KEYS"] = config["SEQ_KEYS"] + ["escape"]  
    
    return(config)

def get_texts(language):
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
    
    score = 1/MT
    return((accuracy, MT, score))

def startSession(config_file=None, schedule_file=None):

    """ 
    Starts a new session.
    """    
    config = get_config()
    texts = get_texts(config["LANGUAGE"])
        
    # get username and user group
    if config["ASK_USER"] == 0:
        try:
            user_json = open("./config/user.json", "r")
            json_obj = json.load(user_json)
            username = json_obj["USERNAME"]
            sched_group = json_obj["SCHEDULE_GROUP"]
            user_json.close()
        except IOError: 
            print "Error: User file is missing!"
        
    else:
        myDlg = gui.Dlg(title="Sequence training.")
        myDlg.addField("Enter your username:")
        myDlg.show()
        if myDlg.OK:  
            username = myDlg.data[0]
        else:
            username = 'test0000'
        sched_group = 0
        
    # get schedule
    if schedule_file == None:
        schedule_file = "./scheduling/schedule{}.csv".format(sched_group)
    try:
        schedule = pd.read_csv(schedule_file, sep = ";")
        print schedule_file
    except IOError: 
        print "Error: Schedule file is missing!"

        
    keysfilename = "./data/keysfile-{}.csv".format(username)
    trialsfilename = "./data/trialsfile-{}.csv".format(username) 
    
    try:
        # proceed from where it was left before
        keysfile = open(keysfilename, "a")
        trialsfile = open(trialsfilename, "a")
        trialstable = pd.read_csv(trialsfilename, sep=';')
        sess_num = np.max(trialstable["sess_num"]) + 1
        maxscore = defaultdict(float)
        maxgroupscore = defaultdict(float)
        for seq in np.unique(trialstable["true_sequence"]):
            maxscore[seq] = np.max(
                    trialstable.loc[trialstable["true_sequence"] == seq, 
                                    "score"])
            maxgroupscore[seq] = maxscore[seq]*1.2
        print maxscore
        print maxgroupscore
        # connect files with a csv writer
        keyswriter = csv.writer(keysfile, delimiter=";")
        trialswriter = csv.writer(trialsfile, delimiter=";")

    except pd.errors.EmptyDataError: 
        # create new session
        keysfile = open(keysfilename, "wb")
        trialsfile = open(trialsfilename, "wb")
        sess_num = 1
        maxscore = defaultdict(float)
        maxgroupscore = defaultdict(lambda:2.0, {})

        # connect files with a csv writer
        keyswriter = csv.writer(keysfile, delimiter=";")
        trialswriter = csv.writer(trialsfile, delimiter=";")

        # create output file header
        keyswriter.writerow([
                "username",
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
                "RT"
        ])
        trialswriter.writerow([
                "username",
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
                "score"
        ])

    # select schedule for this session
    schedule_unique = schedule[["sequence_string", 
                                "seq_color","seq_train"]].drop_duplicates()     
    schedule = schedule.query('sess_num == %d'%(sess_num))
    
    return(sess_num, username, keyswriter, trialswriter, keysfile, trialsfile,
           maxscore, maxgroupscore, config, texts, schedule, schedule_unique)


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
#    clusters = np.array([ x[0] for x in cut_tree(Z, height= max_chord_interval)])

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


def SetUsername():
    
    myDlg = gui.Dlg(title="Sequence training configuration.")
    myDlg.addField("Enter username:")
    myDlg.addField("Enter schedule group:", 0)
    
    myDlg.show()
    
    if myDlg.OK:  
        username = myDlg.data[0]
        sched_group = int(myDlg.data[1])
    else:
        username = ''
        sched_group = 0
        print("Cancelled.")
        
    print("Username: {}".format(username))
    print("Schedule group: {}".format(sched_group))
    
    json_obj = {"USERNAME": username, 
                "SCHEDULE_GROUP": sched_group}
    
    with open("./config/user.json", "w") as outfile:
        json.dump(json_obj, outfile)
        
