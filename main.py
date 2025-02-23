import pygame.base
import pygame
import pymunk
import pymunk.pygame_util

def main():
    FRICTION = 0.8
    # Initialize Pygame and create a window.
    pygame.init()
    keys = pygame.key.get_pressed()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("AI Health Platformer")
    clock = pygame.time.Clock()

    # Set up the physics simulation space.
    space = pymunk.Space()
    space.gravity = (0, 900)  # Gravity pulling downward.

    # Create static bodies for the park features.
    static_body = space.static_body

    # Ground segment.
    ground = pymunk.Segment(static_body, (0, 500), (900, 500), 5)
    ground.friction = FRICTION
    space.add(ground)

    # Ramp: a simple inclined plane.
    #ramp = pymunk.Segment(static_body, (400, 500), (600, 350), 5)
    #ramp.friction = 1.0
    #space.add(ramp)

    # Rail: a short inclined rail.
    #rail = pymunk.Segment(static_body, (150, 500), (250, 450), 5)
    #rail.friction = 1.0
    #space.add(rail)


    # Create a dynamic body for the skateboard.
    mass = 1
    width, height = 60, 60  # Dimensions of the skateboard.
    moment = pymunk.moment_for_box(mass, (width, height))
    player = pymunk.Body(mass, moment)
    player.position = (100, 450)
    player_shape = pymunk.Poly.create_box(player, (width, height))
    player_shape.friction = FRICTION
    space.add(player, player_shape)

    platform = pymunk.Segment(static_body, (600, 400), (700, 400), 5)
    platform.friction = FRICTION
    space.add(platform)

    # Set up draw options to visualize the physics objects.
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    # Initialize health variable.
    health = 10.0

    # Set up font for displaying health.
    font = pygame.font.Font("./assets/fonts/Sigmar-Regular.ttf", 24)

    def draw_health():
        health_text = font.render(f"Health: {health:.0f}%", True, (0, 0, 0))
        screen.blit(health_text, (10, 10))

    running = True
    onGround = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            # Apply impulses when arrow keys are pressed.
        if event.type == pygame.KEYDOWN:
             #   if event.key == pygame.K_RIGHT:
              #      skateboard_body.velocity = pymunk.Vec2d(200, 0)
                    #skateboard_body.apply_force_at_local_point((200, 0))
               # elif event.key == pygame.K_LEFT:
                #    skateboard_body.velocity = pymunk.Vec2d(-200, 0)
            if event.key == pygame.K_UP and ((player.position.y < 470) and (player.position.y) > 460):
                    # A jump impulse.
                player.apply_impulse_at_local_point((0, -500))
                onGround = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            player.velocity = pymunk.Vec2d(200, player.velocity.y)
        if keys[pygame.K_LEFT]:
            player.velocity = pymunk.Vec2d(-200, player.velocity.y)
        #if keys[pygame.K_UP] and skateboard_body.position.y < 500:
            #skateboard_body.apply_impulse_at_local_point((0, -50))
        # Clear the screen with a white background.
        screen.fill((255, 255, 255))
        # Draw the space objects.
        space.debug_draw(draw_options)
        draw_health()
        pygame.display.flip()

        # Step the physics simulation.
        space.step(1/60.0)  # Adjust the physics step rate for better performance
        clock.tick(60)  # Adjust the frame rate for better performance
        player.angular_velocity = 0

    pygame.quit()

if __name__ == "__main__":
    main()
