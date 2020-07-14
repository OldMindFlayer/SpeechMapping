# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 16:26:56 2020

@author: AlexVosk
"""

import h5py
import matplotlib.pyplot as plt
import numpy as np

path = r'C:\SpeechMappingProject\SpeechMappingData\200712_Test36\152502_experiment\experiment_data.h5'

with h5py.File(path,'r+') as file:
    # X is first n_channels (columns) of amplifier data
    a1 = file['data_rest']['raw_data'][()]
    a2 = file['data_objects']['raw_data'][()]
    a3 = file['data_actions']['raw_data'][()]
    
    # Y is colummns of pn data corresponding to finger movements
    print((sum(a3[:,-1])))
    