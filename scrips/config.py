# -*- coding: utf-8 -*-
"""
Created on Wed Mar  4 09:37:29 2020

@author: dblok
"""

import configparser

def init():
    global config
    config = configparser.ConfigParser()
    config.read('config.ini')

if __name__ == '__main__':
    init()