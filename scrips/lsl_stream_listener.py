# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 13:31:28 2020

@author: dblok
"""

from pylsl import StreamInlet, resolve_stream
import numpy as np
import time
import h5py
from queue import Queue
from lsl_generator_debug import DebudStream
from data_saving import SavePatientData
import config


class LSL_Listener():
    def __init__(self, maxbuffer_size, q_from_display_to_listener = None):
        self.maxbuffer_size = maxbuffer_size
        self.saver = None
        
        self.q_from_display_to_listener = q_from_display_to_listener
        self.lsl_stream_listener_state = False
        self.patient_state = 0
        self.picture_shown = False
        
        if config.config['general'].getboolean('save_through_buffer'):
            self.buffer_size = int(config.config['general'].getfloat('buffer_size_sec')*config.config['general'].getint('fs'))
            self.buffer = []
            self.buffer_length = 0
        else:
            self.memory_none = []
            self.memory_rest = []
            self.memory_actions = []
            self.memory_objects = []
            self.memory = [self.memory_none, self.memory_rest, self.memory_actions, self.memory_objects]
        
        if config.config['general'].getboolean('debug_mode'):
            print('LSL_Listener: Debug mode')
            streams = resolve_stream('name', 'Debug')
            print('LSL_Listener: number of streams: ', len(streams), '  Stream: ', streams[0])
            self.ecogInlet = StreamInlet(streams[0], self.maxbuffer_size)
        else:
            streams = resolve_stream('type', 'EEG')
            self.ecogInlet = StreamInlet(streams[0], self.maxbuffer_size)
        print("LSL_Listener: Stream resolved")


    def record_using_buffer(self):
        print('LSL_Listener: recording with buffer')
        current_patient_state = self.patient_state
        self.saver = SavePatientData(2048)
        self._resolve_q()

        while self.lsl_stream_listener_state:
            self._resolve_q()
            sample, timestamp = self.ecogInlet.pull_sample(timeout=0.0)
            sample = np.asarray(sample)
            
            if (self.patient_state != current_patient_state) and self.buffer_length > 0:
                self._save_buffer(current_patient_state)
                current_patient_state = self.patient_state
            if timestamp:
                sample = np.reshape(sample, (1, 68))
                timestamp = np.array([[timestamp]])
                picture_type_array = np.array([[self.patient_state]])
                if self.picture_shown:
                    picture_shown = np.array([[1]])
                    self.picture_shown = False
                else:
                    picture_shown = np.array([[0]])        
                big_sample = np.concatenate((sample, timestamp, picture_type_array, picture_shown), axis=1)
                
                self.buffer.append(big_sample)
                self.buffer_length += big_sample.shape[0]
                if self.buffer_length >= self.buffer_size:
                    self._save_buffer(self.patient_state)
        if self.buffer_length > 0:
            self._save_buffer(self.patient_state)

        print('LSL_Listener: Stop listening...')
        t1 = time.time()
        self.saver.reforge_into_raw_data()
        t2 = time.time()
        print('Time to save: ', t2-t1)
   
     
    def record_using_memory(self):
        print('LSL_Listener: recording with memory')
        self.saver = SavePatientData(2048)
        self._resolve_q()

        while self.lsl_stream_listener_state:
            self._resolve_q()
            sample, timestamp = self.ecogInlet.pull_sample(timeout=0.0)
            if timestamp:
                sample = np.reshape(sample, (1, 68))
                timestamp = np.array([[timestamp]])
                picture_type_array = np.array([[self.patient_state]])
                if self.picture_shown:
                    picture_shown = np.array([[1]])
                    self.picture_shown = False
                else:
                    picture_shown = np.array([[0]])        
                big_sample = np.concatenate((sample, timestamp, picture_type_array, picture_shown), axis=1)
                #print(big_sample.shape)
                self.memory[self.patient_state].append(big_sample)
        self._save_memory()
        
        print('LSL_Listener: Stop listening...')
        t1 = time.time()
        self.saver.reforge_into_raw_data()
        t2 = time.time()
        print('Saving time: ', t2-t1)


    def _save_buffer(self, patient_state):
        npbuffer = np.vstack(self.buffer)
        if (patient_state == 0):
            pass
        elif (patient_state == 1):
            self.saver.save_data_rest(npbuffer)
        elif (patient_state == 2):
            self.saver.save_data_actions(npbuffer)
        elif (patient_state == 3):
            self.saver.save_data_objects(npbuffer)
        else:
            print('LSL_Listener: wrong patient_state value')
        self.buffer = []
        self.buffer_length = 0


    def _save_memory(self):
        for i in range(1,len(self.memory)):
            if len(self.memory[i]) > 0:
                npmemory = np.vstack(self.memory[i])
                if (i == 1):
                    self.saver.save_data_rest(npmemory)
                elif (i == 2):
                    self.saver.save_data_actions(npmemory)
                elif (i == 3):
                    self.saver.save_data_objects(npmemory)
                self.memory[i] = []
                
                
    def _resolve_q(self):
        while not self.q_from_display_to_listener.empty():
            key, value = self.q_from_display_to_listener.get()
            if key == 'patient_state':
                self.patient_state = value
            elif key == 'lsl_stream_listener_state':
                self.lsl_stream_listener_state = value
            elif key == 'picture_shown':
                self.picture_shown = value
            else:
                print('LSL_Listener: wrong key in queue')





if __name__ == '__main__':
    config.init()
    debug_stream = DebudStream(10000, 68, 2048)
    debug_stream.start()
    time.sleep(1)
    q = Queue()
    lsl_listener = LSL_Listener(2048, q)
    lsl_listener.record_using_buffer()
    
    path = lsl_listener.saver.path_h5file
    with h5py.File(path, "r") as file:
        ds1 = file['data_rest']['raw_data'].shape
        ds2 = file['data_actions']['raw_data'].shape
        ds3 = file['data_objects']['raw_data'].shape
        print(ds1)
    
    








