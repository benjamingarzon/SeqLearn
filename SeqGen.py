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
from itertools import permutations
from argparse import ArgumentParser

def generate_with_predefined_sequences(opts, sched_group):
    """
    Generate schedule using sequences already defined. 
    """
    # get config
    config = get_config()
    type_data = get_seq_types(opts.type_file)
     
    seq_file = \
    opts.seq_file if opts.seq_file else "./scheduling/sequences.json"
    
    color_list = config["COLOR_LIST"]
    
    # create sequences
    row_list = []
    sess_num = 1
    for index, row in type_data.iterrows():
        seq_type, seq_length, max_chord_size, seq_keys, n_free_trials, \
        n_paced_trials, n_free_trials_testing, n_paced_trials_testing, n_seqs,\
        n_sess, testing_sessions = row
        testing_session_list = \
        [int(x) for x in str(testing_sessions).split(",")]
        reorder = list(permutations(range(n_seqs)))    
        seq_list = []
        seq_color = []
    
        seq_keys = seq_keys.split(" ")
    
        mygenerator = Generator(
            set=seq_keys, 
            size=seq_length,
            maxchordsize=max_chord_size)

        seq_list = mygenerator.read(seq_file, seq_type)
        
        if sched_group == 1: # swap trained and untrained
            seq_list.reverse()
        
        if opts.seq_file2:
            seq_list2 = mygenerator.read(opts.seq_file2, seq_type)
            myfac = 3
            seq_list = seq_list + seq_list2
        else: 
            myfac = 2
      
        # generate the sequences
        for seq in range(myfac*n_seqs): # 2 times: trained and untrained       
            index = random.randint(0, len(color_list)-1)
            seq_color.append(color_list[index])
            del color_list[index]            
                 
        for sess in range(n_sess):
            for paced in range(2):

                mypermutation = list(reorder[sess_num % len(reorder)])     
                
                for seq in range(myfac*n_seqs):        
        
                    instruct = 1 if seq == 0 else 0
                    
                    # create training and testing sessions    
                    if not sess+1 in testing_session_list:
                        sess_type = "training"
                        n_trials = n_free_trials if paced == 0 else \
                        n_paced_trials

                        if seq >= n_seqs:
                            continue
                        seq_index = mypermutation[seq]
                        seq_train = "trained"
           
                    else:
                        sess_type = "testing"
                        n_trials = n_free_trials_testing if paced == 0 else \
                        n_paced_trials_testing
     
                        if opts.seq_file2:
                            # interleave trained/untrained/unseen
                                                            
                            if seq % 3 == 2: 
                                seq_index = mypermutation[(seq - 2)/3] + \
                                2*n_seqs 
                                seq_train = "unseen"
                            if seq % 3 == 1:
                                seq_index = mypermutation[(seq - 1)/3] + n_seqs
                                seq_train = "untrained"
                            if seq % 3 == 0: 
                                seq_index = mypermutation[seq/3]
                                seq_train = "trained"
                        
                        else:                            
                            if seq % 2 == 1: # interleave trained/untrained
                                # use the same permutation, 
                                # although it possibly won't make a difference
                                seq_index = mypermutation[(seq - 1)/2] + n_seqs 
                                seq_train = "untrained"
                            else :
                                seq_index = mypermutation[seq/2]
                                seq_train = "trained"
    
                    sequence, sequence_string = seq_list[seq_index]
                    color = seq_color[seq_index]
                        
                    if n_trials > 0 :
                        row_list.append([
                            sess_num,
                            sess_type,
                            n_trials,
                            " ".join(seq_keys),
                            seq_type,
#                            sequence,
                            sequence_string, 
                            seq_train,
                            color,
                            mypermutation,
                            seq_index,
                            paced,
                            instruct,
                            ])
    
            sess_num = sess_num + 1

    schedule = pd.DataFrame(row_list, columns = (
            "sess_num",
            "sess_type",
            "n_trials",    
            "seq_keys", 
            "seq_type", 
    #        "sequence", 
            "sequence_string", 
            "seq_train",
            "seq_color",
            "seq_permutation",
            "seq_order",
            "paced",
            "instruct"
    )
    )
    
