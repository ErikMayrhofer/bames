import numpy as np
from lib.bame import BarsedContext
from lib import Bame, TickContext
import pygame
from pygame.surface import Surface
import cv2
from lib.barser import BarserMethod

def barse_squares(image, field):
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(img_hsv, (80, 31, 31), (100, 255,255))
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        [print(cv2.contourArea(contour)) for contour in contours]
        cnt = sorted(contours, key=cv2.contourArea, reverse=True)[0]
        cv2.drawContours(image, [cnt], 0, (0,0,255), 3)
        x,y,w,h = cv2.boundingRect(cnt)
        rect = (x, y), (x + w, y + h)

class BummyDame:
    def load(self) -> None:
        print("FONT INIT:")
        self.font = pygame.font.SysFont(None, 24)
    
    barse_squares = BarserMethod(barse_squares)

    def tick(self, context: TickContext, barsed_context: BarsedContext):
        print("BummyDame tick with: ", barsed_context.data, barsed_context.age)
        
        img = np.swapaxes(barsed_context.image, 0, 1)
        s = pygame.pixelcopy.make_surface(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        context.screen.blit(s, (0, 0))

        shape = context.screen.get_size()
        textimg = self.font.render(f'Age: {barsed_context.age}', True, (255, 255, 255))
        context.screen.blit(textimg, (shape[0]/2, shape[1]/2))

if __name__ == '__main__':
    Bame(BummyDame).run()
