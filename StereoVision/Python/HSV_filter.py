import sys
import cv2
import numpy as np
import time


def add_HSV_filter(frame, camera):

	# Blurring the frame
    blur = cv2.GaussianBlur(frame,(5,5),0)

    # Converting RGB to HSV
    hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)



    h_min = cv2.getTrackbarPos("HUE Min","HSV")
    h_max = cv2.getTrackbarPos("HUE Max", "HSV")
    s_min = cv2.getTrackbarPos("SAT Min", "HSV")
    s_max = cv2.getTrackbarPos("SAT Max", "HSV")
    v_min = cv2.getTrackbarPos("VALUE Min", "HSV")
    v_max = cv2.getTrackbarPos("VALUE Max", "HSV")


    lower = np.array([h_min,s_min,v_min])
    upper = np.array([h_max,s_max,v_max])

    if(camera == 1):
        mask = cv2.inRange(frame,lower,upper)
    else:
        mask = cv2.inRange(frame,lower,upper)


    # Morphological Operation - Opening - Erode followed by Dilate - Remove noise
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    return mask
