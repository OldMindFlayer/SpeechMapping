# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 16:26:56 2020

@author: AlexVosk
"""

import h5py

path = r'C:\SpeechMappingProject\SpeechMappingData\200709_Isaeva_Zarema\161907_experiment\experiment_data.h5'

with h5py.File(path,'r+') as file:
    # X is first n_channels (columns) of amplifier data
    rest = file['data_rest']['raw_data'][()]
    # Y is colummns of pn data corresponding to finger movements
    print(rest.shape[0]/60)