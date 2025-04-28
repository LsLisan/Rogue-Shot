import pygame
import sys
import math
import random

# Initialize Pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
OBSTACLE_COLOR = (139, 69, 19)  # Brown for obstacles
PLATFORM_COLORS = [(120, 60, 20), (110, 55, 15), (130, 65, 25), (100, 50, 10)]  # Variety of browns

# Player settings
player_width, player_height = 50, 50
player_x, player_y = WIDTH // 2, HEIGHT - player_height - 50
player_velocity = 5
jump_force = -15  # Initial velocity for jump
gravity = 0.75  # Reduced slightly for more realistic jumping feel
max_fall_speed = 12  # Increased max fall speed for realism
player_falling_speed = 0  # Current falling speed
is_jumping = False
is_on_ground = False
can_jump = True  # To prevent double jumping
coyote_time = 5  # Frames where player can still jump after leaving a platform
coyote_counter = 0
jump_buffer_time = 7  # Frames to buffer a jump input
jump_buffer_counter = 0

# Bullet settings
bullet_width, bullet_height = 10, 5
bullet_velocity = 7
bullets = []  # List to store bullets
bullet_impact_effects = []  # For impact visual effects

# Enemy settings
enemy_width, enemy_height = 50, 50
enemy_x, enemy_y = WIDTH - 100, HEIGHT - enemy_height - 50
enemy_velocity = 2
enemy_health = 3
enemy = pygame.Rect(enemy_x, enemy_y, enemy_width, enemy_height)
enemy_direction = -1  # -1 for left, 1 for right
enemy_jump_timer = 0

# Game settings
ground_y = HEIGHT - 50

# Load assets
try:
    player_image = pygame.image.load("../assets/player/character.png")
    player_image = pygame.transform.scale(player_image, (player_width, player_height))
except pygame.error:
    # Fallback if image can't be loaded
    player_image = None

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2D Platformer Action Game")

# Player object (rectangle)
player = pygame.Rect(player_x, player_y, player_width, player_height)

# Clock for controlling FPS
clock = pygame.time.Clock()

# Game variables
obstacles = []
platforms = []  # Separate list for non-ground obstacles
debug_mode = False  # Toggle for showing debug info


