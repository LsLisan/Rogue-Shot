# enemy.py - Main enemy class
import pygame
import random
import math
from healthItem import HealthItem



class Enemy:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.width = width
        self.height = height
        self.color = (255, 0, 0)  # Red color for enemy

        # Initialize systems
        from enemyMovement import EnemyMovement
        self.movement = EnemyMovement(self)
        from enemyCombat import EnemyCombat
        self.combat = EnemyCombat(self)
        from enemyPathfinding import EnemyPathfinding
        self.pathfinding = EnemyPathfinding(self)

        # State management
        from enemyStates import PatrolState
        from enemyStates import ChaseState
        from enemyStates import AttackState
        from enemyStates import FleeState
        from enemyStates import IdleState
        from enemyStates import SeekHealthState
        self.states = {
            'patrol': PatrolState(self),
            'chase': ChaseState(self),
            'attack': AttackState(self),
            'flee': FleeState(self),
            'idle': IdleState(self),
            'seek_health': SeekHealthState(self)
        }
        self.current_state = self.states['patrol']
        self.state_timer = 0
        self.state_cooldown = 0
        self.min_state_time = 30  # Minimum frames to stay in a state

        # Target tracking
        self.target_health_item = None

        # Load image
        try:
            self.image = pygame.image.load("assets/enemy/character.png")
            self.image = pygame.transform.scale(self.image, (width, height))
            self.use_image = True
        except (pygame.error, FileNotFoundError):
            print("Character image not found, using rectangle instead")
            self.use_image = False

    def move(self, obstacles, player=None, health_items=None):
        # Update state based on player and enemy conditions
        self.update_state(player, health_items)

        # Update combat system
        self.combat.update()

        # Execute current state behavior
        self.current_state.execute(obstacles, player, health_items)

        # Apply gravity (common to all states)
        self.movement.apply_gravity(obstacles)

        # Ensure enemy stays within bounds
        self.movement.enforce_boundaries()

        # Update state timer
        self.state_timer += 1

        # Update path checking timer
        self.pathfinding.update_timer()

    def update_state(self, player, health_items):
        if self.state_cooldown > 0:
            self.state_cooldown -= 1
            return  # Don't change state during cooldown

        # First, determine the best state based on current situation
        new_state = self.current_state.get_next_state(player, health_items)

        # Only change state if needed
        if new_state and new_state != self.current_state.name:
            self.transition_to(new_state)

    def transition_to(self, new_state_name):
        if self.state_cooldown == 0:
            self.current_state = self.states[new_state_name]
            self.state_timer = 0
            self.state_cooldown = self.min_state_time

            # Reset target health item if transitioning out of seek health
            if new_state_name != 'seek_health':
                self.target_health_item = None

    def take_damage(self):
        self.combat.take_damage()

    def respawn(self):
        self.combat.reset_health()
        self.current_state = self.states['patrol']
        self.target_health_item = None

        # Randomly choose one of the four corners for the enemy to appear
        corner = random.choice(['top-left', 'top-right', 'bottom-left', 'bottom-right'])

        if corner == 'top-left':
            self.rect.x = 0
            self.rect.y = 0
        elif corner == 'top-right':
            self.rect.x = 1000 - self.width
            self.rect.y = 0
        elif corner == 'bottom-left':
            self.rect.x = 0
            self.rect.y = 600 - self.height - 50
        elif corner == 'bottom-right':
            self.rect.x = 1000 - self.width
            self.rect.y = 600 - self.height - 50

    def draw(self, screen):
        if self.use_image:
            # Draw enemy using image
            screen.blit(self.image, self.rect)
        else:
            # Draw enemy as a rectangle (fallback)
            pygame.draw.rect(screen, self.color, self.rect)

        # Draw health bar
        self.combat.draw_health_bar(screen)

        # State indicator (for debugging)
        state_colors = {
            'patrol': (0, 255, 255),  # Cyan
            'chase': (255, 165, 0),  # Orange
            'attack': (255, 0, 0),  # Red
            'flee': (128, 0, 128),  # Purple
            'idle': (200, 200, 200),  # Light gray
            'seek_health': (0, 255, 0)  # Green for health seeking
        }
        indicator_size = 8
        pygame.draw.circle(
            screen,
            state_colors.get(self.current_state.name, (255, 255, 255)),
            (self.rect.right + 10, self.rect.top + 10),
            indicator_size
        )

        # Draw a line to target health item if in seek health state
        if self.current_state.name == 'seek_health' and self.target_health_item and self.target_health_item.active:
            pygame.draw.line(
                screen,
                (0, 255, 0),
                (self.rect.centerx, self.rect.centery),
                (self.target_health_item.rect.centerx, self.target_health_item.rect.centery),
                2
            )

    def get_debug_info(self):
        target_info = ""
        if self.target_health_item:
            target_info = f"Target Health Item: ({self.target_health_item.rect.x}, {self.target_health_item.rect.y})"
        else:
            target_info = "No Target Health Item"

        return [
            f"Enemy X: {self.rect.x}",
            f"Enemy Y: {self.rect.y}",
            f"Enemy Health: {self.combat.health}/{self.combat.max_health}",
            f"State: {self.current_state.name}",
            f"Is Jumping: {self.movement.is_jumping}",
            f"Shoot Cooldown: {self.combat.shoot_cooldown}/{self.combat.shoot_cooldown_max}",
            target_info
        ]