# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 14:32:30 2020

@author: dblok
"""
import h5py

path = 'C:/Workspace/SpeechMapping/SpeechMapping/data/ABCDEF/07_03_20/experiment_data/experiment_data.h5'
with h5py.File(path,'r+') as f1:
    keys = f1.keys()
    print(keys)
    for i in range(3):
        print(f1[list(keys)[i]]['raw_data'].shape)