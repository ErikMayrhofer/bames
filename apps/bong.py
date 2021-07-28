import pymunk
from lib.barser import BarserMethod
from lib.bolygonbetector import BolygonBetector
import pygame
from lib.bame import Bame, BarsedContext, TickContext
import random
import pygame.gfxdraw


bols = BolygonBetector()


def barse_red_bolygons(image, field):
    field["bolygons"] = bols.detect(image)


class Bong:

    barse_red_lines = BarserMethod(barse_red_bolygons)
    
    def load(self) -> None:
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
        origin = (resolution[0] / 2, resolution[1] / 2)
        scale = resolution[0] / 20

        ball_position = self.__with_origin_and_scale(self.ball.position, origin, scale)
        print(ball_position)
        pygame.gfxdraw.aacircle(context.screen, int(ball_position[0]), int(ball_position[1]), int(self.ball_radius * scale), (255, 0, 0))

    def __with_origin_and_scale(self, point, origin, scale):
        return (origin[0] + point[0] * scale, origin[1] - point[1] * scale)

    def __without_origin_and_scale(self, point, origin, scale):
        return ((point[0] - origin[0]) / scale, (origin[1] - point[1]) / scale)


if __name__ == '__main__':
    Bame(Bong).run()
