import pygame
import random
import math


class MovingObstacle:
    def __init__(self, x, y, width, height, move_type='horizontal', speed=1, amplitude=50):
        self.rect = pygame.Rect(x, y, width, height)
        self.original_x = x
        self.original_y = y
        self.width = width
        self.height = height
        self.move_type = move_type  # 'horizontal', 'vertical', or 'circular'
        self.speed = speed
        self.amplitude = amplitude
        self.time = random.uniform(0, math.pi * 2)  # Random starting phase
        self.platform_colors = [(120, 60, 20), (110, 55, 15), (130, 65, 25), (100, 50, 10)]
        self.color_index = random.randint(0, len(self.platform_colors) - 1)
        self.prev_x = x
        self.prev_y = y

    def update(self):
        # Save previous position
        self.prev_x = self.rect.x
        self.prev_y = self.rect.y

        # Original update code
        self.time += 0.05 * self.speed

        if self.move_type == 'horizontal':
            # Horizontal oscillation
            self.rect.x = self.original_x + math.sin(self.time) * self.amplitude

        elif self.move_type == 'vertical':
            # Vertical oscillation
            self.rect.y = self.original_y + math.sin(self.time) * self.amplitude

        elif self.move_type == 'circular':
            # Circular motion
            self.rect.x = self.original_x + math.cos(self.time) * self.amplitude
            self.rect.y = self.original_y + math.sin(self.time) * self.amplitude

    def get_movement(self):
        """Return how much this obstacle moved in the last frame"""
        dx = self.rect.x - self.prev_x
        dy = self.rect.y - self.prev_y
        return dx, dy

    def draw(self, screen):
        # Choose a slightly different brown for each platform for variety
        color = self.platform_colors[self.color_index]
        pygame.draw.rect(screen, color, self.rect)

        # Add a highlight on top
        pygame.draw.line(screen, (color[0] + 20, color[1] + 20, color[2] + 20),
                         (self.rect.left, self.rect.top),
                         (self.rect.right, self.rect.top), 2)