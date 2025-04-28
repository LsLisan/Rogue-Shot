from random import random

import pygame

WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
OBSTACLE_COLOR = (139, 69, 19)  # Brown for obstacles
PLATFORM_COLORS = [(120, 60, 20), (110, 55, 15), (130, 65, 25), (100, 50, 10)]  # Variety of browns
GROUND_Y = HEIGHT - 50
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