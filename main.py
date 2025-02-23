import pygame
import pymunk
import pymunk.pygame_util
import sys

# Helper function to draw a button with rounded corners
def draw_button(surface, text, rect, font, button_color, text_color, border_color, border_width=2, border_radius=10):
    pygame.draw.rect(surface, button_color, rect, border_radius=border_radius)
    pygame.draw.rect(surface, border_color, rect, width=border_width, border_radius=border_radius)
    text_surf = font.render(text, True, text_color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)

# Main Menu with Play and Credits buttons
class MainMenu:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.bg_color = (30, 30, 30)
        self.button_color = (200, 200, 200)
        self.text_color = (0, 0, 0)
        self.border_color = (50, 50, 50)
        # Define button rects
        self.play_rect = pygame.Rect(600, 300, 200, 60)
        self.credits_rect = pygame.Rect(600, 400, 200, 60)
    
    def run(self):
        running = True
        selected_option = None
        while running:
            self.screen.fill(self.bg_color)
            title_text = self.font.render("Main Menu", True, (255, 255, 255))
            self.screen.blit(title_text, (self.screen.get_width()//2 - title_text.get_width()//2, 150))
            
            draw_button(self.screen, "Play", self.play_rect, self.font, self.button_color, self.text_color, self.border_color)
            draw_button(self.screen, "Credits", self.credits_rect, self.font, self.button_color, self.text_color, self.border_color)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.play_rect.collidepoint(event.pos):
                        selected_option = "play"
                        running = False
                    elif self.credits_rect.collidepoint(event.pos):
                        selected_option = "credits"
                        running = False
        return selected_option

# Level Selection Menu with 5 level buttons and a Back button
class LevelSelectMenu:
    def __init__(self, screen, font, levels):
        self.screen = screen
        self.font = font
        self.levels = levels
        self.bg_color = (30, 30, 30)
        self.button_color = (200, 200, 200)
        self.text_color = (0, 0, 0)
        self.border_color = (50, 50, 50)
        # Create button rects for 5 levels and one back button.
        self.level_buttons = []
        for i in range(len(levels)):
            # Position each level button vertically spaced
            rect = pygame.Rect(600, 250 + i * 70, 200, 60)
            self.level_buttons.append((rect, i))
        self.back_rect = pygame.Rect(50, 50, 150, 50)
    
    def run(self):
        running = True
        selected_level = None
        while running:
            self.screen.fill(self.bg_color)
            title_text = self.font.render("Select Level", True, (255, 255, 255))
            self.screen.blit(title_text, (self.screen.get_width()//2 - title_text.get_width()//2, 150))
            
            for rect, level_index in self.level_buttons:
                draw_button(self.screen, f"Level {level_index+1}", rect, self.font, self.button_color, self.text_color, self.border_color)
            draw_button(self.screen, "Back", self.back_rect, self.font, self.button_color, self.text_color, self.border_color)
            
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = event.pos
                    for rect, level_index in self.level_buttons:
                        if rect.collidepoint(mouse_pos):
                            selected_level = level_index
                            running = False
                    if self.back_rect.collidepoint(mouse_pos):
                        # Return None to indicate back to main menu
                        running = False
            # Limit the loop speed
            pygame.time.Clock().tick(60)
        return selected_level

# Credits screen: a blank screen with a Back button.
class CreditsScreen:
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font
        self.bg_color = (30, 30, 30)
        self.text_color = (255, 255, 255)
        self.button_color = (200, 200, 200)
        self.border_color = (50, 50, 50)
        self.back_rect = pygame.Rect(50, 50, 150, 50)
    
    def run(self):
        running = True
        while running:
            self.screen.fill(self.bg_color)
            # For now, credits screen is blank; you could add credits text if desired.
            credits_text = self.font.render("Credits", True, self.text_color)
            self.screen.blit(credits_text, (self.screen.get_width()//2 - credits_text.get_width()//2, 200))
            
            draw_button(self.screen, "Back", self.back_rect, self.font, self.button_color, self.text_color, self.border_color)
            pygame.display.flip()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.back_rect.collidepoint(event.pos):
                        running = False
            pygame.time.Clock().tick(60)

# Game and Level classes from your platformer code
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

        # Pymunk debug draw options
        self.draw_options = pymunk.pygame_util.DrawOptions(self.screen)

        # Collision tracking
        self.contact = {"on_ground": False}
        self.setup_collisions()

        # Level handling with 5 levels
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
        # Remove all shapes and bodies from the space and re-create the player
        for shape in self.space.shapes[:]:
            self.space.remove(shape)
        for body in self.space.bodies[:]:
            self.space.remove(body)
        self.create_player()
        self.level = Level(self.space, self.levels[level_index])
        self.player.position = self.level.spawn_point
        self.player.velocity = (0, 0)

    def draw_health(self):
        health_text = self.font.render(f"Health: {self.health:.0f}%", True, (0, 0, 0))
        self.screen.blit(health_text, (10, 10))

    def run(self):
        # Main game loop (pressing ESC quits the game)
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()
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
    game = Game()
    while True:
        # Show the main menu
        main_menu = MainMenu(game.screen, game.font)
        option = main_menu.run()
        
        if option == "play":
            # Show level select
            level_menu = LevelSelectMenu(game.screen, game.font, game.levels)
            selected_level = level_menu.run()
            if selected_level is not None:
                game.current_level = selected_level
                game.load_level(selected_level)
                game.run()  # Start the game loop
        elif option == "credits":
            # Show credits screen
            credits = CreditsScreen(game.screen, game.font)
            credits.run()

if __name__ == "__main__":
    main()
