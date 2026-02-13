import cv2
import numpy as np
import mss
import keyboard
import time
import ctypes
import os
import sys

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

PUL = ctypes.POINTER(ctypes.c_ulong)
class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort), ("wScan", ctypes.c_ushort), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong), ("wParamL", ctypes.c_ushort), ("wParamH", ctypes.c_ushort)]
class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long), ("dy", ctypes.c_long), ("mouseData", ctypes.c_ulong), ("dwFlags", ctypes.c_ulong), ("time", ctypes.c_ulong), ("dwExtraInfo", PUL)]
class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput), ("mi", MouseInput), ("hi", HardwareInput)]
class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ii", Input_I)]

def fast_click(down=True):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    flags = 0x0002 if down else 0x0004
    ii_.mi = MouseInput(0, 0, 0, flags, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(0), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))

X1, Y1, X2, Y2 = 1661, 257, 1752, 815
BAR_THRESHOLD = 0.5 
TOGGLE_KEY = 'C'

# Yellow HSV Range
LOWER_YELLOW = np.array([15, 80, 100])
UPPER_YELLOW = np.array([40, 255, 255])

sct = mss.mss()

try:
    bar_image_path = resource_path(os.path.join("image", "bar_1.png"))
    bar_temp = cv2.imread(bar_image_path, 0)
    h_bar, w_bar = bar_temp.shape
    
    bar_mask = np.ones(bar_temp.shape, dtype="uint8") * 255
    margin = 8 
    cv2.rectangle(bar_mask, (margin, margin), (w_bar - margin, h_bar - margin), 0, -1)
    
except Exception as e:
    print(f"Error {e}")
    sys.exit(1)

print(f"Press '{TOGGLE_KEY}' to toggle ON/OFF.")

active = False
last_toggle = 0
mouse_is_down = False

Kp = 0.015  # how aggressively to respond
Kd = 0.008  # damping to prevent overshoot
Ki = 0.0    # gain

# PID state
last_error = 0
integral = 0
last_time = time.time()

MIN_CLICK_TIME = 0.005 
MAX_CLICK_TIME = 0.100 
click_start_time = 0
target_click_duration = 0

while True:
    if keyboard.is_pressed(TOGGLE_KEY) and (time.time() - last_toggle > 0.3):
        active = not active
        last_toggle = time.time()
        if not active:
            fast_click(down=False)
            mouse_is_down = False
            integral = 0  # Reset integral
        print(f"State changed: {'RUNNING' if active else 'PAUSED'}")

    sct_img = sct.grab({"left": X1, "top": Y1, "width": X2-X1, "height": Y2-Y1})
    frame = np.array(sct_img)
    frame_bgr = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
    
    fishY = None
    barY = None
    current_action = "Idle"

    # anchor detect by color
    hsv = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2HSV)
    fish_mask = cv2.inRange(hsv, LOWER_YELLOW, UPPER_YELLOW)
    contours, _ = cv2.findContours(fish_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        largest_cnt = max(contours, key=cv2.contourArea)
        if cv2.contourArea(largest_cnt) > 50:
            x, y, w, h = cv2.boundingRect(largest_cnt)
            fishY = y + (h // 2)
            cv2.rectangle(frame_bgr, (x, y), (x+w, y+h), (0, 255, 0), 2)

    # the moveable bar detection
    gray = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2GRAY)
    res_bar = cv2.matchTemplate(gray, bar_temp, cv2.TM_CCOEFF_NORMED, mask=bar_mask)
    _, max_val_bar, _, max_loc_bar = cv2.minMaxLoc(res_bar)

    if max_val_bar > BAR_THRESHOLD:
        barY = max_loc_bar[1] + (h_bar // 2)
        top_left = max_loc_bar
        bottom_right = (top_left[0] + w_bar, top_left[1] + h_bar)
        cv2.rectangle(frame_bgr, top_left, bottom_right, (0, 0, 255), 2)
        
        inner_tl = (top_left[0] + margin, top_left[1] + margin)
        inner_br = (bottom_right[0] - margin, bottom_right[1] - margin)
        cv2.rectangle(frame_bgr, inner_tl, inner_br, (255, 0, 0), 1)

    # PID CONTROL
    if active and fishY is not None and barY is not None:
        current_time = time.time()
        dt = current_time - last_time
        
        if dt > 0:
            error = fishY - barY
            p_output = Kp * error
            
            integral += error * dt
            integral = max(-100, min(100, integral))
            i_output = Ki * integral
            
            derivative = (error - last_error) / dt
            d_output = Kd * derivative
          
            pid_output = p_output + i_output + d_output
           
            if pid_output < 0:
                desired_click_duration = abs(pid_output)
                desired_click_duration = max(MIN_CLICK_TIME, min(MAX_CLICK_TIME, desired_click_duration))
                
                #new click cycle
                if not mouse_is_down:
                    fast_click(down=True)
                    mouse_is_down = True
                    click_start_time = current_time
                    target_click_duration = desired_click_duration
                    current_action = f"CLICKING ({desired_click_duration*1000:.0f}ms)"
                
                elif current_time - click_start_time >= target_click_duration:
                    fast_click(down=False)
                    mouse_is_down = False
                    current_action = f"RELEASED"
            
            else:
                if mouse_is_down:
                    fast_click(down=False)
                    mouse_is_down = False
                current_action = f"IDLE (error:{error:.1f})"
            
            last_error = error
            last_time = current_time
            
            #print(f"\rError:{error:+6.1f} | P:{p_output:+.3f} D:{d_output:+.3f} | {current_action}        ", end='', flush=True)

    elif not active:
        current_action = "PAUSED"
    else:
        if mouse_is_down:
            fast_click(down=False)
            mouse_is_down = False
        current_action = "Searching..."

    #cv2.imshow(window_name, frame_bgr)

    if cv2.waitKey(1) & 0xFF == 27:
        break

if mouse_is_down:
    fast_click(down=False)
cv2.destroyAllWindows()