# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:37:29 2020

@author: dblok
"""

import configparser
import time
from os import makedirs
from pathlib import Path

def config_init(argv):
    config = configparser.ConfigParser()
    config.read('config.ini')
    
    if len(argv) > 1 and argv[1] == '-debug':
        config['general']['debug_mode'] = 'true'
    else:
        config['general']['debug_mode'] = 'false'
    
    # Path autogeneration ignores path in config and generate path based on location of 'main.py'
    if config['general'].getboolean('root_path_autogeneration'):
        if len(Path('main.py').resolve().parents) >= 3:
            config['paths']['root_path'] = str(Path('main.py').resolve().parents[2])
        else:
            config['paths']['root_path'] = str(Path('main.py').resolve().parents[1])
            
    # Date and time autogeneration ignores values in config and generate them based on current date and time
    if  config['general'].getboolean('patient_date_time_autogeneration'):
        config['patient_info']['patient_date'] = time.strftime('%d_%m_%y')
        config['patient_info']['patient_time'] = time.strftime('%H_%M_%S')
    
    
    # get parts of paths from config file
    root_path = Path(config['paths']['root_path'])
    patient_name = config['patient_info']['patient_name']
    patient_date = config['patient_info']['patient_date']
    patient_time = config['patient_info']['patient_time']
    
    # create Path objects for 'experiment_data' and 'results' directories
    patient_data_path = root_path/'SpeechMappingData'/(patient_date + '_' + patient_name)/(patient_time + '_experiment')
    experiment_data_path = patient_data_path/'experiment_data.h5'
    results_path = patient_data_path/'results'
    
    # create directories
    makedirs(results_path, exist_ok=True)
    
    # Create directory stucture for experiment and update config with 'patient_data_path'
    config['paths']['patient_data_path'] = str(patient_data_path)
    config['paths']['experiment_data_path'] = str(experiment_data_path)
    config['paths']['results_path'] = str(results_path)
    if config['general'].getboolean('debug_mode'):
        config['paths']['lsl_stream_generator_path'] = str(root_path/'SpeechMapping/util/lsl_stream_generator.py')
    
    
    
    
    
    for i in range(config['processing'].getint('grid_channel_from'), config['processing'].getint('grid_channel_to') + 1):
        config['channels']['{}'.format(i)] = str(i - config['processing'].getint('grid_channel_from') + 1)
    
    experiment_config = patient_data_path/'experiment_config.ini'
    with open(experiment_config, 'w') as configfile:
        config.write(configfile)
    
    return config

if __name__ == '__main__':
    config_init()