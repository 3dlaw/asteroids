import pygame
import random
from asteroid import Asteroid, get_velocity_color
from constants import *


class AsteroidField(pygame.sprite.Sprite):
    edges = [
        [
            pygame.Vector2(1, 0),
            lambda y: pygame.Vector2(-ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT),
        ],
        [
            pygame.Vector2(-1, 0),
            lambda y: pygame.Vector2(
                SCREEN_WIDTH + ASTEROID_MAX_RADIUS, y * SCREEN_HEIGHT
            ),
        ],
        [
            pygame.Vector2(0, 1),
            lambda x: pygame.Vector2(x * SCREEN_WIDTH, -ASTEROID_MAX_RADIUS),
        ],
        [
            pygame.Vector2(0, -1),
            lambda x: pygame.Vector2(
                x * SCREEN_WIDTH, SCREEN_HEIGHT + ASTEROID_MAX_RADIUS
            ),
        ],
    ]

    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.containers)
        self.spawn_timer = 0.0

    def spawn(self, radius, position, velocity):
        asteroid = Asteroid(position.x, position.y, radius)
        #print(f"Asteroid Spawn: ({asteroid.position.x}, {asteroid.position.y})")
        
        # Size-based velocity scaling: smaller = faster, larger = slower
        if asteroid.radius <= ASTEROID_MIN_RADIUS:
            # Smallest asteroids: fastest (2.0x to 2.5x)
            asteroid.velocity = velocity * random.uniform(2.0, 2.5)
        elif ASTEROID_MIN_RADIUS < asteroid.radius < ASTEROID_MAX_RADIUS:
            # Medium asteroids: medium speed (1.2x to 1.8x)
            asteroid.velocity = velocity * random.uniform(1.2, 1.8)
        else:
            # Largest asteroids: slowest (0.6x to 1.0x)
            asteroid.velocity = velocity * random.uniform(0.6, 1.0)

    def update(self, dt):
        self.spawn_timer += dt
        if self.spawn_timer > ASTEROID_SPAWN_RATE:
            self.spawn_timer = 0

            # spawn a new asteroid at a random edge
            edge = random.choice(self.edges)
            speed = random.randint(40, 100)
            velocity = edge[0] * speed
            velocity = velocity.rotate(random.randint(-30, 30))
            position = edge[1](random.uniform(0, 1))
            kind = random.randint(1, ASTEROID_KINDS)
            self.spawn(ASTEROID_MIN_RADIUS * kind, position, velocity)