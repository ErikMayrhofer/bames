from sys import hash_info
from typing import List, Tuple
import cv2
import numpy as np
from cv2.cv2 import imshow, rectangle


def extract_colors(image, lower, higher):

    # Into HSV and filter out stuff that actually has colors.
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    if lower[0] <= higher[0]:
        mask = cv2.inRange(img_hsv, lower, higher)
    else:
        mask1 = cv2.inRange(img_hsv, (0, lower[1], lower[2]), higher)
        mask2 = cv2.inRange(img_hsv, lower, (179, higher[1], higher[2]))
        mask = mask1 + mask2

    # Back to normal again.
    mask = cv2.medianBlur(mask, 5)

    return mask


def intersect(line_a, line_b):
    """
    line_a is a straight line defined by: I = line_a[0] + x*line_a[1]
    line_b is a straight line defined by: I = line_b[0] + y*line_b[1]

    Now we say that I = I and solve for x using Cramer's rule
    """
    A = np.array(line_a[0])
    B = np.array(line_a[1])
    # A + xB
    # print(A, "+ x", B)

    D = np.array(line_b[0])
    K = np.array(line_b[1])
    # print(D, "+ y", K)
    # D + yK

    b = D - A

    mat_A = np.array([B, -K])
    mat_Ax = np.array([b, -K])
    # print(mat_A)
    # print(mat_Ax)

    x = np.linalg.det(mat_Ax)/np.linalg.det(mat_A)

    I = A + x*B

    return I

"""
print(intersect(
        [
            [2, 3], [0, -1]
            ],
        [
            [3, 1], [-1, 0]
            ]
        ))
"""


# BGR -> RED, GREEN, BLUE, PURPLE
CLRS = [
                (0,0, 255),
                (0, 255, 0),
                (255, 0, 0),
                (255, 0, 255)
                ]

def verts_to_rect(verts: np.ndarray):
    """
    Takes in the corners of a Rectangle and returns
    ((center_x, center_y),width,height,angle)
    """
    center = np.average(verts, 0)

    width = np.linalg.norm(verts[0]-verts[1], 2) 
    height = np.linalg.norm(verts[1]-verts[2], 2) 


    angle = np.arctan2(*(verts[1] - verts[2]).T) * -1 # Top left is 0,0 -> Y axis is flipped
    
    if height > width:
        height, width = width, height
        angle += np.pi/2

    return center, width, height, angle

