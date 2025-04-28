import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
OBSTACLE_COLOR = (139, 69, 19)  # Brown for obstacles
PLATFORM_COLORS = [(120, 60, 20), (110, 55, 15), (130, 65, 25), (100, 50, 10)]  # Variety of browns
GROUND_Y = HEIGHT - 50


class Player:
    def __init__(self, x, y, width, height):
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.velocity = 5
        self.jump_force = -15
        self.gravity = 0.75
        self.max_fall_speed = 12
        self.falling_speed = 0
        self.is_jumping = False
        self.is_on_ground = False
        self.can_jump = True
        self.coyote_time = 5
        self.coyote_counter = 0
        self.jump_buffer_time = 7
        self.jump_buffer_counter = 0

        # Load player image
        try:
            self.image = pygame.image.load("../assets/player/character.png")
            self.image = pygame.transform.scale(self.image, (width, height))
        except pygame.error:
            self.image = None

    def move(self, obstacles):
        # Get pressed keys
        keys = pygame.key.get_pressed()

        # Horizontal movement
        x_movement = 0
        if keys[pygame.K_a]:  # Move left
            x_movement -= self.velocity
        if keys[pygame.K_d]:  # Move right
            x_movement += self.velocity

        self.rect.x += x_movement

        # Keep player within screen bounds
        self.rect.x = max(0, min(self.rect.x, WIDTH - self.width))

        # Jump buffer - registers jump inputs even before landing
        if keys[pygame.K_w] or keys[pygame.K_SPACE]:
            self.jump_buffer_counter = self.jump_buffer_time
        else:
            self.jump_buffer_counter = max(0, self.jump_buffer_counter - 1)

        # Handle jumping with better physics
        if self.is_on_ground:
            self.coyote_counter = self.coyote_time
            self.can_jump = True
        else:
            self.coyote_counter = max(0, self.coyote_counter - 1)

        # Apply the jump if conditions are met
        if (self.coyote_counter > 0 or self.is_on_ground) and self.jump_buffer_counter > 0 and self.can_jump:
            self.falling_speed = self.jump_force  # Initial velocity upward
            self.is_jumping = True
            self.is_on_ground = False
            self.can_jump = False  # Prevent double jumping
            self.jump_buffer_counter = 0
            self.coyote_counter = 0

        # Variable jump height - hold jump key to jump higher
        if self.is_jumping and self.falling_speed < 0:
            if not (keys[pygame.K_w] or keys[pygame.K_SPACE]):
                self.falling_speed = max(self.falling_speed,
                                         self.jump_force / 2)  # Cut the jump short if button released

        # Apply gravity
        self.falling_speed += self.gravity
        self.falling_speed = min(self.falling_speed, self.max_fall_speed)

        # Apply vertical movement
        self.rect.y += self.falling_speed

        # Reset on_ground status before collision checks
        was_on_ground = self.is_on_ground
        self.is_on_ground = False

        # Check for collisions with obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                # Collision from above (landing)
                if self.falling_speed > 0 and self.rect.bottom - self.falling_speed <= obstacle.rect.top + 5:
                    self.rect.bottom = obstacle.rect.top
                    self.is_on_ground = True
                    self.is_jumping = False
                    self.falling_speed = 0
                    self.can_jump = True

                # Collision from below (hitting ceiling)
                elif self.falling_speed < 0 and self.rect.top - self.falling_speed >= obstacle.rect.bottom - 5:
                    self.rect.top = obstacle.rect.bottom
                    self.falling_speed = 0  # Stop upward momentum

                # Collision from left
                elif x_movement > 0 and self.rect.right - x_movement <= obstacle.rect.left + 5:
                    self.rect.right = obstacle.rect.left

                # Collision from right
                elif x_movement < 0 and self.rect.left - x_movement >= obstacle.rect.right - 5:
                    self.rect.left = obstacle.rect.right

        # Fast fall with S key
        if (keys[pygame.K_s]) and not self.is_on_ground:
            self.falling_speed = max(self.falling_speed, self.max_fall_speed / 1.5)

    def shoot(self, mouse_pos):
        # Calculate angle towards mouse position
        bullet_angle = math.atan2(mouse_pos[1] - self.rect.centery, mouse_pos[0] - self.rect.centerx)
        bullet_velocity_x = 7 * math.cos(bullet_angle)  # Using 7 as bullet velocity
        bullet_velocity_y = 7 * math.sin(bullet_angle)

        return Bullet(
            self.rect.centerx,
            self.rect.centery,
            bullet_velocity_x,
            bullet_velocity_y,
            bullet_angle
        )

    def draw(self, screen):
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            # Fallback if image can't be loaded
            pygame.draw.rect(screen, BLUE, self.rect)

    def get_debug_info(self):
        return [
            f"Player pos: ({self.rect.x}, {self.rect.y})",
            f"Falling speed: {self.falling_speed:.1f}",
            f"On ground: {self.is_on_ground}",
            f"Can jump: {self.can_jump}",
            f"Coyote time: {self.coyote_counter}",
            f"Jump buffer: {self.jump_buffer_counter}"
        ]


