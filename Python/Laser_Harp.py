import cv2
import numpy as np 
from matplotlib import pyplot as plt

#image size from built-in camera:
    #1280x720
    #3 colors
    
#Harp needs 8 quadrants with gaps in between. This gives the following regions
    #-100 px regions with 30px gap on all sides

############# Variables #############
regions = 8
size = 100 #px
boundry = 30 #px
y_position = 720/2 - 80

#image properties
height = 720 #px
width = 1280 #px


#rectangles
rects = [0]*8

#induvidual frames
frames = [0]*regions

#frame_area
frame_area = [0]*regions
trigger_threshold = 7500; #white pixels

#####################################

#video capture
cap = cv2.VideoCapture(0)


#create image for region bitmasking
blank_image = np.zeros((height,width,3), np.uint8)

#create rectangles and region mask
for i in range(0,8):
    rects[i] = (boundry+i*(size + 2*boundry),y_position,100,100)
    
###Color Regions

#hsv
lower_blue = np.array([110,50,50])
upper_blue = np.array([130,255,255])
lower_green = np.array([45,100,100])
upper_green = np.array([75,255,255])
lower_red = np.array([0,100,100])
upper_red = np.array([10,255,255])


#used to check
#cv2.imshow('blank',blank_image)      

while(1):
       
        
        _, frame = cap.read()
    
        #fix up edges (smooth)
        #frame = cv2.GaussianBlur(frame,(9,9),0)
        
        #convert from BGR to HSV 
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        #mask all colors except for blue (threshold the HSV image)
        maskblue = cv2.inRange(hsv,lower_blue, upper_blue)
        maskred = cv2.inRange(hsv, lower_red,upper_red)
        maskgreen = cv2.inRange(hsv,lower_green,upper_green)
        color_mask = maskblue
        
        
        #bitwise_and rectangles and add color mask
        res = cv2.bitwise_and(frame,frame,mask=color_mask)
        
        
        # Regular Thresholding
        ret,thresh = cv2.threshold(res,0,255,cv2.THRESH_BINARY)
        
        #convert to black&white
        color = cv2.cvtColor(thresh, cv2.COLOR_HSV2RGB)
        bw = cv2.cvtColor(thresh,cv2.COLOR_RGB2GRAY)
        
        #create 8 mini-frames
        for i in range(0,len(frames)):
            frames[i] = bw[(width/2 - size/2):(width/2 + size/2),(boundry+i*160):(boundry+100 + i*160)]
            frame_area[i] = cv2.countNonZero(frames[i])
    
        #check the threshold pixel area    
        for i in range(len(frame_area)):
            if frame_area[i] > trigger_threshold:
                cv2.rectangle(bw,(rects[i][0],rects[i][1]),(rects[i][0] + size,rects[i][1]+size),(255,255,255),3,8,0)
                print "Drew rectangle"
        #show images
        cv2.imshow('frame1',frames[0])
        cv2.imshow('frame2',frames[1])
        cv2.imshow('frame3',frames[2])
        cv2.imshow('frame4',frames[3])
        cv2.imshow('frame5',frames[4])
        cv2.imshow('frame6',frames[5])
        cv2.imshow('frame7',frames[6])
        cv2.imshow('frame8',frames[7])
        
        cv2.imshow('fram',bw)
        
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
Created on Nov 13, 2014

@author: travislibsack
'''
