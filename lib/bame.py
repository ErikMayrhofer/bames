import ctypes
from lib.bamepad import BamePadFactory, BamePadManager
import os
from time import time
from lib.bicturemaker import Bicturemaker
from lib.bicturetaker import Bicturetaker
from lib.barameters import Barameters
from typing import Optional, Type, Any, List, Dict
import pygame
from .util.keyframes import Keyframes
from .barser import Barser, BarserOptions
import numpy as np
import cv2

class LoadContext:
    bicturemaker: Bicturemaker

class BarsedContext:
    data: Dict
    age: float
    image: Any

class TickContext:
    fps: float
    delta_ms: int
    screen: Any
    barameters: Barameters
    bamepads: BamePadManager
    bicturemaker: Bicturemaker

    events: List[Any]

class SplashScene:
    def __init__(self, _: "Bame"):
        self.splash_img = pygame.image.load("img/Logo.jpg")
        self.frames = Keyframes([(0, 0), (0.5, 255), (1.3, 255), (1.5, 0)])


    def load(self, context: LoadContext):
        pass

    def tick(self, context: TickContext) -> bool:
        self.frames.advance(context.delta_ms/1000)
        val = self.frames.value()
        context.screen.fill((255,255,255))
        context.screen.blit(self.splash_img, (0, 0, 1920, 1080))
        context.screen.fill((val, val, val), special_flags=pygame.BLEND_MULT)
        return self.frames.done()

    def unload(self):
        pass

class InitTagsScene:
    def __init__(self, bame: "Bame"):
        self.tag_size = bame.barameters.tag_size
        self.tags = [ pygame.transform.scale(pygame.image.load("img/" + str(num) + ".png"), (self.tag_size, self.tag_size)) for num in range(4) ]
        self.found = False
        self.bame = bame

    def load(self, context: LoadContext):
        self.taker = Bicturetaker(cam_index=self.bame.barameters.camera_index, tag_timeout=0.1)

    def tick(self, context: TickContext) -> bool:
        d = self.taker.take_bicture()
        if "img" in d:
            if self.found:
                return True
            self.found = True
        else:
            self.found = False
        img = cv2.cvtColor(d["raw"], cv2.COLOR_BGR2RGB)
        img = np.swapaxes(img, 0, 1)
        s = pygame.pixelcopy.make_surface(img)
        context.screen.blit(s, (0, 0))
        shape = context.screen.get_size()
        context.screen.blits([
            (self.tags[0], (0, shape[1]-self.tag_size)),
            (self.tags[1], (shape[0]-self.tag_size, shape[1]-self.tag_size)),
            (self.tags[2], (shape[0]-self.tag_size, 0)),
            (self.tags[3], (0, 0))
        ])
        return False

    def unload(self):
        del self.taker

class BamePadScene:
    factory: BamePadFactory
    def __init__(self, bame: "Bame") -> None:
        self.bame = bame
        pass

    def load(self):
        self.factory = BamePadFactory()
        
        self.font = pygame.font.SysFont(None, 24)
        pass

    def tick(self, context: TickContext):
        textimg = self.font.render(f'Press bottom symbol button (A) to join. Press it again to be ready', True, (255, 255, 255))
        context.screen.blit(textimg, (0, 0))
        textimg = self.font.render(f'Press right symbol button (B) to leave.', True, (255, 255, 255))
        context.screen.blit(textimg, (0, 20))
        textimg = self.font.render(f'Press right symbol button (B) to leave.', True, (255, 255, 255))
        context.screen.blit(textimg, (0, 40))
        textimg = self.font.render(f'Game starts when everyone is ready.', True, (255, 255, 255))
        context.screen.blit(textimg, (0, 60))

        can_start = len(self.factory.get_active_controllers()) > 0
        for idx, parcel in enumerate(self.factory.get_active_controllers(), start=5):
            textimg = self.font.render(f'Player {parcel.metadata.player_num}: {parcel.metadata.joystick.get_name()} - Ready: {parcel.ready}', True, (0, 255, 0) if parcel.ready else (255, 255, 255))
            context.screen.blit(textimg, (0, idx*20))
            if not parcel.ready:
                can_start = False


        for event in context.events:
            if event.type == pygame.JOYBUTTONDOWN:
                new_instance_id = event.instance_id
                self.factory.handle_press(new_instance_id, event.button)

        return can_start

    def unload(self):
        self.bame.bamepads = self.factory.build()
        pass

