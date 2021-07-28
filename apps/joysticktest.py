from lib.bame import Bame, BarsedContext, TickContext
import pygame

class JoyStickTest:
    def load(self) -> None:
        print("FONT INIT:")
        self.font = pygame.font.SysFont(None, 24)
        self.flowo = pygame.image.load("img/flowo.png")
        self.values = {}
    
    def tick(self, context: TickContext, barsed_context: BarsedContext):
        shape = context.screen.get_size()

        for idx, (key, value) in enumerate(self.values.items()):
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
