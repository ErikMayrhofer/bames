from typing import Type
import pygame

class TickContext:
    fps: float
    delta_ms: int

class Bame:
    def __init__(self, classname: Type):
        self.game_instance = classname()
        self.running = False

    

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 480))


        splash_img = pygame.image.load("img/Logo.jpg")

        for i in range(255):
            self.screen.fill((255,255,255))
            self.screen.blit(splash_img, (0, 0, 640, 480))
            self.screen.fill((i, i, i),special_flags=pygame.BLEND_MULT)
            pygame.display.flip()
            pygame.time.wait(1)
        pygame.time.wait(100)
        for i in reversed(range(255)):
            self.screen.fill((255,255,255))
            self.screen.blit(splash_img, (0, 0, 640, 480))
            self.screen.fill((i, i, i),special_flags=pygame.BLEND_MULT)
            pygame.display.flip()
            pygame.time.wait(1)

        self.start_loop()

    def start_loop(self):
        clock = pygame.time.Clock()

        self.running = True
        while self.running:
            delta_t = clock.tick(60)
            context = TickContext()
            context.fps = 1000/delta_t
            context.delta_ms = delta_t

            self.screen.fill((0, 0, 0)) 

            for event in pygame.event.get():
                self.handle_event(event)
            
            self.game_instance.tick(context)

            pygame.display.flip()

        print("Bye!")
            
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            self.running = False
