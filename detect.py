from signal import signal
import cv2 as cv
import numpy as np
import matplotlib.pyplot as plt
import os

def detect_signs(image):
    signal = 'not none'
    img = image[20:120,300:550]
    hsv= cv.cvtColor(img,cv.COLOR_RGB2HSV)

    # hsv for blue color
    lower_bound = np.array([15,100,100])   
    upper_bound = np.array([25,255,255])
    mask_b= cv.inRange(hsv, lower_bound, upper_bound)
    check_b=np.where(mask_b!=0)

    # hsv for red color
    lower_bound = np.array([130,0,90])   
    upper_bound = np.array([190,90,170])
    mask_r= cv.inRange(hsv, lower_bound, upper_bound)
    check_r=np.where(mask_r!=0)

    if 500 < np.size(check_b) and np.size(check_b) < 1600:
        mask= mask_b
        #print(np.size(check_b))
    elif 100 < np.size(check_r) and np.size(check_r) < 1000:
        mask= mask_r
        #print(np.size(check_r))
    else:
        signal = 'none'   
        return 0,0 
    if signal == 'not none':       
        element= cv.getStructuringElement(cv.MORPH_RECT,(1,2))
        mask=cv.morphologyEx(mask,cv.MORPH_OPEN ,element,iterations=1)
        #cv.imshow('mask b',mask_b)
        #cv.imshow('mask r',mask_r)
        cv.imshow('mask',mask)
        minDist = 500
        param1 = 200 #500
        param2 = 11 #200 #smaller value-> more false circles
        minRadius = 8
        maxRadius = 17 #10
        circles = cv.HoughCircles(mask, cv.HOUGH_GRADIENT, 1, minDist, param1=param1, param2=param2, minRadius=minRadius, maxRadius=maxRadius)

        if circles is not None:
            circles = np.uint16(np.around(circles)) 
            circle = circles[0][0]
            return circle, 1
        else:
            return 0,0
                    
        
def detect_intersection(image,p):
    point_r = 0
    point_l = 0
    point_f = 0
    img = image
    for i in range(50,150,1):
        if 80 <= p and p <= 175:
            if (int(img[i,p+80]) - int(img[i-1,p+80])) == 255 :
                point_r = i
            if (int(img[i,p-80]) - int(img[i-1,p-80])) == 255 :
                point_l = i
    if point_l != 0 :
        for i in range(100,160,1):
            if (int(img[point_l-10,i]) - int(img[point_l-10,i-1])) == 255:
                point_f = i
    elif point_r != 0: 
        for i in range(100,160,1):
            if (int(img[point_r-10,i]) - int(img[point_r-10,i-1])) == 255:
                point_f = i
    #print(point_l,point_f,point_r)
    if point_l ==0 and point_r == 0:
        return '010'
    elif point_f != 0 and point_l != 0 and point_r != 0 :
        return '111'
    elif point_f != 0 and point_l != 0 and point_r == 0 :
        return '110'
    elif point_f != 0 and point_l == 0 and point_r != 0 :
        return '011'
    elif point_f == 0 and point_l != 0 and point_r != 0 :
        return '101'
    