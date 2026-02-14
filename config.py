import numpy as np

ROI = {"left": 1661, "top": 257, "width": 91, "height": 558} # change this if ur using different region

toggleKey = 'C'
exitKey = '27' # esc

# pid controller
pidKP = 0.015
pidKD = 0.008
pidKI = 0.000

minClickTime = 0.005
maxClickTime = 0.100

barMatchThershold = 0.5

# hsv mask to trach fish color
lowerYellow = np.array([15, 40, 150])
upperYellow = np.array([40, 255, 255])

# if it has this color range, ignore
lowerChest = np.array([5, 50, 50])
upperChest = np.array([25, 255, 150])

lowerDark = np.array([0, 0, 0])
upperDark = np.array([180, 255, 120])
