import cv2
import numpy as np 
from matplotlib import pyplot as plt

"""
To-Do list for the laser tracking -- other scripts will handle motor control 
    Ã origonal laser tracking
    x dynamic frame resizing....not critical just nice to have
    x sliders for testing
    x "motion" tracking of dots
    x note mapping (different script??)
        X different octaves for height
        x different notes for different lasers

"""

############# Static Variables #############
#testing variables
regions = 8
size = 100 #px
boundry = 30 #px


height = 720
width = 1280

#rectangles
rects = [0]*8

#induvidual frames
frames = [0]*regions

#frame_area
frame_area = [0]*regions
trigger_threshold = 75; #white pixels

#####################################

#video capture
cap = cv2.VideoCapture(0)

#create rectangles and region mask
for i in range(0,8):
    rects[i] = (boundry+i*(size + 2*boundry),0,size,height)
    
###Color Regions

#hsv
hue_min = 20
hue_max = 160
sat_min = 100
sat_max = 255
val_min = 200
val_max = 255


val_thresh_value = 130


#used to check
#cv2.imshow('blank',blank_image)      

while(1):
       
        
        _, frame = cap.read()
    
        #fix up edges (smooth)
        #frame = cv2.GaussianBlur(frame,(9,9),0)
        
        #convert from BGR to HSV 
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        h,s,v = cv2.split(frame)
        
        
        dirt1, hue_thresh_max = cv2.threshold(h,hue_max,0,cv2.THRESH_TOZERO_INV)
        dirt2, sat_thresh_max = cv2.threshold(s,sat_max,0,cv2.THRESH_TOZERO_INV)
        dirt3, val_thresh_max = cv2.threshold(v,val_max,0,cv2.THRESH_TOZERO_INV)
        
        
        #mask all colors except for blue (threshold the HSV image)
        dirt4, hue_thresh_min = cv2.threshold(hue_thresh_max,hue_min,255,cv2.THRESH_BINARY)
        dirt5, sat_thresh_min = cv2.threshold(sat_thresh_max,sat_min,255,cv2.THRESH_BINARY)
        dirt6, val_thresh_min = cv2.threshold(val_thresh_max,val_min,255,cv2.THRESH_BINARY)
        
        
        
        merged_image = cv2.merge([hue_thresh_min,sat_thresh_min,val_thresh_min])
        merged_image_bgr = cv2.cvtColor(merged_image, cv2.COLOR_HSV2BGR)
        merged_image_bw = cv2.cvtColor(merged_image_bgr, cv2.COLOR_BGR2GRAY)
       
        #bitwise_and rectangles and add color mask
        #res = cv2.bitwise_and(frame,frame,mask=color_mask)
        
        
        #create 8 mini-frames
        for i in range(0,len(frames)):
            frames[i] = merged_image_bw[(height/2 - size/2):(height/2 + size/2),(boundry+i*160):(boundry+100 + i*160)]
            frame_area[i] = cv2.sumElems(frames[i])
            
    
        #check the threshold pixel area    
        for i in range(len(frame_area)):
            if frame_area[i][0] > 1000000:
                    cv2.rectangle(merged_image_bw,(rects[i][0],rects[i][1]),(rects[i][0] + size,rects[i][1]+height),(255,255,255),3,8,0)
                    print "triggered: ", i
        #print frame_area[3]
        
        #show images
        cv2.imshow('frame1',frames[0])
        cv2.imshow('frame2',frames[1])
        cv2.imshow('frame3',frames[2])
        cv2.imshow('frame4',frames[3])
        cv2.imshow('frame5',frames[4])
        cv2.imshow('frame6',frames[5])
        cv2.imshow('frame7',frames[6])
        cv2.imshow('frame8',frames[7])
    
        #show origonal frame
        cv2.imshow('merged',merged_image_bw)
        
        
        #move images
        cv2.moveWindow('frame2',200,0)
        cv2.moveWindow('frame3',400,0)
        cv2.moveWindow('frame4',600,0)
        cv2.moveWindow('frame5',800,0)
        cv2.moveWindow('frame6',1000,0)
        cv2.moveWindow('frame7',1000,135)
        cv2.moveWindow('frame8',1000,260)
        
        #breaking from for loop (press ESC)
        k = cv2.waitKey(5) & 0xFF
        if k ==27:
            break
    

cv2.destroyAllWindows()

'''
Created on Jun 6, 2016

@author: Travis Libsack (libsackt@mit.edu)
@company: Limbeck Engineering
@license: MIT License
'''
