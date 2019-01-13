# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 09:46:11 2018

@author: benjamin.garzon@gmail.com

Discrete sequence production generator class.
"""
from itertools import combinations
from random import choice, sample
from psychopy import visual
import json

class Generator:
    """ Create a generator """

    def __init__(self, set=0, size=1, maxchordsize=1):
        """ Create a new sequence generator"""
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
        sequence_string = seq_to_string(sequence)
 
        return (sequence, sequence_string)

    def read(self, seq_file, seq_type=None):
        """Read sequences from sequence file with predefined sequences."""
                    
        try:
            seq_json = open(seq_file, "r")
            seqs = json.load(seq_json)
            seq_json.close()
        except IOError: 
            print "Error: Sequence file is missing!"
            
        seq_list = [ (string_to_seq(x), x) for x in seqs[seq_type]]
        return(seq_list)
        
    def read_grouped(self, seq_file, seq_type=None):
        """Read sequences from sequence file with predefined sequences."""
                    
        try:
            seq_json = open(seq_file, "r")
            seqs = json.load(seq_json)
            seq_json.close()
        except IOError: 
            print "Error: Sequence file is missing!"
        trained = [ (string_to_seq(x), x) 
        for x in seqs[seq_type]['trained']]
        untrained = [ (string_to_seq(x), x) 
        for x in seqs[seq_type]['untrained']]
        
        return(trained, untrained)
    
    
def string_to_seq(mystring):
    """ Translate string to a sequence. """

    myseq = mystring.split(" - ")
    myseq = [ x.split(" ") for x in myseq ]
    return(myseq)
    
def seq_to_string(myseq):
    """ Translate sequence to a string. """

    mystring = " - ".join([" ".join(x) for x in myseq])
    return(mystring)

def seq_to_stim(mystring, color, win, size):
    """ Translate sequence to squares. """
    myseq = string_to_seq(mystring)
    length = len(myseq)*size
    seq_pos = length - size
 
    #print(myseq)
    square_list = [] 
    for mychord in myseq:
        
        for mykey in mychord:
            square = visual.Rect(win, 
                         height=size, 
                         width=size,
                         lineWidth=0, 
                         fillColor=color, 
                         pos=((int(mykey) - 2.5)*1.5*size, 
                              seq_pos))
            square_list.append(square)
        seq_pos = seq_pos - 2*size
    
    lines = []
    for x in [-3, -1.5, 0, 1.5, 3]:
        vertices = [(size*x, length + 0.25*size), (size*x, - length + 0.25*size)]
        lines.append(visual.ShapeStim(win, 
                                      vertices=vertices, 
                                      lineWidth=0.5,
                                      closeShape=False, 
                                      lineColor='black', 
                                      pos = (0, 0))
                )
                
    arrowVertLeft = [(-size*3.2 , - length + 0.25*size ), 
                     (-size*3, - length ),
                     (-size*2.8, - length + 0.25*size)]

    arrowVertRight = [(size*3.2, - length + 0.25*size), 
                     (size*3, - length ),
                     (size*2.8, - length + 0.25*size)]
    
    
    arrowLeft = visual.ShapeStim(win, 
                                 vertices=arrowVertLeft, 
                                 lineColor='black',
                                 fillColor='black',
                                 lineWidth=0.5)
        
    arrowRight = visual.ShapeStim(win, 
                                  vertices=arrowVertRight, 
                                  lineColor='black',
                                  fillColor='black',
                                  lineWidth=0.5)        
                
    square_list = square_list + lines + [arrowLeft, arrowRight]
    return(square_list)

def seq_to_stim_binary(mystring, color, win, size):
    """ Translate sequence to squares. """
    myseq = string_to_seq(mystring)
    length = len(myseq)*size
    seq_pos = length - size
 
    #print(myseq)
    square_list = [] 
    for mychord in myseq:
        
        for mykey in mychord:
            square = visual.Rect(win, 
                         height=size, 
                         width=size,
                         lineWidth=0, 
                         fillColor=color, 
                         pos=((int(mykey) - 2.5)*1.5*size, 
                              seq_pos))
            square_list.append(square)
        seq_pos = seq_pos - 2*size
    
    lines = []
    for x in [-3, -1.5, 0, 1.5, 3]:
        vertices = [(size*x, length + 0.25*size), (size*x, - length + 0.25*size)]
        lines.append(visual.ShapeStim(win, 
                                      vertices=vertices, 
                                      lineWidth=0.5,
                                      closeShape=False, 
                                      lineColor='black', 
                                      pos = (0, 0))
                )
                
    arrowVertLeft = [(-size*3.2 , - length + 0.25*size ), 
                     (-size*3, - length ),
                     (-size*2.8, - length + 0.25*size)]

    arrowVertRight = [(size*3.2, - length + 0.25*size), 
                     (size*3, - length ),
                     (size*2.8, - length + 0.25*size)]
    
    
    arrowLeft = visual.ShapeStim(win, 
                                 vertices=arrowVertLeft, 
                                 lineColor='black',
                                 fillColor='black',
                                 lineWidth=0.5)
        
    arrowRight = visual.ShapeStim(win, 
                                  vertices=arrowVertRight, 
                                  lineColor='black',
                                  fillColor='black',
                                  lineWidth=0.5)        
                
    square_list = square_list + lines + [arrowLeft, arrowRight]
    return(square_list)
      