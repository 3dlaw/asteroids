from textwrap import wrap
import pygame
from circleshape import CircleShape
import random
from constants import *
from wrapdraw import wrap_offsets

class Objective(CircleShape):
    def __init__(self, x, y, radius, fill_alpha=200, obj_type=None,*, world_w=None, world_h=None,cam=None, wrap_world=True):
        super().__init__(x, y, radius)
        self.fill_alpha = fill_alpha
        self.type = obj_type
        self.world_w = world_w
        self.world_h = world_h
        self.wrap_world = wrap_world
        self.cam = cam
        if self.type == ObjectiveType.STAR:
            self.make_star()

    def _is_visible(self, cam_rect: pygame.Rect) -> bool:
        r = self.radius
        bounding_rect = pygame.Rect(self.position.x - r, self.position.y - r, 2*r, 2*r)
        offs = wrap_offsets(bounding_rect, cam_rect, int(self.world_w or 0), int(self.world_h or 0))
        return len(offs) > 0

    def update(self, dt):
        if self.world_w and self.world_h:
            if self.wrap_world:
                self.position.x %= self.world_w
                self.position.y %= self.world_h
            else: 
                self.position.x = max(0, min(self.position.x, self.world_w))
                self.position.y = max(0, min(self.position.y, self.world_h))
        
        if self.cam is not None:
            cam_rect = self.cam.rect
            if self._is_visible(cam_rect):
                self.fill_alpha -= dt*30
                if self.fill_alpha < 0:
                    self.kill()
        else:
            if (self.position.x > 0 and self.position.x < SCREEN_WIDTH and self.position.y > 0 and self.position.y < SCREEN_HEIGHT):
                self.fill_alpha -= dt*30
                if self.fill_alpha < 0:
                    self.kill()

    def draw(self, screen, cam_rect=None):
        if cam_rect is None and self.cam is not None:
            cam_rect = self.cam.rect    
        self.draw_star(screen, cam_rect)
    
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
        self.type = ObjectiveType.STAR

    def draw_star(self, screen, cam_rect = None):
        if not hasattr(self, '_local_pts'):
            return

        diameter = int(self.radius * 2)
        star_surface = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        center = pygame.Vector2(self.radius, self.radius)
        points = []
        for p in self._local_pts:
            points.append(center + p)
        pygame.draw.polygon(star_surface, (255, 255, 0, self.fill_alpha), points)

        if cam_rect is None or self.world_w is None or self.world_h is None:
            blit_x = self.position.x - self.radius
            blit_y = self.position.y - self.radius
            screen.blit(star_surface, (int(blit_x), int(blit_y)))
            return

        r = self.radius
        bounding_rect = pygame.Rect(self.position.x - r, self.position.y - r, 2*r, 2*r)
        for ox, oy in wrap_offsets(bounding_rect, cam_rect, self.world_w, self.world_h):
            blit_x = self.position.x + ox - self.radius - cam_rect.left
            blit_y = self.position.y + oy - self.radius - cam_rect.top
            screen.blit(star_surface, (int(blit_x), int(blit_y)))

    def spawn_star(self):
        self.make_star()
        self.fill_alpha = 200
        self.velocity = pygame.Vector2(0, 0)
        if self.world_w and self.world_h:
            self.position = pygame.Vector2(
                random.randint(0, int(self.world_w)),
                random.randint(0, int(self.world_h))
            )
        else:
            self.position = pygame.Vector2(random.randint(0, SCREEN_WIDTH), random.randint(0, SCREEN_HEIGHT))

    def spawn_in_view(self, margin: int=20):
        """
        place the star somewhere inside the current camera view (player's screen).
        'margin' keeps it away from the very edges.
        """
        if self.cam is None:
            # Fall back to center of single screen if no camera provided
            self.position = pygame.Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)
            return

        r = self.radius
        cam_rect = self.cam.rect

        # Clamp spawn rect inside the viewport with a margin
        left   = cam_rect.left + margin + r
        right  = cam_rect.right - margin - r
        top    = cam_rect.top + margin + r
        bottom = cam_rect.bottom - margin - r

        if right < left:   left, right = cam_rect.left + r, cam_rect.right - r
        if bottom < top:   top, bottom = cam_rect.top + r, cam_rect.bottom - r

        x = random.uniform(left, right)
        y = random.uniform(top, bottom)

        # Wrap into world to be safe
        if self.world_w and self.world_h and self.wrap_world:
            x %= self.world_w
            y %= self.world_h

        self.position = pygame.Vector2(x, y)
        self.fill_alpha = 200
        


