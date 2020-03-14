# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 08:23:22 2020

@author: dblok
"""

from pathlib import Path
import numpy as np
import h5py
import config


class SavePatientData():
    def __init__(self, fs, patient_experiment_data_path):
        
        # create Path to experiment_data file       
        self.experiment_data_path = Path(patient_experiment_data_path)
        self.path_h5file = self.experiment_data_path/"experiment_data.h5"
        
        # create h5 experiment_data file with empty groups of nonfixed length and group with fs
        self.groups = ['data_rest', 'data_actions', 'data_objects']
        if not self.path_h5file.is_file():
            with h5py.File(self.path_h5file, 'a') as file:
                file.create_dataset(self.groups[0] + '/raw_data', (0, 72), maxshape=(None, 72))
                file.create_dataset(self.groups[1] + '/raw_data', (0, 72), maxshape=(None, 72))
                file.create_dataset(self.groups[2] + '/raw_data', (0, 72), maxshape=(None, 72))
                file.create_dataset('fs', data=np.array(fs))

    # public methods for saving data
    def save_data_rest(self, data):
        self._save_data_buffer(data, 'data_rest')

    def save_data_actions(self, data):
        self._save_data_buffer(data, 'data_actions')
    
    def save_data_objects(self, data):
        self._save_data_buffer(data, 'data_objects')
    
    # save chunk of data into new raw_data# dataset
    def _save_data_buffer(self, data, data_type):
        with h5py.File(self.path_h5file, "a") as file:
            keys = file[data_type].keys()
            dataset_name = '{}/raw_data{}'.format(data_type, len(keys))
            file.create_dataset(dataset_name, shape=data.shape, data=data)
            
    # after saving into file with raw_data# chunks remake into single raw_data
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
        a = np.random.random(size=(3,72))
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
            





