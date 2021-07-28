from ast import parse
from lib import bicturemaker
from lib.bicturemaker import Bicturemaker
from lib.bolygonbetector import BolygonBetector

import numpy as np
from lib.barser import BarserMethod
import pymunk
from lib.bame import Bame, BarsedContext, LoadContext, TickContext
import pygame
import cv2
import time
import pymunk.autogeometry


bols = BolygonBetector()


def barse_red_bolygons(image, field):
    field["bolygons"] = bols.detect(image)


class BoodleBump:

    barse_red_lines = BarserMethod(barse_red_bolygons)

    def load(self, context: LoadContext) -> None:
        pygame.init()

        self.bicturemaker = context.bicturemaker
        self.bicturemaker.set_origin(Bicturemaker.BOTTOM_CENTER)
        self.bicturemaker.set_scale(1/20)

        self.space = pymunk.Space()
        self.space.gravity = (0, -9.81)

        self.ground = pymunk.Segment(self.space.static_body, (-10, 0.5), (10, 0.5), 0.05)
        self.ground.friction = 1
        self.space.add(self.ground)

        self.boodle_sprite = pygame.transform.scale(pygame.image.load("img/Boodle.png"), (96, 96))
        boodle_mass = 1
        boodle_size = (1, 1)
        boodle_moment = pymunk.moment_for_box(1, boodle_size)
        self.boodle = pymunk.Body(boodle_mass, boodle_moment)
        self.boodle_position_init = (0, 7.5)
        self.boodle.position = self.boodle_position_init
        boodle_shape = pymunk.Poly.create_box(self.boodle, boodle_size)
        boodle_shape.friction = 1
        self.space.add(self.boodle, boodle_shape)

        self.left_held = False
        self.right_held = False

        self.drawn_lines = None
        self.last_updated = None

        self.left_held = False
        self.left_held = False
        
    def tick(self, context: TickContext, barsed_context: BarsedContext):


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
                            parsed_line.append(self.bicturemaker.game2munk(point))
                        line_ground = pymunk.Poly(self.space.static_body, parsed_line)
                        line_ground.friction = 1
                        self.space.add(line_ground)
                        self.drawn_lines.append(line_ground)

        grounding = {
            "normal": (0, 0),
            "penetration": (0, 0),
            "impulse": (0, 0),
            "position": (0, 0),
            "body": None,
        }

        def f(arbiter):
            n = -arbiter.contact_point_set.normal
            if n.y > grounding["normal"][1]:
                grounding["normal"] = n
                grounding["penetration"] = -arbiter.contact_point_set.points[0].distance
                grounding["body"] = arbiter.shapes[1].body
                grounding["impulse"] = arbiter.total_impulse
                grounding["position"] = arbiter.contact_point_set.points[0].point_b

        self.boodle.each_arbiter(f)

        well_grounded = False
        if (
            grounding["body"] != None
            and abs(grounding["normal"][0] / grounding["normal"][1]) < 1 # TODO HARD CODED 
        ):
            well_grounded = True

        #Input handling
        for event in context.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.boodle.position = self.boodle_position_init
                self.boodle.angle = 0
                self.boodle.velocity = (0, 0)
                self.boodle.angular_velocity = 0
            if event.type == pygame.KEYDOWN and event.key == pygame.K_UP and well_grounded:
                self.boodle.velocity = (self.boodle.velocity.x, 8)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN and well_grounded:
                self.boodle.velocity = (self.boodle.velocity.x, -8)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self.left_held = True
            if event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                self.left_held = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self.right_held= True
            if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                self.right_held= False

        if self.left_held and well_grounded:
            self.boodle.velocity = (-5, self.boodle.velocity.y)
        if self.right_held and well_grounded:
            self.boodle.velocity = (5, self.boodle.velocity.y)

        #Simulation
        self.space.step(context.delta_ms / 1000)

        #Rendering
        self.bicturemaker.draw_line(255, self.ground.a, self.ground.b, 1)

        for line in self.drawn_lines:
            self.bicturemaker.draw_polygon((63, 0, 0), line)

        rotation = self.boodle.rotation_vector
        self.bicturemaker.draw_sprite(self.boodle_sprite, self.boodle.position, (-0.5, 0.5), rotation)

if __name__ == '__main__':
    Bame(BoodleBump).run()
