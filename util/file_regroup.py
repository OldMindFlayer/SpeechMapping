# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 16:54:16 2020

@author: AlexVosk
"""

import h5py
from pathlib import Path
import numpy as np

path = Path(r'C:\SpeechMappingProject\SpeechMappingData\experiment_data_part2.h5')
path_new = Path(r'C:\SpeechMappingProject\SpeechMappingData\test_file_part2.h5')

groups = ['data_rest', 'data_objects', 'data_actions']

for group in groups:
    with h5py.File(path,'r+') as file:
        raw_data = np.array(file[group]['raw_data'])
        srate = file['fs'][()]
    new_raw_data = np.zeros((raw_data.shape[0], raw_data.shape[1]+1))
    new_raw_data[:, :-1] = raw_data
    new_raw_data[:, -1] = raw_data[:, -1]
    new_raw_data[:, -2] = np.zeros(new_raw_data.shape[0])
    #print(new_raw_data[0, :])
    n_picture = int(sum(new_raw_data[:, -1]))
    new_index = np.zeros((n_picture, 2))
    ind_stim = np.argwhere(new_raw_data[:, -1]==1)
    new_index[:, 0] = ind_stim[:, 0]
    new_index[:, 1] = ind_stim[:, 0] + srate*3

        
    with h5py.File(path_new, 'a') as file:
        file[group + '/raw_data'] = new_raw_data
        file[group + '/picture_indices'] = new_index

with h5py.File(path_new, 'a') as file:
    file.create_dataset('fs', data=np.array(srate))