# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 08:52:02 2020

@author: dblokv@gmail.com
"""

from display import Display
from recorder import Recorder
from config import config_init
import time
from queue import Queue
#from pathlib import Path
from data_processing import DataProcessing
from sys import argv

def start():
    
    # create config dict
    config = config_init(argv)
    
    
    # Queue is used to pass arguments from display thread to main thread (to LSL_Listener)
    q_from_display_to_recorder = Queue()
    
    # remove_mode does not use data from lsl, just show pictures
    if config['general'].getboolean('remove_mode'):
        patient_display = Display(config, q_from_display_to_recorder)
        patient_display.start()
        return
    
    # Debug mode uses LSL_Generator for debuging
    if config['general'].getboolean('debug_mode'):
        print('Debug Mode!!!')
        debug_time = config['general'].getint('debug_time')
        lsl_stream_generator_path = config['paths']['lsl_stream_generator_path']
        import importlib.util
        spec = importlib.util.spec_from_file_location("lsl_stream_generator", lsl_stream_generator_path)
        lsl_stream_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lsl_stream_generator)
        lsl_stream_debug = lsl_stream_generator.LSL_Generator(debug_time, 69, 2048, q_from_display_to_recorder)
        lsl_stream_debug.start()
        time.sleep(2)
    
    # create LSL_Listener object    
    recorder = Recorder(config, 2048, q_from_display_to_recorder)
    
    # Activate Display if not debugging or if debugging with stream from LSL_Generator
    #if not config['general'].getboolean('debug_mode') or config['general'].getboolean('lsl_outlet_random'):
    patient_display = Display(config, q_from_display_to_recorder)
    patient_display.start()
    time.sleep(0.5)
    
    # Type data saving
    recorder.record()

    
    # process data and plot results
    processing = DataProcessing(config)
    processing.calculate()
    processing.plot_results()
    


if __name__ == '__main__':
    start()