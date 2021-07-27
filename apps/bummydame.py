from lib.bame import BarsedContext
from lib import Bame, TickContext
import pygame
from pygame.surface import Surface
from lib.barser import barser


class BummyDame:
    
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
        # print(f"FPS: {context.fps}")

        print("BummyDame tick with: ", barsed_context.data, barsed_context.age)

        shape = context.screen.get_size()
        s = Surface((shape[0], shape[1]))
        s.fill((127, 127, 127))
        #if context.temp_game_field is not None:
            #shape = context.temp_game_field.shape
            #position = (shape[1] / 2, shape[0] / 2)
            #pygame.draw.circle(s, (255, 0, 0), position, 128)
            #pygame.surfarray.blit_array(s, context.temp_game_field)
        
        context.screen.blit(s, (0, 0, shape[0], shape[1]))

if __name__ == '__main__':
    Bame(BummyDame).run()
