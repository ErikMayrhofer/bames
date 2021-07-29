import time
from typing import List
from pygame.event import Event
from pymunk.vec2d import Vec2d
from lib.bicturemaker import Bicturemaker
import pymunk
from lib.barser import BarserMethod
from lib.bolygonbetector import BolygonBetector
import pygame
from lib.bame import Bame, BarsedContext, LoadContext, TickContext
import random
import pygame.gfxdraw
import pymunk.autogeometry
import pygame.font


bols = BolygonBetector()


def barse_red_bolygons(image, field):
    field["bolygons"] = bols.detect(image)


class Bong:

    barse_red_lines = BarserMethod(barse_red_bolygons)
    
    def load(self, context: LoadContext) -> None:
        
        self.bicturemaker = context.bicturemaker
        self.bicturemaker.set_origin(Bicturemaker.BOTTOM_CENTER)
        self.bicturemaker.set_scale(1/20)

        self.space = pymunk.Space()
        self.space.gravity = (0, -9.81)

        self.__init_objects()

        self.started = False

        self.drawn_lines = []
        self.last_updated = None

        self.time_won = None

    def __init_objects(self):

        self.start_x = 9
        self.start_y = 10
        self.end_x = 9
        self.end_y = 1
        self.start = Vec2d(random.randint(-self.start_x, self.start_x), self.start_y)
        self.end = Vec2d(random.randint(-self.end_x, self.end_x), self.end_y)

        ball_mass = 1
        self.ball_radius = 0.5
        ball_moment = pymunk.moment_for_circle(ball_mass, 0, self.ball_radius)
        self.ball = pymunk.Body(ball_mass, ball_moment)
        self.ball.position = self.start
        ball_shape = pymunk.Circle(self.ball, self.ball_radius)
        ball_shape.friction = 0.3
        self.space.add(self.ball, ball_shape)

        self.borders = []
        _, _, self.start_bottom = self.__set_borders(self.start)
        self.__set_borders(self.end)

    def tick(self, context: TickContext, barsed_context: BarsedContext):

        if self.__handle_events(context.events):
            return True

        if not self.started:
            self.__handle_barsed_context(barsed_context)

        self.space.step(context.delta_ms / 1000)

        self.__check_win()

        self.__render()

    def __reset(self):
        self.start = Vec2d(random.randint(-self.start_x, self.start_x), self.start_y)
        self.end = Vec2d(random.randint(-self.end_x, self.end_x), self.end_y)

        self.ball.position = self.start
        self.ball.velocity = (0, 0)

        self.space.remove(*self.borders)

        self.borders = []
        _, _, self.start_bottom = self.__set_borders(self.start)
        self.__set_borders(self.end)

    def __handle_events(self, events: List[Event]):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
                if event.key == pygame.K_SPACE and not self.started:
                    self.started = True
                    self.space.remove(self.start_bottom)
                    self.borders.remove(self.start_bottom)
                if event.key == pygame.K_r:
                    self.started = False
                    self.__reset()
        return False

    def __handle_barsed_context(self, barsed_context: BarsedContext):
        t = time.time()

        if self.last_updated is None or t - self.last_updated > 1:
            self.last_updated = t

            drawn_lines = barsed_context.data["bolygons"]
            if drawn_lines is not None:
                if self.drawn_lines:
                    self.space.remove(*self.drawn_lines)
                self.drawn_lines = []
                for line in drawn_lines:
                    for convexed_line in pymunk.autogeometry.convex_decomposition(line, 10):
                        if len(convexed_line) < 4:
                            continue
                        parsed_line = []
                        for point in convexed_line:
                            parsed_line.append(self.bicturemaker.game2munk(Vec2d(point[0], point[1])))
                        line_ground = pymunk.Poly(self.space.static_body, parsed_line)
                        line_ground.friction = 0.3
                        line_ground.elasticity = 1
                        self.space.add(line_ground)
                        self.drawn_lines.append(line_ground)

    def __check_win(self):
        t = time.time()
        if self.time_won is None:
            print((self.ball.position - self.end).length)
        if ((self.ball.position - self.end).length < 0.2 and self.time_won is None) or self.ball.position.y < 0:
            print("WON")
            self.time_won = time.time()
        if self.time_won is not None and t - self.time_won > 1:
            self.time_won = None
            self.started = False
            self.__reset()

    def __render(self):

        self.bicturemaker.draw_filled_circle(self.ball.position, self.ball_radius, (0, 0, 255))

        for border in self.borders:
            self.bicturemaker.draw_line((255, 0, 0), border.a, border.b)

        for line in self.drawn_lines:
            self.bicturemaker.draw_polygon((63, 0, 0), line)

    def __set_borders(self, point: Vec2d):
        left_top = point + (-self.ball_radius - 0.1, 0)
        left_bottom = point + (-self.ball_radius - 0.1, -self.ball_radius - 0.1)
        right_top = point + (self.ball_radius + 0.1, 0)
        right_bottom = point + (self.ball_radius + 0.1, -self.ball_radius - 0.1)
        bottom_left = point + (-self.ball_radius - 0.1, -self.ball_radius - 0.1)
        bottom_right = point + (self.ball_radius + 0.1, -self.ball_radius - 0.1)
        left = pymunk.Segment(self.space.static_body, left_top, left_bottom, 0)
        left.friction = 0
        right = pymunk.Segment(self.space.static_body, right_top, right_bottom, 0)
        right.friction = 0
        bottom = pymunk.Segment(self.space.static_body, bottom_left, bottom_right, 0)
        bottom.friction = 0.3
        self.space.add(left)
        self.space.add(right)
        self.space.add(bottom)
        self.borders.append(left)
        self.borders.append(right)
        self.borders.append(bottom)
        return left, right, bottom

if __name__ == '__main__':
    Bame(Bong).run()