import pygame

import math


class Bullet:
    def __init__(self, x, y, velocity_x, velocity_y, size):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.size = size
        self.color = (255, 255, 0)  # Yellow bullet
        self.rect = pygame.Rect(x - size // 2, y - size // 2, size, size)

    def move(self, obstacles):
        # Update position
        self.x += self.velocity_x
        self.y += self.velocity_y

        # Update rect position
        self.rect.x = self.x - self.size // 2
        self.rect.y = self.y - self.size // 2

        # Check if bullet is out of screen
        if self.x < 0 or self.x > 1000 or self.y < 0 or self.y > 600:  # Updated for new WIDTH
            return False, None

        # Check collisions with obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                impact_pos = (self.x, self.y)
                return False, impact_pos

        return True, None

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)