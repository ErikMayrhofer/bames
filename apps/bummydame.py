import numpy as np
from lib import Bame, TickContext
import pygame
from pygame.surface import Surface
import cv2

class BummyDame:
    
    #@barser
    #def barse_squares(image, field):
        #field.add(SquareNStuff(x, y))
        #pass

    #@barser
    #def barse_specials(image, field):
        #field.add(Special(x, y))
        #pass


    def tick(self, context: TickContext):
        # print(f"FPS: {context.fps}")


        shape = context.screen.get_size()
        s = Surface(shape)
        s.fill((127, 127, 127))
        if context.temp_game_field is not None:
            img = np.swapaxes(context.temp_game_field, 0, 1)
            s = pygame.pixelcopy.make_surface(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            print(s.get_size())
        
        context.screen.blit(s, (0, 0, shape[0], shape[1]))

if __name__ == '__main__':
    Bame(BummyDame).run()
