from pupil_apriltags import Detector
import cv2
from icecream import ic
import numpy as np

detector = Detector(families='tag36h11',
                       nthreads=1,
                       quad_decimate=1.0,
                       quad_sigma=0.0,
                       refine_edges=1,
                       decode_sharpening=0.25,
                       debug=0)

cap = cv2.VideoCapture(0)

def intp(point):
    return (int(point[0]), int(point[1]))

def oline(inimg, a, b, c=(255, 0, 0)):
    return cv2.line(inimg, intp(a), intp(b), c, 5)

def drsquare(inimg, corners):
    out = oline(inimg, corners[0], corners[1], (255, 0, 0))
    out = oline(out, corners[1], corners[2], (0, 255, 0))
    out = oline(out, corners[2], corners[3], (0, 0, 255))
    out = oline(out, corners[3], corners[0], (128, 128, 0))
    return out

def mksquare(size):
    return np.float32([
           [0.0, size],
           [size, size],
           [size, 0.0],
           [0.0, 0.0]
            ])
            

while True:
    _, img = cap.read()



    gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY);
    
    result = detector.detect(gray)

    if len(result) > 0:
        res = result[0]
        ic(res)
        # info = cv2.line(img, (int(corn[1][0], int(corn[1][1])), (int(corn[2][0]), int(corn[2][1]))), (0,255,0), 5)
        # cv2.imshow("Info: ", info)

        trans = np.identity(3)
        # trans[0][2] = -res.center[0] + img.shape[1]/200
        # trans[1][2] = -res.center[1] + img.shape[1]/200
        trans[2][2] = 40
        ic(trans)
    
        #rightsquare = mksquare(40);
        
        #drsquare(img, res.corners)
        #drsquare(img, rightsquare)
#
        #transformedsquare = cv2.perspectiveTransform(rightsquare, res.homography)
        #drsquare(img,transformedsquare)
#
        #cv2.imshow("Info: ", img)

        ic(res.corners)
        target = mksquare(100)
        ic(target)
        matrix = cv2.getPerspectiveTransform(np.float32(res.corners), target)
        distorted = cv2.warpPerspective(img, matrix, (500, 600))

        #distorted = cv2.warpPerspective(img, trans*res.homography, (img.shape[1],img.shape[0]), cv2.WARP_INVERSE_MAP)
        cv2.imshow("Distorted: ", distorted)

    cv2.imshow("Image: ", img)
    key = cv2.waitKey(20)
    if key == 27:
        break


# detector.detect()