#    schedule.loc[schedule["sess_num"] == 0, "sess_num"] = \
#        np.max(schedule["sess_num"]) + 1
#    schedule.sort_values(by = ["sess_num", "seq_type", "seq_train"], 
#                         inplace = True)

    if opts.schedule_file:
        schedulefilename = opts.schedule_file + "_{}".format(sched_group)
    else:    
        schedulefilename = "./scheduling/schedule{}".format(sched_group) 

    if opts.split:
        schedule_training = \
        schedule.loc[schedule["sess_type"] == "training", :]
        schedule_testing = \
        schedule.loc[schedule["sess_type"] == "testing", :]
        
        schedule_training.to_csv(schedulefilename + ".csv", 
                                 sep =";", index=False)
        schedule_testing.to_csv(schedulefilename + "_fmri.csv", 
                                 sep =";", index=False)
    else:
        schedule.to_csv(schedulefilename + ".csv", sep =";", index=False)
        
        
def generate_with_random_sequences(sched_group):
    """
    Generate schedule using random sequences.
    
    ------- NEEDS UPDATE!!!! ---------
    """
    # fix for TESTING_SESSIONS

    # get config
    config = get_config()
    type_data = get_seq_types()
    schedulefilename = "./scheduling/schedule{}.csv".format(sched_group) 
        
    color_list = config["COLOR_LIST"]
    
    # create sequences
    row_list = []
    
    sess_num = 1
    for index, row in type_data.iterrows():
        seq_type, seq_length, max_chord_size, seq_keys, n_trials, n_seqs, \
        n_sess, testing_sessions = row
        
        reorder = list(permutations(range(n_seqs)))    
        seq_list = []
        seq_color = []
    
        seq_keys = seq_keys.split(" ")
    
        mygenerator = Generator(
            set=seq_keys, 
            size=seq_length,
            maxchordsize=max_chord_size)
    
        # generate the sequences
        for seq in range(2*n_seqs): # 2 times: trained and untrained       
            seq_list.append(mygenerator.random())
            index = random.randint(0, len(color_list)-1)
            seq_color.append(color_list[index])
            del color_list[index]
#            if sched_group == 1: # swap trained and untrained
#                 seq_list.reverse()
                 
        for sess in range(n_sess + 1):
            mypermutation = list(reorder[sess % len(reorder)])        
            for seq in range(2*n_seqs):        
    
                seq_train = "trained"
                # create training and testing sessions
                if sess < n_sess:
                    sess_type = "training"
                    true_sess_num = sess_num
                    if seq >= n_seqs:
                        continue
                    seq_index = mypermutation[seq]
                    
                else:
                    sess_type = "testing"
                    true_sess_num = 0

                    if seq % 2 == 1: # interleave trained/untrained
                        # use the same permutation, 
                        # although it possibly won't make a difference
                        seq_index = mypermutation[(seq - 1)/2] + n_seqs 
                        seq_train = "untrained"
                    else :
                        seq_index = mypermutation[seq/2]
                        seq_train = "trained"
                        
                sequence, sequence_string = seq_list[seq_index]
                color = seq_color[seq_index]
                    
                row_list.append([
                    true_sess_num,
                    sess_type,
                    n_trials,
                    " ".join(seq_keys),
                    seq_type,
    #                sequence,
                    sequence_string, 
                    seq_train,
                    color,
                    mypermutation,
                    seq_index
                    ])
    
            if sess < n_sess:    
                sess_num = sess_num + 1
    
    
    schedule = pd.DataFrame(row_list, columns = (
            "sess_num",
            "sess_type",
            "n_trials",    
            "seq_keys", 
            "seq_type", 
    #        "sequence", 
            "sequence_string", 
            "seq_train",
            "seq_color",
            "seq_permutation",
            "seq_order"
    )
    )
    
    schedule.loc[schedule["sess_num"] == 0, "sess_num"] = \
        np.max(schedule["sess_num"]) + 1
    schedule.sort_values(by = ["sess_num", "seq_type", "seq_train"], 
                         inplace = True)
    schedule.to_csv(schedulefilename, sep =";", index=False)

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
                        "It can be used for non-memorized sequences.",
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

    return(parser)

def main():
  parser = build_parser()

  print("Preparing schedule...")
  opts = parser.parse_args()
  generate_with_predefined_sequences(opts, sched_group = 0)
  generate_with_predefined_sequences(opts, sched_group = 1)
  print("Done!")
  
if __name__== "__main__":
  main()
