# -*- coding: utf-8 -*-
"""
Created on Fri Feb 28 08:23:22 2020

@author: dblok
"""

from pathlib import Path
import numpy as np
import h5py
import config


class SaveExperimentData():
    def __init__(self, config):
        self.config = config
        
        # create Path to experiment_data file       
        self.experiment_data_path = Path(self.config['paths']['experiment_data_path'])
        self.dataset_width = self.config['data_saving'].getint('dataset_width')
        
        # create h5 experiment_data file with empty groups of nonfixed length and group with fs
        self.groups = self.config['data_saving']['group_names'].split(' ')
        if not self.experiment_data_path.is_file():
            with h5py.File(self.experiment_data_path, 'a') as file:
                for group in self.groups:
                    file.create_dataset(group + '/raw_data', (0, self.dataset_width), maxshape=(None, self.dataset_width))
                file.create_dataset('fs', data=np.array(self.config['general'].getint('fs')))

    
    # save chunk of data into new raw_data# dataset
    def save_data_buffer(self, data, data_type):
        with h5py.File(self.experiment_data_path, "a") as file:
            keys = file[data_type].keys()
            dataset_name = '{}/raw_data{}'.format(data_type, len(keys))
            file.create_dataset(dataset_name, shape=data.shape, data=data)
            
    # after saving into file with raw_data# chunks remake into single raw_data
    def reforge_into_raw_data(self):
        with h5py.File(self.experiment_data_path, "a") as file:
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
    save_data = SaveExperimentData(2048)
    save_data.reforge_into_raw_data()
    add = 0
    if add:
        a = np.random.random(size=(3,72))
        for i in range(2):
            save_data.save_data_rest(a)
        for i in range(6):
            save_data.save_data_actions(a)

    with h5py.File(save_data.experiment_data_path, "r") as file:
        keys = file.keys()
        print(keys)
        for key in keys:
            if key != 'fs':
                print(key)
                print(file[key].keys())
                print(key, file[key]['raw_data'].shape)
                for i in range(1, len(file[key].keys())):
                    print(key, file[key]['raw_data{}'.format(i)].shape)
            





