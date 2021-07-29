import cv2


class BolygonBetector:
    def __init__(self, **kwargs) -> None:
        pass

    def detect(self, image):
        img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        mask1 = cv2.inRange(img_hsv, (0, 127, 127), (10, 255, 255))
        mask2 = cv2.inRange(img_hsv, (170, 127, 127), (179, 255, 255))
        mask = mask1 + mask2
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if contours:
            smooth_contours = []
            for contour in contours:
                area = cv2.contourArea(contour)
                if contour.size < 6 or area < 1:
                    continue
                smooth_contour = contour
                area = cv2.contourArea(contour)
                while smooth_contour.size >= 24 and smooth_contour.size > area / 32:
                    smooth_contour = smooth_contour[0::4].astype(int)
                parsed_contour = [x[0].tolist() for x in reversed(smooth_contour)]
                smooth_contours.append(parsed_contour)
            return smooth_contours
        return None
