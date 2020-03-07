# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 08:23:22 2020

@author: dblok
"""

from pathlib import WindowsPath
import numpy as np
import h5py
import config


class SavePatientData():
    def __init__(self, fs):
        self.dir_subject = config.config['general']['root_path'] + '/data/'
        self.fs = fs
        
        windows_path = WindowsPath(self.dir_subject)
        if not windows_path.is_dir():
            windows_path.mkdir()
        
        windows_path = windows_path/config.config['patient_info']['patient_name']
        if not windows_path.is_dir():
            windows_path.mkdir()
        
        windows_path = windows_path/config.config['patient_info']['patient_date']
        if not windows_path.is_dir():
            windows_path.mkdir()
        
        if not (windows_path/'results_full').is_dir():
            (windows_path/'results_full').mkdir()
        
        windows_path = windows_path/'experiment_data'
        if not (windows_path).is_dir():
            (windows_path).mkdir()
            
        
        self.groups = ['data_rest', 'data_actions', 'data_objects']
        self.path_h5file = windows_path/"experiment_data.h5"
        if not self.path_h5file.is_file():
            with h5py.File(self.path_h5file, 'a') as file:
                file.create_dataset(self.groups[0] + '/raw_data', (0, 71), maxshape=(None, 71))
                file.create_dataset(self.groups[1] + '/raw_data', (0, 71), maxshape=(None, 71))
                file.create_dataset(self.groups[2] + '/raw_data', (0, 71), maxshape=(None, 71))
                file.create_dataset('fs', data=np.array(self.fs))


    def save_data_rest(self, data):
        self._save_data_buffer(data, 'data_rest')

    def save_data_actions(self, data):
        self._save_data_buffer(data, 'data_actions')
    
    def save_data_objects(self, data):
        self._save_data_buffer(data, 'data_objects')
    

    def _save_data_buffer(self, data, data_type):
        with h5py.File(self.path_h5file, "a") as file:
            keys = file[data_type].keys()
            dataset_name = '{}/raw_data{}'.format(data_type, len(keys))
            file.create_dataset(dataset_name, shape=data.shape, data=data)
            
                    
    def reforge_into_raw_data(self):
        with h5py.File(self.path_h5file, "a") as file:
            for group in self.groups:
                dataset_raw_data = file[group]['raw_data']
                datasets = []
                if len(file[group].keys()) > 1:
                    for i in range(1, len(file[group].keys())):
                        dataset = file[group]['raw_data{}'.format(i)][()]
                        datasets.append(dataset)
                    if datasets:
                        dataset_stacked = np.vstack(datasets)
                        new_length = dataset_raw_data.shape[0] + dataset_stacked.shape[0]
                        dataset_raw_data.resize(new_length, axis = 0)
                        dataset_raw_data[-dataset_stacked.shape[0]:] = dataset_stacked
                    for i in range(1, len(file[group].keys())):
                        del file[group]['raw_data{}'.format(i)]
                    
            
            
            
            
                

if __name__ == '__main__':
    config.init()
    save_data = SavePatientData(2048)
    save_data.reforge_into_raw_data()
    add = 0
    if add:
        a = np.random.random(size=(3,71))
        for i in range(2):
            save_data.save_data_rest(a)
        for i in range(6):
            save_data.save_data_actions(a)

    with h5py.File(save_data.path_h5file, "r") as file:
        keys = file.keys()
        print(keys)
        for key in keys:
            if key != 'fs':
                print(key)
                print(file[key].keys())
                print(key, file[key]['raw_data'].shape)
                for i in range(1, len(file[key].keys())):
                    print(key, file[key]['raw_data{}'.format(i)].shape)
            





