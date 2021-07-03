from lib import Bame, TickContext

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
        print(f"FPS: {context.fps}")
        pass

Bame(BummyDame).run()
