import pygame
from circleshape import CircleShape
from constants import *
import random

class Asteroid(CircleShape):
    
    def __init__(self, x, y, radius):
        super().__init__(x, y, radius)
        self.color = "white"

    def draw(self, screen):
        
        pygame.draw.circle(screen, self.color, self.position, self.radius, 2)

    def update(self, dt):
        self.position += self.velocity * dt

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
                asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
                asteroid1.color = "blue"
                asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
                asteroid2.color = "blue"
                asteroid1.velocity = velocity1 * 1.5
                asteroid2.velocity = velocity2 * 1.5
            else:
                asteroid1 = Asteroid(self.position.x, self.position.y, new_radius)
                asteroid1.color = "red"
                asteroid2 = Asteroid(self.position.x, self.position.y, new_radius)
                asteroid2.color = "red"
                asteroid1.velocity = velocity1 * 2
                asteroid2.velocity = velocity2 * 2