# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 09:46:11 2018

@author: benjamin.garzon@gmail.com

Discrete sequence production generator class.
"""
import numpy as np

class Generator:
    """ Create a generator """

    def __init__(self, set=0, size=1):
        """ Create a new point sequence generator"""
        self.set = set
        self.size = size
        self.sequence = set

    def random(self, replace=True):
        """ Generates a random sequence with the given attributes."""
        self.sequence = np.random.choice(self.set, 
                                         size=self.size, 
                                         replace=replace) 
        return (self.sequence)
        