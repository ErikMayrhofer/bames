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


        print(context.temp_game_field)
        if context.temp_game_field is not None:
            print("Img: ")
            shape = context.temp_game_field.shape

            s = Surface((shape[0], shape[1]))
            pygame.surfarray.blit_array(s, context.temp_game_field)
            context.screen.blit(s, (0, 0, shape[0], shape[1]))
            

        pass

if __name__ == '__main__':
    Bame(BummyDame).run()
