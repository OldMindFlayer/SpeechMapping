# -*- coding: utf-8 -*-
"""
Created on Thu Aug 13 16:10:45 2020

@author: AlexVosk
"""

import sys
import configparser
from pathlib import Path

experiment_record_path = str(Path('recorder_test.py').resolve().parents[1]/'bci/')
sys.path.append(experiment_record_path)


config = configparser.ConfigParser()
config.read(Path('test_decoder.py').resolve().parents[0]/'decoder_test.ini')
