import sys
import cv2
import numpy as np
import time
import imutils

def find_circles(frame, mask):

    contours = cv2.findContours(mask.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
    contours = imutils.grab_contours(contours)
    center = None
    fMaxArea = 0
    sMaxArea = 0
    fCnt = None
    sCnt = None
    # Only proceed if at least one contour was found
    if len(contours) > 0:
        # Find the largest contour in the mask, then use
        # it to compute the minimum enclosing circle and
        # centroid
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > fMaxArea :
                fMaxArea = area
                fCnt = cnt
            elif area > sMaxArea:
                sMaxArea = area
                sCnt = cnt




        # c = max(contours, key=cv2.contourArea)
        ((xf, yf), radiusf) = cv2.minEnclosingCircle(fCnt)
        ((xs, ys), radiuss) = cv2.minEnclosingCircle(sCnt)

        x = (xs + xf) /2
        y = (ys + yf) /2
        radius = (radiuss + radiusf) / 2


        Mf = cv2.moments(fMaxArea)
        Ms = cv2.moments(sMaxArea)




        # M = cv2.moments(c)       #Finds center point
        centerf = (int(Mf["m10"] / Mf["m00"]), int(Mf["m01"] / Mf["m00"]))
        centers = (int(Ms["m10"] / Ms["m00"]), int(Ms["m01"] / Ms["m00"]))

        print(centerf)
        # Only proceed if the radius is greater than a minimum value
        if radiusf > 10:
            # Draw the circle and centroid on the frame,
            # then update the list of tracked points
            cv2.circle(frame, (int(x), int(y)), int(radius),
            	(0, 255, 255), 2)
            cv2.circle(frame, centerf, 5, (0, 0, 0), -1)
            cv2.drawContours(frame, fMaxArea, -1, (255, 0, 0), 3)
            cv2.drawContours(frame, sMaxArea, -1, (255, 0, 0), 3)

    return centerf
