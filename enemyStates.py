# enemy_states.py - States for enemy behavior
import random
import math


class EnemyState:
    """Base class for all enemy states"""

    def __init__(self, enemy):
        self.enemy = enemy
        self.name = "base"  # Will be overridden by subclasses

    def execute(self, obstacles, player, health_items):
        """Execute state behavior"""
        pass

    def get_next_state(self, player, health_items):
        """Determine the next state based on current conditions"""
        # Check if we need health and there are health items available
        if (self.enemy.combat.health <= self.enemy.combat.flee_health_threshold and health_items and
                self.name != 'seek_health'):

            # Find the nearest health item
            self.enemy.target_health_item = self.find_nearest_health_item(health_items)

            if self.enemy.target_health_item is not None:
                # Check if health item is active and within detection range
                if (self.enemy.target_health_item.active and
                        self.enemy.pathfinding.distance_to(
                            self.enemy.target_health_item.rect.centerx,
                            self.enemy.target_health_item.rect.centery) <= self.enemy.pathfinding.health_item_detection_range):
                    return 'seek_health'  # Health is priority

        # Handle player-based states
        if player is None:
            # If no player and not seeking health, go to patrol
            if self.name != 'seek_health':
                return 'patrol'
            return self.name  # Stay in current state

        # Calculate distance to player
        distance_to_player = self.enemy.pathfinding.distance_to(player.rect.centerx, player.rect.centery)

        # Health is priority, but if player is very close, consider attacking
        if self.name == 'seek_health':
            # If health item disappeared or we collected it, go back to normal behavior
            if (self.enemy.target_health_item is None or
                    not self.enemy.target_health_item.active or
                    self.enemy.combat.health > 50):  # If health is restored enough

                # Choose appropriate state based on player distance
                if distance_to_player <= self.enemy.combat.attack_range:
                    return 'attack'
                elif distance_to_player <= self.enemy.pathfinding.detection_range:
                    return 'chase'
                else:
                    return 'patrol'

            # If player is extremely close, consider attacking even if seeking health
            elif distance_to_player <= self.enemy.combat.attack_range / 2:
                return 'attack'

            return self.name  # Stay in seek_health state

        # Regular state transitions when not seeking health
        if distance_to_player <= self.enemy.combat.attack_range:
            return 'attack'
        elif distance_to_player <= self.enemy.pathfinding.detection_range:
            return 'chase'
        elif self.name == 'chase' and distance_to_player > self.enemy.pathfinding.detection_range:
            return 'patrol'
        elif self.name == 'patrol' and self.enemy.state_timer > 300:
            if random.random() < 0.1:  # 10% chance to idle
                return 'idle'

        return self.name  # Default to current state

    def find_nearest_health_item(self, health_items):
        """Find the nearest active health item"""
        if not health_items:
            return None

        # If health_items is a single item, not a list
        if not isinstance(health_items, list):
            return health_items

        nearest_item = None
        min_distance = float('inf')

        for item in health_items:
            if item.active:  # Only consider active items
                distance = self.enemy.pathfinding.distance_to(item.rect.centerx, item.rect.centery)
                if distance < min_distance and distance <= self.enemy.pathfinding.health_item_detection_range:
                    min_distance = distance
                    nearest_item = item

        return nearest_item


class PatrolState(EnemyState):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.name = "patrol"
        self.direction_change_time = 60  # frames

    def execute(self, obstacles, player, health_items):
        # Change direction periodically
        if self.enemy.state_timer >= self.direction_change_time or self.enemy.movement.velocity_x == 0:
            self.enemy.movement.velocity_x = random.choice([-2, 2])

        # Random jump during patrol
        if not self.enemy.movement.is_jumping and random.randint(0, 100) < 2:  # 2% chance to jump
            self.enemy.movement.jump()

        # Apply horizontal movement
        self.enemy.rect.x += self.enemy.movement.velocity_x

        # Check horizontal collisions
        self.enemy.movement.handle_horizontal_collisions(obstacles)


class ChaseState(EnemyState):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.name = "chase"

    def execute(self, obstacles, player, health_items):
        if not player:
            return

        if player.rect.centerx < self.enemy.rect.centerx:
            self.enemy.movement.velocity_x = -3  # Move left faster
        else:
            self.enemy.movement.velocity_x = 3  # Move right faster

        # Smarter jumping logic
        if not self.enemy.movement.is_jumping:
            should_jump = self.enemy.pathfinding.should_jump(obstacles, player)
            if should_jump:
                self.enemy.movement.jump()

        self.enemy.rect.x += self.enemy.movement.velocity_x
        self.enemy.movement.handle_horizontal_collisions(obstacles)


