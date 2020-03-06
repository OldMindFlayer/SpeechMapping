# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:39:59 2020

@author: dblok
"""

import configparser



config = configparser.ConfigParser()
config['display'] = {'resting_time': '5',
      'pictures_action_time': '5',
      'pictures_object_time': '5',
      'single_picture_time': '3',
      'time_between_pictures': '0.5',
      'time_other_pictures': '2',
      'number_of_pictures_action': '5',
      'number_of_pictures_object': '5',
      'sound_between_pictures': 'false',
      'shuffle_pictures': 'false',}
config['patient_info'] = {'patient_name': 'ABCDEF',
      'patient_date': '01_01_20'}
config['general'] = {'debug_mode': 'true',
      'lsl_outlet_random': 'true',
      'general_path': 'C:/Workspace/SpeechMappingv0_3/',
      'save_through_buffer': 'true',
      'buffer_size_sec': '3',
      'fs': '2048'}

with open('config.ini', 'w') as configfile:
    config.write(configfile)
