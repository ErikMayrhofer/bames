from lib.bicturemaker import Bicturemaker
import pymunk
from lib.barser import BarserMethod
from lib.bolygonbetector import BolygonBetector
import pygame
from lib.bame import Bame, BarsedContext, LoadContext, TickContext
import random
import pygame.gfxdraw


bols = BolygonBetector()


def barse_red_bolygons(image, field):
    field["bolygons"] = bols.detect(image)


class Bong:

    barse_red_lines = BarserMethod(barse_red_bolygons)
    
    def load(self, context: LoadContext) -> None:
        self.bicturemaker = context.bicturemaker
        self.bicturemaker.set_origin(Bicturemaker.CENTER)
        self.bicturemaker.set_scale(1/10)

        self.space = pymunk.Space()

        top = pymunk.Segment(self.space.static_body, (-10, 5), (10, 5), 0)
        bottom = pymunk.Segment(self.space.static_body, (-10, -5), (10, -5), 0)
        self.space.add(top)
        self.space.add(bottom)

        ball_mass = 1
        self.ball_radius = 0.5
        ball_moment = pymunk.moment_for_circle(ball_mass, 0, self.ball_radius)
        self.ball = pymunk.Body(ball_mass, ball_moment)
        self.ball_position_init = (0, 0)
        self.ball.position = self.ball_position_init
        ball_shape = pymunk.Circle(self.ball, self.ball_radius)
        ball_shape.friction = 0
        self.space.add(self.ball, ball_shape)

        starting_direction = bool(random.getrandbits(1))
        self.ball.velocity = (1 if starting_direction else -1, 0)

    def tick(self, context: TickContext, barsed_context: BarsedContext):
        self.space.step(context.delta_ms / 1000)

        resolution = context.screen.get_size()
        scale = resolution[0] / 20

        ball_position = self.bicturemaker.munk2game(self.ball.position)
        print(ball_position)
        pygame.gfxdraw.aacircle(context.screen, int(ball_position[0]), int(ball_position[1]), int(self.ball_radius * scale), (255, 0, 0))


if __name__ == '__main__':
    Bame(Bong).run()
