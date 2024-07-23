# -*- coding: utf-8 -*-
"""
Created on Fri Mar 29 08:21:01 2024
Class to hold all kind of tools

@author: kristina
"""
from PyQt5.QtWidgets import  QMessageBox
import logging
import datetime
import numpy as np
import os
import cv2
import traceback
from cvzone.SelfiSegmentationModule import SelfiSegmentation



class tools:        
    def __init__(self):
        #kind of global for draw_rectangle() / a mouse callBack where we cannot give parameters in Method
        self.drawing = False
        self.ix, self.iy = -1,-1
        self.ixx, self.iyy = -1,-1
        self.img2 = None
        self.capFrame = None
        print("CV2 in class tools loaded")   
        
        logging.info(self.dt() + 'try..segmentor = SelfiSegmentation() ')
        self.segmentor = SelfiSegmentation()
        
    
    '''
    MsgBox von pyQt / https://doc.qt.io/qt-6/qmessagebox.html  / - OK  Cancel
    '''
    def msgBoxInfoOkCancel(self,txt,title):
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - '
        logging.info(dt + 'msgBoxInfoOkCance()')
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)           
        msgBox.setText(txt)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)  
        v = msgBox.exec()
        return v
    
    def msgBoxYesCancel(self,txt,title):
        dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - '
        logging.info(dt + 'msgBoxYes()')
        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Information)           
        msgBox.setText(txt)
        msgBox.setWindowTitle(title)
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
        return msgBox.exec()
    
        
    def dt(self):
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' - '
    
    def testDevice(self, webcamNr):
       logging.info(self.dt() + 'testDevice() - we now check device: ' + str(webcamNr))
       cap = cv2.VideoCapture(webcamNr)         
       if cap is None or not cap.isOpened():
           print('Warning: unable to open video source: ' + str(webcamNr))
           logging.info(self.dt() + 'Warning: unable to open video source: ' + str(webcamNr))
           return False
       else:
           print('YEAA: this video source seem ok: ' + str(webcamNr))
           logging.info(self.dt() + 'YEAA: this video source seem ok: ' + str(webcamNr))
           return True 


    # delete file if exist
    def removeFile(self, filePath):
        # check whether the file exists
        try:
            if os.path.exists(filePath):
                # delete the file
                os.remove(filePath)
        except Exception as e:
            logging.error(traceback.format_exc())
            print(e)
        
        

    def showInMovedWindow(self,  winname, img, x, y):
        cv2.namedWindow(winname)        # Create a named window
        cv2.moveWindow(winname, x, y)   # Move it to (x,y)...THis way the image ma appear on TOP of other screens!
        cv2.imshow(winname,img)
 
    # FILTER   FILTER   FILTER   FILTER   FILTER   FILTER  FILTER   FILTER    
 
    '''
    CVZONE - opencv filtering 
    #https://github.com/cvzone/cvzone?tab=readme-ov-file#installations
    #https://dev.to/azure/opencv-10-lines-to-remove-the-background-in-an-image-3m98
    '''
    #https://github.com/cvzone/cvzone?tab=readme-ov-file#installations
    #https://dev.to/azure/opencv-10-lines-to-remove-the-background-in-an-image-3m98    
    def bgremove(self, myimage, thresh):
        #BLACK = (0, 0, 0)   PINK = (255, 0, 255)    GREEN = (0, 255, 0)
        #resize office to 640x480       
        
        myimage = self.segmentor.removeBG(myimage,  (0, 255, 0), cutThreshold = thresh)
        print(thresh)
        return myimage
    

    def contourFilter1(self, imgOriPath, originalImg ):
        imgFiltered = cv2.imread(imgOriPath,0) # gray img             
       
        #canny
        sigma = 0.33
        median = np.median(cv2.imread(imgOriPath))
        lower = int(max(0, (1.0 - sigma) * median))
        upper = int(min(255, (1.0 + sigma) * median))
        imgFiltered = cv2.Canny(originalImg , lower, upper)
        
        
        #THRESOULD
        #_, binary = cv2.threshold(imgFiltered, self.contour_theshValue, 255, cv2.THRESH_BINARY)
                  
        #imgFiltered = binary
        
        cnts,_ = cv2.findContours(imgFiltered , cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        print ( "nr contours: {}".format(len(cnts)) )
        oimg = cv2.imread(imgOriPath)
        
        # create a white image
       
        img = np.ones((640, 480, 3), dtype = np.uint8)
        imgW = 255* img
        
        #imgW = Image.new('RGB', (_oriImgWidth, _oriImgHeight), color = (255,255,255))
        for c in cnts:
            area = cv2.contourArea(c)
            print("area: " + str(area))
            if area > 130 :
                cv2.drawContours( imgW, [c], 0, (0,0,0), -1)
        #cv2.drawContours(oimg, cnts, -1, (0,255,0), 3)
        return imgW
        
    #https://stackoverflow.com/questions/73097290/separate-lines-from-handwritten-text-using-opencv-in-python
    #is working well but only gives the OUTER contour!  zb wird das innere von buchstaben wie B ausgeblendet
    def removeLinesFromImageResultIsOutline(self, img, minArea):
        gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
        try:
            th = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
            # create black background of same image shape
            black = np.zeros((img.shape[0], img.shape[1], 3), np.uint8)
            # find contours from threshold image
            contours = cv2.findContours(th, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
            # draw contours whose area is above certain value            
            for c in contours:
                area = cv2.contourArea(c)
                print(str(area))
                if area > minArea:
                    imgX = cv2.drawContours(black,[c],0,(255,255,255),2)  
            imgX = cv2.bitwise_not(imgX)
        except Exception as e:
            logging.error(traceback.format_exc())
            print(e)
            return img
        return imgX
    
   
        
        
        
        