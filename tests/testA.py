# -*- coding: utf-8 -*-
"""
Created on Thu Jul  9 14:01:59 2020

@author: AlexVosk
"""

from pylsl import StreamInlet, resolve_stream
import time

streams = resolve_stream()
print(streams)
time.sleep(1)


ecogInlet = StreamInlet(streams[0], 2048)
print(streams[0].name())
time.sleep(1)


a = ecogInlet.pull_chunk(0.0)
print(a)