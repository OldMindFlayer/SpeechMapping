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
from pathlib import Path
from tqdm import tqdm, trange


class Display:
    def __init__(self, config, q_from_display_to_recorder):
        self.config = config

        # get paths to resources
        self.path_action = self.config['paths']['pictures_actions_path']
        self.path_object = self.config['paths']['pictures_objects_path']
        self.path_other = self.config['paths']['pictures_others_path']
        self.path_sound = self.config['paths']['tone_path']
        self.path_file_actions_remove = self.config['paths']['picture_numbers_action_remove']
        self.path_file_objects_remove = self.config['paths']['picture_numbers_object_remove']
        
        # command to LSL listener to start listen the stream
        self.q_from_display_to_recorder = q_from_display_to_recorder
        self.q_from_display_to_recorder.put(('inlet_state', 1))
        
        # initialize amount of time ALL pictures will be shown
        self.pictures_action_time = self.config['display'].getint('pictures_action_time')
        self.pictures_object_time = self.config['display'].getint('pictures_object_time')
        
        # initialize amount of time EACH picture will be shown
        self.single_picture_time = int(self.config['display'].getfloat('single_picture_time')*1000)
        self.time_between_pictures = int(self.config['display'].getfloat('time_between_pictures')*1000)
        self.time_other_pictures = int(self.config['display'].getfloat('time_other_pictures')*1000)
        
        # initialize configuration of display
        self.WINDOW_X = self.config['display'].getint('WINDOW_X')
        self.WINDOW_Y = self.config['display'].getint('WINDOW_Y')
        self.rotate_pictures = self.config['display'].getboolean('rotate_pictures')
        self.pictures_action = []
        self.pictures_object = []
        self.pictures_other = []
        self.picture_types = [self.pictures_action, self.pictures_object, self.pictures_other]
        
        # type of procidure: remove pictures or speech mapping
        self.remove_mode = config['general'].getboolean('remove_mode')
        self.picture_numbers_action_remove = []
        self.picture_numbers_object_remove = []
        if not self.remove_mode and Path(self.path_file_actions_remove).is_file():
            with open(self.path_file_actions_remove, 'r') as file:
                self.picture_numbers_action_remove = list(map(str.strip, file.readlines()))
        if not self.remove_mode and Path(self.path_file_objects_remove).is_file():
            with open(self.path_file_objects_remove, 'r') as file:
                self.picture_numbers_object_remove = list(map(str.strip, file.readlines()))

        # make image to show while rest
        self.image_rest = np.zeros((self.WINDOW_X,self.WINDOW_Y,3), np.uint8)

        # make image with message 'Press any button...'
        self.image_button_any = self._prepare_image('Press any button...')
        
        # make image with message 'Press Enter...'
        self.image_button_enter = self._prepare_image('Press Enter...')
        
        # make image with message 'Pause'
        self.image_pause = self._prepare_image('Pause')
        self.close = 0
        self.pause = 0
        self.paused_while_shown = 0
        
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
        self.q_from_display_to_recorder.put(('patient_state', -1))
        
        # prepare window for patient
        cv.namedWindow('display', cv.WINDOW_NORMAL)
        cv.imshow('display', self.image_button_any)
        cv.waitKey(0)
        #cv.setWindowProperty('display', cv.WND_PROP_FULLSCREEN, cv.WINDOW_FULLSCREEN)
        
        # show time to rest
        if self.config['display'].getint('resting_time') > 0:    
            self._printm('Recording Rest state...')
            self.q_from_display_to_recorder.put(('patient_state', 0))
            self._start_rest()
            self.q_from_display_to_recorder.put(('patient_state', -1))
            self._printm('Press ENTER on the display screen...')
            while True:
                cv.imshow('display', self.image_button_enter)
                k = cv.waitKey(1000)
                if k == 13:
                    break
        
        # demonstrate pictures
        self.q_from_display_to_recorder.put(('patient_state', -1))
        cv.imshow('display', self.pictures_other[1].img)
        cv.waitKey(self.time_other_pictures)
        self.q_from_display_to_recorder.put(('patient_state', 1))
        self._printm('Showing pictures of actions...')
        self._show_pictures(self.pictures_object)
        self.q_from_display_to_recorder.put(('patient_state', -1))
        
        cv.imshow('display', self.pictures_other[2].img)
        cv.waitKey(self.time_other_pictures)
        self.q_from_display_to_recorder.put(('patient_state', 2))
        self._printm('Showing pictures of actions...')
        self._show_pictures(self.pictures_action)
        self.q_from_display_to_recorder.put(('patient_state', -1))
        cv.imshow('display', self.pictures_other[3].img)
        cv.waitKey(self.time_other_pictures)

        # wait before closure
        self._printm('Press any button on the display screen...')
        self.q_from_display_to_recorder.put(('patient_state', -1))
        cv.imshow('display', self.image_button_any)
        cv.waitKey(0)
        self.q_from_display_to_recorder.put(('inlet_state', 0))
        


    def _prepare_image(self, message):
        img_prepare = np.zeros((self.WINDOW_X, self.WINDOW_Y,3), np.uint8)
        cv.putText(img_prepare, message,
                   org = (100, self.WINDOW_Y//2),
                   fontFace = cv.FONT_HERSHEY_SIMPLEX,
                   fontScale = 1,
                   color = (255,255,255),
                   thickness = 2,
                   lineType = cv.LINE_AA)  
        return img_prepare




    
    def _start_rest(self):
        resting_time = self.config['display'].getint('resting_time')
        pbar = trange(resting_time)
        #self.q_from_display_to_recorder.put(('picture_state', 1))
        for sec in pbar:    
            pbar.set_description('Resting...')
            self._show_image(self.image_rest, 1000)
            if self.close:
                self.close = 0
                break
        #self.q_from_display_to_recorder.put(('picture_state', 2))



    def _show_image(self, image, time_to_show):
        time_start = time.time()
        cv.imshow('display', image)
        k = cv.waitKey(time_to_show)
        if k == 27:
            self.pause = 0
            self.q_from_display_to_recorder.put(('pause', 0))
            self.close = 1
        elif k == 32:
            self.pause = not self.pause
            if self.pause:
                self.paused_while_shown = 1
                self.q_from_display_to_recorder.put(('pause', 1))
                while self.pause:
                    self._show_image(self.image_pause, 1000)
            else:
                self.q_from_display_to_recorder.put(('pause', 0))
                self._show_image(self.image_pause, 2000)
        elif k == -1:
            return
        else:
            time_left = int(time_to_show - (time.time() - time_start) * 1000)
            if time_left > 0:
                self._show_image(image, time_left)
                
    
    # show pictures        
    def _show_pictures(self, pictures):
        pbar = tqdm(pictures)
        for picture in pbar:
            self.paused_while_shown = 0
            if self.time_between_pictures > 0:
                if self.config['display'].getboolean('sound_between_pictures'):
                    winsound.PlaySound(self.path_sound, winsound.SND_ASYNC)
                self._show_image(self.pictures_other[0].get_img(), self.time_between_pictures)
                if self.config['display'].getboolean('sound_between_pictures'):
                    winsound.PlaySound(None, winsound.SND_ASYNC)
                if self.close:
                    self.close = 0
                    break
                if self.paused_while_shown:
                    self.paused_while_shown = 0
                    continue
            pbar.set_description("Picture %s" % picture.get_number())
            self.q_from_display_to_recorder.put(('picture_state', 1))
            self._show_image(picture.get_img(), self.single_picture_time)
            if self.close:
                self.close = 0
                break
            else:
                self.q_from_display_to_recorder.put(('picture_state', 2))
            self.paused_while_shown = 0
        if self.time_between_pictures > 0:
            self._show_image(self.pictures_other[0].get_img(), self.time_between_pictures)
            if self.close:
                self.close = 0
                return

    

    
    def _load_pictures(self):
        
        # create lists of names of picturs
        picture_names_other = sorted(os.listdir(self.path_other), key=lambda x: int(x[:-4]))
        picture_names_action = sorted(os.listdir(self.path_action), key=lambda x: int(x[:-4]))
        picture_names_object = sorted(os.listdir(self.path_object), key=lambda x: int(x[:-4]))
        if len(self.picture_numbers_action_remove)>0:
            for picture_number in self.picture_numbers_action_remove:
                s = str(picture_number)+'.jpg'
                if s in picture_names_action:
                    picture_names_action.remove(s)
        if len(self.picture_numbers_object_remove)>0:
            for picture_number in self.picture_numbers_object_remove:
                s = str(picture_number)+'.jpg'
                if s in picture_names_object:
                    picture_names_object.remove(s)
                
        if self.config['display'].getboolean('shuffle_pictures'):
            random.shuffle(picture_names_action)
            random.shuffle(picture_names_object)

        # decide on number of pictures to show
        number_of_pictures_action = self._get_number_of_pictures(self.pictures_action_time)
        number_of_pictures_object = self._get_number_of_pictures(self.pictures_object_time)
        if number_of_pictures_action == -1 or number_of_pictures_action > len(picture_names_action):
            number_of_pictures_action = len(picture_names_action)
        if number_of_pictures_object == -1 or number_of_pictures_object > len(picture_names_object):
            number_of_pictures_object = len(picture_names_object)

        # read pictures into memory and save loaded numbers into files
        picture_numbers_action_to_show = []
        picture_numbers_object_to_show = []
        
        for i in range(number_of_pictures_action):
            self.pictures_action.append(Picture(self.path_action, picture_names_action[i]))
            picture_numbers_action_to_show.append(picture_names_action[i][:-4])
        for i in range(number_of_pictures_object):
            self.pictures_object.append(Picture(self.path_object, picture_names_object[i]))
            picture_numbers_object_to_show.append(picture_names_object[i][:-4])
        for i in range(len(picture_names_other)):
            self.pictures_other.append(Picture(self.path_other, picture_names_other[i]))
            
        if self.config['display'].getboolean('save_picture_numbers'):
            with open(self.config['paths']['patient_data_path'] + "/picture_numbers_action_remove.txt", "w") as file:
                for number in self.picture_numbers_action_remove:
                    file.write(number + '\n')
            with open(self.config['paths']['patient_data_path'] + "/picture_numbers_object_remove.txt", "w") as file:
                for number in self.picture_numbers_object_remove:
                    file.write(number + '\n')
        
        
    def _prepare_pictures(self):
        for picture_type in self.picture_types:
            for picture in picture_type:
                picture.prepare(self.WINDOW_X, self.WINDOW_Y, self.rotate_pictures)
 

    def _get_number_of_pictures(self, pictures_time):
        if pictures_time == -1:
            number_of_pictures = -1
        else:
            number_of_pictures = math.ceil((pictures_time+self.time_between_pictures/1000)/(self.single_picture_time/1000+self.time_between_pictures/1000))
        return number_of_pictures
        
    
    def _printm(self, message):
        print('{} {}: '.format(time.strftime('%H:%M:%S'), type(self).__name__) + message)

    
    
    
    
    
    
    
    
class Picture():
    def __init__(self, directory_path, file_name):
        self.directory_path = directory_path
        self.file_name = file_name
        directory = Path(self.directory_path).parts[-1]
        if directory == 'pictures_action':
            self.picture_type = 'action'
        elif directory == 'pictures_object':
            self.picture_type = 'object'
        elif directory == 'pictures_other':
            self.picture_type = 'other'
        else:
            self.picture_type = None
            print('Picture: looking for picture in wrong directory')
        self.img = cv.imread(self.directory_path + '/' + self.file_name)
        
    
    def _rotate_resize(self, X, Y):
        self.img = cv.rotate(self.img, cv.ROTATE_90_COUNTERCLOCKWISE)
        x, y, _ = self.img.shape
        if x / Y > y / X:
            self.img = cv.resize(self.img, (Y, y*X // Y))
        else:
            self.img = cv.resize(self.img, (x*Y // X, X))

    def _pad(self, X, Y):
        x, y, _ = self.img.shape
        if (X - x) < 0:
            left_pad = 0
            right_pad = 0
        elif (X - x) % 2:
            left_pad = (X - x) // 2
            right_pad = (X - x) // 2 + 1
        else: 
            left_pad = (X - x) // 2
            right_pad = (X - x) // 2
        if (Y - y) < 0:
            top_pad = 0
            bottom_pad = 0    
        elif (Y - y) % 2:
            top_pad = (Y - y) // 2
            bottom_pad = (Y - y) // 2 + 1
        else: 
            top_pad = (Y - y) // 2
            bottom_pad = (Y - y) // 2
        self.img = np.pad(self.img, ((left_pad, right_pad), (top_pad, bottom_pad), (0,0)), mode='constant',)

    def prepare(self, X, Y, rotate):
        if rotate:
            self._rotate_resize(X, Y)
        self._pad(X, Y)

    def get_img(self):
        return self.img
    
    def get_file_name(self):
        return self.file_name
    
    def get_number(self):
        return int(self.file_name[:-4])
    
    def get_type(self):
        return self.picture_type
    
    def shape(self):
        return self.img.shape
    
    










if __name__ == '__main__':
    from queue import Queue
    q = Queue()
    from config import config_init
    argv = []
    config = config_init(argv)
    d = Display(config, q)
    d.start()
#    d._show_image(d.image_button_any, 5000)
















