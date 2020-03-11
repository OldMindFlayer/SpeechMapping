# -*- coding: utf-8 -*-
"""
Created on Wed Mar 11 14:50:00 2020

@author: Администратор
"""
from queue import Queue
from display import Display
import config

config.init()
patient_display = Display(Queue())
patient_display.start()

