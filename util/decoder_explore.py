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

experiment_record_path = str(Path('decoder_explore.py').resolve().parents[1]/'spmap/')
sys.path.append(experiment_record_path)

from decoder import Decoder
from models import get_model
from filterEMG import filterEMG


config = configparser.ConfigParser()
config.read('decoder_explore.ini')
#config.read(Path('decoder_explore.py').resolve().parents[0]/'decoder_explore.ini')

dec = Decoder(config)
#dec.process_current_file()

processed_data = dec.process_file(dec.experiment_data_path)
score_obj = dec.prediction_score(processed_data[dec.DATA_GROUPS[0]],
                               processed_data[dec.DATA_GROUPS[1]],
                               get_model(dec.measure))
#print
score_act = dec.prediction_score(processed_data[dec.DATA_GROUPS[0]],
                               processed_data[dec.DATA_GROUPS[2]],
                               get_model(dec.measure))
#dec.save_score(dec.DATA_GROUPS[1], score_obj.values)
#dec.save_score(dec.DATA_GROUPS[2], score_act.values)
dec.plot_results([score_obj, score_act], processed_data)
