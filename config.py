import numpy as np

ROI = {"left": 1661, "top": 257, "width": 91, "height": 558} # change this if ur using different region

toggleKey = 'C'
exitKey = '27' # esc

# pid controller
pidKP = 0.025
pidKD = 0.012
pidKI = 0.000

minClickTime = 0.003
maxClickTime = 0.080

barMatchThershold = 0.5

# hsv mask to trach fish color
lowerYellow = np.array([15, 40, 150])
upperYellow = np.array([40, 255, 255])

# if it has this color range, ignore
lowerChest = np.array([5, 50, 50])
upperChest = np.array([25, 255, 150])

lowerDark = np.array([0, 0, 0])
upperDark = np.array([180, 255, 120])

# im trying to use Kalman Filter
useKalman = True
kalmanProcessNoise = 0.05
kalmanMeasurementNoise = 0.5
kalmanEstimiateError = 1.0
