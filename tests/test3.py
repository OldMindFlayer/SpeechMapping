# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 14:32:30 2020

@author: dblok
"""
import h5py
import numpy as np

path = 'C:/Workspace/SpeechMapping/SpeechMapping/data/Patient1/10_03_20/experiment_data/experiment_data.h5'
with h5py.File(path,'r+') as f1:
    keys = f1.keys()
    print(keys)
    for i in range(3):
        dataset = f1[list(keys)[i]]['raw_data']
        print(list(keys)[i], dataset.shape)
        for i in range(dataset.shape[0]//2048):
            delta = dataset[(i+1)*2048, 69] - dataset[(i)*2048, 69]
            error = abs(1 - delta)*2048
            print(error)