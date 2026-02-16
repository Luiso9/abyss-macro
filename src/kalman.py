import numpy as np

class KalmanFilter:
    def __init__(self, processNoise=0.01, measurementNoise=0.1, estimateError=1.0):
        self.pN = processNoise
        self.mN = measurementNoise
        self.eErr = estimateError
        self.sE = 0.0 # state estimate
        self.gain = 0 # gain
        
    def update(self, measurement):
        if measurement is None:
            return None
        
        self.eErr = self.eErr + self.pN
        # if measurement noise bigger or huge the gain become smaller if esimate error bigger the gain become bigger
        self.gain = self.eErr / (self.eErr + self.mN)
        self.sE = self.sE + self.gain * (measurement - self.sE)
        self.eErr = (1 - self.gain) * self.eErr
    
        return self.sE

    def reset(self):
        self.sE = 0.0
        self.gain = 0.0
        self.eErr = 1.0
    