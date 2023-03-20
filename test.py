import socket
import cv2 as cv
import numpy as np
from keras.models import load_model
import matplotlib.pyplot as plt
import tensorflow as tf
import math
import control
import detect
from tensorflow import keras
import time

global sendBack_angle, sendBack_Speed, current_speed, current_angle
sendBack_angle = 0
sendBack_Speed = 0
current_speed = 0
current_angle = 0

model= tf.keras.models.load_model('D:/Foder_Work/AUTOMATION_CAR/Demo/seman.h5')
model_2 = keras.models.load_model("D:\Foder_Work\AUTOMATION_CAR\Demo\model.h5")
status_turn = 'disable'
# Create a socket object
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Define the port on which you want to connect
PORT = 54321
# connect to the server on local computer
s.connect(('127.0.0.1', PORT))


def Control(angle, speed):
    global sendBack_angle, sendBack_Speed
    sendBack_angle = angle
    sendBack_Speed = speed


if __name__ == "__main__":
    try:
        while True:

 
            """
            - Chương trình đưa cho bạn 1 giá trị đầu vào:
                * image: hình ảnh trả về từ xe
                * current_speed: vận tốc hiện tại của xe
                * current_angle: góc bẻ lái hiện tại của xe
            - Bạn phải dựa vào giá trị đầu vào này để tính toán và
            gán lại góc lái và tốc độ xe vào 2 biến:
                * Biến điều khiển: sendBack_angle, sendBack_Speed
                Trong đó:
                    + sendBack_angle (góc điều khiển): [-25, 25]
                        NOTE: ( âm là góc trái, dương là góc phải)
                    + sendBack_Speed (tốc độ điều khiển): [-150, 150]
                        NOTE: (âm là lùi, dương là tiến)
            """

            message_getState = bytes("0", "utf-8")
            s.sendall(message_getState)
            state_date = s.recv(100)

            try:
                current_speed, current_angle = state_date.decode(
                    "utf-8"
                    ).split(' ')
            except Exception as er:
                print(er)
                pass

            message = bytes(f"1 {sendBack_angle} {sendBack_Speed}", "utf-8")
            s.sendall(message)
            data = s.recv(100000)

            try:
                image_origin = cv.imdecode(
                    np.frombuffer(
                        data,
                        np.uint8
                        ), -1
                    )

                # your process here
                if status_turn == 'turn':
                    time.sleep(1.5)
                    status_turn = 'disable'

                image = cv.resize(image_origin, (256, 256)) 
                image_pre = image[None,:,:,:]
                predictions = model.predict(image_pre)[0]
                prediction = predictions*255
                prediction=prediction.astype(np.uint8)
                gray = cv.cvtColor(prediction, cv.COLOR_BGR2GRAY)
                binary=cv.threshold(gray,90,255,cv.THRESH_BINARY)[1]
                h=135
                p=control.midpoint(binary,255-h)
                a=control.calculate_angle(p,255-h)
                a_pid=control.pid_angle(a) 
                speed= int(30*(1-abs(a)*0.035))
                cv.circle(binary,(p,255-h),2,(255,255,255),3)  
                #cv.circle(binary,(p+50,255-h),2,(255,255,255),3)
                #cv.circle(binary,(p-50,255-h),2,(0,0,0),3)
                #print(type(binary))
                #print(binary)
                cv.imshow('binary',binary)
                #cv.imshow('image',image_origin)
                #cv.imshow('image',image_origin)
                               

                # Detect sings
                circle,check = detect.detect_signs(image_origin)                
                if check ==1 :  
                    speed = 5 
                    #roi = cv.circle(image_origin, (circle[0]+300,circle[1]+20), circle[2]+5, (0, 0, 255), 2)
                    #cv.imshow('roi', roi)
                    img = image_origin[circle[1]-5:circle[1]+40,circle[0]+278:circle[0]+322]
                    cv.imshow("img",img)
                    img = cv.cvtColor(np.float32(img), cv.COLOR_RGB2GRAY)
                    img = cv. resize(img,(50, 50)) 
                    cv.normalize(img,img,0, 1.0,cv.NORM_MINMAX)
                    img = np.reshape(img,(1,50,50,1))
                    results = model_2.predict(img)[0]
                    max=0.0
                    index=0
                    for i in range(0,5):
                        if results[i]>max:
                            max=results[i]
                            index=i
                    
                    if max >= 0.7:
                        if (index==0):
                            kind = "Cam re trai"
                        elif (index==1):
                            kind = "Re phai"
                        elif (index==2):
                            kind = "Re trai"
                        elif (index==3):
                            kind = "Di thang"
                        elif (index==4):
                            kind = "Cam re phai"

                        print(kind)                                            

                    # Detect intersection
                    kind_intersection = detect.detect_intersection(binary,p)
                    if kind_intersection != '010':
                        status_turn = 'enable'
                        print(kind_intersection)
                        if kind == 'Cam re trai' and kind_intersection == '110':
                            turn_direction = 'go straight'
                        elif kind == 'Cam re trai' and kind_intersection == '101':
                            turn_direction = 'turn right'
                        elif kind == 'Cam re phai' and kind_intersection == '101':
                            turn_direction = 'turn left'
                        elif kind == 'Cam re phai' and kind_intersection == '011':     
                            turn_direction = 'go straight'
                        elif kind == 'Di thang' :     
                            turn_direction = 'go straight'
                        elif kind == 'Re phai' :     
                            turn_direction = 'turn right'
                        elif kind == 'Re trai' :     
                            turn_direction = 'turn left'
                        print(turn_direction)

                    if status_turn == 'enable':                      
                        a_pid = 0                     
                        if 60 <= p and p <= 195:
                            if turn_direction == 'turn left':
                                for i in range(120,180,1):
                                    if (int(binary[i,p-80]) - int(binary[i-1,p-80])) == -255 :
                                        print('Turn')
                                        a_pid = -15
                                        status_turn = 'turn'
                                        time.sleep(1.5)
                                        break                                        

                            elif turn_direction == 'turn right':
                                for i in range(120,180,1):
                                    if (int(binary[i,p+80]) - int(binary[i-1,p+80])) == -255  :
                                        print('Turn')
                                        a_pid = 15
                                        status_turn = 'turn'
                                        time.sleep(2)
                                        break
                                
                            elif turn_direction == 'go straight':
                                if kind_intersection == '110' or kind_intersection == '111':
                                    for i in range(120,160,1):
                                        if (int(binary[i,p-80]) - int(binary[i-1,p-80])) == -255  :
                                            print('Turn')
                                            a_pid = 0
                                            status_turn = 'turn'
                                            time.sleep(2)
                                            break
                                elif kind_intersection == '011' :
                                    for i in range(120,160,1):
                                        if (int(binary[i,p+80]) - int(binary[i-1,p+80])) == -255  :
                                            print('Turn')
                                            a_pid = 0
                                            status_turn = 'turn'
                                            time.sleep(2)
                                            break

                    

                cv.waitKey(1)

                # Control(angle, speed)
                print(a_pid,speed) 
                Control(a_pid,speed)
                
            except Exception as er:
                print(er)
                pass

    finally:
        print('closing socket')
        s.close()