# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 13:43:46 2020

@author: dblok
"""

#import sys; sys.path.append('..')
import pylsl
import random
import time
from threading import Thread
import h5py


class LSL_Generator():
    def __init__(self, stream_time):
        self.channel_count = 68
        self.nominal_srate = 2048
        self.seconnds_per_sample = 1 / self.nominal_srate
        self.stream_time = stream_time
        self.stream_time = 20000
        self.thread = Thread(target=self._stream_debug, args=())
        
    def start(self):
        self.thread.start()

    def _stream(self):
        info = pylsl.stream_info('Debug', 'EEG', self.channel_count, 
                                 self.nominal_srate, pylsl.cf_float32, 'dsffwerwer')
        outlet = pylsl.stream_outlet(info)
        print('DebudStream: Streaming start...')
        
        start_time = time.time()
        current_time = time.time()
        while (time.time() - start_time < self.stream_time):
            if time.time() - current_time > self.seconnds_per_sample:
                current_time = time.time()
                sample = [random.random() for i in range(self.channel_count)]
                outlet.push_sample(sample)
                #time.sleep(0.0002)
            time.sleep(0.0001)
            
        print('DebudStream: Streaming stop...')
        
    def _stream_debug(self):
        info = pylsl.stream_info('Debug', 'EEG', self.channel_count, 
                                 self.nominal_srate, pylsl.cf_float32, 'dsffwerwer')
        outlet = pylsl.stream_outlet(info)
        print('DebudStream: Streaming start...')
        path_rest = 'C:/Workspace/SpeechMapping/SpeechMappingv0_3/data/Sysoeva/10_10_19/data_rest/experiment_data.h5'
        path_actions = 'C:/Workspace/SpeechMapping/SpeechMappingv0_3/data/Sysoeva/10_10_19/data_actions/experiment_data.h5'
        path_objects = 'C:/Workspace/SpeechMappingv0_3/data/Sysoeva/10_10_19/data_objects/experiment_data.h5'
        paths = [path_rest, path_actions, path_objects]
        time.sleep(3)
        for i in range(len(paths)):
            with h5py.File(paths[i], "r") as file:
                data = file['protocol1']['raw_data']
                data_length = data.shape[0]
                index = 0
                start_time = time.time()
                current_time = time.time()
                while (time.time() - start_time < self.stream_time) and index < data_length:
                    if time.time() - current_time > 1/2048:
                        current_time = time.time()
                        sample = data[index, :68]
                        outlet.push_sample(sample)
                        index += 1
                        if index % 100 == 0:
                            print('Index: ', index)
                    time.sleep(0.0001)
        time.sleep(3)      
            
        print('DebudStream: Streaming stop...')    
        
    
            
if __name__ == '__main__':
    stream = LSL_Generator(10000)
    stream.start()

    #print(streams[0].name())
    #print(streams[1].name())
    pass
