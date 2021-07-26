from lib import Bame, TickContext
import pygame
from pygame.surface import Surface

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
        s = Surface((shape[0], shape[1]))
        s.fill((127, 127, 127))
        if context.temp_game_field is not None:
            shape = context.temp_game_field.shape
            position = (shape[1] / 2, shape[0] / 2)
            pygame.draw.circle(s, (255, 0, 0), position, 128)
            #pygame.surfarray.blit_array(s, context.temp_game_field)
        
        context.screen.blit(s, (0, 0, shape[0], shape[1]))

if __name__ == '__main__':
    Bame(BummyDame).run()
