import pygame
from circleshape import CircleShape
from constants import *
import random

def get_velocity_color(velocity):
    """
    Get a color based on velocity.length(), creating a gradient from red (fastest) to blue (slowest).
    
    Args:
        velocity: Pygame Vector2 representing velocity
    
    Returns:
        tuple: RGB color tuple (r, g, b)
    """
    # Handle edge cases
    if velocity is None or velocity.length() == 0:
        return (255, 255, 255)  # White for stationary objects
    
    speed = velocity.length()
    
    # Color mapping based on actual velocity ranges (25-414)
    if speed > 350:
        return (255, 0, 0)      # Red for very fast (>350)
    elif speed > 280:
        return (255, 128, 0)    # Orange for fast (280-350)
    elif speed > 200:
        return (255, 255, 0)    # Yellow for medium-fast (200-280)
    elif speed > 120:
        return (0, 255, 0)      # Green for medium (120-200)
    elif speed > 60:
        return (0, 0, 255)      # Blue for slow (60-120)
    else:
        return (255, 255, 255)    # White for very slow (25-60)

class Asteroid(CircleShape):
    
    def __init__(self, x, y, radius, fill_alpha=200):
        super().__init__(x, y, radius)
        self.thick = 2
        self._local_points = self._make_polygon()
        self.angle = random.uniform(0,360)
        self.spin = random.uniform(-60, 60)
        self.fill_alpha = fill_alpha

    def _make_polygon(self, min_sides = 6, max_sides = 12, angle_jitter = 0.35, radial_jitter = 0.30):
        sides = random.randint(min_sides, max_sides)
        step = 360/sides
        max_angle_jitter = step * angle_jitter
        points = []
        angles = []

        for i in range(sides):
            a = i * step + random.uniform(-max_angle_jitter, max_angle_jitter)
            angles.append(a)
        angles.sort()

        for a in angles:
            r = self.radius * (1 + random.uniform(-radial_jitter, radial_jitter))
            r = max(0.35*self.radius,r)
            v = pygame.Vector2(0, -r).rotate(a)
            points.append(v)

        return points

    def asteroid_shape(self):
        points = []
        for p in self._local_points:
            points.append(self.position + p)
        return points

    def draw(self, screen):
        # Use velocity-based coloring
        velocity_color = get_velocity_color(self.velocity)
        #pygame.draw.circle(screen, velocity_color, self.position, self.radius, self.thick)
        pygame.draw.polygon(screen, velocity_color, self.asteroid_shape(), self.thick)
        temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        fill_color = (*velocity_color[:3], self.fill_alpha)
        pygame.draw.polygon(temp_surface, fill_color, self.asteroid_shape())
        screen.blit(temp_surface, (0, 0))

    def update(self, dt):
        self.position += self.velocity * dt
        buffer = 60
        
        if self.position.x> SCREEN_WIDTH + buffer:
            self.kill() 
        elif self.position.x < 0 - buffer:
            self.kill()
        elif self.position.y > SCREEN_HEIGHT + buffer:
            self.kill()
        elif self.position.y < 0 - buffer:
            self.kill()
        

    def split(self):
        self.kill()
        if self.radius <= ASTEROID_MIN_RADIUS:
            return 
        else:
            rand_angle = random.uniform(20,50)
            velocity1 = self.velocity.rotate(rand_angle)
            velocity2 = self.velocity.rotate(-rand_angle)
            new_radius = self.radius - ASTEROID_MIN_RADIUS
            if new_radius > ASTEROID_MIN_RADIUS:
                # Medium asteroids: medium speed (1.2x to 1.8x)
                asteroid1 = Asteroid(self.position.x, self.position.y, new_radius, 64)
                #asteroid1.thick *= 5
                asteroid1.velocity = velocity1 * random.uniform(1.2, 1.8)
                asteroid2 = Asteroid(self.position.x, self.position.y, new_radius, 64)
                #asteroid2.thick *= 5
                asteroid2.velocity = velocity2 * random.uniform(1.2, 1.8)
            else:
                # Smallest asteroids: fastest (2.0x to 2.5x)
                asteroid1 = Asteroid(self.position.x, self.position.y, new_radius, 0)
                #asteroid1.thick *= 5
                asteroid1.velocity = velocity1 * random.uniform(2.0, 2.5)
                asteroid2 = Asteroid(self.position.x, self.position.y, new_radius, 0)
                #asteroid2.thick *= 5
                asteroid2.velocity = velocity2 * random.uniform(2.0, 2.5)
