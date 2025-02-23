import pygame
import pymunk
import pymunk.pygame_util
import sys
import time

class Spike:
    def __init__(self, space, position):
        self.space = space
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = position
        self.shape = pymunk.Poly(self.body, [(-20, 10), (20, 10), (0, -20)])
        self.shape.color = (255, 0, 0, 255)  # Red color
        self.shape.collision_type = 3  # Unique collision type for spikes
        space.add(self.body, self.shape)

class Food:
    def __init__(self, space, position, food_type, use_png=False, image_path=None):
        """
        food_type: "healthy" or "junk"
        use_png: Boolean flag to determine if an image should override the default sprite.
        image_path: Path to the PNG image.
        """
        self.space = space
        self.food_type = food_type
        self.use_png = use_png and image_path and image_path.lower().endswith('.png')
        self.image = None
        if self.use_png:
            # Load the PNG image with transparency.
            self.image = pygame.image.load(image_path).convert_alpha()
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = position
        self.radius = 15
        self.shape = pymunk.Circle(self.body, self.radius)
        # Use green for healthy food and red for junk food (if no image override).
        if food_type == "healthy":
            self.shape.color = (0, 255, 0, 255)  # green
            self.shape.collision_type = 4
        elif food_type == "junk":
            self.shape.color = (255, 0, 0, 255)  # red
            self.shape.collision_type = 5
        space.add(self.body, self.shape)

