from lib.bame import Bame, BameMetadata, BarsedContext, LoadContext, TickContext
from lib import bamepad
import pygame

class JoyStickTest:
    def load(self, context: LoadContext) -> None:
        print("FONT INIT:")

        context.beymap_registrar.add_action("UP", bamepad.BUTTON_SYMBOL_TOP)
        context.beymap_registrar.add_action("DOWN", bamepad.BUTTON_SYMBOL_BOTTOM)

        context.beymap_registrar.add_action("SPEED", bamepad.AXIS_LEFT_HORIZONTAL)

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
            print(event)
            if isinstance(event, bamepad.Bvent):
                # print(event)
                self.values[f"{event.player} - {event.control_name}"]=event.value

joystick_test = BameMetadata(name="Joystick Test", clazz=JoyStickTest)

if __name__ == '__main__':
    Bame(JoyStickTest).run()
