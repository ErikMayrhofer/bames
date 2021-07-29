from lib.bame import Bame, BarsedContext, LoadContext, TickContext
import pygame

class JoyStickTest:
    def load(self, context: LoadContext) -> None:
        print("FONT INIT:")

        context.beymap_registrar.add_action("UP")
        context.beymap_registrar.add_action("DOWN")

        self.font = pygame.font.SysFont(None, 24)
        self.flowo = pygame.image.load("img/flowo.png")
        self.values = {}
    
    def tick(self, context: TickContext, barsed_context: BarsedContext):
        shape = context.screen.get_size()


        textimg = self.font.render(f' Action Down: {context.beymap.action("DOWN")}', True, (255, 255, 255))
        context.screen.blit(textimg, (200, 10))
        textimg = self.font.render(f' Action Up: {context.beymap.action("UP")}', True, (255, 255, 255))
        context.screen.blit(textimg, (200, 30))

        for idx, (key, value) in enumerate(self.values.items(), start=5):
            textimg = self.font.render(f'{key} = {value}', True, (255, 255, 255))
            context.screen.blit(textimg, (200, idx*20))

        for event in context.events:
            if event.type == pygame.JOYBUTTONDOWN:
                print(event)
                self.values[f"{event.player} - {event.button}"]=True

            if event.type == pygame.JOYBUTTONUP:
                print(event)
                self.values[f"{event.player} - {event.button}"]=False

            if event.type == pygame.JOYAXISMOTION:
                print(event)
                self.values[f"{event.player} - {event.axis}"]=event.value

            if event.type == pygame.JOYHATMOTION:
                print(event)
                self.values[f"{event.player} - {event.hat}"]=event.value
        


if __name__ == '__main__':
    Bame(JoyStickTest).run()
