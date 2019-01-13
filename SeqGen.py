#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 08:51:16 2018

@author: benjamin.garzon@gmail.com

A tool for generating discrete sequences.
"""
# add a sequence number / code

from lib.utils import get_config, get_seq_types
from generator.generator import Generator
import pandas as pd
import numpy as np
import random
from itertools import permutations, combinations
from argparse import ArgumentParser

def shuffle_order(x):
    y = list(x)
    random.shuffle(y) 
    return(y)

def generate_with_predefined_sequences(opts, sched_group):
    """
    Generate schedule using sequences already defined. 
    """
    # get config
    config = get_config()
    type_data = get_seq_types(opts.type_file)
     
    seq_file = \
    opts.seq_file + "_{}.json".format(sched_group) \
    if opts.seq_file else "./scheduling/sequences.json"
    color_list = config["COLOR_LIST"]
    
    # create sequences
    row_list = []
    sess_num = 1


    for index, row in type_data.iterrows():        

        seq_type, seq_length, max_chord_size, seq_keys, n_free_trials, \
        n_paced_trials, n_free_trials_testing, n_paced_trials_testing, \
        blocks, n_seqs, n_seqs_fmri, \
        n_sess, testing_sessions, n_runs = row
        testing_session_list = \
        [int(x) for x in str(testing_sessions).split(",")]

    
        seq_keys = seq_keys.split(" ")
        blocks = [int(x) for x in blocks.split(",")]
    
        mygenerator = Generator(
            set=seq_keys, 
            size=seq_length,
            maxchordsize=max_chord_size)

        trained_seqs, untrained_seqs \
        = mygenerator.read_grouped(seq_file, seq_type)
          
        n_trained = len(trained_seqs)
        n_untrained = len(untrained_seqs)
        reorder_trained = list(permutations(range(n_trained)))    
        reorder_trained_fmri = list(combinations(range(n_trained), n_seqs_fmri))    
        reorder_untrained = list(combinations(range(n_untrained), n_seqs)) if not opts.no_untrained else []  
        
#        if sched_group == 1: # swap trained and untrained
#            seq_list.reverse()
       # n_seqs: how many are presented
       # get colors
        seq_color = {}
        for myseq in trained_seqs: 
            index = random.randint(0, len(color_list) - 1)
            seq_color[myseq[1]] = color_list[index]
            del color_list[index]            

        for myseq in untrained_seqs:        
            index = random.randint(0, len(color_list) - 1)
            seq_color[myseq[1]] = color_list[index]
            del color_list[index]            

#        untrained_index = 0                 
        trained_comb_num = 1
        untrained_comb_num = 1
 
        for sess in range(n_sess):

            # controls the order across sessions
            trained_combination = list(reorder_trained[trained_comb_num \
                                                       % len(reorder_trained)])     
            
            trained_fmri_combination = list(reorder_trained_fmri[trained_comb_num \
                                                       % len(reorder_trained_fmri)])     
            trained_comb_num = trained_comb_num + 1
            
            for paced in range(2):

                myruns = n_runs if paced and \
                sess+1 in testing_session_list else 1 
                                        
                if not sess + 1 in testing_session_list: # training
                    sess_type = "training"
                    n_trials = n_free_trials if paced == 0 else \
                    n_paced_trials
                    
                    for seq in range(n_seqs):        
                        instruct = 1 if seq == 0 else 0
                        seq_index = trained_combination[seq]
                        seq_train = "trained"
                        sequence, sequence_string = \
                        trained_seqs[seq_index]

                        if n_trials > 0:
                            row_list.append([
                                sess_num,
                                sess_type,
                                n_trials,
                                " ".join(seq_keys),
                                seq_type,
                                sequence_string, 
                                seq_train,
                                seq_color[sequence],
                                trained_combination,
                                seq_index,
                                paced,
                                instruct,
                                1, #run
                                1 # block
                            ])


                else: # testing / fmri
                    untrained_combination = \
                    list(reorder_untrained[untrained_comb_num \
                                         % len(reorder_untrained)]) if not opts.no_untrained > 0 else []   
                    untrained_comb_num = untrained_comb_num + 1

                    
                    if paced == 0:
                        sess_type = "testing"
                        n_trials = n_free_trials_testing

                        for seq in range(2*n_seqs): # trained and untrained        
                            instruct = 1 if seq == 0 else 0

                            # interleave trained/untrained 
                            if seq % 2 == 1 and not opts.no_untrained: 
                                seq_index = untrained_combination[(seq - 1)/2]
                                seq_train = "untrained"
                                sequence, sequence_string = \
                                untrained_seqs[seq_index]
                                
                            else :
                                seq_index = trained_combination[seq/2]
                                seq_train = "trained"
                                sequence, sequence_string = \
                                trained_seqs[seq_index]

                            if n_trials > 0:
                                row_list.append([
                                    sess_num,
                                    sess_type,
                                    n_trials,
                                    " ".join(seq_keys),
                                    seq_type,
                                    sequence_string, 
                                    seq_train,
                                    seq_color[sequence_string],
                                    trained_combination,
                                    seq_index,
                                    paced,
                                    instruct,
                                    1, #run
                                    1 # block
                                ])


                    else:
                        sess_type = "fmri"

                        combination_index = trained_fmri_combination + \
                        untrained_combination
                        combination_type = \
                        len(trained_fmri_combination)*["trained"] + \
                        len(trained_combination)*["untrained"]
                        combination = zip(combination_type, combination_index)

                        n_trials = np.sum(np.array(blocks))
                        # compute run statistics
                        nbeats = config["MAX_CHORD_SIZE"] + \
                        config["EXTRA_BEATS"]
                        trial_duration = config["BEAT_INTERVAL"]*nbeats + \
                        config["BUFFER_TIME"] + config["FIXATION_TIME"] + \
                        config["ITIMEAN_FMRI"] 
                        run_duration = trial_duration*n_trials*\
                        (len(combination)) + config["START_TIME_FMRI"]
                        
                        total_duration = run_duration*n_runs 
                        total_trials = n_runs*n_trials
                    
                        print("Trial duration: %.2f s; "
                              %(trial_duration) +
                              "Run duration: %.2f m; "
                              %(run_duration/60) +
                              "Total duration: %.2f m; "
                              %(total_duration/60) + 
                              "Total trials per sequence: %d"
                              %(total_trials)
                              )                    


                        for run in range(myruns):
                            
                            shuffled_combination_run = \
                            shuffle_order(combination)
                            
                            for block, n_group in enumerate(blocks):

                                shuffled_combination = \
                                shuffle_order(shuffled_combination_run)
                                
                                # shuffle trained and untrained
                                for seq in range(len(shuffled_combination)):         
                                    instruct = 1 if seq == 0 and \
                                    block == 0 else 0
                                    
                                    combination_type, combination_index = \
                                    shuffled_combination[seq]
                                    if combination_type == "untrained": 
                                        seq_train = "untrained"
                                        sequence, sequence_string = \
                                        untrained_seqs[combination_index]
                                        
                                    else:
                                        seq_train = "trained"
                                        sequence, sequence_string = \
                                        trained_seqs[combination_index]
        
                                    if n_trials > 0:
                                        row_list.append([
                                            sess_num,
                                            sess_type,
                                            n_group,
                                            " ".join(seq_keys),
                                            seq_type,
                                            sequence_string, 
                                            seq_train,
                                            seq_color[sequence_string],
                                            shuffled_combination,
                                            seq_index,
                                            paced,
                                            instruct,
                                            run + 1, #run
                                            block + 1 # block
                                        ])
                                    
                    
            sess_num = sess_num + 1

    schedule = pd.DataFrame(row_list, columns = (
            "sess_num",
            "sess_type",
            "n_trials",    
            "seq_keys", 
            "seq_type", 
            "sequence_string", 
            "seq_train",
            "seq_color",
            "combination",
            "seq_order",
            "paced",
            "instruct",
            "run",
            "block"
    )
    )
    
   #    schedule.loc[schedule["sess_num"] == 0, "sess_num"] = \
#        np.max(schedule["sess_num"]) + 1
#    schedule.sort_values(by = ["sess_num", "paced", "seq_train"], 
#                         inplace = True)

    if opts.schedule_file:
        schedulefilename = opts.schedule_file + "_{}".format(sched_group)
    else:    
        schedulefilename = "./scheduling/schedule{}".format(sched_group) 

    if opts.split:
        schedule_home = \
        schedule.loc[schedule["sess_type"] != "fmri", :]
        schedule_fmri = \
        schedule.loc[schedule["sess_type"] == "fmri", :]
        
        schedule_home.to_csv(schedulefilename + ".csv", 
                                 sep =";", index=False)
        schedule_fmri.to_csv(schedulefilename + "_fmri.csv", 
                                 sep =";", index=False)
    else:
        schedule.to_csv(schedulefilename + ".csv", sep =";", index=False)

        
def build_parser():
    parser = ArgumentParser()

    parser.add_argument("--sequence_file", 
                        type = str,
                        dest = "seq_file", 
                        help = "Enter sequence file.",
                        required = False)

    parser.add_argument("--sequence_file2", 
                        type = str,
                        dest = "seq_file2", 
                        help = "Enter additional sequence file. " + \
                        "It can be used for non-memorized sequences " + \
                        "or to vary untrained sequences.",
                        required = False)

    parser.add_argument("--unseen", 
                        dest = "unseen", 
                        help = "Add non-memorized sequences to test.",
                        required = False)


    parser.add_argument("--schedule_file", 
                        type = str,
                        dest = "schedule_file", 
                        help = "Enter schedule file.",
                        required = False)

    parser.add_argument("--type_file", 
                        type = str,
                        dest = "type_file", 
                        help = "Enter sequence type file.",
                        required = False)

    parser.add_argument("--split", 
                        dest = "split", 
                        help = "Returns separate files for training and " + 
                        "testing (_fMRI).",
                        action="store_true",
                        required = False)

    parser.add_argument("--no_untrained", 
                        dest = "no_untrained", 
                        help = "Ignore untrained sequences.",
                        action="store_true",
                        required = False)

    return(parser)

def main():
    parser = build_parser()
    
    print("Preparing schedule...")
    opts = parser.parse_args()
    opts.seq_file =  "./scheduling/sequences/sequences_grouped_001_lund1"
    opts.schedule_file =  "./scheduling/schedules/lup1schedule1"
    opts.type_file = "./scheduling/seq_types_lu1.csv"
    opts.no_untrained = True
    opts.split = True
    generate_with_predefined_sequences(opts, sched_group = 0)
#    generate_with_predefined_sequences(opts, sched_group = 1)
    print("Done!")
  
if __name__== "__main__":
  main()
