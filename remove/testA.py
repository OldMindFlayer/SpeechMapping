# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 14:01:59 2020

@author: AlexVosk
"""

from pylsl import StreamInlet, resolve_stream
import time

#streams = resolve_stream()
streams = resolve_stream('name', 'EBNeuro_BePLusLTM_192.168.171.81')
print(streams)
time.sleep(1)

stream = streams[0]
ecogInlet = StreamInlet(stream, 2048)
print(stream.name())
time.sleep(1)


a = ecogInlet.pull_sample()
print(a)