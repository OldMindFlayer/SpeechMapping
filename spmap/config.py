# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:37:29 2020

@author: dblok
"""

import configparser

def config_init():
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config

if __name__ == '__main__':
    config_init()