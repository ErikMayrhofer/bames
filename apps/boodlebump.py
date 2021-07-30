import math

from pymunk.vec2d import Vec2d
from lib.bectangleretector import BectangleRetector, rect_to_verts
from lib import bamepad
from lib.bicturemaker import Bicturemaker
from lib.bolygonbetector import BolygonBetector

import pygame.transform
import pygame.draw
from lib.barser import BarserMethod
import pymunk
from lib.bame import Bame, BarsedContext, LoadContext, TickContext
import pygame
import cv2
import time
import pymunk.autogeometry


bols = BolygonBetector((170, 127, 127), (10, 255, 255))
rects = BectangleRetector((110, 255, 255), (130, 255, 255))


def barse_red_bolygons(image, field):
    field["red_bolygons"] = bols.betect(image)


def barse_blue_rectangles(image, field):
    field["blue_rectangles"] = rects.retect(image)


class BoodleBump:

    barse_red_lines = BarserMethod(barse_red_bolygons)
    barse_blue_rectangles = BarserMethod(barse_blue_rectangles)

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
        
        self.__init_objects()

        self.left_held = False
        self.right_held = False

        self.red_lines = []
        self.blue_rectangles = []
        self.last_updated = None
        self.time_won = None
        
    def tick(self, context: TickContext, barsed_context: BarsedContext):
        
        
        self.__handle_barsed_context(barsed_context)
        
        #Input handling
        if self.__handle_events(context):
            return True
        
        #Simulation
        sub_step_stuff = context.delta_ms / 1000 / self.sub_steps
        for _ in range(self.sub_steps):
            self.space.step(sub_step_stuff)

        self.__check_win()

        self.__render()

    def __init_objects(self):
        self.ground = pymunk.Segment(self.space.static_body, (-10, 0.5), (10, 0.5), 0.2)
        self.ground.friction = 1
        self.space.add(self.ground)

        self.boodle_sprite = pygame.transform.scale(pygame.image.load("img/Boodle.png"), (96, 96))
        boodle_mass = 1
        self.boodle_size = Vec2d(1, 1)
        boodle_moment = pymunk.moment_for_box(1, self.boodle_size)
        self.boodle = pymunk.Body(boodle_mass, boodle_moment)
        self.boodle_position_init = Vec2d(0, 1.5)
        self.boodle.position = self.boodle_position_init
        boodle_shape = pymunk.Poly.create_box(self.boodle, self.boodle_size)
        boodle_shape.friction = 1
        self.space.add(self.boodle, boodle_shape)

    def __reset(self):
        self.boodle.position = self.boodle_position_init
        self.boodle.angle = 0
        self.boodle.velocity = (0, 0)
        self.boodle.angular_velocity = 0

    def __handle_events(self, context: TickContext):

        well_grounded = self.__is_well_grounded()

        x = 0
        if context.beymap.player_action(1, "LEFT") and well_grounded:
            x -= 5
        if context.beymap.player_action(1, "RIGHT") and well_grounded:
            x = 5
        self.boodle.velocity = (x if x != 0 else self.boodle.velocity.x, self.boodle.velocity.y)

        for bvent in context.bvents:
            if bvent.action == "UP" and well_grounded:
                self.boodle.velocity = (self.boodle.velocity.x, 8)
            if bvent.action == "RESTART":
                self.__reset()
        
        for event in context.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                 return True#

        return False

    def __handle_barsed_context(self, barsed_context: BarsedContext):
        t = time.time()

        if self.last_updated is None or t - self.last_updated > 1:
            self.last_updated = t

            red_lines = barsed_context.data["red_bolygons"]
            if red_lines is not None:
                if self.red_lines:
                    self.space.remove(*self.red_lines)
                self.red_lines = []
                for line in red_lines:
                    for convexed_line in pymunk.autogeometry.convex_decomposition(line, 10):
                        if len(convexed_line) < 4:
                            continue
                        parsed_line = []
                        for point in convexed_line:
                            parsed_line.append(self.bicturemaker.game2munk(point))
                        line_ground = pymunk.Poly(self.space.static_body, parsed_line)
                        line_ground.friction = 1
                        self.space.add(line_ground)
                        self.red_lines.append(line_ground)

        self.blue_rectangles = barsed_context.data["blue_rectangles"]

    def __check_win(self):
        if self.time_won is None:
            for rectangle in self.blue_rectangles:
                rect = (self.bicturemaker.game2munk(rectangle[0]), rectangle[1] / self.bicturemaker.scale, math.degrees(rectangle[2]))
                boodle_rect = (self.boodle.position, self.boodle_size, math.degrees(self.boodle.angle))
                if cv2.rotatedRectangleIntersection(boodle_rect, rect)[0] != 0:
                    self.time_won = time.time()
        elif time.time() - self.time_won > 1:
            self.time_won = None
            self.__reset()

    def __render(self):
        self.bicturemaker.draw_line((255, 0, 255), self.ground.a, self.ground.b)

        for line in self.red_lines:
            self.bicturemaker.draw_polygon((63, 0, 0), line)

        for rectangle in self.blue_rectangles:
            self.bicturemaker.draw_polygon_from_game_vertices((0, 0, 63), rect_to_verts(rectangle))

        rotation = self.boodle.rotation_vector

        self.bicturemaker.draw_sprite(self.boodle_sprite, self.boodle.position, rotation)

    def __is_well_grounded(self):
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
        return well_grounded

if __name__ == '__main__':
    Bame(BoodleBump).run()
