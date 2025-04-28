# enemy_pathfinding.py - Handles enemy pathfinding and spatial awareness
import pygame
import math


class EnemyPathfinding:
    def __init__(self, enemy):
        self.enemy = enemy

        # Detection variables
        self.detection_range = 200  # Distance to detect player
        self.health_item_detection_range = 300  # Distance to detect health items

        # Path finding variables
        self.path_check_timer = 0
        self.path_check_interval = 15  # Check path every 15 frames

    def update_timer(self):
        """Update path checking timer"""
        self.path_check_timer += 1

    def distance_to(self, x, y):
        """Calculate distance from enemy to a point"""
        return math.sqrt((self.enemy.rect.centerx - x) ** 2 + (self.enemy.rect.centery - y) ** 2)

    def check_path_to_target(self, obstacles, target_x, target_y):
        """Check if there's a clear path to the target"""
        # Simple ray casting
        start_x, start_y = self.enemy.rect.centerx, self.enemy.rect.centery

        # Calculate direction
        dx = target_x - start_x
        dy = target_y - start_y
        distance = max(1, math.sqrt(dx * dx + dy * dy))
        dx /= distance
        dy /= distance

        # Check points along the path
        path_clear = True
        for i in range(0, int(distance), 10):  # Check every 10 pixels
            check_x = start_x + dx * i
            check_y = start_y + dy * i

            # Create a small test rect
            test_rect = pygame.Rect(check_x - 2, check_y - 2, 4, 4)

            # Check for collisions with obstacles
            for obstacle in obstacles:
                if test_rect.colliderect(obstacle):
                    path_clear = False
                    break

            if not path_clear:
                break

        return path_clear

    def should_jump(self, obstacles, player):
        """Determine if the enemy should jump to reach the player"""
        should_jump = False

        # Check if there's an obstacle in front of us
        jump_check_rect = pygame.Rect(
            self.enemy.rect.x + (self.enemy.width if self.enemy.movement.velocity_x > 0 else -self.enemy.width),
            self.enemy.rect.y,
            self.enemy.width,
            self.enemy.height
        )

        for obstacle in obstacles:
            if jump_check_rect.colliderect(obstacle):
                should_jump = True
                break

        # Jump if player is above us
        if player.rect.bottom < self.enemy.rect.top + 50:
            should_jump = True

        # Jump if there's a gap in front (check for ground)
        if not should_jump:
            ground_check_rect = pygame.Rect(
                self.enemy.rect.x + (self.enemy.width + 10 if self.enemy.movement.velocity_x > 0 else -10),
                self.enemy.rect.y + self.enemy.height + 5,
                20,
                10
            )

            ground_detected = False
            for obstacle in obstacles:
                if ground_check_rect.colliderect(obstacle):
                    ground_detected = True
                    break

            # If no ground ahead and we're on ground, we should jump over the gap
            if not ground_detected and not self.enemy.movement.is_jumping:
                should_jump = True

        return should_jump

    def should_jump_for_path(self, obstacles, target):
        """Determine if the enemy should jump to reach a target"""
        # Check if there's an obstacle in front of us
        jump_check_rect = pygame.Rect(
            self.enemy.rect.x + (30 if self.enemy.movement.velocity_x > 0 else -30),
            self.enemy.rect.y,
            self.enemy.width,
            self.enemy.height
        )

        # Check for obstacle ahead
        obstacle_ahead = False
        for obstacle in obstacles:
            if jump_check_rect.colliderect(obstacle):
                obstacle_ahead = True
                break

        # Check for gap ahead
        ground_check_rect = pygame.Rect(
            self.enemy.rect.x + (self.enemy.width + 10 if self.enemy.movement.velocity_x > 0 else -10),
            self.enemy.rect.y + self.enemy.height + 5,
            20,
            10
        )

        ground_ahead = False
        for obstacle in obstacles:
            if ground_check_rect.colliderect(obstacle):
                ground_ahead = True
                break

        # Jump if obstacle ahead, target is above, or there's a gap
        return obstacle_ahead or target.rect.centery < self.enemy.rect.centery - 40 or not ground_ahead