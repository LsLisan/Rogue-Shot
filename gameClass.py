import sys

import pygame

from enemy import Enemy
from healthItem import HealthItem
from impactEffect import ImpactEffect
from obstacalsManager import ObstacleManager
from player import Player
from healthManager import HealthItemManager

pygame.init()
WIDTH, HEIGHT = 1000, 600
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GRAY = (128, 128, 128)
BLACK = (0, 0, 0)
OBSTACLE_COLOR = (139, 69, 19)  # Brown color for obstacles
PLATFORM_COLORS = [(120, 60, 20), (110, 55, 15), (130, 65, 25), (100, 50, 10)]  # Variety of browns
GROUND_Y = HEIGHT - 50


class Game:
    def __init__(self):
        # Create the screen
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Rogue Shot")

        # Clock for controlling FPS
        self.clock = pygame.time.Clock()

        # Game objects
        self.player = Player(WIDTH // 2, HEIGHT - 100, 50, 50)
        self.enemy = Enemy(WIDTH - 100, HEIGHT - 100, 50, 50)
        self.obstacle_manager = ObstacleManager()
        self.health_item_manager = HealthItemManager()  # Add health item manager

        # Game variables
        self.bullets = []
        self.enemy_bullets = []
        self.impact_effects = []
        self.debug_mode = False
        self.running = True

        # Generate initial level
        self.obstacle_manager.generate_level(self.player)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            # Mouse click to shoot bullet
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pos = pygame.mouse.get_pos()
                    self.bullets.append(self.player.shoot(mouse_pos))

            # Toggle debug mode with F3
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F3:
                    self.debug_mode = not self.debug_mode
                # Reset game with R key
                if event.key == pygame.K_r:
                    self.reset_game()
                # Debug: Spawn health item with H key
                if event.key == pygame.K_h and self.debug_mode:
                    self.health_item_manager.spawn_health_item()

    def reset_game(self):
        self.obstacle_manager.generate_level(self.player)
        self.player.falling_speed = 0
        self.player.is_jumping = False
        self.player.is_on_ground = False
        self.bullets.clear()
        self.enemy_bullets.clear()
        self.impact_effects.clear()
        self.health_item_manager.clear()  # Clear health items
        self.enemy.respawn()

    def handle_enemy_shooting(self):
        # Check if enemy should shoot - using the combat system
        if self.enemy.combat.should_shoot(self.player):
            bullet = self.enemy.combat.shoot(self.player)
            if bullet:
                self.enemy_bullets.append(bullet)

        # Move enemy bullets and check for collisions
        bullets_to_remove = []
        for i, bullet in enumerate(self.enemy_bullets):
            active, impact_pos = bullet.move(self.obstacle_manager.get_all_obstacles())

            # Check for collision with player
            if bullet.rect.colliderect(self.player.rect):
                self.player.take_damage(5)  # Enemy bullets deal 5 damage
                bullets_to_remove.append(i)
                # Add player hit effect (red)
                self.impact_effects.append(ImpactEffect(
                    bullet.rect.centerx, bullet.rect.centery,
                    color=(255, 0, 0), life=15, max_radius=15
                ))

            # Remove bullet if it hit something or went off-screen
            if not active:
                bullets_to_remove.append(i)
                if impact_pos:
                    # Add impact effect for obstacle hit
                    self.impact_effects.append(ImpactEffect(
                        impact_pos[0], impact_pos[1],
                        color=(200, 200, 100), life=10, max_radius=10
                    ))

        # Remove bullets that hit something or went off-screen, check if list is not empty
        if bullets_to_remove:
            for i in sorted(bullets_to_remove, reverse=True):
                if i < len(self.enemy_bullets):  # Check if index is valid
                    self.enemy_bullets.pop(i)

    def update(self):
        # Update obstacles
        self.obstacle_manager.update()

        # Move the player - use updated obstacles list
        self.player.move(self.obstacle_manager.get_all_obstacles())

        # Move the enemy - use updated obstacles list
        self.enemy.move(
            self.obstacle_manager.get_all_obstacles(),
            self.player,
            self.health_item_manager.health_items
        )

        # Handle enemy shooting
        self.handle_enemy_shooting()

        # Update health items
        self.health_item_manager.update(
            self.obstacle_manager.get_all_obstacles(),
            self.player,
            self.enemy
        )

        # Update bullets with new obstacle list
        bullets_to_keep = []
        for bullet in self.bullets:
            keep_bullet, impact_pos = bullet.move(self.obstacle_manager.get_all_obstacles())

            # Check bullet-enemy collision
            if keep_bullet and bullet.rect.colliderect(self.enemy.rect):
                keep_bullet = False
                impact_pos = (bullet.rect.centerx, bullet.rect.centery)
                self.enemy.take_damage()
                # Add enemy hit effect (red)
                self.impact_effects.append(ImpactEffect(
                    impact_pos[0], impact_pos[1],
                    color=(255, 100, 100), life=15, max_radius=12
                ))

            if keep_bullet:
                bullets_to_keep.append(bullet)
            elif impact_pos:
                # Add impact effect for obstacle hit (orange)
                self.impact_effects.append(ImpactEffect(
                    impact_pos[0], impact_pos[1]
                ))

        self.bullets = bullets_to_keep

        # Update impact effects
        self.impact_effects = [effect for effect in self.impact_effects if effect.update()]

    def draw(self):
        # Draw background
        self.screen.fill((200, 230, 255))  # Light blue sky background

        # Draw obstacles
        self.obstacle_manager.draw(self.screen)

        # Draw health items
        self.health_item_manager.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw enemy bullets
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)

        # Draw impact effects
        for effect in self.impact_effects:
            effect.draw(self.screen)

        # Draw enemy
        self.enemy.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Update the display
        pygame.display.update()

    def draw_hud(self):
        font = pygame.font.SysFont(None, 30)

        # Display enemy health
        health_text = font.render(f"Enemy Health: {self.enemy.combat.health} / {self.enemy.combat.max_health}", True, BLACK)
        self.screen.blit(health_text, (10, 10))

        # Display player health
        player_health_text = font.render(f"Player Health: {self.player.health} / {self.player.max_health}", True, BLACK)
        self.screen.blit(player_health_text, (10, 40))

        # Display controls
        controls_text = [
            "Controls:",
            "A/D - Move",
            "W/SPACE - Jump",
            "S - Fast Fall",
            "Mouse - Aim",
            "Left Click - Shoot",
            "R - Reset Level",
            "F3 - Debug Mode"
        ]

        for i, text in enumerate(controls_text):
            control_text = font.render(text, True, GRAY)
            self.screen.blit(control_text, (WIDTH - 200, 10 + i * 25))

        # Debug info
        if self.debug_mode:
            debug_info = self.player.get_debug_info() + [
                f"Bullet count: {len(self.bullets)}",
                f"Enemy bullet count: {len(self.enemy_bullets)}",
                f"Health items: {len(self.health_item_manager.health_items)}"
            ] + self.enemy.get_debug_info()

            for i, info in enumerate(debug_info):
                debug_text = font.render(info, True, BLACK)
                self.screen.blit(debug_text, (10, 80 + i * 25))

    def run(self):
        while self.running:
            self.clock.tick(60)  # FPS
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
        sys.exit()


# Start the game
if __name__ == "__main__":
    game = Game()
    game.run()