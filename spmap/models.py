# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 14:05:59 2020

@author: AlexVosk
"""

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy import stats


def linregress(xi, xj, model_params):
    x = np.vstack((xi,xj))
    y = np.vstack((np.zeros((xi.shape[0],1)), np.ones((xj.shape[0],1))))
    scaler = MinMaxScaler([-1, 1])
    scaler.fit(x)
    x = scaler.transform(x)    
    slope, intercept, r_value_1, p_value, std_err = stats.linregress(x[:,0], y[:,0])
    r2 = r_value_1**2 if r_value_1 > 0 else 0;
    return r2
