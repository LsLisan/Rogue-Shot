# enemy_combat.py - Handles enemy combat and health mechanics
import pygame
import random
import math


class EnemyCombat:
    def __init__(self, enemy):
        self.enemy = enemy

        # Health variables
        self.max_health = 100
        self.health = self.max_health
        self.flee_health_threshold = 30  # Health below which enemy seeks health

        # Combat variables
        self.attack_range = 200  # Distance to attack player

        # Shooting variables
        self.bullet_speed = 10
        self.bullet_size = 5
        self.shoot_cooldown = 0
        self.shoot_cooldown_max = 30  # Frames between shots

    def update(self):
        """Update combat-related timers"""
        # Update shooting cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

    def take_damage(self):
        """Handle enemy taking damage"""
        self.health -= 10
        if self.health <= 0:
            self.enemy.respawn()
        else:
            # Chance to flee when hit
            if random.random() < 0.3:  # 30% chance to flee when hit
                self.enemy.transition_to('flee')
            # Higher chance (70%) to seek health when hit and health is low
            elif self.health <= self.flee_health_threshold and random.random() < 0.7:
                self.enemy.transition_to('seek_health')

    def reset_health(self):
        """Reset health to max"""
        self.health = self.max_health

    def shoot(self, player):
        """Create a bullet aimed at the player"""
        # Check if cooldown allows shooting
        if self.shoot_cooldown > 0:
            return None

        # Reset cooldown
        self.shoot_cooldown = self.shoot_cooldown_max

        # Calculate direction vector
        dx = player.rect.centerx - self.enemy.rect.centerx
        dy = player.rect.centery - self.enemy.rect.centery

        # Normalize the vector
        distance = max(1, math.sqrt(dx * dx + dy * dy))  # Avoid division by zero
        dx = dx / distance
        dy = dy / distance

        # Add some randomness to make it less accurate
        accuracy_variation = 0.2  # Lower means more accurate
        dx += random.uniform(-accuracy_variation, accuracy_variation)
        dy += random.uniform(-accuracy_variation, accuracy_variation)

        # Re-normalize after adding randomness
        distance = max(1, math.sqrt(dx * dx + dy * dy))
        dx = dx / distance
        dy = dy / distance

        # Create and return the bullet
        from bullet import Bullet
        return Bullet(
            self.enemy.rect.centerx,
            self.enemy.rect.centery,
            dx * self.bullet_speed,
            dy * self.bullet_speed,
            self.bullet_size
        )

    def should_shoot(self, player):
        """Determine if the enemy should shoot now"""
        # Only shoot in attack state and when cooldown is ready
        if self.enemy.current_state.name != 'attack' or self.shoot_cooldown > 0:
            return False

        # Random chance to shoot when in attack state (to prevent constant firing)
        return random.random() < 0.05  # 5% chance to shoot each frame when in attack state

    def draw_health_bar(self, screen):
        """Draw the enemy's health bar"""
        health_bar_width = self.enemy.width * (self.health / self.max_health)
        health_bar_height = 5
        health_bar_rect = pygame.Rect(
            self.enemy.rect.x,
            self.enemy.rect.y - 10,
            health_bar_width,
            health_bar_height
        )
        pygame.draw.rect(screen, (0, 255, 0), health_bar_rect)