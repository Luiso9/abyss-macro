import time
from config import *

class PIDController:
    def __init__(self):
        self.lastError = 0
        self.intergral = 0
        self.lastTime = time.time()
        
    def reset(self):
        self.lastError = 0
        self.intergral = 0
        self.lastTime = time.time()
        
    def update(self, currentY, targetY):
        currentTime = time.time()
        dt = currentTime - self.lastTime
        if dt <= 0: return 0
        
        error = targetY - currentY
        
        pOut = pidKP * error
        
        self.intergral += error * dt
        self.intergral = max(-100, min(100, self.intergral)) # clamp
        iOut = pidKI * self.intergral
        
        derivative = (error - self.lastError) / dt
        dOut = pidKD * derivative
        
        self.lastError = error
        self.lastTime = currentTime
          
        return pOut + iOut + dOut