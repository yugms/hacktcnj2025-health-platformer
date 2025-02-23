import pygame
import pymunk
import pymunk.pygame_util

def main():
    FRICTION = 0.8
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("AI Health Platformer")
    clock = pygame.time.Clock()

    # Set up the physics simulation space.
    space = pymunk.Space()
    space.gravity = (0, 900)
    static_body = space.static_body

    # Create ground segment.
    ground = pymunk.Segment(static_body, (0, 500), (900, 500), 5)
    ground.friction = FRICTION
    ground.collision_type = 2  # Assign collision type for ground/platform.
    space.add(ground)

    # Create a platform.
    platform = pymunk.Segment(static_body, (600, 400), (700, 400), 5)
    platform.friction = FRICTION
    platform.collision_type = 2  # Same collision type as ground.
    space.add(platform)

    # Create a dynamic body for the player.
    mass = 1
    width, height = 60, 60
    moment = pymunk.moment_for_box(mass, (width, height))
    player = pymunk.Body(mass, moment)
    player.position = (100, 450)
    player_shape = pymunk.Poly.create_box(player, (width, height))
    player_shape.friction = FRICTION
    player_shape.collision_type = 1  # Assign collision type for player.
    space.add(player, player_shape)

    # Set up draw options to visualize the physics objects.
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # Initialize health variable and font.
    health = 10.0
    font = pygame.font.Font("./assets/fonts/Sigmar-Regular.ttf", 24)
    def draw_health():
        health_text = font.render(f"Health: {health:.0f}%", True, (0, 0, 0))
        screen.blit(health_text, (10, 10))

    # Use a dictionary to track whether the player is on the ground.
    contact = {"on_ground": False}

    # Define collision callbacks for when the player touches or leaves a ground object.
    def begin_player_ground(arbiter, space, data):
        contact["on_ground"] = True
        return True

    def separate_player_ground(arbiter, space, data):
        contact["on_ground"] = False
        return True

    # Add a collision handler between the player (collision_type 1) and ground/platform (collision_type 2).
    handler = space.add_collision_handler(1, 2)
    handler.begin = begin_player_ground
    handler.separate = separate_player_ground

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Check for jump input and ensure the player is on the ground.
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP and contact["on_ground"]:
                    player.apply_impulse_at_local_point((0, -500))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            player.velocity = pymunk.Vec2d(200, player.velocity.y)
        if keys[pygame.K_LEFT]:
            player.velocity = pymunk.Vec2d(-200, player.velocity.y)

        screen.fill((255, 255, 255))
        space.debug_draw(draw_options)
        draw_health()
        pygame.display.flip()

        space.step(1/60.0)
        clock.tick(60)
        # Lock rotation to prevent flipping.
        player.angular_velocity = 0

    pygame.quit()

if __name__ == "__main__":
    main()