class SceneWithBarser:
    def __init__(self, bame: "Bame", *, sub_scene):
        self.sub_scene = sub_scene
        self.bame = bame
        self.tags = [ pygame.transform.scale(pygame.image.load("img/" + str(num) + ".png"), (self.bame.barameters.tag_size, self.bame.barameters.tag_size)) for num in range(4) ]
        # TODO: Barser is initiated here and therefore always scans...1920.

    def load(self, context: LoadContext):
        self.barser = Barser(self.sub_scene,options=BarserOptions.from_barameters(self.bame.barameters))
        self.barser.launch()

    def tick(self, context: TickContext) -> bool:
        next_scene = False
        parsed_game = self.barser.get_bayload()
        if parsed_game or False:
            barsed_context = BarsedContext()
            barsed_context.age = time() - parsed_game.time
            barsed_context.data = parsed_game.data.barsed_info
            barsed_context.image = parsed_game.data.image
            next_scene = self.sub_scene.tick(context, barsed_context)
        else:
            if self.bame.barameters.start_without_barser:
                next_scene = self.sub_scene.tick(context, None)
            # print("Waiting for barser to do something....")
            # TODO: Draw some sort of loading sign on the game... parsed_game is None until the barser emtis for the first time.
            pass

        shape = context.screen.get_size()
        context.screen.blits([
            (self.tags[0], (0, shape[1]-context.barameters.tag_size)),
            (self.tags[1], (shape[0]-context.barameters.tag_size, shape[1]-context.barameters.tag_size)),
            (self.tags[2], (shape[0]-context.barameters.tag_size, 0)),
            (self.tags[3], (0, 0))
        ])
        return next_scene

    def unload(self):
        self.barser.stop()


class Bame:
    bamepads: Optional[BamePadManager]
    def __init__(self, classname: Type):
        self.barameters = Barameters()
        self.game_instance = classname()
        # Get Barsers from game_instance using the decorators
        # Pass Barsers to SceneWithBarser
        self.running = False
        self.scenes = ([] if self.barameters.quick_start else [
                    SplashScene(self), 
                    InitTagsScene(self), 
                ]) + (
                        [BamePadScene(self)] if self.barameters.use_joystick else []
                        ) + [
                    SceneWithBarser(self, sub_scene=self.game_instance)
                ]

        self.bamepads = None

    def run(self):
        if os.name == 'nt':
            ctypes.windll.user32.SetProcessDPIAware()

        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN if self.barameters.fullscreen else pygame.RESIZABLE)
        self.bicturemaker = Bicturemaker(self.screen, self.barameters)

        context = LoadContext()
        context.bicturemaker = self.bicturemaker
        self.game_instance.load(context)

        self.start_loop()

    def next_scene(self):
        self.scenes[0].unload()
        self.scenes.pop(0)
        if len(self.scenes) == 0:
            self.running = False
        else:
            context = LoadContext()
            context.bicturemaker = self.bicturemaker
            self.scenes[0].load(context)

    def start_loop(self):
        clock = pygame.time.Clock()

        self.running = True

        context = LoadContext()
        context.bicturemaker = self.bicturemaker
        self.scenes[0].load(context)
        while self.running:
            delta_t = clock.tick(60)
            context = TickContext()
            context.fps = 1000/delta_t
            context.delta_ms = delta_t
            context.screen = self.screen
            context.barameters = self.barameters
            context.events = self.handle_events()
            context.bamepads = self.bamepads
            context.bicturemaker = self.bicturemaker

            #print(f"Unhandled Events {context.events}")

            self.screen.fill((0, 0, 0)) 
            
            next_scene = self.scenes[0].tick(context)
            if next_scene:
                self.next_scene()

            pygame.display.flip()

        if len(self.scenes) > 0:
            self.scenes[0].unload()
        print("Bye!")

    def handle_events(self) -> List[Any]:
        unhandled_events = []

        mouse_motion = None


        # Pump events from pygame
        for event in pygame.event.get():
            # See if there are bame-related events (Quit or sth) and if not add it to unhandled events.
            if not self.handle_event(event):
                # Accumulate mouse-motion events into one single big mouse-motion
                if event.type == pygame.MOUSEMOTION:
                    mouse_motion = event # TODO: Mouse-Motion own deltax and deltay .... update them accordingly.
                else:
                    # Map Gamepad events
                    if self.bamepads is not None:
                        event = self.bamepads.map_event(event)
                    if event is not None:
                        unhandled_events.append(event)

        if mouse_motion is not None:
            unhandled_events.append(mouse_motion)
        return unhandled_events
            
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return True
        if event.type == pygame.WINDOWRESIZED:
            pygame.display.update()
            return True

