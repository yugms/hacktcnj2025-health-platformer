import pygame
import pymunk
import pymunk.pygame_util
import sys

class Game:
    def __init__(self):
        self.FRICTION = 0.8
        pygame.init()
        pygame.display.set_caption("AI Health Platformer")
        self.screen = pygame.display.set_mode((800, 600))

        self.clock = pygame.time.Clock()

        # Set up the physics simulation space.
        self.space = pymunk.Space()
        self.space.gravity = (0, 900)
        self.static_body = self.space.static_body

        # Create ground segment.
        self.ground = pymunk.Segment(self.static_body, (0, 500), (900, 500), 5)
        self.ground.friction = self.FRICTION
        self.ground.collision_type = 2  # Assign collision type for ground/platform.
        self.space.add(self.ground)

        # Create a platform.
        self.platform = pymunk.Segment(self.static_body, (600, 400), (700, 400), 5)
        self.platform.friction = self.FRICTION
        self.platform.collision_type = 2  # Same collision type as ground.
        self.space.add(self.platform)

        # Create a dynamic body for the player.
        mass = 1
        width, height = 60, 60
        moment = pymunk.moment_for_box(mass, (width, height))
        self.player = pymunk.Body(mass, moment)
        self.player.position = (100, 450)
        self.player_shape = pymunk.Poly.create_box(self.player, (width, height))
        self.player_shape.friction = self.FRICTION
        self.player_shape.collision_type = 1  # Assign collision type for player.
        self.space.add(self.player, self.player_shape)

        # Set up draw options to visualize the physics objects.
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        # Initialize health variable and font.
        self.health = 10.0
        self.font = pygame.font.Font("./assets/fonts/Sigmar-Regular.ttf", 24)

        # Use a dictionary to track whether the player is on the ground.
        self.contact = {"on_ground": False}

        # Define collision callbacks for when the player touches or leaves a ground object.
        def begin_player_ground(arbiter, space, data):
            self.contact["on_ground"] = True
            return True

        def separate_player_ground(arbiter, space, data):
            self.contact["on_ground"] = False
            return True

        # Add a collision handler between the player (collision_type 1) and ground/platform (collision_type 2).
        handler = self.space.add_collision_handler(1, 2)
        handler.begin = begin_player_ground
        handler.separate = separate_player_ground

    def draw_health(self):
        health_text = self.font.render(f"Health: {self.health:.0f}%", True, (0, 0, 0))
        self.screen.blit(health_text, (10, 10))

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                # Check for jump input and ensure the player is on the ground.
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.contact["on_ground"]:
                        self.player.apply_impulse_at_local_point((0, -500))

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
            # Lock rotation to prevent flipping.
            self.player.angular_velocity = 0

    pygame.quit()

def main():
    Game().run()

if __name__ == "__main__":
    main()