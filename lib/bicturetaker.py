import time
import cv2
from typing import Dict, List, Tuple
from pupil_apriltags import Detector
import numpy as np

def extrude_corner(center_current: Tuple[int, int], corner: Tuple[int, int]):
    """
    Returns a point relative to the current tag which responds to the outer edge of the white rim.

    Center = C
    Eck = E

    C>O := Vector from C to O
    X>Y = Y - X

    OC + CE * 4/3 = OC + CA | - OC
    (OE-OC) * 4/3 = OA-OC 
    OC + 4/3OE - 4/3OC = OA

    (1 - 4/3)OC + 4/3OE = OA
    -1/3OC + 4/3OE = OA

    """

    # actual_corner = np.array(center_current)*(-1/3) + np.array(corner)*4/3

    actual_corner = (
            center_current[0] * (-1/3) + corner[0] * 4/3,
            center_current[1] * (-1/3) + corner[1] * 4/3,
            )

    return actual_corner

class Smoother:
    history: List[np.ndarray] #ndarray is [4,2]
    def __init__(self) -> None:
        self.history = []

    def push(self, points: np.ndarray): 
        """
        points: [4,2]
        """
        self.history.append(points)
        if len(self.history) > 5:
            self.history.pop(0)

    def points(self) -> List[Tuple[int, int]]:
        return np.average(self.history, 0)

class Bicturetaker:

    def __init__(self, resolution=(1920, 1080), family='tag16h5', *, cam_index, tag_timeout):
        self.cap = cv2.VideoCapture(cam_index)
        self.resolution = resolution
        self.cap.set(3, self.resolution[0])
        self.cap.set(4, self.resolution[1])
        self.detector = Detector(families=family,
                        nthreads=8,
                        quad_decimate=2.0,
                        quad_sigma=0.0,
                        refine_edges=0,
                        decode_sharpening=0.25,
                        debug=0)
        self.last_results = None
        self.tag_timeout = tag_timeout
        self.last_read = None
        self.matrix = None

        self.smoother = Smoother()


    def take_bicture(self) -> Dict:
        """
        Takes a 🅱️icture, analyzes it for Apriltags and stretches it.
        Currently searches for 16h5 tags with IDs 0-3 and stretches it as follows:
        +---------------+
        |3             2|
        |               |
        |0             1|
        +---------------+
        This may seem kind of autistic, but pupil-apriltags orders their corners in the same way, so this is more consistent when processing.
        """
        _, img = self.cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_RGBA2GRAY)

        t = time.time()
        if self.last_read is None or t - self.last_read >= self.tag_timeout:
            self.last_read = t
            results = []
            if self.last_results:
                for last_result in self.last_results:
                    x1 = int(min([x for (x, _) in last_result.corners])) - 10
                    x1 = x1 if x1 >= 0 else 0
                    x2 = int(max([x for (x, _) in last_result.corners])) + 10
                    x2 = x2 if x1 < img.shape[1] else img.shape[1]
                    y1 = int(min([y for (_, y) in last_result.corners])) - 10
                    y1 = y1 if y1 >= 0 else 0
                    y2 = int(max([y for (_, y) in last_result.corners])) + 10
                    y2 = y2 if y2 < img.shape[0] else img.shape[0]
                    res = self.detector.detect(gray[y1:y2,x1:x2])
                    if len(res) != 1:
                        break
                    for i in range(4):
                        res[0].corners[i] += (x1, y1)
                    res[0].center += (x1, y1)
                    results.append(res[0])
            if len(results) != 4:
                results = self.detector.detect(gray)

            results = [result for result in results if result.tag_id in range(4)]

            #for result in results:
            #    cv2.fillPoly(img, np.int32([result.corners]), (255, 255, 255))
            #    cv2.circle(img, np.int32(result.center), 5, (255, 0, 0), 3)

            if len(results) == 4:
                actual = np.zeros([4, 2], dtype=np.float32)
                for result in results:
                    id = result.tag_id
                    if actual[id][0] != 0 or actual[id][1]:
                        return { "raw": img }
                    actual[id] = extrude_corner(result.center, result.corners[id])

                self.last_results = results

                self.smoother.push(actual)

                target = np.float32([
                    [0.0, self.resolution[1]],
                    [self.resolution[0], self.resolution[1]],
                    [self.resolution[0], 0.0],
                    [0.0, 0.0]
                ])
                self.matrix = cv2.getPerspectiveTransform(self.smoother.points(), target)
        
        ret = { "raw": img }
        if self.matrix is not None:
            distorted = cv2.warpPerspective(img, self.matrix, self.resolution)
            ret["img"] = distorted
        else:  
            last_result = None
        return ret

    def __del__(self):
        #======= TODO!!!!!!!!!! ==========
        # WTF???? 
        # When manually calling these fuckers everything works.
        # When just calling del self.detector this crashes on linux.
        print("0")
        self.detector.libc.tag16h5_destroy.restype = None
        self.detector.libc.tag16h5_destroy(self.detector.tag_families["tag16h5"])
        print("A")
        # ========= BIGGER TODO!!!!!!!!!!! ========
        # This will leak.
        # self.detector.libc.apriltag_detector_destroy(self.detector.tag_detector_ptr)
        self.detector.tag_detector_ptr = None
        print("B")
        del self.detector

        print("C")
        self.cap.release()


def main():
    bt = Bicturetaker(cam_index=1)
    while True:
        d = bt.take_bicture()

        if d is not None and "img" in d:
            img = cv2.resize(d["img"], (960, 540))
            cv2.imshow("Image: ", img)
            key = cv2.waitKey(1)
            if key == 27:
                return
        else:
            print("no img...")

if __name__ == '__main__':
    main()
