# -*- coding: utf-8 -*-
"""
Created on Fri Mar  6 14:41:45 2020

@author: dblok
"""
from pathlib import Path

s = Path('test2.py').resolve().parents[1]
print(s)