import pymunk
from lib.bame import Bame, BarsedContext, TickContext
import pygame


class BoodleBump:

    def load(self) -> None:
        pygame.init()

        self.space = pymunk.Space()
        self.space.gravity = (0, -9.81)

        self.ground = pymunk.Segment(self.space.static_body, (-5, 0.5), (5, 0.5), 0.05)
        self.ground.friction = 0.3
        self.space.add(self.ground)

        self.boodle_sprite = pygame.transform.scale(pygame.image.load("img/Boodle.png"), (192, 192))
        boodle_mass = 1
        boodle_size = (1, 1)
        boodle_moment = pymunk.moment_for_box(1, boodle_size)
        self.boodle = pymunk.Body(boodle_mass, boodle_moment)
        self.boodle.position = (0, 7.5)
        boodle_shape = pymunk.Poly.create_box(self.boodle, boodle_size)
        boodle_shape.friction = 0.3
        self.space.add(self.boodle, boodle_shape)

        self.left_pressed = False
        self.right_pressed = False
        
    def tick(self, context: TickContext, barsed_context: BarsedContext):

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
            and abs(grounding["normal"][0] / grounding["normal"][1]) < 0.3 # TODO HARD CODED 
        ):
            well_grounded = True

        for event in context.events:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return True
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE and well_grounded:
                self.boodle.apply_impulse_at_local_point((0, 5))
            if event.type == pygame.KEYDOWN and event.key == pygame.K_LEFT:
                self.left_pressed = True
            if event.type == pygame.KEYUP and event.key == pygame.K_LEFT:
                self.left_pressed = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RIGHT:
                self.right_pressed = True
            if event.type == pygame.KEYUP and event.key == pygame.K_RIGHT:
                self.right_pressed = False

        if self.right_pressed:
            self.boodle.velocity = (2, self.boodle.velocity[1])
        if self.left_pressed:
            self.boodle.velocity = (-2, self.boodle.velocity[1])

        resolution = context.screen.get_size()
        origin = (resolution[0] / 2, resolution[1])
        scale = resolution[0] / 10

        self.space.step(context.delta_ms / 1000)

        print()
        a = self.__with_origin_and_scale(self.ground.a, origin, scale)
        b = self.__with_origin_and_scale(self.ground.b, origin, scale)
        pygame.draw.line(context.screen, 255, a, b, 1)
        boodle_position = (self.boodle.position[0] -  0.5, self.boodle.position[1] + 0.5)
        boodle_position = self.__with_origin_and_scale(boodle_position, origin, scale)
        context.screen.blit(self.boodle_sprite, boodle_position)
        print(boodle_position)
    
    def __with_origin_and_scale(self, point, origin, scale):
        return (origin[0] + point[0] * scale, origin[1] - point[1] * scale)

if __name__ == '__main__':
    Bame(BoodleBump).run()
