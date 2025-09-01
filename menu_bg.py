import random
import pygame
from background import create_space_background

class MenuAsteroid():
    def __init__(self, w, h, rng):
        self._rng = rng
        self.w = w
        self.h = h
        self._build_shape()
        self.position = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2()
        self.angle = 0
        self.spin = 0
        self._respawn_edge()

    def _build_shape(self):
        r = self._rng.randint(10, 36)
        sides = self._rng.randint(6, 10)
        self.radius = r
        self.local_pts = []
        for i in range(sides):
            a = (360/sides)*i + self._rng.uniform(-8, 8)
            rr = r * (1 + self._rng.uniform(-0.25, 0.25))
            self.local_pts.append(pygame.Vector2(0, -rr).rotate(a))
        #self.angle = self._rng.uniform(0, 360)
        #self.spin  = self._rng.uniform(-30, 30)

    def update(self, dt):
        self.position += self.velocity * dt
        self.angle += self.spin * dt
        margin = 80
        if (self.position.x < -margin or
            self.position.x > self.w + margin or
            self.position.y < -margin or
            self.position.y > self.h + margin):
            self._respawn_edge()

    def _respawn_edge(self):
        side = self._rng.choice(("L","R","T","B"))
        r = self.radius
        if side == "L":
            self.position = pygame.Vector2(-r - 20, self._rng.uniform(0, self.h))
            dir_deg = self._rng.uniform(-20,20)
        elif side == "R":
            self.position = pygame.Vector2(self.w + r + 20, self._rng.uniform(0, self.h))
            dir_deg = self._rng.uniform(160, 200)
        elif side == "T":
            self.position = pygame.Vector2(self._rng.uniform(0, self.w), -r - 20)
            dir_deg = self._rng.uniform(70, 110)
        else:
            self.position = pygame.Vector2(self._rng.uniform(0, self.w), self.h + r + 20)
            dir_deg = self._rng.uniform(-110, -70)
        
        speed = self._rng.uniform(40, 120)
        self.velocity = pygame.Vector2(1, 0).rotate(dir_deg) * speed
        self.angle = self._rng.uniform(0, 360)
        self.spin = self._rng.uniform(-30,30)

    def draw(self, screen, cam_rect=None):
        cam_pts = []
        for p in self.local_pts:
            q = self.position + p.rotate(self.angle)
            cam_pts.append((int(q.x), int(q.y)))
        pygame.draw.polygon(screen, (30, 32, 40), cam_pts)
        pygame.draw.polygon(screen, (200, 220, 255), cam_pts, 1)

class MenuBackground:
    def __init__(self, width, height, *, seed = None, n_asteroids = 8, planets = True):
        self.w, self.h = width, height
        self.base = create_space_background(width, height, seed=seed, planets=planets)
        if self.base.get_alpha() is not None:
            self.base = self.base.convert()
        self._rng = random.Random(seed)
        self.asteroids = [MenuAsteroid(width, height, self._rng) for _ in range(n_asteroids)]

    def update(self,dt):
        for a in self.asteroids:
            a.update(dt)

    def draw(self, screen):
        screen.blit(self.base, (0, 0))
        for a in self.asteroids:
            a.draw(screen)