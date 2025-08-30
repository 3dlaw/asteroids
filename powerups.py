import pygame
from circleshape import CircleShape
import random
from constants import *

class Objective(CircleShape):
    def __init__(self, x, y, radius, fill_alpha=200):
        super().__init__(x, y, radius)
        self.fill_alpha = fill_alpha
        self.make_star()

    def update(self, dt):
        if (self.position.x > 0 and self.position.x < SCREEN_WIDTH and self.position.y > 0 and self.position.y < SCREEN_HEIGHT):
            self.fill_alpha -= dt*30
            if self.fill_alpha < 0:
                self.kill()
        

    def draw(self, screen):
        self.draw_star(screen)
    
    def _make_star(self, outer_radius, inner_radius, num_pts = 5, start_angle = 90):
        '''
        Creates local points for N-Pointed Star

        Args: 
            outer radius = where outer vertices will go
            inner radius = where inner vertices will go
            num_points = number of outer vertices (default 5)
            start angle = where first point should be (defaults to straight up)
        '''
        pts = []
        step = 360/(num_pts * 2)
        angle = start_angle
        for i in range(num_pts*2):
            current_radius = outer_radius if i % 2 == 0 else inner_radius
            direction_vector = pygame.Vector2(0, -current_radius).rotate(angle)
            pts.append(direction_vector)
            angle += step
        return pts
    
    def make_star(self, num_points=5, inner_ratio=0.5):
        '''
        calls/creates the star. 

        optional args:
            num_points - if don't want a 5 point star, change this
            inner ratio = increase if want smaller points
        '''
        outer_radius = self.radius
        inner_radius = self.radius*inner_ratio
        self._local_pts = self._make_star(outer_radius, inner_radius, num_points)

    def draw_star(self, screen):
        if hasattr(self, '_local_pts'):
            #print(f"Drawing star with alpha: {self.fill_alpha}")  # Debug
            star_surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            center = pygame.Vector2(self.radius, self.radius)
            points = []
            for p in self._local_pts:
                points.append(center + p)
            pygame.draw.polygon(star_surface, (255, 255, 0, self.fill_alpha), points)
            screen.blit(star_surface, (self.position.x - self.radius, self.position.y - self.radius))
       

    def spawn_star(self):
        self.make_star()
        self.fill_alpha = 200
        self.velocity = pygame.Vector2(0, 0)
        self.position = pygame.Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))
        


