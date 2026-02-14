import ctypes
import time

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
    
    
class Mouse:
    def __init__(self):
        self.isDown = False
        
    def sendInput(self, down=True):
        extra = ctypes.c_ulong(0)
        ii_ = Input_I()
        flags = 0x0002 if down else 0x0004
        ii_.mi = MouseInput(0, 0, 0, flags, 0, ctypes.pointer(extra))
        x = Input(ctypes.c_ulong(0), ii_)
        ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))
        
    def clickDown(self):
        if not self.isDown:
            self.sendInput(down=True)
            self.isDown = True
            
    def clickUp(self):
        if self.isDown:
            self.sendInput(down=False)
            self.isDown = False
            
    def release(self):
        self.sendInput(down=False)
        self.isDown = False