class Obstacle:
    def __init__(self, x, y, width, height, is_ground=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.is_ground = is_ground
        self.color_index = random.randint(0, len(PLATFORM_COLORS) - 1)

    def draw(self, screen):
        if self.is_ground:
            # Draw ground with a gradient
            pygame.draw.rect(screen, GREEN, self.rect)
            pygame.draw.rect(screen, (0, 180, 0), (0, GROUND_Y, WIDTH, 10))
        else:
            # Choose a slightly different brown for each platform for variety
            color = PLATFORM_COLORS[self.color_index]
            pygame.draw.rect(screen, color, self.rect)
            # Add a highlight on top
            pygame.draw.line(screen, (color[0] + 20, color[1] + 20, color[2] + 20),
                             (self.rect.left, self.rect.top),
                             (self.rect.right, self.rect.top), 2)


class ObstacleManager:
    def __init__(self):
        self.obstacles = []
        self.platforms = []

    def generate_level(self, player):
        self.obstacles = []
        self.platforms = []

        # Add ground as an obstacle
        ground = Obstacle(0, GROUND_Y, WIDTH, 50, is_ground=True)
        self.obstacles.append(ground)

        # Create a more realistic level layout with different types of platforms
        # 1. Create a few main horizontal platforms at different heights
        main_platform_heights = [GROUND_Y - 120, GROUND_Y - 220, GROUND_Y - 320]
        for height in main_platform_heights:
            # Create 2-3 platforms at this height
            for _ in range(random.randint(2, 3)):
                width = random.randint(150, 250)
                x_pos = random.randint(0, WIDTH - width)

                # Ensure platforms at the same height don't overlap
                valid_position = True
                for platform in self.platforms:
                    if abs(platform.rect.y - height) < 10:  # Same height level
                        if not (x_pos + width < platform.rect.x or x_pos > platform.rect.x + platform.rect.width):
                            valid_position = False
                            break

                if valid_position:
                    platform = Obstacle(x_pos, height, width, random.randint(20, 30))
                    self.platforms.append(platform)
                    self.obstacles.append(platform)

        # 2. Add some smaller stepping stones/platforms between main platforms
        for _ in range(random.randint(5, 8)):
            width = random.randint(50, 100)
            height = random.randint(15, 25)
            x_pos = random.randint(0, WIDTH - width)
            y_pos = random.randint(GROUND_Y - 400, GROUND_Y - 50)

            # Check if this platform overlaps with existing ones
            valid_position = True
            for platform in self.platforms:
                if (abs(platform.rect.y - y_pos) < height + 10 and
                        not (
                                x_pos + width < platform.rect.x - 10 or x_pos > platform.rect.x + platform.rect.width + 10)):
                    valid_position = False
                    break

            if valid_position:
                platform = Obstacle(x_pos, y_pos, width, height)
                self.platforms.append(platform)
                self.obstacles.append(platform)

        # 3. Add some vertical obstacles/walls
        for _ in range(random.randint(2, 4)):
            width = random.randint(20, 30)
            height = random.randint(80, 150)
            x_pos = random.randint(50, WIDTH - width - 50)
            y_pos = random.randint(GROUND_Y - height, GROUND_Y - 20)

            # Check if this wall doesn't block important areas
            valid_position = True
            for platform in self.platforms:
                if (abs(platform.rect.x - x_pos) < width + 10 and
                        not (
                                y_pos + height < platform.rect.y - 10 or y_pos > platform.rect.y + platform.rect.height + 10)):
                    valid_position = False
                    break

            if valid_position:
                wall = Obstacle(x_pos, y_pos, width, height)
                self.platforms.append(wall)
                self.obstacles.append(wall)

        # Add player spawn platform
        spawn_platform = Obstacle(WIDTH // 2 - 75, GROUND_Y - 70, 150, 20)
        self.platforms.append(spawn_platform)
        self.obstacles.append(spawn_platform)

        # Ensure the player has a safe starting position
        player.rect.x = WIDTH // 2 - player.width // 2
        player.rect.y = spawn_platform.rect.y - player.height - 5

    def draw(self, screen):
        for obstacle in self.obstacles:
            obstacle.draw(screen)


class Enemy:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.velocity = 2
        self.health = 3
        self.max_health = 3
        self.direction = -1  # -1 for left, 1 for right
        self.jump_timer = 0

    def move(self, obstacles):
        # Basic enemy AI - move left and right, and occasionally jump
        self.rect.x += self.velocity * self.direction

        # Change direction if hitting screen edge
        if self.rect.x <= 0:
            self.direction = 1
        elif self.rect.x + self.width >= WIDTH:
            self.direction = -1

        # Simple gravity for enemy
        enemy_falling_speed = 5  # Constant falling speed
        self.rect.y += enemy_falling_speed

        # Check for collisions with obstacles
        enemy_on_ground = False
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle.rect):
                # Collision from above (landing)
                if self.rect.bottom - enemy_falling_speed <= obstacle.rect.top + 5:
                    self.rect.bottom = obstacle.rect.top
                    enemy_on_ground = True
                # Hit wall - change direction
                elif (self.direction > 0 and self.rect.right >= obstacle.rect.left and
                      self.rect.right - self.velocity <= obstacle.rect.left):
                    self.direction = -1
                elif (self.direction < 0 and self.rect.left <= obstacle.rect.right and
                      self.rect.left + self.velocity >= obstacle.rect.right):
                    self.direction = 1

        # Reset enemy if it falls off the screen
        if self.rect.y > HEIGHT:
            self.rect.x = random.randint(50, WIDTH - 50 - self.width)
            self.rect.y = 100

        # Random jumping if on ground
        if enemy_on_ground:
            self.jump_timer -= 1
            if self.jump_timer <= 0:
                self.rect.y -= 10  # Small jump
                self.jump_timer = random.randint(60, 120)  # Random timer for next jump

    def take_damage(self):
        self.health -= 1
        if self.health <= 0:
            self.respawn()
        return self.health <= 0

    def respawn(self):
        self.health = self.max_health
        self.rect.x = random.randint(50, WIDTH - 50 - self.width)
        self.rect.y = random.randint(50, 150)

    def draw(self, screen):
        # Draw the enemy
        pygame.draw.rect(screen, RED, self.rect)

        # Health bar for enemy
        health_bar_width = 40
        health_bar_height = 5
        health_percentage = self.health / self.max_health
        pygame.draw.rect(screen, (100, 100, 100),
                         (self.rect.x + self.width // 2 - health_bar_width // 2,
                          self.rect.y - 10, health_bar_width, health_bar_height))
        pygame.draw.rect(screen, (255, 0, 0),
                         (self.rect.x + self.width // 2 - health_bar_width // 2,
                          self.rect.y - 10, health_bar_width * health_percentage, health_bar_height))

    def get_debug_info(self):
        return [f"Enemy pos: ({self.rect.x}, {self.rect.y})"]


class Bullet:
    def __init__(self, x, y, velocity_x, velocity_y, angle):
        self.width = 10
        self.height = 5
        self.rect = pygame.Rect(x - self.width // 2, y - self.height // 2, self.width, self.height)
        self.velocity = (velocity_x, velocity_y)
        self.angle = math.degrees(angle)

    def move(self, obstacles):
        # Move the bullet according to its velocity
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]

        # Check if the bullet is still on screen
        if -50 < self.rect.x < WIDTH + 50 and -50 < self.rect.y < HEIGHT + 50:
            # Check for collisions with obstacles
            for obstacle in obstacles:
                if self.rect.colliderect(obstacle.rect):
                    return False, (self.rect.centerx, self.rect.centery)
            return True, None
        else:
            return False, None

    def draw(self, screen):
        bullet_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(bullet_surface, RED, (0, 0, self.width, self.height))
        rotated_surface = pygame.transform.rotate(bullet_surface, -self.angle)
        screen.blit(rotated_surface, (self.rect.x - rotated_surface.get_width() // 2 + self.width // 2,
                                      self.rect.y - rotated_surface.get_height() // 2 + self.height // 2))


class ImpactEffect:
    def __init__(self, x, y, color=(255, 200, 100), life=10, max_radius=8):
        self.pos = (x, y)
        self.radius = 5
        self.max_radius = max_radius
        self.color = color
        self.life = life
        self.max_life = life

    def update(self):
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        radius = self.radius * (1 - self.life / self.max_life)  # Start small, grow larger
        alpha = 255 * self.life / self.max_life  # Fade out
        effect_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(effect_surface, (*self.color, alpha), (radius, radius), radius)
        screen.blit(effect_surface, (self.pos[0] - radius, self.pos[1] - radius))


class Game:
    def __init__(self):
        # Create the screen
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("2D Platformer Action Game")

        # Clock for controlling FPS
        self.clock = pygame.time.Clock()

        # Game objects
        self.player = Player(WIDTH // 2, HEIGHT - 100, 50, 50)
        self.enemy = Enemy(WIDTH - 100, HEIGHT - 100, 50, 50)
        self.obstacle_manager = ObstacleManager()

        # Game variables
        self.bullets = []
        self.impact_effects = []
        self.debug_mode = False
        self.running = True

        # Generate initial level
        self.obstacle_manager.generate_level(self.player)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Mouse click to shoot bullet
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    self.bullets.append(self.player.shoot(mouse_pos))

            # Toggle debug mode with F3
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                # Reset game with R key
                if event.key == pygame.K_r:
                    self.reset_game()

    def reset_game(self):
        self.obstacle_manager.generate_level(self.player)
        self.player.falling_speed = 0
        self.player.is_jumping = False
        self.player.is_on_ground = False
        self.bullets.clear()
        self.impact_effects.clear()
        self.enemy.respawn()

    def update(self):
        # Move the player
        self.player.move(self.obstacle_manager.obstacles)

        # Move the enemy
        self.enemy.move(self.obstacle_manager.obstacles)

        # Update bullets
        bullets_to_keep = []
        for bullet in self.bullets:
            keep_bullet, impact_pos = bullet.move(self.obstacle_manager.obstacles)

            # Check bullet-enemy collision
            if keep_bullet and bullet.rect.colliderect(self.enemy.rect):
                keep_bullet = False
                impact_pos = (bullet.rect.centerx, bullet.rect.centery)
                self.enemy.take_damage()
                # Add enemy hit effect (red)
                self.impact_effects.append(ImpactEffect(
                    impact_pos[0], impact_pos[1],
                    color=(255, 100, 100), life=15, max_radius=12
                ))

            if keep_bullet:
                bullets_to_keep.append(bullet)
            elif impact_pos:
                # Add impact effect for obstacle hit (orange)
                self.impact_effects.append(ImpactEffect(
                    impact_pos[0], impact_pos[1]
                ))

        self.bullets = bullets_to_keep

        # Update impact effects
        self.impact_effects = [effect for effect in self.impact_effects if effect.update()]

    def draw(self):
        # Draw background
        self.screen.fill((200, 230, 255))  # Light blue sky background

        # Draw obstacles
        self.obstacle_manager.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw impact effects
        for effect in self.impact_effects:
            effect.draw(self.screen)

        # Draw enemy
        self.enemy.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Update the display
        pygame.display.update()

    def draw_hud(self):
        font = pygame.font.SysFont(None, 30)

        # Display enemy health
        health_text = font.render(f"Enemy Health: {self.enemy.health} / {self.enemy.max_health}", True, BLACK)
        self.screen.blit(health_text, (10, 10))

        # Display controls
        controls_text = [
            "Controls:",
            "A/D - Move",
            "W/SPACE - Jump",
            "S - Fast Fall",
            "Mouse - Aim",
            "Left Click - Shoot",
            "R - Reset Level",
            "F3 - Debug Mode"
        ]

        for i, text in enumerate(controls_text):
            control_text = font.render(text, True, BLACK)
            self.screen.blit(control_text, (WIDTH - 150, 10 + i * 25))

        # Debug info
        if self.debug_mode:
            debug_info = self.player.get_debug_info() + [
                f"Bullet count: {len(self.bullets)}"] + self.enemy.get_debug_info()

            for i, info in enumerate(debug_info):
                debug_text = font.render(info, True, BLACK)
                self.screen.blit(debug_text, (10, 50 + i * 25))

    def run(self):
        while self.running:
            self.clock.tick(60)  # FPS
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()


# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()