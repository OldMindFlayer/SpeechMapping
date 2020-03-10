# -*- coding: utf-8 -*-
"""
Created on Tue Mar 10 19:06:42 2020

@author: Администратор
"""
from pylsl import StreamInlet, resolve_stream

streams = resolve_stream('type', 'EEG')
print(streams[0].name())
print(streams[0].type())