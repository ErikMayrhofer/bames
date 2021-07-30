from lib.bectangleretector import BectangleRetector, imshow_small, rect_to_verts
import numpy as np
from lib.bame import BameMetadata, BarsedContext, LoadContext
from lib import Bame, TickContext, barameters
import pygame
from pygame.surface import Surface
import cv2
from lib.barser import BarserContext, BarserMethod


def debug_image(image, _, _context):
    imshow_small("input", image)

def barse_squares(image, field, context):
    field["rects"] = context.bects.detect(image)


    print("Detecting rects: ")
    for rect in field["rects"]:
        cv2.polylines(image, [rect_to_verts(rect).reshape((-1, 1, 2))], True, (255, 255, 255), 1)
    print("Detected rects")


    imshow_small("rects: ", image)

def rot_center(image, angle):
    # TODO: Why is this still here... bicturetaker?
    """rotate a Surface, maintaining position."""

    loc = image.get_rect().center  #rot_image is not defined 
    rot_sprite = pygame.transform.rotate(image, angle)
    rot_sprite.get_rect().center = loc
    return rot_sprite

class BummyDame:

    barser_context = BarserContext(
            bects = BectangleRetector()
    )

    def load(self, context: LoadContext) -> None:
        print("FONT INIT:")
        self.bicturemaker = context.bicturemaker
        self.font = pygame.font.SysFont(None, 24)
        self.flowo = pygame.image.load("img/flowo.png")
    
    barse_squares = BarserMethod(barse_squares)
    # debug_image = BarserMethod(debug_image)

    def tick(self, context: TickContext, barsed_context: BarsedContext):
        # print("BummyDame tick with: ", barsed_context.data, barsed_context.age)
        
        # img = np.swapaxes(barsed_context.image, 0, 1)
        # s = pygame.pixelcopy.make_surface(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        # context.screen.blit(s, (0, 0))
        
        # if "cont" in barsed_context.data:
            # print("Conts yay")
            # img = np.swapaxes(barsed_context.data["cont"], 0, 1)
            # s = pygame.pixelcopy.make_surface(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            # context.screen.blit(s, (0, 0))


        
        if "rects" in barsed_context.data:
            rects = barsed_context.data["rects"]

            for rect in rects:
                pygame.draw.lines(context.screen, (32, 32, 32), True, rect_to_verts(rect))
                #context.screen.blit(self.flowo, (cx, cy))


        shape = context.screen.get_size()
        textimg = self.font.render(f'Age: {barsed_context.age}', True, (255, 255, 255))
        context.screen.blit(textimg, (shape[0]/2, shape[1]/2))

bame_data = BameMetadata(name="Bummy dame", clazz=BummyDame)

if __name__ == '__main__':
    Bame(BummyDame).run()
