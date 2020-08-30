# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 15:28:10 2020

@author: Администратор
"""

import numpy as np


#s = np.arange(1,33)
s = np.arange(7,39)
s = (s.reshape(4, 8)).T[::-1,:]
print(s)