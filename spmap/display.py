# -*- coding: utf-8 -*-
"""
Created on Fri Feb 29 09:29:19 2020

@author: dblokv
"""

import os
import numpy as np
import cv2 as cv
from threading import Thread
import time
import winsound
import random
import math


class Display:
    def __init__(self, config, q_from_display_to_listener):
        self.config = config
        
        # initialise paths to resources
        self.path_action = self.config['general']['root_path'] + '/resources/pictures_action/'
        self.path_object = self.config['general']['root_path'] + '/resources/pictures_object/'
        self.path_other = self.config['general']['root_path'] + '/resources/pictures_other/'
        self.path_sound = self.config['general']['root_path'] + '/resources/sounds/tone.wav'
        
        # command to LSL listener to start listen the stream
        self.q_from_display_to_listener = q_from_display_to_listener
        self.q_from_display_to_listener.put(('lsl_stream_listener_state', True))
        
        # initialise amount of time EACH picture will be shown
        self.single_picture_time = int(self.config['display'].getfloat('single_picture_time')*1000)
        self.time_between_pictures = int(self.config['display'].getfloat('time_between_pictures')*1000)
        self.time_other_pictures = int(self.config['display'].getfloat('time_other_pictures')*1000)
        
        # initialise amount of time ALL pictures will be shown
        pictures_action_time = self.config['display'].getint('pictures_action_time')
        pictures_object_time = self.config['display'].getint('pictures_object_time')
        self.number_of_pictures_action = self._get_number_of_pictures(pictures_action_time)
        self.number_of_pictures_object = self._get_number_of_pictures(pictures_object_time)

        # initialise configuration of display
        self.pictures_rotated = self.config['display'].getboolean('pictures_rotated')
        self.WINDOW_X = self.config['display'].getint('WINDOW_X')
        self.WINDOW_Y = self.config['display'].getint('WINDOW_Y')
        self.pictures_action = []
        self.pictures_object = []
        self.pictures_other = []
        self.pictures_types = [self.pictures_action, self.pictures_object, self.pictures_other]

        # make image with message 'Press any button...'
        self.img_prepare = None
        self._img_prepare()
        
        # process the pictures
        self._load_pictures()
        self._prepare_pictures()
        
        # initialise thread for display
        self.thread = Thread(target=self._update, args=())
        
        
    def start(self):
        self.thread.start()
        cv.destroyAllWindows()
            
        
    def _update(self):
        # command to LSL listener
        self.q_from_display_to_listener.put(('patient_state', 0))
        
        # prepare window for patient
        cv.namedWindow('display', cv.WINDOW_NORMAL)
        cv.imshow('display', self.img_prepare)
        cv.waitKey(0)
        cv.setWindowProperty('display', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        
        # show time to rest
        self.q_from_display_to_listener.put(('patient_state', 1))
        self._start_clock()
        
        # demonstrate pictures
        self.q_from_display_to_listener.put(('patient_state', 0))
        cv.imshow('display', self.pictures_other[1])
        cv.waitKey(self.time_other_pictures)
        self.q_from_display_to_listener.put(('patient_state', 2))
        self._show_pictures(self.pictures_action)
        self.q_from_display_to_listener.put(('patient_state', 0))
        cv.imshow('display', self.pictures_other[3])
        cv.waitKey(self.time_other_pictures)
        cv.imshow('display', self.pictures_other[2])
        cv.waitKey(self.time_other_pictures)
        self.q_from_display_to_listener.put(('patient_state', 3))
        self._show_pictures(self.pictures_object)
        self.q_from_display_to_listener.put(('patient_state', 0))
        cv.imshow('display', self.pictures_other[3])
        cv.waitKey(self.time_other_pictures)

        # wait before closure
        self.q_from_display_to_listener.put(('patient_state', 0))
        cv.imshow('display', self.img_prepare)
        cv.waitKey(0)
        self.q_from_display_to_listener.put(('lsl_stream_listener_state', False))


    def _img_prepare(self):
        self.img_prepare = np.zeros((self.WINDOW_X, self.WINDOW_Y,3), np.uint8)
        cv.putText(self.img_prepare, 'Press any button...',
                   org = (100, self.WINDOW_Y//2),
                   fontFace = cv.FONT_HERSHEY_SIMPLEX,
                   fontScale = 1,
                   color = (255,255,255),
                   thickness = 2,
                   lineType = cv.LINE_AA)    
        
        
    def _start_clock(self):
        t = time.perf_counter()
        resting_time = self.config['display'].getint('resting_time')
        img = np.zeros((self.WINDOW_X,self.WINDOW_Y,3), np.uint8)
        while time.perf_counter() < t + resting_time:
            time_pass = t + resting_time - time.perf_counter()
            if int(time_pass) % 5 == 0:
                print('Rest time: {} out of {}'.format(resting_time - int(time_pass), resting_time))
            cv.imshow('display', img)
            k = cv.waitKey(1000)
            if k == 27:
                break
        
    # show pictures        
    def _show_pictures(self, pictures):
        for picture in pictures:
            if self.time_between_pictures > 0:
                if self.config['display'].getboolean('sound_between_pictures'):
                    winsound.PlaySound(self.path_sound, winsound.SND_ASYNC)
                    cv.imshow('display', self.pictures_other[0])
                    cv.waitKey(self.time_between_pictures)
                    winsound.PlaySound(None, winsound.SND_ASYNC)
                else:
                    cv.imshow('display', self.pictures_other[0])
                    cv.waitKey(self.time_between_pictures)
            self.q_from_display_to_listener.put(('picture_shown', True))
            cv.imshow('display', picture)
            k = cv.waitKey(self.single_picture_time)
            if k == 27:
                break
        
    
    def _load_pictures(self):
        
        # create lists of names of picturs
        pictures_names_action = sorted(os.listdir(self.path_action))
        pictures_names_object = sorted(os.listdir(self.path_object))
        pictures_names_other = sorted(os.listdir(self.path_other))
        if self.config['display'].getboolean('shuffle_pictures'):
            random.shuffle(pictures_names_action)
            random.shuffle(pictures_names_object)

#            text_file1 = open(windows_path/"pictures_names_action.txt", "w") 
#            for picture_number in pictures_names_action:
#                text_file1.write(picture_number[:-4] + '\n')
#            text_file1.close()
#            text_file2 = open(windows_path/"pictures_names_object.txt", "w") 
#            for picture_number in pictures_names_object:
#                text_file2.write(picture_number[:-4] + '\n')
#            text_file2.close()
            
        # decide on number of pictures to show
        if self.number_of_pictures_action == -1 or self.number_of_pictures_action > len(pictures_names_action):
            self.number_of_pictures_action = len(pictures_names_action)
        if self.number_of_pictures_object == -1 or self.number_of_pictures_object > len(pictures_names_object):
            self.number_of_pictures_object = len(pictures_names_object)
        
        # read pictures into memory
        for i in range(self.number_of_pictures_action):
            self.pictures_action.append(cv.imread(self.path_action + pictures_names_action[i]))
        for i in range(self.number_of_pictures_object):
            self.pictures_object.append(cv.imread(self.path_object + pictures_names_object[i]))
        for i in range(len(pictures_names_other)):
            self.pictures_other.append(cv.imread(self.path_other + pictures_names_other[i]))
    
    
    def _prepare_pictures(self):
        for i in range(len(self.pictures_types)):
            if self.pictures_rotated:
                self._prepare_pictures_helper_rotate_and_resize(self.pictures_types[i])
            self._prepare_pictures_helper_pad(self.pictures_types[i])
                
    def _prepare_pictures_helper_rotate_and_resize(self, pictures):
        for i in range(len(pictures)):
            picture = cv.rotate(pictures[i], cv.ROTATE_90_COUNTERCLOCKWISE)
            x, y, _ = picture.shape
            if x / self.WINDOW_Y > y / self.WINDOW_X:
                picture = cv.resize(picture, (self.WINDOW_Y, y*self.WINDOW_X//self.WINDOW_Y))
            else:
                picture = cv.resize(picture, (x*self.WINDOW_Y//self.WINDOW_X, self.WINDOW_X))
            pictures[i] = picture
        
    def _prepare_pictures_helper_pad(self, pictures):
        for i in range(len(pictures)):
            x, y, _ = pictures[i].shape
            if (self.WINDOW_X - x) < 0:
                left_pad = 0
                right_pad = 0
            elif (self.WINDOW_X - x) % 2:
                left_pad = (self.WINDOW_X - x) // 2
                right_pad = (self.WINDOW_X - x) // 2 + 1
            else: 
                left_pad = (self.WINDOW_X - x) // 2
                right_pad = (self.WINDOW_X - x) // 2
            if (self.WINDOW_Y - y) < 0:
                top_pad = 0
                bottom_pad = 0    
            elif (self.WINDOW_Y - y) % 2:
                top_pad = (self.WINDOW_Y - y) // 2
                bottom_pad = (self.WINDOW_Y - y) // 2 + 1
            else: 
                top_pad = (self.WINDOW_Y - y) // 2
                bottom_pad = (self.WINDOW_Y - y) // 2
            pictures[i] = np.pad(pictures[i], ((left_pad, right_pad), (top_pad, bottom_pad), (0,0)), mode='constant',)


    def _get_number_of_pictures(self, pictures_time):
        if pictures_time == -1:
            number_of_pictures = -1
        else:
            number_of_pictures = math.ceil(pictures_time / (self.single_picture_time/1000 + self.time_between_pictures/1000))
        return number_of_pictures
        


if __name__ == '__main__':
    pass
