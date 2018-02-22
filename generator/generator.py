# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 09:46:11 2018

@author: benjamin.garzon@gmail.com

Discrete sequence production generator class.
"""
from itertools import combinations
import numpy as np
from random import choice, sample
    
class Generator:
    """ Create a generator """

    def __init__(self, set=0, size=1, maxchordsize=1):
        """ Create a new point sequence generator"""
        self.set = [str(x) for x in set]
        self.size = size
        
        # create all possible chords of maxchordsize
        self.chords = []
        for k in range(maxchordsize):
            combs = [[str(y) for y in x] for x in combinations(set, k+1)]
            self.chords.extend(combs)
                
    def random(self, replace=True):
        """ Generates a random sequence with the given attributes."""
        if replace:
            sequence = [ choice(self.chords) 
            for i in range(self.size) ]
        else:
            sequence = sample(self.chords, size=self.size) 
        sequence_string = " \n ".join([" ".join(x) for x in sequence])
 
        return (sequence, sequence_string)