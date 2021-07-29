from typing import Tuple
import numpy as np

import pygame
import pygame.gfxdraw
import pygame.draw
from pymunk import Vec2d


class Bicturemaker:

    TOP_LEFT = Vec2d(0, 0)
    TOP_CENTER = Vec2d(0.5, 0)
    TOP_RIGHT = Vec2d(1, 0)
    CENTER_LEFT = Vec2d(0, 0.5)
    CENTER = Vec2d(0.5, 0.5)
    CENTER_RIGHT = Vec2d(1, 0.5)
    BOTTOM_LEFT = Vec2d(0, 1)
    BOTTOM_CENTER = Vec2d(0.5, 1)
    BOTTOM_RIGHT = Vec2d(1, 1)

    resolution: Tuple[int, int]
    origin: Tuple[int, int]
    scale: int

    def __init__(self, screen, barameters):
        self.screen = screen
        resolution = screen.get_size()
        self.resolution = Vec2d(resolution[0], resolution[1])


    def draw_sprite(self, sprite, center_pos, rotation=0):
        angle = np.degrees(np.arctan2(rotation.y, rotation.x))
        # actual_position = (position[0] + offset[0], position[1] + offset[1])
        (rotated_image, new_rect) = self.__rot_center(sprite, angle, self.munk2game(center_pos))
        self.screen.blit(rotated_image, new_rect)

    def __rot_center(self, image, angle, center):
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_rect(center = image.get_rect(center = center).center)
        return rotated_image, new_rect

    def draw_line(self, color, start_pos, end_pos, width=1):
        pygame.draw.line(self.screen, color, self.munk2game(start_pos), self.munk2game(end_pos), width)

    def draw_filled_circle(self, position, radius, color):
        actual_position = self.munk2game(position)
        pygame.gfxdraw.filled_circle(self.screen, int(actual_position.x), int(actual_position.y), int(radius * self.scale), color)

    def draw_aacircle(self, position, radius, color):
        actual_position = self.munk2game(position)
        pygame.gfxdraw.aacircle(self.screen, int(actual_position.x), int(actual_position.y), int(radius * self.scale), color)

    def draw_rect(self, color, topleft, bottomright, width=0, border_radius=-1):
        actual_topleft = self.munk2game(topleft)
        actual_bottomright = self.munk2game(bottomright)
        width_height = actual_bottomright - actual_topleft
        rect = pygame.Rect(actual_topleft, width_height)
        pygame.draw.rect(self.screen, color, rect, int(width * self.scale), int(border_radius * self.scale))

    def draw_lines(self, color, closed, points, width=1):
        pygame_points = []
        for point in points:
            pygame_points.append(self.munk2game(point))
        pygame.draw.lines(self.screen, color, closed, pygame_points, width)

    def draw_polygon(self, color, polygon):
        pygame_vertices = []
        for vertex in polygon.get_vertices():
            pygame_vertices.append(self.munk2game(vertex))
        pygame.draw.polygon(self.screen, color, pygame_vertices)


    def set_origin(self, origin: Vec2d):
        self.origin = Vec2d(origin.x * self.resolution.x, origin.y * self.resolution.y)

    def set_scale(self, scale: int):
        self.scale = scale * self.screen.get_width()

    def munk2game(self, point: Vec2d):
        return Vec2d(self.origin.x + point.x * self.scale, self.origin.y - point.y * self.scale)

    def game2munk(self, point: Vec2d):
        return Vec2d((point.x - self.origin.x) / self.scale, (self.origin.y - point.y) / self.scale)
