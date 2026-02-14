import time
import mss
import cv2
import keyboard
import numpy as np
from config import *
from src.inputs import Mouse
from src.detection import Detection
from src.controller import PIDController

def main():
    sct = mss.mss()
    mouse = Mouse()
    visual = Detection()
    pid = PIDController()
    
    print(f"Macro Loaded. Press '{toggleKey}' to Start/Stop.")
    
    active = False
    lastToggleTime = 0
    
    clickStart = 0
    targetDuration = 0
    
    windowName = "Debug"
    
    while True:        
        if keyboard.is_pressed(toggleKey) and (time.time() - lastToggleTime > 0.3):
            active = not active
            lastToggleTime = time.time()
            if not active:
                mouse.release()
                pid.reset()
                print("PAUSED")
            else:
                print("RUNNING")
    
        if cv2.waitKey(1) & 0xFF == exitKey:
            break
        
        rawScreen = sct.grab(ROI)
        frame = np.array(rawScreen)
        frameBGR = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
        
        fishY, barY = visual.findObjects(frameBGR)
        
        if active:
             cv2.imshow(windowName, frameBGR)
             cv2.setWindowProperty(windowName, cv2.WND_PROP_TOPMOST, 1)
        
        key = cv2.waitKey(1) & 0xFF
        if key == exitKey or key == 27: # Exit on ESC
            break
        
        if active and fishY is not None and barY is not None:
            output = pid.update(barY, fishY)
            
            now = time.time()
            
            if output < 0:
                desiredDuration = abs(output)
                desiredDuration = max(minClickTime, min(maxClickTime, desiredDuration))
                
                now = time.time()
                if not mouse.isDown:
                    mouse.clickDown()
                    clickStart = now
                    targetDuration = desiredDuration
                elif now - clickStart >= targetDuration:
                    mouse.clickUp()
                    
            else:
                if mouse.isDown:
                    mouse.clickUp()
                    
        elif not active:
            time.sleep(0.01)
        else:
            if mouse.isDown: mouse.clickUp()
            
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()