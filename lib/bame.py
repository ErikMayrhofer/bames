import ctypes
from lib import barameters
from lib.beymap import BeymapManager, BeymapRegistrar
from lib.bamepad import BUTTON_SYMBOL_BOTTOM, BUTTON_SYMBOL_TOP, BamePadFactory, BamePadManager, Bvent, MENU_RIGHT
import os
from time import time

from pygame.event import Event
from lib.bicturemaker import Bicturemaker
from lib.bicturetaker import Bicturetaker
from lib.barameters import Barameters
from typing import Optional, Tuple, Type, Any, List, Dict, Union
import pygame
from .util.keyframes import Keyframes
from .barser import Barser, BarserOptions
import numpy as np
import cv2

class BameMetadata:
    def __init__(self, *, name: str, clazz: Type, players: Union[int, None] = None) -> None:
        self.name = name
        self.players = players
        self.clazz = clazz
    
    def __str__(self) -> str:
        return f"<BameMetadata(name=${self.name} clazz={self.clazz})>"

class LoadContext:
    bicturemaker: Bicturemaker
    beymap_registrar: BeymapRegistrar

class SceneLoadContext:
    bicturemaker: Bicturemaker
    beymap_registrar: BeymapRegistrar

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
    beymap: BeymapManager
    bicturemaker: Bicturemaker

    events: List[Event]
    bvents: List[Bvent]

class SplashScene:
    def __init__(self, _: "Bame"):
        self.splash_img = pygame.image.load("img/Logo.jpg")
        self.frames = Keyframes([(0, 0), (0.5, 255), (1.3, 255), (1.5, 0)])


    def load(self, context: SceneLoadContext):
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

    def load(self, context: SceneLoadContext):
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
    registrar: BeymapRegistrar
    def __init__(self, bame: "Bame") -> None:
        self.bame = bame
        pass

    def load(self, context: SceneLoadContext):
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

        player_list_start = 5

        can_start = len(self.factory.get_active_controllers()) > 0

        player_height = 20
        for idx, parcel in enumerate(self.factory.get_active_controllers()):
            textimg = self.font.render(f'Player {parcel.metadata.player_num}: {parcel.metadata.get_name()} - Ready: {parcel.ready}', True, (0, 255, 0) if parcel.ready else (255, 255, 255))
            context.screen.blit(textimg, (0, player_list_start*20 + idx*player_height))
            if not parcel.ready:
                can_start = False


        for event in context.events:
                self.factory.handle_event(event)

        return can_start

    def unload(self):
        self.bame.bamepads = self.factory.build(self.bame.barameters)
        # self.bame.beymap = self.registrar.build(self.bame.bamepads, self.bame.barameters)
        pass

class SceneWithBarser:
    def __init__(self, bame: "Bame", game_instance: Any):
        self.bame = bame
        self.game_instance = game_instance
        self.tags = [ pygame.transform.scale(pygame.image.load("img/" + str(num) + ".png"), (self.bame.barameters.tag_size, self.bame.barameters.tag_size)) for num in range(4) ]
        # TODO: Barser is initiated here and therefore always scans...1920.

    def load(self, scene_context: SceneLoadContext):
        context = LoadContext()
        context.bicturemaker = scene_context.bicturemaker
        context.beymap_registrar = scene_context.beymap_registrar
        self.game_instance.load(context)
        # TODO HANDLE THIS PROPERLY:
        if not self.bame.barameters.start_without_barser:
            self.barser = Barser(self.game_instance,options=BarserOptions.from_barameters(self.bame.barameters))
            self.barser.launch()

    def tick(self, context: TickContext) -> bool:
        next_scene = False
        if self.bame.barameters.start_without_barser:
            next_scene = self.game_instance.tick(context, None)
        else:
            parsed_game = self.barser.get_bayload()
            if parsed_game:
                barsed_context = BarsedContext()
                barsed_context.age = time() - parsed_game.time
                barsed_context.data = parsed_game.data.barsed_info
                barsed_context.image = parsed_game.data.image
                next_scene = self.game_instance.tick(context, barsed_context)
            else:
                print("Waiting for barser to do something....")
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

