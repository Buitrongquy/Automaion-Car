from cmath import pi
import math
import time

last_angle = e2 = e1 = t = 0

''' (x,y) put value in, (y,x) get value out'''
def midpoint(img,y):
    point_1 = 0
    point_2 = 0
    first_pixel= img[y,0] # giá trị pixel đầu 

    if first_pixel == 0:
        point_1 = 0
        for i in range(1,256,1):
            edge = int(img[y,i]) - int(img[y,i-1])
            if edge != 0:
                point_2 = i
                break
            if point_2==0 and i==255:
                point_2 = 255
    else:
        for i in range(1,256,1):
            edge = int(img[y,i]) - int(img[y,i-1])
            if edge !=0:
                if point_1 == 0:
                    point_1 = i
                    continue
                else:
                    point_2 = i
                    break
            if (point_1!=0) and (i == 255):
                point_2 = 255

    point_avr = (point_1 + point_2) // 2
    return point_avr

def calculate_angle(point_avr,y):
    ang = int(math.atan((point_avr - 128)/(256-y)) * (180 /math.pi))
    if ang>25:
        ang = 25
    elif ang<-25:
        ang = -25
    return ang

def pid_angle(e,p = 0.5, i = 0, d = 0.029):
    global t,e2,e1,last_angle
    delta_t = time.time() - t
    t= time.time()   
    alpha = 2*delta_t*p+i*i*delta_t+2*d
    beta = delta_t*delta_t*i-4*d-2*delta_t*p
    gamma = 2*d
    delta = 2*delta_t
    ang=(alpha*e+beta*e1+gamma*e2+2*delta_t*last_angle)/delta
    last_angle = ang
    e2 = e1
    e1 = e

    if ang > 25:
        ang = 25
    elif ang < -25:
        ang = -25
        
    return int(ang)