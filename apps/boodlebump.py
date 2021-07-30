from ast import parse
from lib import bamepad, bicturemaker
from lib.bicturemaker import Bicturemaker
from lib.bolygonbetector import BolygonBetector

import pygame.transform
import pygame.draw
import numpy as np
from lib.barser import BarserContext, BarserMethod
import pymunk
from lib.bame import Bame, BameMetadata, BarsedContext, LoadContext, TickContext
import pygame
import cv2
import time
import pymunk.autogeometry




def barse_red_bolygons(image, field, context):
    field["bolygons"] = context.bols.detect(image)


class BoodleBump:

    barser_context = BarserContext(
            bols = BolygonBetector((170, 127, 127), (10, 255, 255))
            )

    barse_red_lines = BarserMethod(barse_red_bolygons)

    def load(self, context: LoadContext) -> None:

        context.beymap_registrar.add_action("UP", bamepad.BUTTON_SYMBOL_TOP)
        context.beymap_registrar.add_action("DOWN", bamepad.BUTTON_SYMBOL_BOTTOM)
        context.beymap_registrar.add_action("LEFT", bamepad.BUTTON_SYMBOL_LEFT)
        context.beymap_registrar.add_action("RIGHT", bamepad.BUTTON_SYMBOL_RIGHT)
        context.beymap_registrar.add_action("RESTART", bamepad.MENU_RIGHT)

        self.bicturemaker = context.bicturemaker
        self.bicturemaker.set_origin(Bicturemaker.BOTTOM_CENTER)
        self.bicturemaker.set_scale(1/20)

        self.space = pymunk.Space()
        self.space.iterations = 10
        self.space.idle_speed_threshold = 0.0000001
        self.space.gravity = (0, -9.81)
        self.sub_steps = 20

        self.ground = pymunk.Segment(self.space.static_body, (-10, 0.5), (10, 0.5), 0.2)
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

        self.drawn_lines = []
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
        for bvent in context.bvents:
            if bvent.action == "UP" and well_grounded:
                self.boodle.velocity = (self.boodle.velocity.x, 8)
            if bvent.action == "DOWN" and well_grounded:
                self.boodle.velocity = (self.boodle.velocity.x, -8)
            if bvent.action == "RESTART":
                self.boodle.position = self.boodle_position_init
                self.boodle.angle = 0
                self.boodle.velocity = (0, 0)
                self.boodle.angular_velocity = 0
        for event in context.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                 return True

        if context.beymap.player_action(1, "LEFT") and well_grounded:
            self.boodle.velocity = (-5, self.boodle.velocity.y)
        if context.beymap.player_action(1, "RIGHT") and well_grounded:
            self.boodle.velocity = (5, self.boodle.velocity.y)

        #Simulation
        sub_step_stuff = context.delta_ms / 1000 / self.sub_steps
        for _ in range(self.sub_steps):
            self.space.step(sub_step_stuff)

        #Rendering
        self.bicturemaker.draw_line((255, 0, 255), self.ground.a, self.ground.b)

        for line in self.drawn_lines:
            self.bicturemaker.draw_polygon((63, 0, 0), line)

        rotation = self.boodle.rotation_vector

        self.bicturemaker.draw_sprite(self.boodle_sprite, self.boodle.position, rotation)

bame_metadata = BameMetadata(name="Boodle Bump", clazz=BoodleBump)

if __name__ == '__main__':
    Bame(BoodleBump).run()