def generate_obstacles():
    global obstacles, platforms
    obstacles = []
    platforms = []

    # Add ground as an obstacle
    ground = pygame.Rect(0, ground_y, WIDTH, 50)
    obstacles.append(ground)

    # Create a more realistic level layout with different types of platforms

    # 1. Create a few main horizontal platforms at different heights
    main_platform_heights = [ground_y - 120, ground_y - 220, ground_y - 320]
    for height in main_platform_heights:
        # Create 2-3 platforms at this height
        for _ in range(random.randint(2, 3)):
            width = random.randint(150, 250)
            x_pos = random.randint(0, WIDTH - width)

            # Ensure platforms at the same height don't overlap
            valid_position = True
            for platform in platforms:
                if abs(platform.y - height) < 10:  # Same height level
                    if not (x_pos + width < platform.x or x_pos > platform.x + platform.width):
                        valid_position = False
                        break

            if valid_position:
                platform = pygame.Rect(x_pos, height, width, random.randint(20, 30))
                platforms.append(platform)
                obstacles.append(platform)

    # 2. Add some smaller stepping stones/platforms between main platforms
    for _ in range(random.randint(5, 8)):
        width = random.randint(50, 100)
        height = random.randint(15, 25)
        x_pos = random.randint(0, WIDTH - width)
        y_pos = random.randint(ground_y - 400, ground_y - 50)

        # Check if this platform overlaps with existing ones
        valid_position = True
        for platform in platforms:
            if (abs(platform.y - y_pos) < height + 10 and
                    not (x_pos + width < platform.x - 10 or x_pos > platform.x + platform.width + 10)):
                valid_position = False
                break

        if valid_position:
            platform = pygame.Rect(x_pos, y_pos, width, height)
            platforms.append(platform)
            obstacles.append(platform)

    # 3. Add some vertical obstacles/walls
    for _ in range(random.randint(2, 4)):
        width = random.randint(20, 30)
        height = random.randint(80, 150)
        x_pos = random.randint(50, WIDTH - width - 50)
        y_pos = random.randint(ground_y - height, ground_y - 20)

        # Check if this wall doesn't block important areas
        valid_position = True
        for platform in platforms:
            if (abs(platform.x - x_pos) < width + 10 and
                    not (y_pos + height < platform.y - 10 or y_pos > platform.y + platform.height + 10)):
                valid_position = False
                break

        if valid_position:
            wall = pygame.Rect(x_pos, y_pos, width, height)
            platforms.append(wall)
            obstacles.append(wall)

    # Add player spawn platform
    spawn_platform = pygame.Rect(WIDTH // 2 - 75, ground_y - 70, 150, 20)
    platforms.append(spawn_platform)
    obstacles.append(spawn_platform)

    # Ensure the player has a safe starting position
    player.x = WIDTH // 2 - player_width // 2
    player.y = spawn_platform.y - player_height - 5


def move_player():
    global player_falling_speed, is_jumping, is_on_ground, can_jump, coyote_counter, jump_buffer_counter

    # Get pressed keys
    keys = pygame.key.get_pressed()

    # Horizontal movement with slight acceleration/deceleration for realism
    x_movement = 0
    if keys[pygame.K_a]:  # Move left
        x_movement -= player_velocity
    if keys[pygame.K_d]:  # Move right
        x_movement += player_velocity

    player.x += x_movement

    # Keep player within screen bounds
    player.x = max(0, min(player.x, WIDTH - player_width))

    # Jump buffer - registers jump inputs even before landing
    if keys[pygame.K_w] or keys[pygame.K_SPACE]:
        jump_buffer_counter = jump_buffer_time
    else:
        jump_buffer_counter = max(0, jump_buffer_counter - 1)

    # Handle jumping with better physics
    if is_on_ground:
        coyote_counter = coyote_time
        can_jump = True
    else:
        coyote_counter = max(0, coyote_counter - 1)

    # Apply the jump if conditions are met
    if (coyote_counter > 0 or is_on_ground) and jump_buffer_counter > 0 and can_jump:
        player_falling_speed = jump_force  # Initial velocity upward
        is_jumping = True
        is_on_ground = False
        can_jump = False  # Prevent double jumping
        jump_buffer_counter = 0
        coyote_counter = 0

    # Variable jump height - hold jump key to jump higher
    if is_jumping and player_falling_speed < 0:
        if not (keys[pygame.K_w] or keys[pygame.K_SPACE]):
            player_falling_speed = max(player_falling_speed, jump_force / 2)  # Cut the jump short if button released

    # Apply gravity
    player_falling_speed += gravity
    player_falling_speed = min(player_falling_speed, max_fall_speed)

    # Apply vertical movement
    player.y += player_falling_speed

    # Reset on_ground status before collision checks
    was_on_ground = is_on_ground
    is_on_ground = False

    # Check for collisions with obstacles
    for obstacle in obstacles:
        if player.colliderect(obstacle):
            # Collision from above (landing)
            if player_falling_speed > 0 and player.bottom - player_falling_speed <= obstacle.top + 5:
                player.bottom = obstacle.top
                is_on_ground = True
                is_jumping = False
                player_falling_speed = 0
                can_jump = True

            # Collision from below (hitting ceiling)
            elif player_falling_speed < 0 and player.top - player_falling_speed >= obstacle.bottom - 5:
                player.top = obstacle.bottom
                player_falling_speed = 0  # Stop upward momentum

            # Collision from left
            elif x_movement > 0 and player.right - x_movement <= obstacle.left + 5:
                player.right = obstacle.left

            # Collision from right
            elif x_movement < 0 and player.left - x_movement >= obstacle.right - 5:
                player.left = obstacle.right

    # Fast fall with S key
    if (keys[pygame.K_s]) and not is_on_ground:
        player_falling_speed = max(player_falling_speed, max_fall_speed / 1.5)


def move_enemy():
    global enemy_direction, enemy_jump_timer

    # Basic enemy AI - move left and right, and occasionally jump
    enemy.x += enemy_velocity * enemy_direction

    # Change direction if hitting screen edge
    if enemy.x <= 0:
        enemy_direction = 1
    elif enemy.x + enemy_width >= WIDTH:
        enemy_direction = -1

    # Simple gravity for enemy
    enemy_falling_speed = 5  # Constant falling speed
    enemy.y += enemy_falling_speed

    # Check for collisions with obstacles
    enemy_on_ground = False
    for obstacle in obstacles:
        if enemy.colliderect(obstacle):
            # Collision from above (landing)
            if enemy.bottom - enemy_falling_speed <= obstacle.top + 5:
                enemy.bottom = obstacle.top
                enemy_on_ground = True
            # Hit wall - change direction
            elif enemy_direction > 0 and enemy.right >= obstacle.left and enemy.right - enemy_velocity <= obstacle.left:
                enemy_direction = -1
            elif enemy_direction < 0 and enemy.left <= obstacle.right and enemy.left + enemy_velocity >= obstacle.right:
                enemy_direction = 1

    # Reset enemy if it falls off the screen
    if enemy.y > HEIGHT:
        enemy.x = random.randint(50, WIDTH - 50 - enemy_width)
        enemy.y = 100

    # Random jumping if on ground
    if enemy_on_ground:
        enemy_jump_timer -= 1
        if enemy_jump_timer <= 0:
            enemy.y -= 10  # Small jump
            enemy_jump_timer = random.randint(60, 120)  # Random timer for next jump


def shoot_bullet(mouse_pos):
    # Calculate angle towards mouse position
    bullet_angle = math.atan2(mouse_pos[1] - player.centery, mouse_pos[0] - player.centerx)
    bullet_velocity_x = bullet_velocity * math.cos(bullet_angle)
    bullet_velocity_y = bullet_velocity * math.sin(bullet_angle)

    # Create bullet with proper rotation
    bullet = {
        'rect': pygame.Rect(player.centerx - bullet_width // 2, player.centery - bullet_height // 2, bullet_width,
                            bullet_height),
        'velocity': (bullet_velocity_x, bullet_velocity_y),
        'angle': math.degrees(bullet_angle)
    }
    bullets.append(bullet)


def move_bullets():
    global bullets, bullet_impact_effects
    bullets_to_keep = []

    for bullet in bullets:
        old_x = bullet['rect'].x
        old_y = bullet['rect'].y

        # Move the bullet according to its velocity
        bullet['rect'].x += bullet['velocity'][0]
        bullet['rect'].y += bullet['velocity'][1]

        # Check for collisions with obstacles
        bullet_hit_obstacle = False
        for obstacle in obstacles:
            if bullet['rect'].colliderect(obstacle):
                bullet_hit_obstacle = True
                # Create impact effect
                impact_effect = {
                    'pos': (bullet['rect'].centerx, bullet['rect'].centery),
                    'radius': 5,
                    'max_radius': 8,
                    'color': (255, 200, 100),
                    'life': 10
                }
                bullet_impact_effects.append(impact_effect)
                break

        # Keep bullet if it hasn't hit an obstacle and is still on screen
        if not bullet_hit_obstacle and -50 < bullet['rect'].x < WIDTH + 50 and -50 < bullet['rect'].y < HEIGHT + 50:
            bullets_to_keep.append(bullet)

    # Update impact effects
    for effect in bullet_impact_effects[:]:
        effect['life'] -= 1
        if effect['life'] <= 0:
            bullet_impact_effects.remove(effect)

    return bullets_to_keep


def handle_enemy_collision():
    global enemy_health
    for bullet in bullets[:]:  # Create a copy to safely modify during iteration
        if enemy.colliderect(bullet['rect']):
            enemy_health -= 1  # Decrease health when hit
            bullets.remove(bullet)  # Remove bullet after collision

            # Create impact effect
            impact_effect = {
                'pos': (bullet['rect'].centerx, bullet['rect'].centery),
                'radius': 5,
                'max_radius': 12,
                'color': (255, 100, 100),
                'life': 15
            }
            bullet_impact_effects.append(impact_effect)

            if enemy_health <= 0:
                # Respawn the enemy with full health after defeat
                enemy_health = 3
                enemy.x = random.randint(50, WIDTH - 50 - enemy_width)
                enemy.y = random.randint(50, 150)


def draw_game():
    screen.fill((200, 230, 255))  # Light blue sky background

    # Draw the obstacles/platforms
    for i, obstacle in enumerate(obstacles):
        if i == 0:  # Ground
            # Draw ground with a gradient
            pygame.draw.rect(screen, GREEN, obstacle)
            pygame.draw.rect(screen, (0, 180, 0), (0, ground_y, WIDTH, 10))
        else:  # Platforms
            # Choose a slightly different brown for each platform for variety
            color = random.choice(PLATFORM_COLORS) if obstacle not in platforms else PLATFORM_COLORS[
                platforms.index(obstacle) % len(PLATFORM_COLORS)]
            pygame.draw.rect(screen, color, obstacle)
            # Add a highlight on top
            pygame.draw.line(screen, (color[0] + 20, color[1] + 20, color[2] + 20),
                             (obstacle.left, obstacle.top),
                             (obstacle.right, obstacle.top), 2)

    # Draw the player
    if player_image:
        screen.blit(player_image, player)
    else:
        # Fallback if image can't be loaded
        pygame.draw.rect(screen, BLUE, player)

    # Draw the bullets with proper rotation
    for bullet in bullets:
        bullet_surface = pygame.Surface((bullet_width, bullet_height), pygame.SRCALPHA)
        pygame.draw.rect(bullet_surface, RED, (0, 0, bullet_width, bullet_height))
        rotated_surface = pygame.transform.rotate(bullet_surface, -bullet['angle'])
        screen.blit(rotated_surface, (bullet['rect'].x - rotated_surface.get_width() // 2 + bullet_width // 2,
                                      bullet['rect'].y - rotated_surface.get_height() // 2 + bullet_height // 2))

    # Draw bullet impact effects
    for effect in bullet_impact_effects:
        radius = effect['radius'] * (1 - effect['life'] / 15)  # Start small, grow larger
        alpha = 255 * effect['life'] / 15  # Fade out
        effect_surface = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(effect_surface, (*effect['color'], alpha), (radius, radius), radius)
        screen.blit(effect_surface, (effect['pos'][0] - radius, effect['pos'][1] - radius))

    # Draw the enemy
    pygame.draw.rect(screen, RED, enemy)

    # Health bar for enemy
    health_bar_width = 40
    health_bar_height = 5
    health_percentage = enemy_health / 3  # Assuming max health is 3
    pygame.draw.rect(screen, (100, 100, 100), (
    enemy.x + enemy_width // 2 - health_bar_width // 2, enemy.y - 10, health_bar_width, health_bar_height))
    pygame.draw.rect(screen, (255, 0, 0), (
    enemy.x + enemy_width // 2 - health_bar_width // 2, enemy.y - 10, health_bar_width * health_percentage,
    health_bar_height))

    # Display the health of the enemy and controls in the HUD
    font = pygame.font.SysFont(None, 30)
    health_text = font.render(f"Enemy Health: {enemy_health} / 3", True, BLACK)
    screen.blit(health_text, (10, 10))

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
        control_text = font.render(text, True, BLACK)
        screen.blit(control_text, (WIDTH - 150, 10 + i * 25))

    # Debug info
    if debug_mode:
        debug_info = [
            f"Player pos: ({player.x}, {player.y})",
            f"Falling speed: {player_falling_speed:.1f}",
            f"On ground: {is_on_ground}",
            f"Can jump: {can_jump}",
            f"Coyote time: {coyote_counter}",
            f"Jump buffer: {jump_buffer_counter}",
            f"Bullet count: {len(bullets)}",
            f"Enemy pos: ({enemy.x}, {enemy.y})"
        ]

        for i, info in enumerate(debug_info):
            debug_text = font.render(info, True, BLACK)
            screen.blit(debug_text, (10, 50 + i * 25))

    pygame.display.update()


# Main game loop
running = True
generate_obstacles()  # Initial obstacle generation

while running:
    clock.tick(60)  # FPS

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        # Mouse click to shoot bullet
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left click
                mouse_pos = pygame.mouse.get_pos()
                shoot_bullet(mouse_pos)

        # Toggle debug mode with F3
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_F3:
                debug_mode = not debug_mode
            # Reset game with R key
            if event.key == pygame.K_r:
                generate_obstacles()
                player_falling_speed = 0
                is_jumping = False
                is_on_ground = False
                bullets.clear()
                bullet_impact_effects.clear()
                enemy_health = 3
                enemy.x = WIDTH - 100
                enemy.y = 100

    # Move the player
    move_player()

    # Move the enemy
    move_enemy()

    # Handle bullet movement and collision with obstacles
    bullets = move_bullets()

    # Handle enemy collision with bullets
    handle_enemy_collision()

    # Draw everything
    draw_game()

pygame.quit()
sys.exit()