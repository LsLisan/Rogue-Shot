import pygame


class ImpactEffect:
    def __init__(self, x, y, color=(255, 165, 0), life=10, max_radius=10):
        self.x = x
        self.y = y
        self.color = color
        self.life = life
        self.max_life = life
        self.max_radius = max_radius

    def update(self):
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        # Calculate current radius based on remaining life
        radius = self.max_radius * (self.life / self.max_life)

        # Draw the impact effect as a circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(radius))