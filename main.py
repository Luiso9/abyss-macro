import time
import mss
import cv2
import keyboard
import numpy as np
from config import *
from src.inputs import Mouse
from src.detection import Detection
from src.controller import PIDController
from src.kalman import KalmanFilter

def main():
	sct = mss.mss()
	mouse = Mouse()
	visual = Detection()
	pid = PIDController()
	
	kalmanFish = None
	kalmanBar = None
	
	if useKalman:
		kalmanFish = KalmanFilter(kalmanProcessNoise, kalmanMeasurementNoise, kalmanEstimiateError)
		kalmanBar = KalmanFilter(kalmanProcessNoise, kalmanMeasurementNoise, kalmanEstimiateError)
	
	print(f"Macro Loaded. Press '{toggleKey}' to Start/Stop.")
	
	active = False
	lastToggleTime = 0
	clickStart = 0
	targetDuration = 0
	
	#debug state
	windowName = "Debug"
	frameCount = 0
	fpsStartTime = time.time()
	currentFPS = 0.0
	
	while True:        
		if cv2.waitKey(1) & 0xFF == exitKey:
			break
			
		if keyboard.is_pressed(toggleKey) and (time.time() - lastToggleTime > 0.3):
			active = not active
			lastToggleTime = time.time()
			if not active:
				mouse.release()
				pid.reset()
				if kalmanFish:
					kalmanFish.reset()
				if kalmanBar:
					kalmanBar.reset()
				print("PAUSED")
			else:
				print("RUNNING")
		
		rawScreen = sct.grab(ROI)
		frame = np.array(rawScreen)
		frameBGR = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
  
		frameCount += 1
		if frameCount >= 30: 
			elapsed = time.time() - fpsStartTime
			currentFPS = frameCount / elapsed
			frameCount = 0
			fpsStartTime = time.time()
				
		fishY, barY = visual.findObjects(frameBGR)
		
		if useKalman and fishY is not None and barY is not None:
			fishY = kalmanFish.update(fishY)
			barY = kalmanBar.update(barY)
			
		#debug window uncomment to use
		# if active:
		# 	debugFrame = frameBGR.copy()

		# 	cv2.putText(debugFrame, f"FPS: {currentFPS:.1f}", (5, 20), 
        #                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

		# 	if fishY is not None:
		# 		cv2.circle(debugFrame, (45, int(fishY)), 5, (0, 255, 255), -1)
		# 		cv2.putText(debugFrame, f"Fish: {int(fishY)}", (5, 40), 
		# 				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1)
			
		# 	if barY is not None:
		# 		cv2.circle(debugFrame, (45, int(barY)), 5, (255, 0, 0), -1) 
		# 		cv2.putText(debugFrame, f"Bar: {int(barY)}", (5, 60), 
		# 				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 1)

		# 	if fishY is not None and barY is not None:
		# 		error = fishY - barY
		# 		cv2.putText(debugFrame, f"Error: {int(error)}", (5, 80), 
		# 				cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
			
		# 	cv2.imshow(windowName, debugFrame)
		# 	cv2.setWindowProperty(windowName, cv2.WND_PROP_TOPMOST, 1)
		
		
		if active and fishY is not None and barY is not None:
			output = pid.update(barY, fishY)
			
			now = time.time()
			
			if output < 0:
				desiredDuration = abs(output)
				desiredDuration = max(minClickTime, min(maxClickTime, desiredDuration))
				
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