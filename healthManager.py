import random
import pygame
from healthItem import HealthItem


class HealthItemManager:
    def __init__(self):
        self.health_items = []
        self.spawn_timer = 0
        self.spawn_interval = 600  # 10 seconds at 60 FPS (10 * 60 = 600)

    def update(self, obstacles, player, enemy):
        # Only increment spawn timer if we're below the max number of active items
        if len(HealthItem.active_items) < HealthItem.max_items:
            self.spawn_timer += 1

        # Update existing health items
        items_to_keep = []

        for item in self.health_items:
            was_active = item.active

            # Update item position and check if still active
            is_active = item.update(obstacles)

            # Check if the item just disappeared and we need a new one
            if was_active and not is_active:
                # If below max items, set timer to spawn soon
                if len(HealthItem.active_items) < HealthItem.max_items:
                    self.spawn_timer = max(self.spawn_timer, self.spawn_interval - 180)  # At most 3 seconds

            # Check for collection by player
            if item.active and item.rect.colliderect(player.rect):
                if item.collect(player):
                    # Item was collected - no need to adjust timer here
                    pass

            # Check for collection by enemy
            elif item.active and item.rect.colliderect(enemy.rect):
                if item.collect(enemy):
                    # Item was collected - no need to adjust timer here
                    pass

            # Keep item if active or has particles
            if not item.active:
                has_particles = item.update_particles()
                if has_particles:
                    items_to_keep.append(item)
            elif is_active:
                items_to_keep.append(item)

        self.health_items = items_to_keep

        # Spawn new health item if timer reaches interval and below max items
        if self.spawn_timer >= self.spawn_interval and len(HealthItem.active_items) < HealthItem.max_items:
            self.spawn_health_item()
            # Reset timer
            self.spawn_timer = 0

    def spawn_health_item(self):
        """Create a new health item at a random position"""
        x = random.randint(50, 950)  # Random position across the screen
        new_item = HealthItem(x, -50)  # Start above the screen
        self.health_items.append(new_item)

    def draw(self, screen):
        """Draw all active health items"""
        for item in self.health_items:
            item.draw(screen)

    def clear(self):
        """Clear all health items"""
        self.health_items.clear()
        self.spawn_timer = 0