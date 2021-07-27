import cv2
import numpy as np
from cv2.cv2 import imshow



def imshow_small(name, image):
    small_img = cv2.resize(image, [960, 540])
    cv2.imshow(name,small_img)
    cv2.waitKey(1)

def extract_colors(mat, *, saturation_threshold=80):

    # Into HSV and filter out stuff that actually has colors.
    img_hsv = cv2.cvtColor(mat, cv2.COLOR_BGR2HSV_FULL)
    color_mask = cv2.inRange(img_hsv, (0, saturation_threshold, 100), (255, 255, 255))
    img_hsv = cv2.bitwise_or(img_hsv, img_hsv, mask=color_mask)

    # Back to normal again.
    img_hsv = cv2.medianBlur(img_hsv, 5)
    # img_hsv = np.uint8(img_hsv * np.array([1, 10, 1]))
    img_hsv = cv2.cvtColor(img_hsv, cv2.COLOR_HSV2BGR_FULL)
    imshow_small("Clean",img_hsv)

    # mask = cv2.inRange(img_hsv, (118, 100, 100), (138, 255, 255))

    return img_hsv



def angle_of_vec(vec):
    vec1 = vec
    vec2 = [1, 0]
    
    unit1 = vec1 / np.linalg.norm(vec1)
    unit2 = vec2 / np.linalg.norm(vec2)
    dot_product = np.dot(unit1, unit2)
    return np.arccos(dot_product)

def detect_stuff(mat):
    gray = cv2.cvtColor(mat, cv2.COLOR_BGR2GRAY)
    contours, _ = cv2.findContours(gray.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    cont_mat = np.zeros(mat.shape, np.uint8) 
    cv2.drawContours(cont_mat, contours, -1, (0, 0, 255), 1)


    # Simplify stuff
    for cnt in contours:
        hist_res = 50 
        hist = np.zeros((hist_res, ))
        hist2 = np.zeros((hist_res, ))

        better_cnt = np.reshape(cnt, [cnt.shape[0], 2])

        # == 1: Find out Angle via Hughes.. (Probably this could be achieved more easily but nows not the time.)
        for index, point_b in enumerate(better_cnt[1:], 0):
            cv2.circle(cont_mat, point_b, 1, (255, 0, 0), 1)

            point_a = better_cnt[index - 1] 


            # Hist will range from 0 - 90 deg
            phi = np.fmod((np.arctan2(*(point_b - point_a).T)+np.pi)/(np.pi*2) * 100, 25)/25
            print(phi)

            dist = np.linalg.norm(point_b - point_a, 2)

            hist_index = int(np.floor(phi*hist_res))
            hist[hist_index] = hist[hist_index]+(dist**2)
            hist2[hist_index] = hist2[hist_index]+(dist**2)

        best_guess = np.argmax(hist)/hist_res * np.pi/2
    
        hist = hist / np.max(hist)
        hist2 = hist2 / np.max(hist2)
        hist = cv2.resize(hist, (100, 100))
        hist2 = cv2.resize(hist2, (100, 100))
        cv2.imshow("Hist: ", hist)
        cv2.imshow("Hist2: ", hist2)
                
        # == 1x: Angles found. Calculate all of them for easier use.
        actual_angles = [best_guess + n*np.pi/2 for n in range(0, 4)] 

        #Output only.
        print(actual_angles)
        #for angle in actual_angles:
            #line_a = (60, 60)
            #line_b = (line_a[0]+int(100*np.cos(angle)), line_a[1]+int(100*np.sin(angle)))
            #cv2.line(cont_mat, line_a, line_b, (255, 0, 0), 2)
    
        # == 2: Group all the points into parts of the line.
        # === Prepare groups
        group_thresholds = [p-np.pi/4 for p in actual_angles] 
        lelz = False
        if group_thresholds[0] < 0:
            lelz = True
            group_thresholds = [*group_thresholds[1:], group_thresholds[0]+2*np.pi]

        print("Group Thresholds: ", group_thresholds)
        groups = [[], [], [], []]
        # === Stick everything into a groups
        for index, point_b in enumerate(better_cnt[1:], 0):
            point_a = better_cnt[index - 1] 

            phi = np.arctan2(*(point_b - point_a).T)+np.pi
            for grp_index, thresh in enumerate(group_thresholds):
                if phi < thresh:
                    # groups[grp_index].append(index)
                    groups[grp_index].append(point_b)
                    cv2.circle(cont_mat, point_b, 1, (255, 255*(grp_index%2), 255*((grp_index+1)%2)), 1)
                    break
        print("GROUPS: ", groups) 

        # 3: Calculate the actual line-averages for each border.
        # Borders contains for every side of the rectangle [A, unit(AC] where A and C are points on the line
        borders = []
        for idx, group in enumerate(groups): # TODO: Correction factor for 'if group_thresholds[0]'
            com = np.average(group, 0)
            print("COM: ", com)
            print("Lelz: ", lelz)
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!! TODO !!!!!!!!!!!!!!!!!!
            # Sometimes these angles are off by one. why (test case test2 vs test3)
            angle = actual_angles[idx if lelz else ((idx-1)%4)] 
            line_a = (int(com[0]-100*np.cos(angle)), int(com[1]-100*np.sin(angle)))
            line_b = (int(com[0]+100*np.cos(angle)), int(com[1]+100*np.sin(angle)))
            cv2.line(cont_mat, line_a, line_b, (255, 0, 0), 2)
            cv2.circle(cont_mat, np.uint8(com), 1, (0, 0, 255), 4)

            ac = np.subtract(line_b, line_a)

            borders.append([line_a, ac / np.linalg.norm(ac, 2)])

            
            pass

        vertices = []
        for idx_a in range(0, 4):
            idx_b = (idx_a+1)%4

            # TODO: Intersect borders[idx_a] and borders[idx_b]
            # TODO: Save the resulting point in vertices

        #TODO Add Vertices to a greater collection outside



    cv2.imshow("Contours: ", cont_mat)
    # imshow_small("Contours: ", cont_mat)



def wait_for_esc():
    while True:
        key = cv2.waitKey(None)
        if key == 27:
            break

if __name__ == "__main__":
    cap = cv2.VideoCapture(2)

    detect_stuff(cv2.imread("test2.png"))
    wait_for_esc()
    # detect_stuff(cv2.imread("test2.png"))
    # wait_for_esc()
    
    """
    while False:
        _, img = cap.read()
        cv2.imshow("Image: ", img)
        extracted = extract_colors(img)
        detect_stuff(extracted)

        key = cv2.waitKey(1)
        if key == 27:
            break
    """
