# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:39:59 2020

@author: dblokv@gmail.com
"""

import configparser
from pathlib import Path


config = configparser.ConfigParser()
config['display'] = {'resting_time': '15',
      'pictures_action_time': '15',
      'pictures_object_time': '15',
      'single_picture_time': '3',
      'time_between_pictures': '0.5',
      'time_other_pictures': '2',
      'number_of_pictures_action': '5',
      'number_of_pictures_object': '5',
      'sound_between_pictures': 'false',
      'shuffle_pictures': 'false',
      'pictures_rotated':'true',      
      'WINDOW_X': '800',
      'WINDOW_Y': '1280'}

config['patient_info'] = {'patient_name': 'ABC',
      'patient_date_autogeneration': 'true',
      'patient_date': '01_01_20'}

config['general'] = {'debug_mode': 'true',
      'debug_time': '60',
      'lsl_outlet_random': 'true',
      'root_path_autogeneration': 'true',
      'root_path': 'C:/SpeechMapping/',
      'save_through_buffer': 'true',
      'buffer_size_sec': '3',
      'fs': '2048',
      'lsl_stream_name': 'EBNeuro_BePLusLTM_192.168.171.83'}

path = Path('write_config.py').resolve().parents[1]/'spmap'/'config.ini'
with open(path, 'w') as configfile:
    config.write(configfile)