# -*- coding: utf-8 -*-
"""
Created on Sat Mar  7 14:32:30 2020

@author: dblok
"""
import h5py
import numpy as np
from scipy.stats import describe
import matplotlib.pyplot as plt

path = 'C:/SpeechMapping/data/Patient9/11_03_20/experiment_data/experiment_data.h5'
with h5py.File(path,'r+') as f1:
    keys = f1.keys()
    print(keys)
    for i in range(3):
        dataset = f1[list(keys)[i]]['raw_data'][()]
        print(list(keys)[i], dataset.shape)
        #timestaps = dataset[1000:9000, 69]
        #sorted_indecies = np.argsort(dataset[:,69])
        #dataset_new = dataset[sorted_indecies]
        #timesteps_new = dataset_new[1000:9000, 69]
        #forward_diff_new = np.diff(timesteps_new)
        #forward_diff = np.diff(timestaps)
        #print(forward_diff_new)
        #print(describe(forward_diff_new))
        #ab = np.arange(0,8000)
        #print(np.sum(np.abs(forward_diff_new - 0.000488) > 0.00001))
        #print(np.sum(np.abs(forward_diff - 0.000488) > 0.0001))
        
        #a = np.arange(0,7999)
        #plt.figure()
        #plt.plot(dataset[:2048*8, :32])
        #plt.imshow(dataset[:2048*8,:64].T)
        #plt.show()
        #print(dataset[68,:])

#path2 = 'C:/Workspace/SpeechMapping/Sysoeva/10_10_19/data_rest/experiment_data.h5'
#with h5py.File(path2,'r+') as f1:
#    dataset = f1['protocol1']['raw_data']
#    print(dataset.shape)
#    print(dataset[:,68])












