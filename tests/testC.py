# -*- coding: utf-8 -*-
"""
Created on Sun Jul 12 12:11:36 2020

@author: AlexVosk
"""


from time import sleep
from progress.bar import Bar

with Bar('Processing...', max=2048*10) as bar:
    while True:
        sleep(0.0)
        bar.next()
        if bar.index == 2048*10:
            bar.index = 0