import pygame
import pymunk
import pymunk.pygame_util
import sys
import time

# Camera class to handle zooming and following the player.
class Camera:
    def __init__(self, screen_width, screen_height, zoom=1.0, smooth_speed=0.1):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.zoom = zoom
        self.smooth_speed = smooth_speed
        self.x = 0
        self.y = 0

    def update(self, target_pos):
        # Center the camera on the target position.
        desired_x = target_pos.x - self.screen_width / (2 * self.zoom)
        desired_y = target_pos.y - self.screen_height / (2 * self.zoom)
        self.x += (desired_x - self.x) * self.smooth_speed
        self.y += (desired_y - self.y) * self.smooth_speed

    def get_transform(self):
        # Create a pymunk.Transform that scales and translates the world coordinates.
        return pymunk.Transform(self.zoom, 0, 0, self.zoom, -self.x * self.zoom, -self.y * self.zoom)

    def apply(self, pos):
        # Convert world coordinates to screen coordinates.
        return ((pos.x - self.x) * self.zoom, (pos.y - self.y) * self.zoom)

# Spike object used for in-level hazards.
class Spike:
    def __init__(self, space, position):
        self.space = space
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = position
        # Define a triangle shape.
        self.shape = pymunk.Poly(self.body, [(-20, 10), (20, 10), (0, -20)])
        self.shape.color = (255, 0, 0, 255)  # Red color for spikes
        self.shape.collision_type = 3  # Unique collision type for spikes
        space.add(self.body, self.shape)

# Food object. Optionally uses an image if a valid PNG path is provided.
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
            self.image = pygame.image.load(image_path).convert_alpha()
        self.body = pymunk.Body(body_type=pymunk.Body.STATIC)
        self.body.position = position
        self.radius = 15
        self.shape = pymunk.Circle(self.body, self.radius)
        if food_type == "healthy":
            self.shape.color = (0, 255, 0, 255)  # Green for healthy food
            self.shape.collision_type = 4
        elif food_type == "junk":
            self.shape.color = (255, 0, 0, 255)  # Red for junk food
            self.shape.collision_type = 5
        space.add(self.body, self.shape)

# Base Level class.
class Level:
    def __init__(self, space, level_data):
        self.space = space
        self.FRICTION = 0.8
        self.static_body = self.space.static_body
        self.platforms = []
        self.spikes = []
        self.foods = []

        # Define safe area boundaries (used for clamping platform endpoints).
        min_x, max_x = 20, 1380
        min_y, max_y = 20, 880

        # Create platforms and clamp endpoints within the safe area.
        for start, end in level_data["platforms"]:
            clamped_start = (max(min_x, min(start[0], max_x)),
                             max(min_y, min(start[1], max_y)))
            clamped_end = (max(min_x, min(end[0], max_x)),
                           max(min_y, min(end[1], max_y)))
            platform = pymunk.Segment(self.static_body, clamped_start, clamped_end, 5)
            platform.friction = self.FRICTION
            platform.collision_type = 2
            self.space.add(platform)
            self.platforms.append(platform)

        # Create in-level spikes defined in the level data.
        for pos in level_data.get("spikes", []):
            spike = Spike(self.space, pos)
            self.spikes.append(spike)

        # Create a rectangular border instead of boundary triangles.
        # Adjust the border to be slightly larger than the visible screen if needed.
        border_thickness = 10  # thickness of the border
        left = -border_thickness
        right = 1400 + border_thickness
        top = -border_thickness
        bottom = 900 + border_thickness

        border_segments = []
        # Top border.
        border_segments.append(pymunk.Segment(self.static_body, (left, top), (right, top), border_thickness))
        # Bottom border.
        border_segments.append(pymunk.Segment(self.static_body, (left, bottom), (right, bottom), border_thickness))
        # Left border.
        border_segments.append(pymunk.Segment(self.static_body, (left, top), (left, bottom), border_thickness))
        # Right border.
        border_segments.append(pymunk.Segment(self.static_body, (right, top), (right, bottom), border_thickness))
        for segment in border_segments:
            segment.friction = self.FRICTION
            segment.color = (128, 128, 128, 255)  # Grey border
            self.space.add(segment)

        # Create food items.
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

        # Determine spawn and end points based on the platforms.
        platform_x = {i: self.platforms[i]._get_a()[0] for i in range(len(self.platforms))}
        min_key = min(platform_x, key=platform_x.get)
        middle_x_start = (self.platforms[min_key]._get_a()[0] + self.platforms[min_key]._get_b()[0]) / 2
        self.spawn_point = (middle_x_start, self.platforms[min_key]._get_a()[1] - 100)
        max_key = max(platform_x, key=platform_x.get)
        middle_x_end = (self.platforms[max_key]._get_a()[0] + self.platforms[max_key]._get_b()[0]) / 2
        self.end_point = (middle_x_end, self.platforms[max_key]._get_a()[1] - 20)

# Five distinct level classes with different platform arrangements.
class Level1(Level):
    def __init__(self, space):
        level_data = {
            "platforms": [
                [(100, 850), (400, 800)],
                [(450, 750), (700, 700)],
                [(750, 650), (1000, 600)],
                [(1050, 550), (1250, 500)],
                [(1300, 450), (1380, 430)]
            ],
            "spikes": [(400, 770), (800, 570)],
            "healthy_food": [(200, 750), (500, 650)],
            "junk_food": [(700, 650), (1000, 550)]
        }
        super().__init__(space, level_data)