class BameSelectorScene:
    def __init__(self, bame: "Bame", metadatas: List[BameMetadata]) -> None:
        self.metadatas = metadatas
        self.selected = -1
        self.bame = bame
        pass
    
    def load(self, scene_context: SceneLoadContext):
        scene_context.beymap_registrar.add_action("UP", BUTTON_SYMBOL_TOP)
        scene_context.beymap_registrar.add_action("DOWN", BUTTON_SYMBOL_BOTTOM)
        scene_context.beymap_registrar.add_action("SELECT", MENU_RIGHT)
        self.font = pygame.font.SysFont(None, 24)
    
    def tick(self, context: TickContext):
        for idx, metadata in enumerate(self.metadatas):
            players = len(context.bamepads.get_players())
            color = (255, 255, 255)
            if metadata.players is not None:
                if metadata.players != players:
                    color = (64, 64, 64)
            if self.selected == idx:
                color = (0, 255, 0)
            textimg = self.font.render(f"{metadata.name} (Player Requirements: {metadata.players})", True, color)
            context.screen.blit(textimg, (0, idx*20))
        
        for event in context.bvents:
            if event.action == "DOWN" and event.value == True:
                self.selected += 1
            if event.action == "UP" and event.value == True:
                self.selected -= 1
            if self.selected >= len(self.metadatas):
                self.selected = 0
            if self.selected < 0:
                self.selected = len(self.metadatas)-1
            if event.action == "SELECT" and event.value == True:
                metadata = self.metadatas[self.selected]
                if metadata.players is not None:
                    players = len(context.bamepads.get_players())
                    if players:
                        if players != metadata.players:
                            continue
                game_instance = metadata.clazz()
                self.bame.scenes.append(SceneWithBarser(self.bame, game_instance))
                return True
        return False

    def unload(self):
        pass

class Bame:
    bamepads: Optional[BamePadManager]
    beymap: Optional[BeymapManager]
    def __init__(self, classname: Union[Type, List[BameMetadata]]):
        self.barameters = Barameters()
        self.bamepads = None
        # Get Barsers from game_instance using the decorators
        # Pass Barsers to SceneWithBarser
        self.running = False
        self.beymap = None


        self.scenes = (
                    [SplashScene(self)] if not self.barameters.quick_start else []
                ) + (
                    [BamePadScene(self)] if self.barameters.use_joystick else []
                ) + (
                    [InitTagsScene(self)] if not self.barameters.quick_start else []
                ) + (
                    [BameSelectorScene(self, classname)] if isinstance(classname, list) else [SceneWithBarser(self, classname())]
                ) #+ (
                 #   [SceneWithBarser(self)]
                #)

    def run(self):
        if os.name == 'nt':
            ctypes.windll.user32.SetProcessDPIAware()

        pygame.init()
        self.screen = pygame.display.set_mode((1920, 1080), pygame.FULLSCREEN if self.barameters.fullscreen else pygame.RESIZABLE)
        self.bicturemaker = Bicturemaker(self.screen, self.barameters)

        self.start_loop()

    def next_scene(self):
        self.scenes[0].unload()
        self.scenes.pop(0)
        if len(self.scenes) == 0:
            self.running = False
        else:
            print(f"Loading scene: {self.scenes[0]}")
            beymap_registrar = BeymapRegistrar()
            context = LoadContext()
            context.bicturemaker = self.bicturemaker
            context.beymap_registrar = beymap_registrar
            self.scenes[0].load(context)
            if self.bamepads is not None:
                self.beymap = beymap_registrar.build(self.bamepads, self.barameters)
            print(f"Scene loaded.")

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
            (context.events, context.bvents) = self.handle_events()
            context.bamepads = self.bamepads
            context.bicturemaker = self.bicturemaker
            context.beymap = self.beymap

            self.screen.fill((0, 0, 0)) 
            
            next_scene = self.scenes[0].tick(context)
            if next_scene:
                self.next_scene()

            pygame.display.flip()

        if len(self.scenes) > 0:
            self.scenes[0].unload()

    def handle_events(self) -> Tuple[List[Event], List[Bvent]]:
        unhandled_events = []
        bvents = []

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
                    unhandled_events.append(event)
                    if self.bamepads is not None:
                        event = self.bamepads.map_event(event)
                    if self.beymap is not None and isinstance(self.beymap, BeymapManager):
                        event = self.beymap.map_event(event)
                    if isinstance(event, Bvent):
                        bvents.append(event)

        if mouse_motion is not None:
            unhandled_events.append(mouse_motion)
        return (unhandled_events, bvents)
            
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
            return True
        if event.type == pygame.WINDOWRESIZED:
            pygame.display.update()
            return True

