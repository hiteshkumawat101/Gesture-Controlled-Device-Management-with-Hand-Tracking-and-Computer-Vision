import cv2
import time 
import numpy as np
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
import HandTrackingModule as htm
from ctypes import cast, POINTER
import pyautogui  

# Function to check if fingers are folded
def fingers_folded(lmlst):
    return all(lmlst[finger][2] < lmlst[finger - 2][2] for finger in [8, 12, 16, 20])

# Function to check if fingers are open
def fingers_open(lmlst):
    return all(lmlst[finger][2] > lmlst[finger - 2][2] for finger in [8, 12, 16, 20])

# Camera setup
wcam, hcam = 2048, 1024
cap = cv2.VideoCapture(0)
cap.set(3, wcam)
cap.set(4, hcam)

# Hand detector setup
ptime = 0
hand = htm.HandDetector(detection=0.9)

# Audio setup
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volrange = volume.GetVolumeRange()

minvol = volrange[0]
maxvol = volrange[1]

# Screenshot mode setup
screenshot_mode = False
min_brightness = 10  
max_brightness = 100  
brightness_mode = False 

while True:
    success, img = cap.read()
    img = hand.findhands(img)
    lmlst = hand.handpositions(img)

    if len(lmlst) != 0:
        ds_4_20 = math.hypot(lmlst[20][1] - lmlst[4][1], lmlst[20][2] - lmlst[4][2])

        # Handle screenshot mode
        if fingers_folded(lmlst):  
            screenshot_mode = True
            cv2.putText(img, "Ready for Screenshot", (50, 100), 1, 2, (0, 255, 255), 3)

        if screenshot_mode and fingers_open(lmlst):  
            screenshot_mode = False  
            pyautogui.screenshot("screenshot.png")  
            cv2.putText(img, "Screenshot Taken!", (50, 150), 1, 2, (0, 255, 0), 3)

        # Adjust brightness using hand gesture
        if ds_4_20 < 50:
            if not brightness_mode:  
                brightness_mode = True
                time.sleep(0.3)
            else:  
                brightness_mode = False
                time.sleep(0.3)
        
            if brightness_mode:
                bx1, by1 = lmlst[8][1], lmlst[8][2]  
                bx2, by2 = lmlst[12][1], lmlst[12][2]  
                bcx, bcy = (bx1 + bx2) // 2, (by1 + by2) // 2  

                cv2.circle(img, (bx1, by1), 15, (200, 25, 0), cv2.FILLED)
                cv2.circle(img, (bx2, by2), 15, (200, 25, 0), cv2.FILLED)
                cv2.circle(img, (bcx, bcy), 15, (200, 25, 0), cv2.FILLED)
                cv2.line(img, (bx1, by1), (bx2, by2), (200, 25, 0), 2)

                length = math.hypot(bx2 - bx1, by2 - by1)
                brightness = np.interp(length, [50, 300], [min_brightness, max_brightness])
                sbc.set_brightness(int(brightness))

                brightness_bar = np.interp(length, [50, 300], [350, 120])
                cv2.rectangle(img, (50, 120), (85, 350), (0, 255, 0), 3)
                cv2.rectangle(img, (50, int(brightness_bar)), (85, 350), (0, 255, 0), cv2.FILLED)
                cv2.putText(img, f'{int(brightness)}%', (40, 400), 1, 2, (255, 255, 255), 3)
            
        else:
            x1, y1 = lmlst[4][1], lmlst[4][2]
            x2, y2 = lmlst[8][1], lmlst[8][2]
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            cv2.circle(img, (x1, y1), 15, (200, 25, 0), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (200, 25, 0), cv2.FILLED)
            cv2.circle(img, (cx, cy), 15, (200, 25, 0), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (200, 25, 0), 2)

            length = math.hypot(x2 - x1, y2 - y1)
            vol = np.interp(length, [50, 300], [minvol, maxvol])
            volbar = np.interp(length, [50, 300], [350, 120])
            volume.SetMasterVolumeLevel(vol, None)

            cv2.rectangle(img, (50, 120), (85, 350), (0, 255, 0), 3)
            cv2.rectangle(img, (50, int(volbar)), (85, 350), (0, 255, 0), cv2.FILLED)

    timestamp = time.time()
    fps = 1 / (timestamp - ptime)
    ptime = timestamp
    cv2.putText(img, f'FPS:{int(fps)}', (30, 50), 1, 2, (255, 0, 0), 3)

    cv2.imshow("Img", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
