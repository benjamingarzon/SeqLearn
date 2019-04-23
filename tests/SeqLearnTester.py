# -*- coding: utf-8 -*-
"""
Created on Sun Apr 21 12:07:40 2019

@author: Benjamin.Garzon
"""
from argparse import ArgumentParser
import sys, os
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '..'))
from SeqLearn import SeqLearn
from psychopy import core
parser = ArgumentParser()
opts = parser.parse_args()
opts.automate = True
opts.no_upload = False
opts.restart = True
opts.config_file = None
opts.demo = False
opts.schedule_file = None

opts.run = None
opts.session = None

# testing home sessions 
opts.run_fmri = False

for session in range(40):
    print("Test session %d"%(session))
    opts.restart = True if session == 0 else False
    SeqLearn(opts)
    
# testing home sessions 
opts.run_fmri = True
for session in range(10):
    opts.restart = True if session == 0 else False
    SeqLearn(opts)

core.quit()

