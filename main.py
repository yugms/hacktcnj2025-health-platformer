import pygame
import pymunk
import pymunk.pygame_util
import sys

class Level:
    def __init__(self, space, level_data):
        self.space = space
        self.FRICTION = 0.8
        self.static_body = self.space.static_body
        self.platforms = []

        # Create platforms based on level data
        for start, end in level_data["platforms"]:
            platform = pymunk.Segment(self.static_body, start, end, 5)
            platform.friction = self.FRICTION
            platform.collision_type = 2
            self.space.add(platform)
            self.platforms.append(platform)

        platform_x = {}
        for i in range(len(self.platforms)):
            platform_x[i] = self.platforms[i]._get_a()[0]

        # Find the platform with the smallest x value for the spawn point
        min_key = min(platform_x, key=platform_x.get)
        middle_x_point = (self.platforms[min_key]._get_a()[0] + self.platforms[min_key]._get_b()[0]) / 2
        self.spawn_point = (middle_x_point, self.platforms[min_key]._get_a()[1]-100)

        # Find the platform with the greatest x value for the end point
        max_key = max(platform_x, key=platform_x.get)
        middle_x_point_end = (self.platforms[max_key]._get_a()[0] + self.platforms[max_key]._get_b()[0]) / 2
        self.end_point = (middle_x_point_end, self.platforms[max_key]._get_a()[1]-20)
class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("AI Health Platformer")
        self.screen = pygame.display.set_mode((1400, 900))
        self.clock = pygame.time.Clock()

        self.space = pymunk.Space()
        self.space.gravity = (0, 900)

        # Initialize player
        self.player = None
        self.player_shape = None
        self.create_player()

        self.health = 10.0
        self.font = pygame.font.Font("./assets/fonts/Sigmar-Regular.ttf", 24)

        # Draw options
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        # Collision tracking
        self.contact = {"on_ground": False}
        self.setup_collisions()

        # Level handling
        self.current_level = 0
        self.levels = [
            {
            "platforms": [
                [(50, 800), (300, 800)],
                [(350, 700), (600, 700)],
                [(650, 600), (900, 600)],
                [(950, 500), (1200, 500)],
                [(1250, 400), (1400, 400)],
                [(50, 300), (300, 300)],
                [(350, 200), (600, 200)],
                [(650, 100), (900, 100)],
                [(950, 50), (1200, 50)],
            ]
            },
            {
            "platforms": [
                [(100, 850), (400, 850)],
                [(450, 750), (750, 750)],
                [(800, 650), (1100, 650)],
                [(1150, 550), (1350, 550)],
                [(100, 450), (400, 450)],
                [(450, 350), (750, 350)],
                [(800, 250), (1100, 250)],
                [(1150, 150), (1350, 150)],
            ]
            },
            {
            "platforms": [
                [(50, 800), (200, 800)],
                [(250, 700), (400, 700)],
                [(450, 600), (600, 600)],
                [(650, 500), (800, 500)],
                [(850, 400), (1000, 400)],
                [(1050, 300), (1200, 300)],
                [(1250, 200), (1400, 200)],
            ]
            },
            {
            "platforms": [
                [(50, 850), (150, 850)],
                [(200, 750), (300, 750)],
                [(350, 650), (450, 650)],
                [(500, 550), (600, 550)],
                [(650, 450), (750, 450)],
                [(800, 350), (900, 350)],
                [(950, 250), (1050, 250)],
                [(1100, 150), (1200, 150)],
                [(1250, 50), (1350, 50)],
            ]
            },
            {
            "platforms": [
                [(50, 800), (150, 800)],
                [(200, 700), (300, 700)],
                [(350, 600), (450, 600)],
                [(500, 500), (600, 500)],
                [(650, 400), (750, 400)],
                [(800, 300), (900, 300)],
                [(950, 200), (1050, 200)],
                [(1100, 100), (1200, 100)],
                [(1250, 50), (1350, 50)],
            ]
            }
        ]
    def create_player(self):
        mass = 1
        width, height = 60, 60
        moment = pymunk.moment_for_box(mass, (width, height))
        self.player = pymunk.Body(mass, moment)
        self.player.position = (100, 450)
        self.player_shape = pymunk.Poly.create_box(self.player, (width, height))
        self.player_shape.friction = 0.8
        self.player_shape.collision_type = 1
        self.space.add(self.player, self.player_shape)

    def setup_collisions(self):
        def begin_player_ground(arbiter, space, data):
            self.contact["on_ground"] = True
            return True

        def separate_player_ground(arbiter, space, data):
            self.contact["on_ground"] = False
            return True

        handler = self.space.add_collision_handler(1, 2)
        handler.begin = begin_player_ground
        handler.separate = separate_player_ground

    def load_level(self, level_index):
        self.space.remove(*self.space.shapes)
        self.space.remove(*self.space.bodies)
        self.create_player()
        self.level = Level(self.space, self.levels[level_index])
        self.player.position = self.level.spawn_point
        self.player.velocity = (0,0)

    def draw_health(self):
        health_text = self.font.render(f"Health: {self.health:.0f}%", True, (0, 0, 0))
        self.screen.blit(health_text, (10, 10))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.contact["on_ground"]:
                        self.player.apply_impulse_at_local_point((0, -500))
                    if event.key == pygame.K_n:  # Move to next level
                        self.current_level = (self.current_level + 1) % len(self.levels)
                        self.load_level(self.current_level)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.player.velocity = pymunk.Vec2d(200, self.player.velocity.y)
            if keys[pygame.K_LEFT]:
                self.player.velocity = pymunk.Vec2d(-200, self.player.velocity.y)

            self.screen.fill((255, 255, 255))
            self.space.debug_draw(self.draw_options)
            self.draw_health()
            pygame.display.flip()

            self.space.step(1/60.0)
            self.clock.tick(60)
            self.player.angular_velocity = 0

    pygame.quit()

def main():
    Game().run()

if __name__ == "__main__":
    main()