class Level2(Level):
    def __init__(self, space):
        level_data = {
            "platforms": [
                [(50, 800), (250, 800)],
                [(300, 750), (500, 750)],
                [(550, 700), (750, 700)],
                [(800, 650), (1000, 650)],
                [(1050, 600), (1300, 600)]
            ],
            "spikes": [(350, 770), (850, 720)],
            "healthy_food": [(150, 780), (600, 700)],
            "junk_food": [(900, 700), (1150, 600)]
        }
        super().__init__(space, level_data)

class Level3(Level):
    def __init__(self, space):
        level_data = {
            "platforms": [
                [(200, 850), (350, 850)],
                [(400, 800), (550, 800)],
                [(600, 750), (750, 750)],
                [(800, 700), (950, 700)],
                [(1000, 650), (1150, 650)]
            ],
            "spikes": [(500, 820), (900, 720)],
            "healthy_food": [(250, 800), (700, 750)],
            "junk_food": [(800, 700), (1050, 650)]
        }
        super().__init__(space, level_data)

class Level4(Level):
    def __init__(self, space):
        level_data = {
            "platforms": [
                [(100, 800), (300, 780)],
                [(350, 740), (600, 720)],
                [(650, 680), (900, 660)],
                [(950, 620), (1150, 600)],
                [(1200, 580), (1380, 560)]
            ],
            "spikes": [(400, 760), (800, 710)],
            "healthy_food": [(200, 780), (550, 700)],
            "junk_food": [(750, 680), (1100, 630)]
        }
        super().__init__(space, level_data)

class Level5(Level):
    def __init__(self, space):
        level_data = {
            "platforms": [
                [(150, 850), (350, 840)],
                [(400, 800), (600, 790)],
                [(650, 750), (850, 740)],
                [(900, 700), (1100, 690)],
                [(1150, 650), (1350, 640)]
            ],
            "spikes": [(500, 830), (900, 780), (1300, 730)],
            "healthy_food": [(250, 840), (650, 790)],
            "junk_food": [(850, 780), (1200, 730)]
        }
        super().__init__(space, level_data)

# Main Game class.
class Game:
    def __init__(self):
        pygame.init()
        self.in_game = False
        pygame.display.set_caption("AI Health Platformer")
        self.screen = pygame.display.set_mode((1400, 900))
        self.clock = pygame.time.Clock()

        self.space = pymunk.Space()
        self.space.gravity = (0, 900)

        # Player setup.
        self.player = None
        self.player_shape = None
        self.create_player()

        self.health = 10.0
        self.start_time = time.time()
        self.font = pygame.font.Font("./assets/fonts/Sigmar-Regular.ttf", 36)

        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)
        self.contact = {"on_ground": False}
        self.setup_collisions()

        # Camera to follow the player.
        self.camera = Camera(1400, 900, zoom=1.0, smooth_speed=0.1)

        # List of level classes.
        self.level_classes = [Level1, Level2, Level3, Level4, Level5]
        self.current_level = 0

        # Uncomment and set valid PNG paths if desired:
        # self.healthy_food_image = "./assets/images/healthy_food.png"
        # self.junk_food_image = "./assets/images/junk_food.png"

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
            for shape in arbiter.shapes:
                if shape.collision_type == 4:
                    space.remove(shape, shape.body)
                    break
            # Increase velocity by 20% and health by 5.
            self.player.velocity = self.player.velocity * 1.20
            self.health += 5
            return False

        def player_collect_junk(arbiter, space, data):
            for shape in arbiter.shapes:
                if shape.collision_type == 5:
                    space.remove(shape, shape.body)
                    break
            # Reduce velocity by 35% and decrease health by 5.
            self.player.velocity = self.player.velocity * 0.65
            self.health = max(self.health - 5, 0)
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
        self.level = self.level_classes[level_index](self.space)
        self.player.position = self.level.spawn_point
        self.player.velocity = (0, 0)
        self.setup_collisions()

    def teleport_to_next_level(self):
        fade_surface = pygame.Surface((1400, 900))
        fade_surface.fill((0, 0, 0))
        # Fade out effect.
        for alpha in range(0, 256, 5):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(20)
        # Load the next level.
        self.current_level = (self.current_level + 1) % len(self.level_classes)
        self.load_level(self.current_level)
        # Fade in effect.
        for alpha in range(255, -1, -5):
            fade_surface.set_alpha(alpha)
            self.screen.blit(fade_surface, (0, 0))
            pygame.display.flip()
            pygame.time.delay(20)

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
        pygame.display.flip()

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

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if play_button_rect.collidepoint(event.pos):
                    self.in_game = True

    def run(self):
        while True:
            if not self.in_game:
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

            # Update the camera.
            self.camera.update(self.player.position)
            self.draw_options.transform = self.camera.get_transform()

            # Movement controls.
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                self.player.velocity = pymunk.Vec2d(200, self.player.velocity.y)
            if keys[pygame.K_LEFT]:
                self.player.velocity = pymunk.Vec2d(-200, self.player.velocity.y)

            self.screen.fill((255, 255, 255))
            self.space.debug_draw(self.draw_options)
            # Draw food images with camera transformation.
            for food in self.level.foods:
                if food.use_png and food.image:
                    pos_screen = self.camera.apply(food.body.position)
                    rect = food.image.get_rect(center=(int(pos_screen[0]), int(pos_screen[1])))
                    self.screen.blit(food.image, rect)
            self.draw_health()
            self.draw_time()
            pygame.display.flip()

            self.space.step(1/60.0)

            # Check if the player reached the end and trigger teleportation.
            player_pos = self.player.position
            end_point = self.level.end_point
            distance = ((player_pos.x - end_point[0])**2 + (player_pos.y - end_point[1])**2) ** 0.5
            if distance < 50:
                self.teleport_to_next_level()

            self.clock.tick(60)
            self.player.angular_velocity = 0

        pygame.quit()

def main():
    Game().run()

if __name__ == "__main__":
    main()