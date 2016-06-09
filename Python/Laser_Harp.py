import cv2
import numpy as np 
from matplotlib import pyplot as plt

"""
To-Do list for the laser tracking -- other scripts will handle motor control 
    + laser tracking
    + dynamic frame resizing....not critical just nice to have
    - sliders for testing
    x "motion" tracking of dots
    x note mapping (different script??)
        X different octaves for height
        x different notes for different lasers

"""
#video capture
cap = cv2.VideoCapture(0)

_,frame = cap.read()
height,width = frame.shape[0:2]


############# Static Variables #############
#testing variables
regions = 8
boundry = 30 #px
size = width/regions - boundry*2
print size

#rectangles
rects = [0]*regions

#induvidual frames
frames = [0]*regions

#frame_area
frame_pixels = [0]*regions
pixel_trig = 1000000; #white pixels

#####################################


#create rectangles and region mask
for i in range(0,8):
    rects[i] = (boundry+i*(size + 2*boundry),0,size,height)
    

#### HSV Color Scheme
#default HSV values -- change with slider
hue_min = 20
hue_max = 160
sat_min = 100
sat_max = 255
val_min = 200
val_max = 255


##Sliders!

#function to be called when the slider interrupt happens...not use
def slider_call(x):
    pass

slider_window = np.zeros((100,800),np.uint8)
cv2.namedWindow('Slider Window')

#trackbars!
cv2.createTrackbar('HUE_min','Slider Window',0,180,slider_call)
cv2.createTrackbar('HUE_max','Slider Window',0,180,slider_call)

cv2.createTrackbar('SAT_min','Slider Window',0,255,slider_call)
cv2.createTrackbar('SAT_max','Slider Window',0,255,slider_call)

cv2.createTrackbar('VAL_min','Slider Window',0,255,slider_call)
cv2.createTrackbar('VAL_min','Slider Window',0,255,slider_call)

#add button to return to defaults
switch = '0: Default \n1: Mixing'
cv2.createTrackbar(switch,'Slider Window',0,1,slider_call)
   

while(1):
    
      #capture video
        _, frame = cap.read()
        
       #show slider window
        cv2.imshow('Slider Window', slider_window)
       
       
        #Get Trackbar positions
        h_min = cv2.getTrackbarPos('HUE_min','Slider Window')
        h_max = cv2.getTrackbarPos('HUE_max','Slider Window') 
        s_min = cv2.getTrackbarPos('SAT_min','Slider Window')
        s_max = cv2.getTrackbarPos('SAT_max','Slider Window')
        v_min = cv2.getTrackbarPos('VAL_min','Slider Window')
        v_max = cv2.getTrackbarPos('VAL_max','Slider Window')
    
        #get button state
        s = cv2.getTrackbarPos(switch,'Slider Window');
    
        if(s == 0):
            h_min = hue_min
            h_max = hue_max
            s_min = sat_min
            s_max = sat_max
            v_min = val_min
            v_max = val_max
    
        #fix up edges (smooth)
        frame = cv2.GaussianBlur(frame,(9,9),0)
        
        #convert from BGR to HSV 
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        h,s,v = cv2.split(frame)
        
        #threshold the maximum values first
        dirt, hue_thresh_max = cv2.threshold(h,h_max,0,cv2.THRESH_TOZERO_INV)
        dirt, sat_thresh_max = cv2.threshold(s,s_max,0,cv2.THRESH_TOZERO_INV)
        dirt, val_thresh_max = cv2.threshold(v,v_max,0,cv2.THRESH_TOZERO_INV)
        
        
        #use first imagae in second thresholdin -- filtering algorithm
        dirt, hue_thresh = cv2.threshold(hue_thresh_max,h_min,255,cv2.THRESH_BINARY)
        dirt, sat_thresh = cv2.threshold(sat_thresh_max,s_min,255,cv2.THRESH_BINARY)
        dirt, val_thresh = cv2.threshold(val_thresh_max,v_min,255,cv2.THRESH_BINARY)
        
        
        #merge images to create entire HSV image
        merged_image = cv2.merge([hue_thresh,sat_thresh,val_thresh])
        
        #convert 3-channel HSV image to a binary bw image
        merged_image_bgr = cv2.cvtColor(merged_image, cv2.COLOR_HSV2BGR)
        merged_image_bw = cv2.cvtColor(merged_image_bgr, cv2.COLOR_BGR2GRAY)
        
        #create 8 mini-frames
        for i in range(0,len(frames)):
            frames[i] = merged_image_bw[(height/2 - size/2):(height/2 + size/2),(boundry+i*160):(boundry+100 + i*160)]
            frame_pixels[i] = cv2.sumElems(frames[i])
            
    
        #check the threshold pixel area    
        for i in range(len(frame_pixels)):
            #if large then pixel_trig, draw a rectangle!
            if frame_pixels[i][0] > pixel_trig:
                    cv2.rectangle(merged_image_bw,(rects[i][0],rects[i][1]),(rects[i][0] + size,rects[i][1]+height),(255,255,255),3,8,0)
                    print "triggered: ", i
        
        #show individual regions
        cv2.imshow('frame1',frames[0])
        cv2.imshow('frame2',frames[1])
        cv2.imshow('frame3',frames[2])
        cv2.imshow('frame4',frames[3])
        cv2.imshow('frame5',frames[4])
        cv2.imshow('frame6',frames[5])
        cv2.imshow('frame7',frames[6])
        cv2.imshow('frame8',frames[7])
    
        #show merged image after filtering -- rectangles added
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

Algorithm/filtering method based off of bradmontgomery's laser dot tracking program
    https://github.com/bradmontgomery/python-laser-tracker
'''
