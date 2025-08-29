import pygame
from circleshape import CircleShape

class Objective(CircleShape):
    def __init__(self, x, y, radius, fill_alpha=200):
        super().__init__(x, y, radius)
        self.fill_alpha = fill_alpha
        self._local_pts = self._make_star()
    
    def _make_star(self, outer_radius, inner_radius, num_pts = 5, start_angle = 90):
        '''
        Creates points for N-Pointed Star

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
