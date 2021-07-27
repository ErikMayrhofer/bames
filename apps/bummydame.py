from lib.betrachter import imshow_small
import numpy as np
from lib.bame import BarsedContext
from lib import Bame, TickContext, barameters
import pygame
from pygame.surface import Surface
import cv2
from lib.barser import BarserMethod

def debug_image(image, _):
    imshow_small("input", image)

def barse_squares(image, field):
    print("B")
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV_FULL)
    mask = cv2.inRange(img_hsv, (0, 150, 100), (255, 255, 255))

    imshow_small("mask", mask)

    contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        cont_mat = np.zeros(image.shape, np.uint8) 
        cv2.drawContours(cont_mat, contours, -1, (0, 0, 255), 1)

        field["cont"]=cont_mat
        # x,y,w,h = cv2.boundingRect(cnt)
        # rect = (x, y), (x + w, y + h)

class BummyDame:
    def load(self) -> None:
        print("FONT INIT:")
        self.font = pygame.font.SysFont(None, 24)
    
    barse_squares = BarserMethod(barse_squares)
    debug_image = BarserMethod(debug_image)

    def tick(self, context: TickContext, barsed_context: BarsedContext):
        # print("BummyDame tick with: ", barsed_context.data, barsed_context.age)
        
        # img = np.swapaxes(barsed_context.image, 0, 1)
        # s = pygame.pixelcopy.make_surface(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        # context.screen.blit(s, (0, 0))
        
        if "cont" in barsed_context.data:
            print("Conts yay")
            img = np.swapaxes(barsed_context.data["cont"], 0, 1)
            s = pygame.pixelcopy.make_surface(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            context.screen.blit(s, (0, 0))

        shape = context.screen.get_size()
        textimg = self.font.render(f'Age: {barsed_context.age}', True, (255, 255, 255))
        context.screen.blit(textimg, (shape[0]/2, shape[1]/2))

if __name__ == '__main__':
    Bame(BummyDame).run()
