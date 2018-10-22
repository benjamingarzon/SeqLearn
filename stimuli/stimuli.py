# -*- coding: utf-8 -*-
"""
Created on Wed Feb 21 15:17:50 2018

@author: benjamin.garzon@gmail.com

File with all the stimuli.
"""
from psychopy import sound
from psychopy import visual

def define_stimuli(win, username, config, texts, sess_num, seq_length, 
                   total_trials):

    stimuli = {}
    
    stimuli["buzzer"] = sound.Sound(config["BUZZER_FILE"])
    
    stimuli["tick"] = sound.Sound(1200, secs=0.01, sampleRate=44100)  # sample rate ignored because already set

    stimuli["tock"] = sound.Sound(900, secs=0.01, sampleRate=44100)
    
    stimuli["intro_message"] = visual.TextStim(win, 
                                    text = texts["TEXT_INTRO"].format(username, 
                                               sess_num), 
                                               height = \
                                               config["HEADING_TEXT_HEIGHT"], 
                                               alignHoriz="center") 

    stimuli["instructions_space"] = visual.TextStim(win, 
                                           text = texts["TEXT_SPACE"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center",
                                           pos = (0, -7)) 

    stimuli["instructions_select"] = visual.TextStim(win, 
                                           text = texts["TEXT_SELECT"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center",
                                           pos = (0, -7)) 
    
    stimuli["instructionspre1_message"] = visual.TextStim(win, 
                                           text = texts["TEXT_INSTRUCTPRE1"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center",
                                           pos = (-5, 0), 
                                           wrapWidth = 11 ) 

    stimuli["instructionspre2_message"] = visual.TextStim(win, 
                                           text = texts["TEXT_INSTRUCTPRE2"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center")
    
    stimuli["instructions1_message"] = visual.TextStim(win, 
                                           text = texts["TEXT_INSTRUCT1"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center",
                                           pos = (-5, 0), 
                                           wrapWidth = 11) 
    
    stimuli["instructions2_message"] = visual.TextStim(win, 
                                        text = texts["TEXT_INSTRUCT2"].format(
                                        seq_length*\
                                        config["MAX_WAIT_PER_KEYPRESS"], 
                                        total_trials), 
                                        height = config["TEXT_HEIGHT"], 
                                        alignHoriz="center") 
    
    stimuli["instructions3_message"] = visual.TextStim(win, 
                                           text = texts["TEXT_INSTRUCT3"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center",
                                           pos = (0, 2)) 
    
    stimuli["instructions4_message"] = visual.TextStim(win, 
                                           text = texts["TEXT_INSTRUCT4"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center", 
                                           pos = (0, 1))

    stimuli["instructions4_space"] = visual.TextStim(win, 
                                           text = texts["TEXT_SPACE4"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center",
                                           pos = (0, -5),
                                           color="red") 
    
    stimuli["instructionspaced1_message"] = visual.TextStim(win, 
                                           text = texts["TEXT_INSTRUCTPACED1"]\
                                           .format(config["EXTRA_BEATS"]), 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center") 

    stimuli["instructionsfmri1_message"] = visual.TextStim(win, 
                                           text = texts["TEXT_INSTRUCTFMRI1"]\
                                           .format(config["EXTRA_BEATS"]), 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center", 
                                           pos = (0, 1))

    stimuli["instructionsfmripaced1_message"] = visual.TextStim(win, 
                                           text = texts["TEXT_INSTRUCTFMRIPACED1"]\
                                           .format(config["EXTRA_BEATS"]), 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center", 
                                           pos = (0, 1))

    stimuli["instructionsbreak_message"] = visual.TextStim(win, 
                                           text = texts["TEXT_BREAK"], 
                                           height = config["TEXT_HEIGHT"], 
                                           alignHoriz="center", 
                                           pos = (0, 1))


    stimuli["last_label"] = visual.TextStim(win, 
                                    text = texts["LAST_LABEL"], 
                                    height = config["TEXT_HEIGHT"], 
                                    pos = (-3*config["BAR_WIDTH"], 
                                           -0.5*config["BAR_HEIGHT"] - 2),
                                    alignHoriz="center") 

    stimuli["best_label"] = visual.TextStim(win, 
                                 text = texts["BEST_LABEL"], 
                                 height = config["TEXT_HEIGHT"],
                                 pos = (0, 
                                        -0.5*config["BAR_HEIGHT"] - 2),
                                 alignHoriz="center") 
    
    stimuli["group_best_label"] = visual.TextStim(win, 
                                 text = texts["GROUP_BEST_LABEL"], 
                                 height = config["TEXT_HEIGHT"],
                                 pos = (3*config["BAR_WIDTH"], 
                                        -0.5*config["BAR_HEIGHT"] - 2),
                                 alignHoriz="center") 
                                 
    stimuli["error_message"] = visual.TextStim(win, 
                                    text = texts["TEXT_ERROR"], 
                                    alignHoriz="center", 
                                    pos = (0, -3))  

    stimuli["error_sign"] = visual.ImageStim(win, 
                                  image=config["WRONG_FILE"],
                                  pos = (0, 2))
    
    stimuli["hand_sign"] = visual.ImageStim(win, 
                                  image=config["HAND_FILE"],
                                  pos = (6, 0))

    stimuli["bars_sign"] = visual.ImageStim(win, 
                                  image=config["BARS_FILE"],
                                  pos = (0, -6))     
    stimuli["bottomline"] = visual.ShapeStim(win,
           vertices= [(-3*config["BAR_WIDTH"] - 3, - 3 ), 
                      (3*config["BAR_WIDTH"] + 3, - 3 )],
                      lineWidth=0.5,
                      closeShape=False, 
                      lineColor='black')

    stimuli["late_message"] = visual.TextStim(win, 
                                    text = texts["TEXT_LATE"], 
                                    alignHoriz="center", 
                                    pos = (0, -3))  

    stimuli["miss_message"] = visual.TextStim(win, 
                                    text = texts["TEXT_MISS"], 
                                    alignHoriz="center")

    stimuli["fixation"] = visual.ShapeStim(win, 
        vertices=((0, -0.5), (0, 0.5), (0,0), (-0.5,0), (0.5, 0)),
        lineWidth=5,
        closeShape=False,
        lineColor="white")

    stimuli["bye_message"] = visual.TextStim(win, 
                                    text = texts["TEXT_BYE"], 
                                    alignHoriz="center")

    stimuli["ok_message"] = visual.TextStim(win, 
                                    text = texts["TEXT_OK"], 
                                    alignHoriz="center", 
                                    pos = (0, -3))

    stimuli["ok_sign"] = visual.ImageStim(win, 
                                  image=config["OK_FILE"],
                                  pos = (0, 2))

#    stimuli["thumbsup_sign"] = visual.ImageStim(win, 
#                                  image=config["THUMBSUP_FILE"],
#                                  pos = (0, -6))

#    stimuli["thumbsdown_sign"] = visual.ImageStim(win, 
#                                  image=config["THUMBSDOWN_FILE"],
#                                  pos = (0, -6))


    return(stimuli)
    


