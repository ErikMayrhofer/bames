from typing import Type, Any
import pygame
from .util.keyframes import Keyframes
from .barser import Barser

class TickContext:
    fps: float
    delta_ms: int
    screen: Any

    temp_game_field: Any

class SplashScene:
    def __init__(self):
        self.splash_img = pygame.image.load("img/Logo.jpg")
        self.frames = Keyframes([(0, 0), (0.5, 255), (1.3, 255), (1.5, 0)])


    def load(self):
        pass

    def tick(self, context: TickContext) -> bool:
        self.frames.advance(context.delta_ms/1000)
        val = self.frames.value()
        context.screen.fill((255,255,255))
        context.screen.blit(self.splash_img, (0, 0, 640, 480))
        context.screen.fill((val, val, val), special_flags=pygame.BLEND_MULT)
        return self.frames.done()

    def unload(self):
        pass

class SceneWithBarser:
    def __init__(self, sub_scene):
        self.sub_scene = sub_scene
        self.tag_size = 48
        self.tags = [ pygame.transform.scale(pygame.image.load("img/" + str(num) + ".png"), (self.tag_size, self.tag_size)) for num in range(4) ]
        # TODO: Barser is initiated here and therefore always scans...1920.

    def load(self):
        self.barser = Barser()
        self.barser.launch()

    def tick(self, context: TickContext) -> bool:
        _parsed_game = self.barser.get_bayload()
        _parsed_age = self.barser.get_bayload_age()
        if _parsed_game:
            context.temp_game_field = _parsed_game.image
        else:
            context.temp_game_field = None
        done = self.sub_scene.tick(context)
        if context.temp_game_field is not None:
            shape = context.temp_game_field.shape
            context.screen.blits([
                (self.tags[0], (0, shape[0]-self.tag_size)),
                (self.tags[1], (shape[1]-self.tag_size, shape[0]-self.tag_size)),
                (self.tags[2], (shape[1]-self.tag_size, 0)),
                (self.tags[3], (0, 0))
            ])
        return done

    def unload(self):
        self.barser.stop()


class Bame:
    def __init__(self, classname: Type):
        self.game_instance = classname()
        # Get Barsers from game_instance using the decorators
        # Pass Barsers to SceneWithBarser
        self.running = False
        self.scenes = [SplashScene(), SceneWithBarser(self.game_instance)]

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480), pygame.RESIZABLE)

        self.start_loop()

    def next_scene(self):
        self.scenes[0].unload()
        self.scenes.pop(0)
        if len(self.scenes) == 0:
            self.running = False
        else:
            self.scenes[0].load()

    def start_loop(self):
        clock = pygame.time.Clock()

        self.running = True
        while self.running:
            delta_t = clock.tick(60)
            context = TickContext()
            context.fps = 1000/delta_t
            context.delta_ms = delta_t
            context.screen = self.screen

            self.screen.fill((0, 0, 0)) 
            
            self.handle_events()
            
            next_scene = self.scenes[0].tick(context)
            if next_scene:
                self.next_scene()

            pygame.display.flip()

        if len(self.scenes) > 0:
            self.scenes[0].unload()
        print("Bye!")

    def handle_events(self):
        for event in pygame.event.get():
            self.handle_event(event)
            
    def handle_event(self, event):
        print(f"EventType {event}")
        if event.type == pygame.QUIT:
            self.running = False
        if event.type == pygame.WINDOWRESIZED:
            pygame.display.update()
