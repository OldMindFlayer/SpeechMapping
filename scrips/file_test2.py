# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 14:41:45 2020

@author: dblok
"""

import config

config.init()
path_to_experiment_data = config.config['general']['general_path'] + 'data/' + \
    config.config['patient_info']['patient_name'] + '/' + config.config['patient_info']['patient_date'] + '/' + \
    'experiment_data/experiment_data.h5'
print(path_to_experiment_data)