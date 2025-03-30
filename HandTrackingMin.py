import cv2
import mediapipe as mp
import numpy as np
import time

class HandDetector():
    """
    Class to detect hand landmarks and track hand movements.
    """
    def __init__(self, mode=False, max_hand=2, detection=0.5, tracking=0.5):
        self.mode = mode
        self.max_hand = max_hand
        self.detection = detection
        self.tracking = tracking
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands()
        self.mpdraw = mp.solutions.drawing_utils

    def findhands(self, img):
        """
        Detect hands and draw landmarks on the image.
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        res = self.hands.process(imgRGB)
        rst = res.multi_hand_landmarks

        if rst:
            for handlm in rst:
                self.mpdraw.draw_landmarks(img, handlm, self.mpHands.HAND_CONNECTIONS)
        
        return img

    def handpositions(self, img, handNo=0):
        """
        Extract hand positions from the image.
        """
        lmlist = []
        if self.res.multi_hand_landmarks:
            if handNo < len(self.res.multi_hand_landmarks): 
                myhand = self.res.multi_hand_landmarks[handNo]
                for id, lm in enumerate(myhand.landmark):
                    h, w, c = img.shape  
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    lmlist.append([id, cx, cy])
        return lmlist
