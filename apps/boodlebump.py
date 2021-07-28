from ast import parse

import numpy as np
from lib.barser import BarserMethod
import pymunk
from lib.bame import Bame, BarsedContext, TickContext
import pygame
import cv2
import time


def barse_red_lines(image, field):
    img_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(img_hsv, (0, 127, 127), (10, 255, 255))
    mask2 = cv2.inRange(img_hsv, (170, 127, 127), (179, 255, 255))
    mask = mask1 + mask2
    contours, hierarchy = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if contours:
        smooth_contours = []
        for contour in contours:
            smooth_contour = contour
            area = cv2.contourArea(contour)
            while smooth_contour.size > area / 32:
                smooth_contour = smooth_contour[1::4].astype(int)
            parsed_contour = [x[0].tolist() for x in smooth_contour]
            smooth_contours.append(parsed_contour)
            #cv2.drawContours(image, [smooth_contour], -1, (0,0,0), 2)
    #cv2.imshow("lines", cv2.resize(image, (960, 540)))
    #cv2.waitKey(1)
    field["drawn_lines"] = smooth_contours

class BoodleBump:

    barse_red_lines = BarserMethod(barse_red_lines)

    def load(self) -> None:
        pygame.init()

        self.space = pymunk.Space()
        self.space.gravity = (0, -9.81)

        self.ground = pymunk.Segment(self.space.static_body, (-10, 0.5), (10, 0.5), 0.05)
        self.ground.friction = 0.5
        self.space.add(self.ground)

        self.boodle_sprite = pygame.transform.scale(pygame.image.load("img/Boodle.png"), (96, 96))
        boodle_mass = 1
        boodle_size = (1, 1)
        boodle_moment = pymunk.moment_for_box(1, boodle_size)
        self.boodle = pymunk.Body(boodle_mass, boodle_moment)
        self.boodle.position = (0, 7.5)
        boodle_shape = pymunk.Poly.create_box(self.boodle, boodle_size)
        boodle_shape.friction = 1
        self.space.add(self.boodle, boodle_shape)

        self.left_pressed = False
        self.right_pressed = False

        self.drawn_lines = None
        self.last_updated = None
        
    def tick(self, context: TickContext, barsed_context: BarsedContext):

        resolution = context.screen.get_size()
        origin = (resolution[0] / 2, resolution[1])
        scale = resolution[0] / 20

        t = time.time()
        if self.last_updated is None or t - self.last_updated > 1:
            self.last_updated = t
            if self.drawn_lines:
                self.space.remove(*self.drawn_lines)
            self.drawn_lines = []
            drawn_lines = barsed_context.data["drawn_lines"]
            for line in drawn_lines:
                parsed_line = []
                for point in line:
                    parsed_line.append(self.__without_origin_and_scale(point, origin, scale))
                line_ground = pymunk.Poly(self.space.static_body, parsed_line)
                line_ground.friction = 0.5
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

        for event in context.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and well_grounded:
                self.boodle.apply_impulse_at_local_point((0, 8))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT and well_grounded:
                self.left_pressed = True
            if (event.type == pygame.KEYUP and event.key == pygame.K_LEFT):
                self.left_pressed = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT and well_grounded:
                self.right_pressed = True
            if (event.type == pygame.KEYUP and event.key == pygame.K_RIGHT):
                self.right_pressed = False

        if self.right_pressed and well_grounded:
            self.boodle.velocity = (2, self.boodle.velocity[1])
        if self.left_pressed and well_grounded:
            self.boodle.velocity = (-2, self.boodle.velocity[1])

        self.space.step(context.delta_ms / 1000)

        a = self.__with_origin_and_scale(self.ground.a, origin, scale)
        b = self.__with_origin_and_scale(self.ground.b, origin, scale)
        pygame.draw.line(context.screen, 255, a, b, 1)
        for line in self.drawn_lines:
            parsed_line = []
            for point in line.get_vertices():
                parsed_line.append(self.__with_origin_and_scale(point, origin, scale))
            pygame.draw.polygon(context.screen, 255, parsed_line)
        boodle_position = (self.boodle.position[0] -  0.5, self.boodle.position[1] + 0.5)
        boodle_position = self.__with_origin_and_scale(boodle_position, origin, scale)
        rotation = self.boodle.rotation_vector
        context.screen.blit(pygame.transform.rotate(self.boodle_sprite, np.degrees(np.arctan2(rotation.y, rotation.x))), boodle_position)
    
        print(self.boodle.rotation_vector)

    def __with_origin_and_scale(self, point, origin, scale):
        return (origin[0] + point[0] * scale, origin[1] - point[1] * scale)

    def __without_origin_and_scale(self, point, origin, scale):
        return ((point[0] - origin[0]) / scale, (origin[1] - point[1]) / scale)

if __name__ == '__main__':
    Bame(BoodleBump).run()