class Level:
    def __init__(self, space, level_data):
        self.space = space
        self.FRICTION = 0.8
        self.static_body = self.space.static_body
        self.platforms = []
        self.spikes = []
        self.foods = []
        # Create platforms
        for start, end in level_data["platforms"]:
            platform = pymunk.Segment(self.static_body, start, end, 5)
            platform.friction = self.FRICTION
            platform.collision_type = 2
            self.space.add(platform)
            self.platforms.append(platform)

        # Create spikes
        for pos in level_data.get("spikes", []):
            spike = Spike(self.space, pos)
            self.spikes.append(spike)

        for i in range(1400 // 20):
            spike = Spike(self.space, (i * 20, 900))
            self.spikes.append(spike)

        for i in range(900 // 20):
            spike = Spike(self.space, (0, i * 20))
            self.spikes.append(spike)

        for i in range(900 // 20):
            spike = Spike(self.space, (1400, i * 20))
            self.spikes.append(spike)

        # Create food items if defined in level_data.
        # Optionally override the sprite if an image is provided.
        healthy_img = level_data.get("healthy_food_image", None)
        if "healthy_food" in level_data:
            for pos in level_data["healthy_food"]:
                use_image = healthy_img is not None and healthy_img.lower().endswith('.png')
                food = Food(self.space, pos, "healthy", use_png=use_image, image_path=healthy_img)
                self.foods.append(food)
        junk_img = level_data.get("junk_food_image", None)
        if "junk_food" in level_data:
            for pos in level_data["junk_food"]:
                use_image = junk_img is not None and junk_img.lower().endswith('.png')
                food = Food(self.space, pos, "junk", use_png=use_image, image_path=junk_img)
                self.foods.append(food)

        platform_x = {i: self.platforms[i]._get_a()[0] for i in range(len(self.platforms))}

        # Spawn and End Points
        min_key = min(platform_x, key=platform_x.get)
        middle_x_start = (self.platforms[min_key]._get_a()[0] + self.platforms[min_key]._get_b()[0]) / 2
        self.spawn_point = (middle_x_start, self.platforms[min_key]._get_a()[1] - 100)

        max_key = max(platform_x, key=platform_x.get)
        middle_x_end = (self.platforms[max_key]._get_a()[0] + self.platforms[max_key]._get_b()[0]) / 2
        self.end_point = (middle_x_end, self.platforms[max_key]._get_a()[1] - 20)

class Game:
    def __init__(self):
        pygame.init()
        self.in_game = False
        pygame.display.set_caption("AI Health Platformer")
        self.screen = pygame.display.set_mode((1400, 900))
        self.clock = pygame.time.Clock()

        self.space = pymunk.Space()
        self.space.gravity = (0, 900)

        # Player setup
        self.player = None
        self.player_shape = None
        self.create_player()

        self.health = 10.0
        self.start_time = time.time()
        self.font = pygame.font.Font("./assets/fonts/Sigmar-Regular.ttf", 36)

        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.contact = {"on_ground": False}
        self.setup_collisions()

        self.current_level = 0
        # In this level data, you can optionally provide an image path for healthy or junk food.
        # If the image path is provided and ends with '.png', the image will override the default sprite.
        self.levels = [
            {
                "platforms": [
                    [(50, 800), (300, 800)],
                    [(350, 700), (600, 700)],
                    [(650, 600), (900, 600)],
                    [(950, 500), (1200, 500)],
                    [(1250, 400), (1400, 400)],
                ],
                "spikes": [(400, 770), (800, 570)],
                "healthy_food": [(200, 750), (500, 650)],
                "junk_food": [(700, 650), (1000, 550)],
                # Uncomment or change the paths below to use PNG images for food items.
                # "healthy_food_image": "./assets/images/healthy_food.png",
                # "junk_food_image": "./assets/images/junk_food.png"
            },
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

        def player_hit_spike(arbiter, space, data):
            self.health = 0
            return False

        def player_collect_healthy(arbiter, space, data):
            # Remove the healthy food item upon collision.
            for shape in arbiter.shapes:
                if shape.collision_type == 4:
                    space.remove(shape, shape.body)
                    break
            return False

        def player_collect_junk(arbiter, space, data):
            for shape in arbiter.shapes:
                if shape.collision_type == 5:
                    space.remove(shape, shape.body)
                    break
            return False

        handler = self.space.add_collision_handler(1, 2)
        handler.begin = begin_player_ground
        handler.separate = separate_player_ground

        spike_handler = self.space.add_collision_handler(1, 3)
        spike_handler.begin = player_hit_spike

        healthy_handler = self.space.add_collision_handler(1, 4)
        healthy_handler.begin = player_collect_healthy

        junk_handler = self.space.add_collision_handler(1, 5)
        junk_handler.begin = player_collect_junk

    def load_level(self, level_index):
        self.space.remove(*self.space.shapes)
        self.space.remove(*self.space.bodies)
        self.create_player()
        self.level = Level(self.space, self.levels[level_index])
        self.player.position = self.level.spawn_point
        self.player.velocity = (0, 0)
        self.setup_collisions()

    def get_time(self):
        return round(time.time() - self.start_time, 1)

    def draw_health(self):
        health_text = self.font.render(f"Health: {self.health:.0f}%", True, (0, 0, 0))
        self.screen.blit(health_text, (25, 10))

    def draw_time(self):
        time_text = self.font.render(f"Time: {self.get_time()} seconds", True, (0, 0, 0))
        self.screen.blit(time_text, (1025, 10))

    def draw_death_screen(self):
        self.screen.fill((0, 0, 0))
        text = self.font.render("Game Over! Press R to Restart", True, (255, 255, 255))
        self.screen.blit(text, (450, 400))
        pygame.display.flip()  # Update the display to show the death screen

    def draw_end_screen(self):
        self.screen.fill((0, 0, 0))
        text = self.font.render(
            f"You Won! Great Job!\nYour Health was {self.health} and your time was {self.get_time()}",
            True, (255, 255, 255))
        self.screen.blit(text, (450, 400))

    def draw_menu(self):
        self.screen.fill((255, 255, 255))
        title_font = pygame.font.Font("./assets/fonts/Sigmar-Regular.ttf", 72)
        button_font = pygame.font.Font("./assets/fonts/Sigmar-Regular.ttf", 48)

        title_text = title_font.render("Eating Adventure", True, (0, 0, 0))
        play_button_text = button_font.render("Play", True, (255, 255, 255))

        play_button_rect = pygame.Rect(600, 400, 200, 100)
        pygame.draw.rect(self.screen, (0, 0, 0), play_button_rect)
        self.screen.blit(title_text, (400, 200))
        self.screen.blit(play_button_text, (play_button_rect.x + 50, play_button_rect.y + 25))

        pygame.display.flip()
        # Handle play button click
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    self.in_game = True  # Start the game when "Play" is clicked

    def run(self):
        while True:
            if not self.in_game:  # Show menu if not in game
                self.draw_menu()
                self.load_level(self.current_level)
                continue
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if self.health == 0 and event.key == pygame.K_r:
                        self.health = 10
                        self.load_level(self.current_level)
                        self.start_time = time.time()
                    elif event.key == pygame.K_UP and self.contact["on_ground"]:
                        self.player.apply_impulse_at_local_point((0, -500))

            if self.health == 0:
                self.draw_death_screen()
                continue

            # Add movement controls for left and right
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.player.velocity = pymunk.Vec2d(200, self.player.velocity.y)
            if keys[pygame.K_LEFT]:
                self.player.velocity = pymunk.Vec2d(-200, self.player.velocity.y)

            self.screen.fill((255, 255, 255))
            self.space.debug_draw(self.draw_options)
            # Draw food images over the debug drawing if an image override is active.
            for food in self.level.foods:
                if food.use_png and food.image:
                    pos = food.body.position
                    rect = food.image.get_rect(center=(int(pos.x), int(pos.y)))
                    self.screen.blit(food.image, rect)
            self.draw_health()
            self.draw_time()
            pygame.display.flip()

            self.space.step(1/60.0)

            # Check if player reached the end
            player_pos = self.player.position
            end_point = self.level.end_point
            distance = ((player_pos.x - end_point[0])**2 + (player_pos.y - end_point[1])**2) ** 0.5
            if distance < 50:
                self.current_level = (self.current_level + 1) % len(self.levels)
                self.load_level(self.current_level)

            self.clock.tick(60)
            self.player.angular_velocity = 0

        pygame.quit()

def main():
    Game().run()

if __name__ == "__main__":
    main()