def betect_rectangles(image) -> List[np.ndarray]:
    """
    Takes in an image (which shou)
    Returns a List of Rectangles in the form: [((center_x, center_y),width,height,angle)]
    """
    contours, _ = cv2.findContours(image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    rectangles = []
    # Simplify stuff
    for cnt in contours:
        # Sanity exit. No square will be detected with less than 5 points....
        if len(cnt) < 5:
            continue
        hist_res = 50 
        hist = np.zeros((hist_res, ))
        hist2 = np.zeros((hist_res, ))

        better_cnt = np.reshape(cnt, [cnt.shape[0], 2])

        # == 1: Find out Angle via Hughes.. (Probably this could be achieved more easily but nows not the time.)
        for index, point_b in enumerate(better_cnt[1:], 0):
            
            point_a = better_cnt[index - 1] 

            # Hist will range from 0 - 90 deg
            phi = np.fmod((np.arctan2(*(point_b - point_a).T)+np.pi)/(np.pi*2) * 100, 25)/25

            dist = np.linalg.norm(point_b - point_a, 2)

            hist_index = int(np.floor(phi*hist_res))
            hist[hist_index] = hist[hist_index]+(dist**2)
            hist2[hist_index] = hist2[hist_index]+(dist**2)

        best_guess = np.argmax(hist)/hist_res * np.pi/2
    
        hist = hist / np.max(hist)
        hist2 = hist2 / np.max(hist2)
        hist = cv2.resize(hist, (100, 100))
        hist2 = cv2.resize(hist2, (100, 100))
                
        # == 1x: Angles found. Calculate all of them for easier use.
        actual_angles = [best_guess + n*np.pi/2 for n in range(0, 4)] 
    
        # == 2: Group all the points into parts of the line.
        # === Prepare groups
        group_thresholds = [p-np.pi/4 for p in actual_angles] 
        correction_factor = -group_thresholds[0]+np.pi/2
        group_thresholds = [t + correction_factor for t in group_thresholds] #TODO: Are per definition now fixed to [90, 180, 270, 360]

        groups = [[], [], [], []]
        # === Stick everything into a groups
        for index, point_b in enumerate(better_cnt[1:], 0):
            point_a = better_cnt[index - 1] 

            phi = np.arctan2(*(point_b - point_a).T)+np.pi
            for grp_index, thresh in enumerate(group_thresholds):
                if np.fmod(phi + correction_factor, 2*np.pi)  < thresh:
                    groups[grp_index].append(point_b)
                    break

        # TODO: Refactor this using defs
        has_empty_groups = False
        for grp in groups:
            if len(grp) < 1:
                has_empty_groups = True
        if has_empty_groups:
            print("Has empty groups.")
            continue


        # 3: Calculate the actual line-averages for each border.
        # Borders contains for every side of the rectangle [A, unit(AC] where A and C are points on the line
        borders = []
        for idx, group in enumerate(groups): # TODO: Correction factor for 'if group_thresholds[0]'
            com = np.average(group, 0)
            angle = actual_angles[idx]
            line_b = (int(com[0]+100*np.cos(angle)), int(com[1]-100*np.sin(angle))) #Minus Sinus because the coordinate system is origin upper left (Is this explaination correct?)

            ac = np.subtract(line_b, com)

            borders.append([com, ac / np.linalg.norm(ac, 2)])

            pass

        vertices = []
        for idx_a in range(0, 4):
            idx_b = (idx_a+1)%4

            vertex = intersect(borders[idx_a], borders[idx_b])

            vertices.append(vertex)

            # TODO: Intersect borders[idx_a] and borders[idx_b]
            # TODO: Save the resulting point in vertices
        
        vertices = np.int32(np.array(vertices))

        # TODO: Threshold measures if the contour does not in fact belong to a recangle:
        #  * Error measure in association with groups
        #  * Check if total area is at least n% of the area of the bounding box


        #TODO Add Vertices to a greater collection outside

        rectangles.append(vertices)
    return [verts_to_rect(v) for v in rectangles]


def rect_to_verts(rectangle):
    if len(rectangle) != 4:
        print(rectangle)
        raise Exception("REE")
    center, width, height, angle = rectangle
    wrad, hrad = width/2, height/2
    center = np.array(center)


    verts = [
            [- wrad, -hrad],
            [- wrad, +hrad],
            [+ wrad, +hrad],
            [+ wrad, -hrad],
            ]

    rotMatrix = np.array([[np.cos(angle), -np.sin(angle)], 
                         [np.sin(angle),  np.cos(angle)]])
    
    rotated = np.array([rotMatrix.dot(np.array(v)) + center for v in verts], dtype=np.int32)
    # print("Rotated: ", rotated)
    return rotated


class KalmanRects:
    def __init__(self, dist_threshold=10, life=5) -> None:
        self.rects: List["KalmanRect"] = []
        self.dist_threshold = dist_threshold
        self.life = life

    def push(self,new_rect) -> Tuple[Tuple[int, int], int, int, float]:
        new_center, *_ = new_rect
        
        # Todo use the rect which is closest.
        for rect in self.rects:
            c, *_ = rect.current()

            dist = np.linalg.norm((new_center - c), 2)
            if dist < self.dist_threshold:

                rect.push(new_rect)
                return rect.current()

        rect = KalmanRect(5)
        rect.push(new_rect)
        self.rects.append(rect)
        return rect.current()

    def age(self):
        for r in self.rects:
            r.age()

        self.rects = [a for a in self.rects if a.invalid_for < self.life]       


class KalmanRect:
    def __init__(self, begin_with_invalidity) -> None:
        self.history = []
        self.invalid_for = begin_with_invalidity
    
    def push(self, rect):
        (cx, cy), w, h, a = rect

        if len(self.history) > 0:
            (acx, acy), aw, ah, aa = self.current()

            dx, dy, dw, dh, da = cx-acx, cy-acy, w-aw, h-ah, a-aa
            if dx > 10 or dy > 10 or dw > 5 or dh > 5 or da > (45/180*np.pi):
                return

        



        if len(rect) != 4:
            print(rectangle)
            raise Exception("REE")
        self.history.append((cx, cy, w, h, a))
        self.invalid_for = max(0, self.invalid_for - 1)
        if len(self.history) > 20:
            self.history.pop(0)

    def age(self):
        self.invalid_for += 1

    def current(self):
        avg = np.average(self.history, 0)
        cx, cy, w, h, a = avg
        return (cx, cy), w, h, a


class BectangleRetector:
    def __init__(self, lower, higher, **kwargs) -> None:
        self.kalmanrects= KalmanRects(**kwargs)
        self.lower = lower
        self.higher = higher

    def retect(self, image):
        extracted = extract_colors(image, self.lower, self.higher)
        rects = betect_rectangles(extracted)

        self.kalmanrects.age()
        for rect in rects:
            self.kalmanrects.push(rect)
        return self.last_rects()

    def last_rects(self):
        return [r.current() for r in self.kalmanrects.rects]


if __name__ == "__main__":
    cap = cv2.VideoCapture(0)

    angle = 0
    retector = BectangleRetector((110, 127, 127), (130, 255, 255))
    while True:
        _, img = cap.read()
        cv2.imshow("Image: ", img)

        for rect in retector.retect(img):
            cv2.polylines(img, [rect_to_verts(rect).reshape((-1, 1, 2))], True, (255, 255, 255), 1)

        cv2.imshow("Rect: ", img)
        angle += np.pi/180

        key = cv2.waitKey(1)
        if key == 27:
            break