class AttackState(EnemyState):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.name = "attack"

    def execute(self, obstacles, player, health_items):
        if not player:
            return

        # Slow down when attacking
        if player.rect.centerx < self.enemy.rect.centerx:
            self.enemy.movement.velocity_x = -1
        else:
            self.enemy.movement.velocity_x = 1

        # Add jumping logic (same as in ChaseState)
        if not self.enemy.movement.is_jumping:
            should_jump = self.enemy.pathfinding.should_jump(obstacles, player)
            if should_jump:
                self.enemy.movement.jump()

        # Apply movement (slower during attack)
        self.enemy.rect.x += self.enemy.movement.velocity_x

        # Check horizontal collisions
        self.enemy.movement.handle_horizontal_collisions(obstacles)

        # Try to shoot player
        if self.enemy.combat.should_shoot(player):
            self.enemy.combat.shoot(player)


class FleeState(EnemyState):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.name = "flee"

    def execute(self, obstacles, player, health_items):
        if player:
            # Move away from player
            if player.rect.centerx < self.enemy.rect.centerx:
                self.enemy.movement.velocity_x = 3  # Flee right
            else:
                self.enemy.movement.velocity_x = -3  # Flee left
        else:
            # If no player to flee from, just move in a random direction away
            if self.enemy.movement.velocity_x == 0:
                self.enemy.movement.velocity_x = random.choice([-3, 3])  # Random direction

        # Jump more frequently when fleeing
        if not self.enemy.movement.is_jumping and random.randint(0, 100) < 8:  # 8% chance to jump
            self.enemy.movement.jump()

        # Apply horizontal movement
        self.enemy.rect.x += self.enemy.movement.velocity_x

        # Check horizontal collisions
        self.enemy.movement.handle_horizontal_collisions(obstacles)

        # Change direction after some time if no player
        if not player and self.enemy.state_timer > 120:
            return 'patrol'  # Will be picked up by next state update


class IdleState(EnemyState):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.name = "idle"

    def execute(self, obstacles, player, health_items):
        # Stop moving
        self.enemy.movement.velocity_x = 0

        # State transition handled in get_next_state


class SeekHealthState(EnemyState):
    def __init__(self, enemy):
        super().__init__(enemy)
        self.name = "seek_health"

    def execute(self, obstacles, player, health_items):
        """Dedicated behavior for seeking health items with improved pathfinding"""
        if not health_items or self.enemy.target_health_item is None or not self.enemy.target_health_item.active:
            # Lost our target, find a new one
            self.enemy.target_health_item = self.find_nearest_health_item(health_items)
            if self.enemy.target_health_item is None:
                # No health items available, go back to patrol
                return  # Will be handled in next state update

        target = self.enemy.target_health_item

        # Calculate path to health item considering obstacles
        path_clear = self.enemy.pathfinding.check_path_to_target(
            obstacles, target.rect.centerx, target.rect.centery)

        # Move towards health item with increased determination
        if target.rect.centerx < self.enemy.rect.centerx:
            self.enemy.movement.velocity_x = -4  # Move left faster - higher priority movement
        else:
            self.enemy.movement.velocity_x = 4  # Move right faster

        # Pathfinding: Check periodically if we need to jump to reach the item
        if self.enemy.pathfinding.path_check_timer >= self.enemy.pathfinding.path_check_interval:
            self.enemy.pathfinding.path_check_timer = 0

            # If the path is blocked or item is above us, consider jumping
            if not path_clear or target.rect.centery < self.enemy.rect.centery - 20:
                # Check for obstacles and gaps
                should_jump = self.enemy.pathfinding.should_jump_for_path(obstacles, target)

                if should_jump and not self.enemy.movement.is_jumping:
                    self.enemy.movement.jump()

                # If there's a gap and we need to jump farther, increase horizontal velocity
                if should_jump and not self.enemy.movement.is_jumping:
                    self.enemy.movement.velocity_x *= 1.5  # More speed to jump farther

        # Apply horizontal movement
        self.enemy.rect.x += self.enemy.movement.velocity_x

        # Check horizontal collisions
        self.enemy.movement.handle_horizontal_collisions(obstacles)

        # Check for collision with health item
        if self.enemy.rect.colliderect(target.rect):
            target.collect(self.enemy)