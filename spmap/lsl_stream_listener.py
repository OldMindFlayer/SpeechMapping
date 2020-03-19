# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 13:31:28 2020

@author: dblok
"""

from pylsl import StreamInlet, resolve_stream
import numpy as np
import time
from data_saving import SaveExperimentData


class LSL_Listener():
    def __init__(self, config, maxbuffer_size, q_from_display_to_listener = None):
        
        # initialize basic configuration
        # 0 - none (not recording)
        # 1 - rest
        # 2 - actions
        # 3 - objects
        self.config = config
        self.maxbuffer_size = maxbuffer_size
        self.saver = SaveExperimentData(config)
        self.q_from_display_to_listener = q_from_display_to_listener
        self.lsl_stream_listener_state = False
        self.patient_state = 0
        self.picture_shown = False
        
        self.groups = self.config['data_saving']['group_names'].split(' ')
        
        # initialize configuration based on saving method (though buffer or without it)
        if self.config['data_saving'].getboolean('save_through_buffer'):
            self.buffer_size = int(self.config['data_saving'].getfloat('buffer_size_sec')*self.config['general'].getint('fs'))
            self.buffer = []
            self.buffer_length = 0
        else:
            self.memory_none = []
            self.memory_rest = []
            self.memory_actions = []
            self.memory_objects = []
            self.memory = [self.memory_none, self.memory_rest, self.memory_actions, self.memory_objects]
        
        # resolve lsl stream
        if self.config['general'].getboolean('debug_mode'):
            print('LSL_Listener: Debug mode')
            streams = resolve_stream('name', 'Debug')
            print('LSL_Listener: number of streams: ', len(streams), '  Stream: ', streams[0])
            self.ecogInlet = StreamInlet(streams[0], self.maxbuffer_size)
            print("LSL_Listener: Stream resolved, {}".format(str(streams[0])))
        else:
            streams = resolve_stream('name', self.config['general']['lsl_stream_name'])
            self.ecogInlet = StreamInlet(streams[0], self.maxbuffer_size)
            print("LSL_Listener: Stream resolved, {}".format(self.config['general']['lsl_stream_name']))
        
        # check, is stram working
        sample, timestamp = self.ecogInlet.pull_sample(timeout=0.0)
        if not timestamp:
            print('LSL Listener: Empty timestap from stream, check the stream generator')



    def record_using_buffer(self):
        print('LSL_Listener: recording with buffer')
        
        # pre-loop preparation
        current_patient_state = self.patient_state
        self._resolve_q()

        # active while command from display say so
        while self.lsl_stream_listener_state:
            self._resolve_q()
            
            # take single sample from stream
            sample, timestamp = self.ecogInlet.pull_sample(timeout=0.0)
            sample = np.asarray(sample)
            
            # if patient_state changes - save buffer before continue with new data
            if (self.patient_state != current_patient_state) and self.buffer_length > 0:
                self._save_buffer(current_patient_state)
                current_patient_state = self.patient_state
                
            # if timestamp exists, concatenate sample of stream data with patient data and put into buffer
            if timestamp:
                sample = np.reshape(sample, (1, 69))
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
                # if buffer is too big, save it
                if self.buffer_length >= self.buffer_size:
                    self._save_buffer(self.patient_state)
        
        # if there is any data still in the buffer, save it before the end
        if self.buffer_length > 0:
            self._save_buffer(self.patient_state)
        print('LSL_Listener: Stop listening...')
        
        # how long it takes to reforge h5 file
        t1 = time.time()
        self.saver.reforge_into_raw_data()
        t2 = time.time()
        print('Time to save: ', t2-t1)
   
    # not used
    def record_using_memory(self):
        print('LSL_Listener: recording with memory')
        self._resolve_q()

        while self.lsl_stream_listener_state:
            self._resolve_q()
            sample, timestamp = self.ecogInlet.pull_sample(timeout=0.0)
            if timestamp:
                sample = np.reshape(sample, (1, 69))
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

    # save data buffer based on current patient state
    def _save_buffer(self, patient_state):
        npbuffer = np.vstack(self.buffer)
        if patient_state == 0:
            pass
        elif patient_state < 0 or patient_state > 3:
            print('LSL_Listener: wrong patient_state value')
        else:
            self.saver.save_data_buffer(npbuffer, self.groups[patient_state - 1])
        self.buffer = []
        self.buffer_length = 0

    # not used
    def _save_memory(self):
        for i in range(1,len(self.memory)):
            if len(self.memory[i]) > 0:
                npmemory = np.vstack(self.memory[i])
                self.saver.save_data_buffer(npmemory, self.groups[i - 1])
                self.memory[i] = []
                

    # resolve commands from Display object to navigate recording of data
    def _resolve_q(self):
        while not self.q_from_display_to_listener.empty():
            key, value = self.q_from_display_to_listener.get()
            if self.config['general'].getboolean('debug_mode'):
                print(key, value)
            if key == 'patient_state':
                self.patient_state = value
            elif key == 'lsl_stream_listener_state':
                self.lsl_stream_listener_state = value
            elif key == 'picture_shown':
                self.picture_shown = value
            else:
                print('LSL_Listener: wrong key in queue')





if __name__ == '__main__':
    pass
    #config.init()
    #debug_stream = LSL_Generator(10000, 68, 2048)
    #debug_stream.start()
    #time.sleep(1)
    #q = Queue()
    #lsl_listener = LSL_Listener(2048, q)
    #lsl_listener.record_using_buffer()
    
    #path = lsl_listener.saver.path_h5file
    #with h5py.File(path, "r") as file:
    #    ds1 = file['data_rest']['raw_data'].shape
    #    ds2 = file['data_actions']['raw_data'].shape
    #    ds3 = file['data_objects']['raw_data'].shape
    #    print(ds1)
    
    








