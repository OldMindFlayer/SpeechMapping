# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:39:59 2020

@author: dblokv@gmail.com
"""

import configparser
from pathlib import Path


config = configparser.ConfigParser()
config['display'] = {'resting_time': '240',
      'pictures_action_time': '240',
      'pictures_object_time': '240',
      'single_picture_time': '4',
      'time_between_pictures': '0.5',
      'time_other_pictures': '2',
      'number_of_pictures_action': '5',
      'number_of_pictures_object': '5',
      'sound_between_pictures': 'false',
      'shuffle_pictures': 'true',
      'pictures_rotated':'true',      
      'WINDOW_X': '800',
      'WINDOW_Y': '1280'}

config['patient_info'] = {'patient_name': 'Patient14',
      'patient_date_autogeneration': 'true',
      'patient_date': '01_01_20'}

config['general'] = {'debug_mode': 'false',
      'debug_time': '60',
      'lsl_outlet_random': 'true',
      'root_path_autogeneration': 'true',
      'root_path': 'C:/SpeechMapping/',
      'save_through_buffer': 'true',
      'buffer_size_sec': '3',
      'fs': '2048',
      'lsl_stream_name': 'EBNeuro_BePLusLTM_192.168.171.83'}

config['processing'] = {'grid_size_X': '4',
      'grid_size_Y': '8',
      'grid_channel_min': '1',
      'grid_channel_max': '32'}

path = Path('write_config.py').resolve().parents[1]/'spmap'/'config.ini'
with open(path, 'w') as configfile:
    config.write(configfile)