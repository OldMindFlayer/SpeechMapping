# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 08:52:02 2020

@author: dblok
"""

from display import Display
from lsl_stream_listener import LSL_Listener
import config
import time
import os
from queue import Queue
from pathlib import Path

def start():
   
    # Queue is used to pass arguments from display thread to main thread (to LSL_Listener)
    q_from_display_to_listener = Queue()
    
    # Debug mode uses LSL_Generator for debuging
    if config.config['general'].getboolean('debug_mode'):
        print('Debug Mode!!!')
        debug_time = config.config['general'].getint('debug_time')
        time_pictures = int((debug_time-15)/3)
        config.config['display']['resting_time'] = str(time_pictures)
        config.config['display']['pictures_action_time'] = str(time_pictures)
        config.config['display']['pictures_object_time'] = str(time_pictures)
        lsl_stream_generator_path = config.config['general']['root_path']+'/util'+'/lsl_stream_generator.py'
        import importlib.util
        spec = importlib.util.spec_from_file_location("lsl_stream_generator", lsl_stream_generator_path)
        lsl_stream_generator = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(lsl_stream_generator)
        lsl_stream_debug = lsl_stream_generator.LSL_Generator(debug_time, 68, 2048, q_from_display_to_listener)
        lsl_stream_debug.start()
        time.sleep(1)
        
    # Path autogeneration ignores path in config and generate path based on location of 'main.py'
    if config.config['general'].getboolean('root_path_autogeneration'):
        config.config['general']['root_path'] = str(Path('main.py').resolve().parents[1])
    if  config.config['patient_info'].getboolean('patient_date_autogeneration'):
        config.config['patient_info']['patient_date'] = time.strftime('%d_%m_%y')
        

    lsl_listener = LSL_Listener(2048, q_from_display_to_listener)
    
    # Activate Display if not debugging or if debugging with stream from LSL_Generator
    if not config.config['general'].getboolean('debug_mode') or config.config['general'].getboolean('lsl_outlet_random'):
        patient_display = Display(q_from_display_to_listener)
        patient_display.start()
        time.sleep(0.5)
    
    # Type data saving
    if config.config['general'].getboolean('save_through_buffer'):    
        lsl_listener.record_using_buffer()
    else:
        lsl_listener.record_using_memory()
    
    # activate decoder
    path_processing = config.config['general']['root_path'] + '/data/' + config.config['patient_info']['patient_name'] + \
    '/' + config.config['patient_info']['patient_date']
    os.system("python {}/spmap/data_processing.py {}".format(config.config['general']['root_path'], path_processing))


if __name__ == '__main__':
    config.init()
    start()