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

# get config
config = get_config()
type_data = get_seq_types()
schedulefilename = "./scheduling/schedule.csv"

color_list = config["COLOR_LIST"]

# create sequences
row_list = []

sess_num = 1
for index, row in type_data.iterrows():
    seq_type, seq_length, max_chord_size, seq_keys, n_trials, n_seqs, n_sess =\
    row
    
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
        
    for sess in range(n_sess + 1): 
        for seq in range(2*n_seqs):        

            seq_train = "trained"
            # create training and testing sessions

            if sess < n_sess:
                sess_type = "training"
                true_sess_num = sess_num
                if seq >= n_seqs:
                    continue
            else:
                sess_type = "testing"
                true_sess_num = 0
                if seq >= n_seqs:
                    seq_train = "untrained"

            sequence, sequence_string = seq_list[seq]
            color = seq_color[seq]
            row_list.append([
                true_sess_num,
                sess_type,
                n_trials,
                " ".join(seq_keys),
                seq_type,
#                sequence,
                sequence_string, 
                seq_train,
                color
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
        "seq_color"
)
)

schedule.loc[schedule["sess_num"] == 0, "sess_num"] = np.max(schedule["sess_num"]) + 1
schedule.sort_values(by = ["sess_num", "seq_type", "seq_train", "sequence_string" ], inplace = True)
schedule.to_csv(schedulefilename, sep =";", index=False)

