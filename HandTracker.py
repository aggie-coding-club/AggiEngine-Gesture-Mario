# Using python version 3.7.9 for media-pipe
import cv2
import mediapipe as mp
import numpy as np


def dotProduct(v1, v2):
    return v1[0] * v2[0] + v1[1] * v2[1]


def normalize(v):
    mag = np.sqrt(v[0] ** 2 + v[1] ** 2)
    v[0] = v[0] / mag
    v[1] = v[1] / mag
    return v


def gesture(f, hand):
    """
    Uses the open fingers list to recognize gestures
    :param f: list of open fingers (+ num) and closed fingers (- num)
    :param hand: hand information
    :return: string representing the gesture that is detected
    """

    if f[1] > 0 > f[2] and f[4] > 0 > f[3]:
        return "Rock & Roll"
    elif f[0] > 0 and (f[1] < 0 and f[2] < 0 and f[3] < 0 and f[4] < 0):
        thumb_tip = hand.landmark[4]
        thumb_base = hand.landmark[2]

        if thumb_tip.y < thumb_base.y:  # Y goes from top to bottom instead of bottom to top
            return "Thumbs Up"
        else:
            return "Thumbs Down"
    elif f[0] < 0 and f[1] > 0 and f[2] < 0 and (f[3] < 0 and f[4] < 0):
        return "1 finger"
    elif f[0] < 0 and f[1] > 0 and f[2] > 0 and (f[3] < 0 and f[4] < 0):
        return "Peace"
    elif f[0] > 0 and f[1] > 0 and f[2] > 0 and f[3] > 0 and f[4] > 0:
        return "Open Hand"
    elif f[0] < 0 and f[1] < 0 and f[2] < 0 and f[3] < 0 and f[4] < 0:
        return "Fist"
    elif f[0] < 0 and f[1] > 0 and f[2] > 0 and f[3] > 0 and f[4] > 0:
        return "4 fingers"
    elif f[0] < 0 and f[1] > 0 and f[2] > 0 and f[3] > 0 and f[4] < 0:
        return "3 fingers"
    else:
        return "No Gesture"


def straightFingers(hand):
    """
    Calculates which fingers are open and which fingers are closed
    :param hand: media-pipe object of the hand
    :param img: frame with the hand in it
    :return: list of open (+ num) and closed (- num) fingers
    """
    fingerTipIDs = [4, 8, 12, 16, 20]  # list of the id's for the finger tip landmarks
    openFingers = []
    lms = hand.landmark  # 2d list of all 21 landmarks with there respective x, an y coordinates
    for id in fingerTipIDs:
        if id == 4:  # This is for the thumb calculation, because it works differently than the other fingers
            x2, y2 = lms[id].x, lms[id].y  # x, and y of the finger tip
            x1, y1 = lms[id - 2].x, lms[id - 2].y  # x, and y of the joint 2 points below the finger tip
            x0, y0 = lms[0].x, lms[0].y  # x, and y of the wrist
            fv = [x2 - x1, y2 - y1]  # joint to finger tip vector
            fv = normalize(fv)
            pv = [x1 - x0, y1 - y0]  # wrist to joint vector
            pv = normalize(pv)

            thumb = dotProduct(fv, pv)
            # Thumb that is greater than 0, but less than .65 is typically
            # folded across the hand, which should be calculated as "down"
            if thumb > .65:
                openFingers.append(thumb)  # Calculates if the finger is open or closed
            else:
                openFingers.append(-1)

        else:  # for any other finger (not thumb)
            x2, y2 = lms[id].x, lms[id].y  # x, and y of the finger tip
            x1, y1 = lms[id - 2].x, lms[id - 2].y  # x, and y of the joint 2 points below the finger tip
            x0, y0 = lms[0].x, lms[0].y  # x, and y of the wrist
            fv = [x2 - x1, y2 - y1]  # joint to finger tip vector
            fv = normalize(fv)
            pv = [x1 - x0, y1 - y0]  # wrist to joint vector
            pv = normalize(pv)
            openFingers.append(dotProduct(fv, pv))  # Calculates if the finger is open or closed

    return openFingers


class HandInput:

    def __init__(self):
        # Getting openCV ready
        self.cap = cv2.VideoCapture(0)

        # Dimensions of the camera output window
        self.wCam = int(self.cap.get(3))
        self.hCam = int(self.cap.get(4))

        # Getting media-pipe ready
        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(min_detection_confidence=.6)

        # Mouse movement anchor
        self.handDelta = [0, 0]
        self.handCenter = [0.5, 0]
        self.wristPositionHistory = []

        self.currentGesture = ''
        self.lastGesture = ''

    def getHandInput(self):
        """
        Main code loop
        """
        self.handDelta = [0, 1]
        # Gets the image from openCV and gets the hand data from media-pipe
        success, img = self.cap.read()

        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        results = self.hands.process(imgRGB)

        counts = 0
        # if there are hands in frame, calculate which fingers are open and draw the landmarks for each hand
        if results.multi_hand_landmarks:
            for handLms in results.multi_hand_landmarks:
                self.currentGesture = gesture(straightFingers(handLms), handLms)

                # Enters mouse movement mode on thumbs up gesture, setting a mouse anchor point at that position
                if self.lastGesture != "Thumbs Up" and self.lastGesture != "Fist" and self.currentGesture == "Thumbs Up":
                    print("Centering")
                    #self.handCenter = [results.multi_hand_landmarks[0].landmark[0].x, results.multi_hand_landmarks[0].landmark[0].y]

                for point in handLms.landmark:
                    if point.x != 0:
                        self.handDelta[0] += point.x
                        self.handDelta[1] += point.y
                        counts += 1

                self.lastGesture = self.currentGesture
        else:
            print("No Hand")
            self.handDelta = [0, 1]

        return [self.handDelta[0] / counts - self.handCenter[0], self.handDelta[1] / counts - self.handCenter[1]] if counts != 0 else [0, 1]

    def exit(self):
        self.cap.release()
        cv2.destroyAllWindows()
