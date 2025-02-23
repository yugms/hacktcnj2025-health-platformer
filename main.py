import pygame.base
import pygame
import pymunk
import pymunk.pygame_util

def main():
    # Initialize Pygame and create a window.
    pygame.init()
    keys = pygame.key.get_pressed()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Basic Skateboard Park Simulation")
    clock = pygame.time.Clock()

    # Set up the physics simulation space.
    space = pymunk.Space()
    space.gravity = (0, 900)  # Gravity pulling downward.

    # Create static bodies for the park features.
    static_body = space.static_body

    # Ground segment.
    ground = pymunk.Segment(static_body, (0, 500), (900, 500), 5)
    ground.friction = 0.8
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
    skateboard_body = pymunk.Body(mass, moment)
    skateboard_body.position = (100, 450)
    skateboard_shape = pymunk.Poly.create_box(skateboard_body, (width, height))
    skateboard_shape.friction = 0.8
    space.add(skateboard_body, skateboard_shape)
    
    mass = 0.1
    width, height = 100, 10
    moment = pymunk.moment_for_box(mass, (width, height))
    platform_body = pymunk.Body(body_type=pymunk.Body.STATIC)
    platform_body.position = (600, 400)
    platform_shape = pymunk.Poly.create_box(platform_body, (width, height))
    platform_shape.friction = 0.8
    space.add(platform_body, platform_shape)

    # Set up draw options to visualize the physics objects.
    draw_options = pymunk.pygame_util.DrawOptions(screen)

    running = True
    onGround = True
    while running:
        platform_body.velocity = pymunk.Vec2d(0, 0)
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
            if event.key == pygame.K_UP and ((skateboard_body.position.y < 470) and (skateboard_body.position.y) > 460 or ((skateboard_body.position.y > platform_body.position.y + 20 and (skateboard_body.position.y < platform_body.position.y - 20)))):
                    # A jump impulse.
                skateboard_body.apply_impulse_at_local_point((0, -500))
                onGround = False

        keys = pygame.key.get_pressed()
        if keys[pygame.K_RIGHT]:
            skateboard_body.velocity = pymunk.Vec2d(200, skateboard_body.velocity.y)
        if keys[pygame.K_LEFT]:
            skateboard_body.velocity = pymunk.Vec2d(-200, skateboard_body.velocity.y)
        #if keys[pygame.K_UP] and skateboard_body.position.y < 500:
            #skateboard_body.apply_impulse_at_local_point((0, -50))
        # Clear the screen with a white background.
        screen.fill((255, 255, 255))
        # Draw the space objects.
        space.debug_draw(draw_options)
        pygame.display.flip()

        # Step the physics simulation.
        space.step(1/60.0)  # Adjust the physics step rate for better performance
        clock.tick(60)  # Adjust the frame rate for better performance

    pygame.quit()

if __name__ == "__main__":
    main()
