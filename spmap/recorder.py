# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 13:31:28 2020

@author: dblok
"""

from pylsl import StreamInlet, resolve_stream
import numpy as np
import time
from queue import Queue
#from data_saving import SaveExperimentData
from progress.bar import Bar
from pathlib import Path
import h5py


class Recorder():
    def __init__(self, config, q_from_display_to_recorder = None):
        
        # initialize basic configuration
        self.config = config
        self.q_from_display_to_recorder = q_from_display_to_recorder
        
        # variables, changed by commands form q
        
        # inlet_state:
        # 0 - recording disabled
        # 1 - recording enabled
        self.inlet_state = 0
        
        # patient states:
        # -1 - none (not recording)
        # 0 - rest
        # 1 - objects
        # 2 - actions
        self.patient_state = 0
        
        # picture state:
        # 0 - none
        # 1 - start
        # 2 - stop
        self.picture_state = 0
        
        self.pause = 0
        #self.patient_state_paused = -1
        
        # initialize memort variables
        self.memory = [[], [], []]
        self.picture_indices = [[], [], []]
        
        # 
        self.picture_pause = 0
        self.picture_end = 0
        self.index_picture_start = (-1, -1)
        self.index_picture_stop = (-1, -1)
        self.index_pause = (-1, -1)        
        
        # resolve lsl stream
        stream_name = self.config['recorder']['lsl_stream_name']
        #stream_name = "Debug"
        streams = resolve_stream('name', stream_name)
        self._printm('Resolving stream \'{}\', {} streams found'.format(stream_name, len(streams)))
        self.inlet = StreamInlet(streams[0], 2048)
        self._printm('Stream resolved')

    



    def record(self):
        self._printm('Start recording, if \'Recording...\' progress bar is not filling, check lsl input stream')
        
        self._resolve_q()
        
        channel_sample = 69
        channel_timestemp = 70
        channel_patient_state = 71
        channel_picture_pause = 72
        channel_picture_state = 73
        dataset_width = self.config['recorder'].getint('dataset_width')
        
        with Bar('Recording...', max=1000) as bar:
            while self.inlet_state:
                self._resolve_q()
                sample, timestamp = self.inlet.pull_sample()
                if bar.index < 999:
                    bar.next()
                elif bar.index == 999:
                    bar.next()
                    bar.finish()
                                
                # if patient state is 0 - skip
                if self.patient_state == -1:
                    continue
                elif self.pause:
                    self.picture_pause = 1
                    continue
                
                # if timestamp exists, concatenate sample with previous data
                if timestamp:
                    sample_index = len(self.memory[self.patient_state])
                    
                    big_sample = np.zeros(dataset_width)
                    # add ecog data
                    big_sample[0:channel_sample] = np.asarray(sample)
                    # add timestemp
                    big_sample[channel_timestemp-1] = timestamp
                    # add patient_state
                    big_sample[channel_patient_state-1] = self.patient_state
                    # add picture_pause
                    big_sample[channel_picture_pause-1] = self.picture_pause
                    # add picture_state
                    big_sample[channel_picture_state-1] = self.picture_state
                    # put big_sample into the memory
                    self.memory[self.patient_state].append(big_sample)
                    
                    if self.picture_pause:
                        self.index_pause = (sample_index - 1, self.patient_state)
                        self.picture_pause = 0
                    if self.picture_state == 1:
                        self.index_picture_start = (sample_index, self.patient_state)
                    elif self.picture_state == 2:
                        self.index_picture_stop = (sample_index, self.patient_state)
                        if self._good_picture():
                            self.picture_indices[self.patient_state].append((self.index_picture_start[0], self.index_picture_stop[0]))
                    self.picture_state = 0     
                        
        self._printm('Stop recording')
        t = time.time()
        self._save()
        self._printm('Data saved: {}s:'.format(time.time()-t))


    def _good_picture(self):
        current_state = self.patient_state == self.index_picture_stop[1]
        same_patient_state = self.index_picture_start[1] == self.index_picture_stop[1]
        pause_not_inside_picture = not (self.index_picture_start[1] == self.index_pause[1] and \
                                self.index_picture_start[0] <= self.index_pause[0])
        return current_state and same_patient_state and pause_not_inside_picture


    def _save(self):
        experiment_data_path = Path(self.config['paths']['experiment_data_path'])
        dataset_width = self.config['recorder'].getint('dataset_width')
        groups = self.config['recorder']['group_names'].split(' ')
        with h5py.File(experiment_data_path, 'a') as file:
            for i in range(len(self.memory)):
                if len(self.memory[i]) > 0:
                    stacked_data = np.vstack(self.memory[i])
                    if len(self.picture_indices[i]) > 0:
                        stacked_indices = np.vstack(self.picture_indices[i])
                    elif i == 0:
                        stacked_indices = np.array([0, stacked_data.shape[0]-1]).reshape((1,2))
                    else:
                        stacked_indices = np.array(()).reshape((0,2))
                    file[groups[i]+'/raw_data'] = stacked_data
                    file[groups[i]+'/picture_indices'] = stacked_indices
                    self.memory[i] = []
                    self.picture_indices[i] = []
                    self._printm('Saved {}, {}, {} pictures'.format(groups[i], stacked_data.shape, stacked_indices.shape[0]))
                else:
                    empty_shape = (0, dataset_width)
                    file.create_dataset(groups[i]+'/raw_data', empty_shape)
                    file.create_dataset(groups[i]+'/picture_indices', (0, 2))
                    self._printm('Saved {}, {}'.format(groups[i], empty_shape))
            file.create_dataset('fs', data=np.array(self.config['recorder'].getint('fs')))
            

    # resolve commands from Display object to navigate recording of data
    def _resolve_q(self):
        while not self.q_from_display_to_recorder.empty():
            key, value = self.q_from_display_to_recorder.get()
            #if self.config['general'].getboolean('debug_mode'):
            #    self._printm('key: {}, value: {}'.format(key, value))
            if key == 'inlet_state':
                self.inlet_state = value
            elif key == 'patient_state':
                self.patient_state = value
            elif key == 'picture_state':
                self.picture_state = value
            elif key == 'pause':
                self.pause = value
            else:
                self._printm('wrong key in queue: {}'.format(key))


    def _printm(self, message):
        print('{} {}: '.format(time.strftime('%H:%M:%S'), type(self).__name__) + message)


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
    
    








