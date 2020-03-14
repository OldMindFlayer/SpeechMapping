# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 08:52:02 2020

@author: dblokv@gmail.com
"""

from display import Display
from lsl_stream_listener import LSL_Listener
from make_directories import make_directories
from config import config_init
import time
import os
from queue import Queue
from pathlib import Path
from data_processing import DataProcessing


def start():
    
    # create config dict
    config = config_init()
    
    # Queue is used to pass arguments from display thread to main thread (to LSL_Listener)
    q_from_display_to_listener = Queue()
    
    # Path autogeneration ignores path in config and generate path based on location of 'main.py'
    if config['general'].getboolean('root_path_autogeneration'):
        config['general']['root_path'] = str(Path('main.py').resolve().parents[1])
    if  config['patient_info'].getboolean('patient_date_time_autogeneration'):
        config['patient_info']['patient_date'] = time.strftime('%d_%m_%y')
        config['patient_info']['patient_time'] = time.strftime('%H_%M_%S')

    # Create directory stucture for experiment and update config with 'patient_data_path'
    directory_paths = make_directories(config)
    config['patient_info']['patient_data_path'] = directory_paths[0]
    config['patient_info']['patient_experiment_data_path'] = directory_paths[1]
    config['patient_info']['patient_results_path'] = directory_paths[2]
    
    
    # Debug mode uses LSL_Generator for debuging
    if config['general'].getboolean('debug_mode'):
        print('Debug Mode!!!')
        debug_time = config['general'].getint('debug_time')
        time_pictures = int((debug_time-15)/3)
        config['display']['resting_time'] = str(time_pictures)
        config['display']['pictures_action_time'] = str(time_pictures)
        config['display']['pictures_object_time'] = str(time_pictures)
        lsl_stream_generator_path = config['general']['root_path']+'/util'+'/lsl_stream_generator.py'
        import importlib.util
        spec = importlib.util.spec_from_file_location("lsl_stream_generator", lsl_stream_generator_path)
        lsl_stream_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lsl_stream_generator)
        lsl_stream_debug = lsl_stream_generator.LSL_Generator(debug_time, 69, 2048, q_from_display_to_listener)
        lsl_stream_debug.start()
        time.sleep(1)
        
    # create LSL_Listener object    
    lsl_listener = LSL_Listener(config, 2048, q_from_display_to_listener)
    
    # Activate Display if not debugging or if debugging with stream from LSL_Generator
    if not config['general'].getboolean('debug_mode') or config['general'].getboolean('lsl_outlet_random'):
        patient_display = Display(config, q_from_display_to_listener)
        patient_display.start()
        time.sleep(0.5)
    
    # Type data saving
    if config['general'].getboolean('save_through_buffer'):    
        lsl_listener.record_using_buffer()
    else:
        lsl_listener.record_using_memory()
    
    # process data and plot results
    processing = DataProcessing(config)
    processing.calculate()
    processing.plot_results()
    


if __name__ == '__main__':
    start()