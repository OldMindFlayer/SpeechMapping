# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 14:05:59 2020

@author: AlexVosk
"""

import numpy as np
from sklearn.preprocessing import MinMaxScaler
from scipy import stats
from sklearn.linear_model import LogisticRegression
from statsmodels.discrete.discrete_model import Logit
import statsmodels.api as sm


def get_model(name):
    if name == 'linregress':
        return linregress
    elif name == 'logregress':
        return logregress


def linregress(xi, xj, *args, **kwargs):
    x = np.vstack((xi,xj))
    y = np.vstack((np.zeros((xi.shape[0],1)), np.ones((xj.shape[0],1))))
    scaler = MinMaxScaler([-1, 1])
    scaler.fit(x)
    x = scaler.transform(x)    
    slope, intercept, r_value_1, p_value, std_err = stats.linregress(x[:,0], y[:,0])
    r2 = r_value_1**2 if r_value_1 > 0 else 0;
    return r2

def logregress(xi, xj, *args, **kwargs):
    x = np.vstack((xi,xj))[::3]
    y = np.vstack((np.zeros((xi.shape[0],1)), np.ones((xj.shape[0],1))))[::3]
    scaler = MinMaxScaler([-1, 1])
    scaler.fit(x)
    x = scaler.transform(x)    
    #clf = LogisticRegression(random_state=0).fit(x, y[:, 0])
    model = Logit(y, x)
    res = model.fit()
    #print(res.prsquared)
    return res.prsquared
    
def markov(xi, xj, *args, **kwargs):
    x = np.vstack((xi,xj))
    y = np.vstack((np.zeros((xi.shape[0],1)), np.ones((xj.shape[0],1))))
    scaler = MinMaxScaler([-1, 1])
    scaler.fit(x)
    x = scaler.transform(x)
    print(x)
    #clf = LogisticRegression(random_state=0).fit(x, y[:, 0])
    model = sm.tsa.MarkovRegression(x[:, 0], k_regimes=2)
    res = model.fit()
    print(res.summary())
    #return res.prsquared
    

if __name__ == '__main__':
    xi, xj = np.array([0, 1, 1, 0, 1, 1, 0, 1, 1]).reshape((9, 1)), np.array([0, 1, 1, 0, 1, 1, 0, 1, 1]).reshape((9, 1))
    s = markov(xi, xj)
