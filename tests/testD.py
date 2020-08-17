# -*- coding: utf-8 -*-
"""
Created on Fri Jul 17 13:15:56 2020

@author: AlexVosk
"""
import numpy as np

ecog_i = np.arange(100)
ind_stim_i = np.zeros(0)
ind_stim_j = np.arange(0,100,20)

indj = np.zeros(0);
print(indj)
for k  in ind_stim_j:
    indj = np.append(indj, np.array(range(k+6,k+12)))
    print(indj)
indi = np.array(range(0,min(ecog_i.shape[0],indj.shape[0])))
print(indi)