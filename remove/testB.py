# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 16:26:56 2020

@author: AlexVosk
"""

import h5py
import matplotlib.pyplot as plt
import numpy as np

path = r'C:\SpeechMappingProject\SpeechMappingData\200809_MutalievMM\131837_experiment\experiment_data.h5'

with h5py.File(path,'r+') as file:
    # X is first n_channels (columns) of amplifier data
    a1 = file['data_rest']['raw_data'][()]
    a2 = file['data_objects']['raw_data'][()]
    a3 = file['data_actions']['raw_data'][()]
    b1 = file['data_rest']['picture_indices'][()]
    b2 = file['data_objects']['picture_indices'][()]
    b3 = file['data_actions']['picture_indices'][()]
    
print(a1.shape)
print(a2.shape)
print(a3.shape)
print(b1.shape)
print(b2.shape)
print(b3.shape)
print(b1)
print(b2)
print(b3)
