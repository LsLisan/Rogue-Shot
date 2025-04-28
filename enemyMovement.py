# enemy_movement.py - Handles enemy movement mechanics
import pygame


class EnemyMovement:
    def __init__(self, enemy):
        self.enemy = enemy

        # Movement variables
        self.velocity_x = 2
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_height = -15  # Negative for upward motion
        self.is_jumping = False

    def apply_gravity(self, obstacles):
        """Apply gravity and handle vertical collisions"""
        # Apply gravity
        self.velocity_y += self.gravity
        self.enemy.rect.y += self.velocity_y

        # Check vertical collisions
        for obstacle in obstacles:
            if self.enemy.rect.colliderect(obstacle):
                if self.velocity_y > 0:  # Falling down
                    self.enemy.rect.bottom = obstacle.top
                    self.velocity_y = 0
                    self.is_jumping = False  # Landed on the ground
                elif self.velocity_y < 0:  # Moving up
                    self.enemy.rect.top = obstacle.bottom
                    self.velocity_y = 0

        # Prevent falling through the ground
        if self.enemy.rect.bottom > 600:  # Assuming screen height is 600
            self.enemy.rect.bottom = 600
            self.velocity_y = 0
            self.is_jumping = False

    def handle_horizontal_collisions(self, obstacles):
        """Handle collisions with obstacles during horizontal movement"""
        for obstacle in obstacles:
            if self.enemy.rect.colliderect(obstacle):
                if self.velocity_x > 0:  # Moving right
                    self.enemy.rect.right = obstacle.left
                    self.velocity_x *= -1  # Reverse direction
                elif self.velocity_x < 0:  # Moving left
                    self.enemy.rect.left = obstacle.right
                    self.velocity_x *= -1  # Reverse direction

    def enforce_boundaries(self):
        """Keep enemy within screen bounds"""
        if self.enemy.rect.left < 0:
            self.enemy.rect.left = 0
            self.velocity_x *= -1
        if self.enemy.rect.right > 1000:  # Updated to 1000 for new WIDTH
            self.enemy.rect.right = 1000
            self.velocity_x *= -1

    def jump(self):
        """Make the enemy jump"""
        if not self.is_jumping:
            self.velocity_y = self.jump_height
            self.is_jumping = True