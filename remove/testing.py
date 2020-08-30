# -*- coding: utf-8 -*-
"""
Created on Sun Aug  9 10:20:38 2020

@author: AlexVosk
"""



import os
import numpy as np
import cv2 as cv
import time

WINDOW_X = 800
WINDOW_Y = 1280

img_prepare = np.zeros((WINDOW_X, WINDOW_Y,3), np.uint8)
cv.putText(img_prepare, 'Hi',
           org = (100, WINDOW_Y//2),
           fontFace = cv.FONT_HERSHEY_SIMPLEX,
           fontScale = 2,
           color = (255,255,255),
           thickness = 2,
           lineType = cv.LINE_AA)  

img_pause = np.zeros((WINDOW_X, WINDOW_Y,3), np.uint8)
cv.putText(img_pause, 'Pause',
           org = (100, WINDOW_Y//2),
           fontFace = cv.FONT_HERSHEY_SIMPLEX,
           fontScale = 2,
           color = (255,255,255),
           thickness = 2,
           lineType = cv.LINE_AA)  



cv.namedWindow('display', cv.WINDOW_NORMAL)
cv.imshow('display', img_prepare)




pause = False


def show_img(img, time_to_show):
    pause = False
    time_start = time.time()
    cv.imshow('display', img)
    k = cv.waitKey(time_to_show)
    print(k)
    if k == 27:
        return
    elif k == 32:
        pause = not pause
        if pause:
            s = -100
            while (s != 27) and (s != 32):
                cv.imshow('display', img_pause)
                s = cv.waitKey(1000)
        else:
            return
        return
    else:
        time_left = time_to_show - (time.time() - time_start) * 1000
        if time_left > 0:
            show_img(img, int(time_left))
            
show_img(img_prepare, 5000)      
        
        
        
def parse_key(key, img, time_left):
    if k == 27:
        return 'esc'
    elif k == 32:
        return 'pause'
    elif k == 13:
        return 'enter'
