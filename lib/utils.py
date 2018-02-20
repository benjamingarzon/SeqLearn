# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 08:41:28 2018

@author: benjamin.garzon@gmail.com

Some functions for SeqLearn
"""

def showStimulus(stimulus):
    stimulus.draw()
    win.flip()

def computePerformance(keys, RTs, sequence):
""" 
Returns accuracy and total movement time
"""
    # accuracy
    correct = [keys[k][0] == s for k, s in enumerate(sequence)]
    accuracy = np.sum(correct) / len(sequence)

    # MT
    MT = np.sum(RTs[1:])
    return((accuracy, MT))

def filter_keys(keys):
""" 
Aggregate keypresses when they are close together (chords)
"""

    stimulus.draw()
    win.flip()


