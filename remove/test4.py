# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 17:32:42 2020

@author: dblok
"""
import h5py
import numpy as np

path_original_rest = 'C:/Workspace/SpeechMapping/Sysoeva/10_10_19/data_rest/experiment_data.h5'
path_original_actions = 'C:/Workspace/SpeechMapping/Sysoeva/10_10_19/data_actions/experiment_data.h5'
path_original_objects = 'C:/Workspace/SpeechMapping/Sysoeva/10_10_19/data_objects/experiment_data.h5'


path = 'C:/Workspace/SpeechMapping/SpeechMapping/data/Sysoeva/07_03_20/experiment_data/experiment_data.h5'
with h5py.File(path,'r+') as f:
    data_rest = np.array(f['data_rest']['raw_data'])
    data_actions = np.array(f['data_actions']['raw_data'])
    data_objects = np.array(f['data_objects']['raw_data'])
    
with h5py.File(path_original_rest,'r+') as f:
    data_original_rest = np.array(f['protocol1']['raw_data'])
    
with h5py.File(path_original_actions,'r+') as f:
    data_original_actions = np.array(f['protocol1']['raw_data'])
    
with h5py.File(path_original_objects,'r+') as f:
    data_original_objects = np.array(f['protocol1']['raw_data'])

print('Shapes         : ', data_rest.shape, data_actions.shape, data_objects.shape)
print('Shapes original: ', data_original_rest.shape, data_original_actions.shape, data_original_objects.shape)

a1 = np.where((data_original_rest[:,:64] == data_rest[0,:64]).all(axis=1))
print(a1)
print(data_original_rest[:3,:3])
print(data_rest[:3,:3])

a2 = np.where((data_original_actions[:,:64] == data_actions[0,:64]).all(axis=1))
print(a2)
print(data_original_actions[9997:10000,:3])
print(data_actions[9997:10000,:3])

a3 = np.where((data_original_objects[:,:64] == data_objects[0,:64]).all(axis=1))
print(a2)
print(data_original_objects[9997:10000,:3])
print(data_objects[9997:10000,:3])

print(np.all(data_original_rest[1:100000,:64] == data_rest[:,:64]))
print(np.all(data_original_actions[:100000,:64] == data_actions[:,:64]))
print(np.all(data_original_objects[:100000,:64] == data_objects[:,:64]))







