# -*- coding: utf-8 -*-
"""
Created on Thu Mar 12 12:09:01 2020

@author: Администратор
"""
import matplotlib.pyplot as plt
import h5py
import numpy as np
from scipy.io.wavfile import write


path = 'C:/SpeechMapping/data/SeleznevaFull6/12_03_20/experiment_data/experiment_data.h5'
with h5py.File(path,'r+') as f1:
    keys = f1.keys()
    print(list(keys))
    print(240 * 2048)
    for i in range(3):
        print(f1[list(keys)[i]]['raw_data'].shape)
        print(list(keys)[i])
        #dataset = f1[list(keys)[i]]['raw_data'][()]
        #print(dataset.shape)
        #plt.figure()
        #plt.plot(dataset[:, 64])
        #plt.imshow(dataset[:2048*8,:64].T)
        #plt.show()
        

        #data = dataset[:, 64]
        #print(data - np.mean(data))
        #scaled = np.int16(data/np.max(np.abs(data)) * 32767)
        #print(scaled)
        #write('test{}.wav'.format(i), 2048, scaled)