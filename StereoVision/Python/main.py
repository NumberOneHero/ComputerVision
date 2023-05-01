import sys
import cv2
import numpy as np
import time
import imutils
from matplotlib import pyplot as plt

# Functions
import HSV_filter as hsv
import shape_recognition as shape
import triangulation as tri
#import calibration as calib


# Open both cameras
def empty(a):
    pass



from urllib.request import urlopen

pTime = 0


cv2.namedWindow("HSV")
cv2.resizeWindow("HSV",640,1000)
cv2.createTrackbar("HUE Min","HSV",0,179,empty)
cv2.createTrackbar("SAT Min","HSV",0,255,empty)
cv2.createTrackbar("VALUE Min","HSV",37,255,empty)
cv2.createTrackbar("HUE Max","HSV",179,179,empty)
cv2.createTrackbar("SAT Max","HSV",29,255,empty)
cv2.createTrackbar("VALUE Max","HSV",255,255,empty)
cv2.createTrackbar("B","HSV",650,1000,empty)
cv2.createTrackbar("ALPHA","HSV",570,1000,empty)
cv2.createTrackbar("F","HSV",483,500,empty)






cv_file = cv2.FileStorage("params_py.xml", cv2.FILE_STORAGE_READ)
Left_Stereo_Map_x = cv_file.getNode("Left_Stereo_Map_x").mat()
Left_Stereo_Map_y = cv_file.getNode("Left_Stereo_Map_y").mat()
Right_Stereo_Map_x = cv_file.getNode("Right_Stereo_Map_x").mat()
Right_Stereo_Map_y = cv_file.getNode("Right_Stereo_Map_y").mat()
cv_file.release()










ret_left = False
ret_right = False

btsR= b''
btsL = b''
# change to your ESP32-CAM ip
urlLeft = "http://192.168.50.159:81/stream"
urlRight = "http://192.168.50.246:81/stream"
CAMERA_BUFFRER_SIZE = 1024
streamLeft = urlopen(urlLeft)
streamRight = urlopen(urlRight)
num=0

ret = None

imgR = None
imgL = None
def Esp32Frame(stream,bts,ret):
    jpghead = -1
    jpgend = -1

    while (jpghead < 0 or jpgend < 0):

        bts += stream.read(CAMERA_BUFFRER_SIZE)

        if jpghead < 0 :
            jpghead = bts.find(b'\xff\xd8')


        if jpgend < 0:


            jpgend = bts.find(b'\xff\xd9')


        if jpghead > -1 and jpgend > -1 and jpgend>jpghead:
            jpg = bts[jpghead:jpgend + 2]
            bts = bts[jpgend + 2:]


            img = cv2.imdecode(np.frombuffer(jpg, dtype=np.uint8), cv2.IMREAD_UNCHANGED)
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)


            k = cv2.waitKey(10)
            ret = True



        elif jpghead > -1 and jpgend > -1 and jpgend<jpghead :
            jpgend = -1
            jpghead = -1
            ret= False



    return bts , img,ret






frame_rate = 15  #Camera frame rate (maximum at 120 fps)

B = 6.5 #Distance between the cameras [cm]
f = 4.13             #Camera lense's focal length [mm]
alpha = 53.3
#alpha = 56.56531197650641       #Camera field of view in the horisontal plane [degrees]


#Initial values
count = -1

while(True):
    #
    # alpha = cv2.getTrackbarPos("ALPHA", "HSV")* 0.1
    # B = cv2.getTrackbarPos("B", "HSV") * 0.01
    # f = cv2.getTrackbarPos("F", "HSV") * 0.01
    print(B)
    print(alpha)

################## CALIBRATION #########################################################
    ptime = time.time()
    btsL, frame_left, ret_left = Esp32Frame(streamLeft, btsL, ret_left)
    btsR, frame_right, ret_right = Esp32Frame(streamRight, btsR, ret_right)
    ptime = time.time()  - ptime
    print(ptime)





    frame_right = cv2.remap(frame_right,
                       Right_Stereo_Map_x,
                       Right_Stereo_Map_y,
                       cv2.INTER_LANCZOS4,
                       cv2.BORDER_CONSTANT,
                       0)

    frame_left = cv2.remap(frame_left,
                           Left_Stereo_Map_x,
                           Left_Stereo_Map_y,
                           cv2.INTER_LANCZOS4,
                           cv2.BORDER_CONSTANT,
                           0)

# Setting the updated parameters before c
    cv2.imshow("left",frame_left)
    cv2.imshow("right", frame_right)


    #frame_right, frame_left = calib.undistorted(frame_right, frame_left)

########################################################################################

    # If cannot catch any frame, break
    if ret_right==False or ret_left==False:                    
        break

    else:
        # APPLYING HSV-FILTER:
        mask_right = hsv.add_HSV_filter(frame_right, 1)
        mask_left = hsv.add_HSV_filter(frame_left, 1)

        # Result-frames after applying HSV-filter mask
        res_right = cv2.bitwise_and(frame_right, frame_right, mask=mask_right)
        res_left = cv2.bitwise_and(frame_left, frame_left, mask=mask_left)

        # APPLYING SHAPE RECOGNITION:
        circles_right = shape.find_circles(frame_right, mask_right)
        circles_left = shape.find_circles(frame_left, mask_left)

        # Hough Transforms can be used aswell or some neural network to do object detection


        ################## CALCULATING BALL DEPTH #########################################################

        # If no ball can be caught in one camera show text "TRACKING LOST"
        if np.all(circles_right) == None or np.all(circles_left) == None:
            cv2.putText(frame_right, "TRACKING LOST", (75,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255),2)
            cv2.putText(frame_left, "TRACKING LOST", (75,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,255),2)

        else:
            # Function to calculate depth of object. Outputs vector of all depths in case of several balls.
            # All formulas used to find depth is in video presentaion
            depth = tri.find_depth(circles_right, circles_left, frame_right, frame_left, B, f, alpha)

            cv2.putText(frame_right, "TRACKING", (75,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (124,252,0),2)
            cv2.putText(frame_left, "TRACKING", (75,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (124,252,0),2)
            cv2.putText(frame_right, "Distance: " + str(round(depth,3)), (200,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (124,252,0),2)
            cv2.putText(frame_left, "Distance: " + str(round(depth,3)), (200,50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (124,252,0),2)
            # Multiply computer value with 205.8 to get real-life depth in [cm]. The factor was found manually.
            print("Depth: ", depth)                                            


        # Show the frames
        # cv2.imshow("frame right", frame_right)
        # cv2.imshow("frame left", frame_left)

        cv2.imshow("mask right", mask_right)
        cv2.imshow("mask left", mask_left)
        Hori = np.concatenate((frame_left, frame_right), axis=1)
        Hori = cv2.resize(Hori, (1620, 1080))

        cv2.imshow("Hori", Hori)

        # Hit "q" to close the window
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


# Release and destroy all windows before termination


cv2.destroyAllWindows()
