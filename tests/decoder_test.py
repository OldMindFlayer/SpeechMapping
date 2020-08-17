# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 16:10:45 2020

@author: AlexVosk
"""

import sys
import configparser
from pathlib import Path
import time
import numpy as np

experiment_record_path = str(Path('decoder_test.py').resolve().parents[1]/'spmap/')
sys.path.append(experiment_record_path)

from decoder import Decoder
from models import linregress
from filterEMG import filterEMG

#a = np.random.normal(size=(200000,1))
#t1 = time.time()
#f = filterEMG(a, 60, 80, 2048)
#t2 = time.time()
#print(t2-t1)

config = configparser.ConfigParser()
config.read(Path('decoder_test.py').resolve().parents[0]/'decoder_test.ini')

dec = Decoder(config)
dec.process_current_file()

#processed_data = dec.process_file(file_path)

#score1 = dec.prediction_score(processed_data['data_rest'], processed_data['data_objects'], linregress)
#score2 = dec.prediction_score(processed_data['data_rest'], processed_data['data_actions'], linregress)
#print(score1.values)
#scores = [score1, score2]
#dec.plot_results(scores)