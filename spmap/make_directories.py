# -*- coding: utf-8 -*-
"""
Created on Sat Mar 14 07:50:53 2020

@author: dblok
"""

from pathlib import Path
from os import makedirs
from config import config_init

def make_directories(config):
    
    # get parts of paths from config file
    root_path = config['general']['root_path']
    patient_name = config['patient_info']['patient_name']
    patient_date = config['patient_info']['patient_date']
    patient_time = config['patient_info']['patient_time']
    
    # create Path objects for 'experiment_data' and 'results' directories
    root_path_parent = Path(root_path).parent
    data_path = root_path_parent/'SpeechMappingData'/patient_name/patient_date/('experiment_'+patient_time)
    experiment_data_path = data_path/'experiment_data'
    results_path = data_path/'results'
    
    # create 'experiment_data' and 'results' directories
    makedirs(experiment_data_path, exist_ok=True)
    makedirs(results_path, exist_ok=True)
     
    return str(data_path), str(experiment_data_path), str(results_path)








if __name__ == '__main__':
    make_directories(config_init())