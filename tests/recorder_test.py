# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 16:10:45 2020

@author: AlexVosk
"""

import sys
import configparser
from pathlib import Path
import numpy as np
import h5py

experiment_record_path = str(Path('decoder_test.py').resolve().parents[1]/'spmap/')
sys.path.append(experiment_record_path)

from decoder import Decoder
from models import get_model

config = configparser.ConfigParser()
config.read(Path('decoder_test.py').resolve().parents[0]/'decoder_test.ini')


def process_file_test():
    dec = Decoder(config)
    processed_data = dec.process_file(Path(config['paths']['experiment_data_path']))
    for key, value in processed_data.items():
        print(value)


def prediction_score_test():
    dec = Decoder(config)
    processed_data = {}
    for group in dec.DATA_GROUPS[:2]:
        print('Processing ' + group)
        with h5py.File(Path(config['paths']['experiment_data_path']),'r+') as file:
            raw_data = np.array(file[group]['raw_data'])
            picture_indices = np.array(file[group]['picture_indices'])
            srate = file['fs'][()]
        processed_data[group] = dec._process_data(group, raw_data, picture_indices, srate)
    print()
    score = dec.prediction_score(processed_data[dec.DATA_GROUPS[0]],
                                 processed_data[dec.DATA_GROUPS[1]],
                                 get_model(dec.measure))

    grids = np.around(score.values.reshape(dec.GRID_X, dec.GRID_Y, len(dec.fbandmins)).T[:,::-1], 2)
    print(grids)
    return score


def save_score_test(score):
    dec = Decoder(config)
    dec.save_score('test_score', score.values)
    
    
def process_current_file_test():
    dec = Decoder(config) 
    dec.process_current_file()



if __name__ == '__main__':
    #processed_data = process_file_test()
    #score = prediction_score_test()
    #save_score_test(score)
    #process_current_file_test()
    pass
