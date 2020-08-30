# -*- coding: utf-8 -*-
"""
Created on Thu Mar  5 18:04:45 2020

@author: dblok
"""
import h5py
import numpy as np

rec = []
path = 'C:/Workspace/SpeechMappingv0_3/data/ABCDEF/01_01_20/experiment_data/experiment_data.h5'
with h5py.File(path, "r") as file:
    dss = [file['data_rest']['raw_data'], file['data_actions']['raw_data'], file['data_objects']['raw_data']]
    
    rec.append(dss[0][9834:,:68])
    rec.append(dss[1][10000:,:68])
    rec.append(dss[2][10000:,:68])
        
path_rest = 'C:/Workspace/SpeechMappingv0_3/data/Sysoeva/10_10_19/data_rest/experiment_data.h5'
path_actions = 'C:/Workspace/SpeechMappingv0_3/data/Sysoeva/10_10_19/data_actions/experiment_data.h5'
path_objects = 'C:/Workspace/SpeechMappingv0_3/data/Sysoeva/10_10_19/data_objects/experiment_data.h5'




paths2 = [path_rest, path_actions, path_objects]
for i in range(3):
    with h5py.File(paths2[i], "r") as file:
        data = file['protocol1']['raw_data']
        test = data[10000:50000, :68]
        print(np.all(test == rec[i]))
        print(test.shape, rec[i].shape)
        print(test[:3, :3])
        print(rec[i][:3, :3])
