import pygame
import random
from movingObstacale import MovingObstacle


class ObstacleManager:
    def __init__(self):
        self.obstacles = []
        self.moving_obstacles = []
        self.platform_colors = [(120, 60, 20), (110, 55, 15), (130, 65, 25), (100, 50, 10)]

    def generate_level(self, player):
        self.obstacles = []
        self.moving_obstacles = []

        # Add ground - now spans the full 1000px width
        ground = pygame.Rect(0, 550, 1000, 50)
        self.obstacles.append(ground)

        # Add static platforms
        for i in range(8):  # Reduced from 12 to 8 (as we'll add 4 moving platforms)
            width = random.randint(100, 200)
            x = random.randint(0, 1000 - width)
            y = random.randint(200, 500)

            # Don't place platforms too close to each other
            valid_position = True
            for obs in self.obstacles:
                if abs(x - obs.x) < 100 and abs(y - obs.y) < 100:
                    valid_position = False
                    break

            if valid_position:
                platform = pygame.Rect(x, y, width, 20)
                self.obstacles.append(platform)

        # Add moving platforms (20% of platforms)
        for i in range(4):  # Adding 4 moving platforms
            width = random.randint(80, 150)
            x = random.randint(0, 1000 - width)
            y = random.randint(200, 500)

            # Don't place platforms too close to each other
            valid_position = True
            for obs in self.obstacles + self.moving_obstacles:
                if isinstance(obs, pygame.Rect):
                    obs_x, obs_y = obs.x, obs.y
                else:
                    obs_x, obs_y = obs.rect.x, obs.rect.y

                if abs(x - obs_x) < 100 and abs(y - obs_y) < 100:
                    valid_position = False
                    break

            if valid_position:
                # Randomly choose movement type
                move_type = random.choice(
                    ['horizontal', 'vertical', 'horizontal', 'vertical','circular'])  # More horizontal/vertical than circular

                # Create moving obstacle with random speed and amplitude
                speed = random.uniform(0.5, 2.0)
                amplitude = random.randint(30, 80)

                moving_platform = MovingObstacle(x, y, width, 20, move_type, speed, amplitude)
                self.moving_obstacles.append(moving_platform)

        # Ensure player can reach at least one platform
        player_platform = pygame.Rect(player.rect.x - 50, player.rect.y + 100, 150, 20)
        self.obstacles.append(player_platform)

    def update(self):
        # Update all moving obstacles
        for obstacle in self.moving_obstacles:
            obstacle.update()

    def draw(self, screen):
        # Draw static obstacles
        for i, obstacle in enumerate(self.obstacles):
            # Skip the ground as it's usually handled separately
            if obstacle.y >= 550:  # Assuming ground is at y=550
                # Draw ground with green color
                pygame.draw.rect(screen, (0, 180, 0), obstacle)
            else:
                # Draw platform with platform colors
                color = self.platform_colors[i % len(self.platform_colors)]
                pygame.draw.rect(screen, color, obstacle)

        # Draw moving obstacles
        for obstacle in self.moving_obstacles:
            obstacle.draw(screen)

    def get_all_obstacles(self):
        """Returns a list containing both static and moving obstacles for collision detection"""
        all_obstacles = self.obstacles.copy()
        for moving_obs in self.moving_obstacles:
            all_obstacles.append(moving_obs.rect)
        return all_obstacles