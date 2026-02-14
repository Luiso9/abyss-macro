import cv2
import numpy as np
import os
import sys
from config import *

class Detection:
    def __init__(self):
        try:
            self.barImg = cv2.imread(self._resourcePath(os.path.join("image", "bar_1.png")), 0)
            self.hBar, self.wBar = self.barImg.shape
            self.barMask = np.ones(self.barImg.shape, dtype="uint8") * 255
            cv2.rectangle(self.barMask, (8, 8), (self.wBar - 8, self.hBar - 8), 0, -1)
        except Exception as e:
            print(f"Warning: Template not found. {e}") 
            
    def _resourcePath(self, relativePath):
        try:
            base_path = sys._MEIPASS
        except Exception:
            basePath = os.path.abspath(".")
        return os.path.join(basePath, relativePath)
    
    def findObjects(self, frameBGR):
        fishY = None
        barY = None
        
        gray = cv2.cvtColor(frameBGR, cv2.COLOR_BGR2GRAY)
        
        if hasattr(self, 'barImg'):
            res = cv2.matchTemplate(gray, self.barImg, cv2.TM_CCOEFF_NORMED, mask=self.barMask)
            _, maxVal, _, maxLoc = cv2.minMaxLoc(res)
            
            if maxVal > barMatchThershold:
                barY = maxLoc[1] + (self.hBar // 2)

        if barY is not None:
            hsv = cv2.cvtColor(frameBGR, cv2.COLOR_BGR2HSV)
            maskYellow = cv2.inRange(hsv, lowerYellow, upperYellow)
            contours, _ = cv2.findContours(maskYellow, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                largest_cnt = max(contours, key=cv2.contourArea)
                
                if cv2.contourArea(largest_cnt) > 50:
                    x, y, w, h = cv2.boundingRect(largest_cnt)
                    fishY = y + (h // 2)
                    cv2.rectangle(frameBGR, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
        return fishY, barY