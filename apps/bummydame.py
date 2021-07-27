import numpy as np
from lib.bame import BarsedContext
from lib import Bame, TickContext
import pygame
from pygame.surface import Surface
import cv2
from lib.barser import barser


class BummyDame:
    def load(self) -> None:
        print("FONT INIT:")
        self.font = pygame.font.SysFont(None, 24)
    
    @barser
    def barse_squares(image, field):
        print("Barse Squares epic many")
        field["öha"] = ["square", "square"]
        pass

    # @barser
    # def barse_specials(image, field):
        # field["öha"].append("circle")
        # pass


    def tick(self, context: TickContext, barsed_context: BarsedContext):
        print("BummyDame tick with: ", barsed_context.data, barsed_context.age)

        shape = context.screen.get_size()
        textimg = self.font.render(f'Age: {barsed_context.age}', True, (255, 255, 255))
        context.screen.blit(textimg, (shape[0]/2, shape[1]/2))

if __name__ == '__main__':
    Bame(BummyDame).run()
