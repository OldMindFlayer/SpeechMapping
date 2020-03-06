# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 08:52:02 2020

@author: dblok
"""

from display import Display
from lsl_generator_debug import DebudStream
from lsl_stream_listener import LSL_Listener
import config
import time
import os
from queue import Queue

def start():
    if config.config['general'].getboolean('debug_mode'):
        debug_stream = DebudStream(20, 68, 2048)
        debug_stream.start()
        time.sleep(1)
    
    
    q_from_display_to_listener = Queue()
    lsl_listener = LSL_Listener(2048, q_from_display_to_listener)
    
    if not config.config['general'].getboolean('debug_mode') or config.config['general'].getboolean('lsl_outlet_random'):
        patient_display = Display(q_from_display_to_listener)
        patient_display.start()
        time.sleep(0.5)
    
    if config.config['general'].getboolean('save_through_buffer'):    
        lsl_listener.record_using_buffer()
    else:
        lsl_listener.record_using_memory()
    
    
    path = config.config['general']['general_path'] + 'data/' + config.config['patient_info']['patient_name'] + \
    '/' + config.config['patient_info']['patient_date']
    os.system("python C:/Workspace/SpeechMappingv0_3/scrips/data_processing.py {}".format(path))


if __name__ == '__main__':
    config.init()
    start()
    #python C:/Workspace/SpeechMappingRelease/scrips/data_processing.py C:/Workspace/SpeechMappingRelease/data/ABCD/01_01_20