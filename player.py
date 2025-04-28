import pygame
import math

from bullet import Bullet


class Player:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.color = (0, 0, 255)  # Blue color as fallback

        # Load the character image and handle potential errors
        try:
            self.image = pygame.image.load("assets/player/character.png")
            self.image = pygame.transform.scale(self.image, (width, height))
            self.use_image = True
        except (pygame.error, FileNotFoundError):
            print("Character image not found, using rectangle instead")
            self.use_image = False

        # Movement variables
        self.velocity_x = 0
        self.falling_speed = 0
        self.move_speed = 5
        self.jump_strength = 15
        self.gravity = 0.8
        self.is_jumping = False
        self.is_on_ground = False
        self.ground_y = y

        # Shooting variables
        self.bullet_speed = 15
        self.bullet_size = 5

        # Health system
        self.max_health = 100
        self.health = self.max_health
        self.invulnerable = False
        self.invulnerable_timer = 0
        self.invulnerable_duration = 60  # Frames of invulnerability after taking damage

        # Respawn variables
        self.respawn_point = (x, y)  # Default respawn at initial position

    def move(self, obstacles):
        # Update invulnerability timer
        if self.invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.invulnerable = False

        keys = pygame.key.get_pressed()

        # Horizontal movement
        self.velocity_x = 0
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.velocity_x = -self.move_speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.velocity_x = self.move_speed

        # Apply horizontal movement
        self.rect.x += self.velocity_x

        # Check horizontal collisions
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if self.velocity_x > 0:  # Moving right
                    self.rect.right = obstacle.left
                elif self.velocity_x < 0:  # Moving left
                    self.rect.left = obstacle.right

        # Keep player within screen bounds
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > 1000:  # Updated to 1000 for new WIDTH
            self.rect.right = 1000

        # Jumping and falling
        if (keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.is_on_ground:
            self.falling_speed = -self.jump_strength
            self.is_jumping = True
            self.is_on_ground = False

        # Fast fall
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            if not self.is_on_ground:
                self.falling_speed += 1

        # Apply gravity
        self.falling_speed += self.gravity
        self.rect.y += self.falling_speed

        # Reset on-ground status
        self.is_on_ground = False

        # Check vertical collisions
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if self.falling_speed > 0:  # Falling down
                    self.rect.bottom = obstacle.top
                    self.is_on_ground = True
                    self.falling_speed = 0
                elif self.falling_speed < 0:  # Jumping up
                    self.rect.top = obstacle.bottom
                    self.falling_speed = 0

        standing_on = None

        # Check vertical collisions
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if self.falling_speed > 0:  # Falling down
                    self.rect.bottom = obstacle.top
                    self.is_on_ground = True
                    self.falling_speed = 0

                    # Remember which obstacle we're standing on
                    standing_on = obstacle

                elif self.falling_speed < 0:  # Jumping up
                    self.rect.top = obstacle.bottom
                    self.falling_speed = 0

        # If we're standing on a moving obstacle, inherit its movement
        if standing_on and hasattr(standing_on, 'get_movement'):
            dx, dy = standing_on.get_movement()
            self.rect.x += dx
            self.rect.y += dy

    def apply_gravity(self, obstacles):
        # Apply gravity
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        # Keep track of what the enemy is standing on
        standing_on = None

        # Check vertical collisions
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                if self.velocity_y > 0:  # Falling down
                    self.rect.bottom = obstacle.top
                    self.velocity_y = 0
                    self.is_jumping = False  # Landed on the ground

                    # Remember which obstacle we're standing on
                    standing_on = obstacle

                elif self.velocity_y < 0:  # Moving up
                    self.rect.top = obstacle.bottom
                    self.velocity_y = 0

        # If we're standing on a moving obstacle, inherit its movement
        if standing_on and hasattr(standing_on, 'get_movement'):
            dx, dy = standing_on.get_movement()
            self.rect.x += dx
            self.rect.y += dy

        # Prevent falling through the ground
        if self.rect.bottom > 600:  # Assuming screen height is 600
            self.rect.bottom = 600
            self.velocity_y = 0
            self.is_jumping = False
    def shoot(self, target_pos):
        # Calculate direction vector
        dx = target_pos[0] - self.rect.centerx
        dy = target_pos[1] - self.rect.centery

        # Normalize the vector
        distance = max(1, math.sqrt(dx * dx + dy * dy))  # Avoid division by zero
        dx = dx / distance
        dy = dy / distance

        # Create bullet
        return Bullet(
            self.rect.centerx,
            self.rect.centery,
            dx * self.bullet_speed,
            dy * self.bullet_speed,
            self.bullet_size
        )

    def take_damage(self, amount=10):
        # Only take damage if not invulnerable
        if not self.invulnerable:
            self.health -= amount

            # Activate invulnerability after being hit
            self.invulnerable = True
            self.invulnerable_timer = self.invulnerable_duration

            # Check if player died
            if self.health <= 0:
                self.respawn()

            return True  # Successfully damaged player
        return False  # Player was invulnerable

    def respawn(self):
        # Reset health
        self.health = self.max_health

        # Reset position to respawn point
        self.rect.x = self.respawn_point[0]
        self.rect.y = self.respawn_point[1]

        # Reset movement
        self.velocity_x = 0
        self.falling_speed = 0

        # Set invulnerability to prevent immediate death after respawn
        self.invulnerable = True
        self.invulnerable_timer = self.invulnerable_duration * 2  # Double invulnerability on respawn

    def set_respawn_point(self, x, y):
        # Update the respawn point
        self.respawn_point = (x, y)

    def draw(self, screen):
        # Flicker when invulnerable
        if self.invulnerable and self.invulnerable_timer % 8 >= 4:
            # Skip drawing player every few frames to create flickering effect
            pass
        else:
            if self.use_image:
                # Draw player using the character image
                screen.blit(self.image, self.rect)
            else:
                # Fallback to drawing a rectangle if image isn't available
                pygame.draw.rect(screen, self.color, self.rect)

        # Draw health bar above player
        health_bar_width = self.width * (self.health / self.max_health)
        health_bar_height = 5
        health_bar_rect = pygame.Rect(
            self.rect.x,
            self.rect.y - 10,
            health_bar_width,
            health_bar_height
        )

        # Health bar color (green to yellow to red based on health percentage)
        health_percent = self.health / self.max_health
        if health_percent > 0.6:
            health_color = (0, 255, 0)  # Green
        elif health_percent > 0.3:
            health_color = (255, 255, 0)  # Yellow
        else:
            health_color = (255, 0, 0)  # Red

        pygame.draw.rect(screen, health_color, health_bar_rect)

    def get_debug_info(self):
        return [
            f"Player X: {self.rect.x}",
            f"Player Y: {self.rect.y}",
            f"Vel X: {self.velocity_x}",
            f"Falling speed: {self.falling_speed:.2f}",
            f"On ground: {self.is_on_ground}",
            f"Health: {self.health}/{self.max_health}",
            f"Invulnerable: {self.invulnerable} ({self.invulnerable_timer})"
        ]