import cv2
from pupil_apriltags import Detector
import numpy as np
from icecream import ic

class Bicturetaker:

    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 1920)
        self.cap.set(4, 1080)
        self.detector = Detector(families='tag16h5',
                        nthreads=8,
                        quad_decimate=1.0,
                        quad_sigma=0.0,
                        refine_edges=1,
                        decode_sharpening=0.25,
                        debug=0)
        self.last_results = []

    def take_bicture(self):
        _, img = self.cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)
        results = self.detector.detect(gray)

        results = [result for result in results if result.tag_id in range(4)]
        ic(len(results))

        if len(results) == 4:
            actual = np.zeros([4, 2], dtype=np.float32)
            for result in results:
                ic(result)
                id = result.tag_id
                if id == 0:
                    actual[id] = result.corners[id]
                elif id == 1:
                    actual[id] = result.corners[id]
                elif id == 2:
                    actual[id] = result.corners[id]
                elif id == 3:
                    actual[id] = result.corners[id]
                else:
                    print("REEEEEEEEEEEEEE " + str(id))

            target = np.float32([
                [0.0, img.shape[0]],
                [img.shape[1], img.shape[0]],
                [img.shape[1], 0.0],
                [0.0, 0.0]
            ])
            ic(actual)
            ic(target)
            matrix = cv2.getPerspectiveTransform(actual, target)
            distorted = cv2.warpPerspective(img, matrix, (img.shape[1], img.shape[0]))

            cv2.imshow("Distorted: ", cv2.resize(distorted, (640, 480)))

        cv2.imshow("Image: ", img)
        key = cv2.waitKey(10)
        if key == 27:
            pass


def main():
    bt = Bicturetaker()
    while True:
        bt.take_bicture()

if __name__ == '__main__':
    main()
