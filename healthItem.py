import math
import pygame
import random


class HealthItem:
    # A class variable to track the current number of health items
    max_items = 2
    active_items = []

    def __init__(self, x=None, y=None, width=30, height=30):
        # If position is not specified, generate random x position
        if x is None:
            self.x = random.randint(50, 950)  # Keeping away from edges
        else:
            self.x = x

        # Start from top of screen if y not specified
        if y is None:
            self.y = -50  # Start above the screen
        else:
            self.y = y

        self.width = width
        self.height = height
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

        # Movement properties
        self.falling_speed = random.uniform(2, 4)
        self.wobble_speed = 0  # Disable wobble
        self.wobble_amount = 0  # Disable wobble
        self.initial_x = self.x
        self.time = 0

        self.lifetime=7*60

        # Health restoration amount
        self.health_amount = random.randint(10, 25)

        # Appearance properties
        self.color = (255, 50, 50)  # Red for health
        self.pulse_speed = 0.1
        self.pulse_time = 0
        self.active = True

        # Particle effect for collection
        self.particles = []

        # Add the item to the active items list if there's space
        if len(HealthItem.active_items) < HealthItem.max_items:
            HealthItem.active_items.append(self)
        else:
            self.active = False  # Deactivate if there are already 2 active items

    def update(self, obstacles):
        if not self.active:
            return False


        self.lifetime -= 1
        if self.lifetime <= 0:
            self.active = False
            if self in HealthItem.active_items:
                HealthItem.active_items.remove(self)
            return False


        # Update position with gravity
        self.y += self.falling_speed

        # Add wobble effect (disabled)
        self.time += self.wobble_speed
        wobble = self.wobble_amount * 0.5 * (1 + math.sin(self.time))
        self.x = self.initial_x + wobble

        # Update rect position
        self.rect.x = self.x
        self.rect.y = self.y

        # Check for collision with obstacles
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):  # Changed from obstacle.rect
                self.y = obstacle.top - self.height
                self.rect.y = self.y
                break

        # Check if item has fallen off the bottom of the screen
        if self.y > 650:  # Greater than screen height + margin
            self.active = False
            HealthItem.active_items.remove(self)
            return False

        # Update pulse animation
        self.pulse_time += self.pulse_speed

        return True

    def collect(self, entity):
        """Apply health effect to the entity that collected the item"""
        if not self.active:
            return False

        # Check if entity is Enemy (has combat attribute) or Player (has direct health attribute)
        if hasattr(entity, 'combat'):
            # Entity is Enemy
            if entity.combat.health < entity.combat.max_health:
                entity.combat.health = min(entity.combat.health + self.health_amount, entity.combat.max_health)
                self.active = False
                HealthItem.active_items.remove(self)

                # Create particles for effect
                for _ in range(15):
                    angle = random.uniform(0, 6.28)  # 0 to 2π
                    speed = random.uniform(1, 3)
                    self.particles.append({
                        'x': self.rect.centerx,
                        'y': self.rect.centery,
                        'dx': speed * math.cos(angle),
                        'dy': speed * math.sin(angle),
                        'life': random.randint(10, 20),
                        'size': random.randint(2, 6)
                    })

                return True
        else:
            # Entity is Player or other entity with direct health attribute
            if entity.health < entity.max_health:
                entity.health = min(entity.health + self.health_amount, entity.max_health)
                self.active = False
                HealthItem.active_items.remove(self)

                # Create particles for effect
                for _ in range(15):
                    angle = random.uniform(0, 6.28)  # 0 to 2π
                    speed = random.uniform(1, 3)
                    self.particles.append({
                        'x': self.rect.centerx,
                        'y': self.rect.centery,
                        'dx': speed * math.cos(angle),
                        'dy': speed * math.sin(angle),
                        'life': random.randint(10, 20),
                        'size': random.randint(2, 6)
                    })

                return True
        return False

    def update_particles(self):
        """Update collection particle effect"""
        if self.active:
            return

        for particle in self.particles[:]:
            particle['x'] += particle['dx']
            particle['y'] += particle['dy']
            particle['life'] -= 1

            if particle['life'] <= 0:
                self.particles.remove(particle)

        # Return True if we still have particles to animate
        return len(self.particles) > 0

    def draw(self, screen):
        if self.active:
            # Calculate pulsing size effect
            pulse = abs(math.sin(self.pulse_time))
            pulse_size = int(5 * pulse)

            # Draw health item (heart shape)
            center_x = self.rect.centerx
            center_y = self.rect.centery

            # Draw a heart shape
            heart_color = self.color

            # Draw the heart shape (simplified)
            points = [
                (center_x, center_y - 5 - pulse_size),  # Top point
                (center_x + 15 + pulse_size, center_y + 10),  # Bottom right
                (center_x, center_y + 20 + pulse_size),  # Bottom center
                (center_x - 15 - pulse_size, center_y + 10),  # Bottom left
            ]

            # Draw filled heart
            pygame.draw.polygon(screen, heart_color, points)

            # Draw heart outline for better visibility
            pygame.draw.polygon(screen, (150, 0, 0), points, 2)
        else:
            # Draw particles
            for particle in self.particles:
                pygame.draw.circle(
                    screen,
                    (255, 100, 100),
                    (int(particle['x']), int(particle['y'])),
                    particle['size']
                )