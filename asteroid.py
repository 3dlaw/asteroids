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
        level5 = (0, 222, 173)
        return level5      # Level 5 Red for very fast (>350)
    elif speed > 280:
        level4 =  (178, 40, 85)
        return level4    # Level 4 Orange for fast (280-350)
    elif speed > 200:
        level3 = (196, 107, 44)
        return level3    # Level 3Yellow for medium-fast (200-280)
    elif speed > 120:
        level2 = (108, 66, 133)
        return level2      # Level 2 Green for medium (120-200)
    elif speed > 60:
        level1 = (64, 119, 142)
        return level1      # Level 1 Blue for slow (60-120)
    else:
        level0 = (25, 38, 56)
        return level0    # Level 0 White for very slow (25-60)

class Asteroid(CircleShape):
    
    def __init__(self, x, y, radius, fill_alpha=200):
        super().__init__(x, y, radius)
        self.thick = 2
        self._local_points = self._make_polygon()
        self.angle = random.uniform(0,360)
        self.spin = random.uniform(-60, 60)
        self.fill_alpha = fill_alpha

        self._detail_surface = self.__build_detail_surface()

    def _make_polygon(self, min_sides = 6, max_sides = 12, angle_jitter = 0.35, radial_jitter = 0.30):
        '''
        creates local points for random polygons

        optional args:
            min_sides - change minimum number of sides from 6
            max_sides - change maximum number of sides from 12
            angle_jitter - step angle variance
            angle_radial - vertex position variance
        '''
        sides = random.randint(min_sides, max_sides) 
        step = 360/sides
        max_angle_jitter = step * angle_jitter 
        points = []
        angles = []

        #gets random angles between sides
        for i in range(sides):
            modified_step_angle = i * step + random.uniform(-max_angle_jitter, max_angle_jitter)  
            angles.append(modified_step_angle)
        angles.sort()

        #gets vertex for sides
        for angle in angles:
            vertex_positoin = self.radius * (1 + random.uniform(-radial_jitter, radial_jitter))
            r = max(0.35*self.radius,vertex_positoin)
            vertex_vector = pygame.Vector2(0, -vertex_positoin).rotate(angle)
            points.append(vertex_vector)

        return points

    def asteroid_shape(self):
        '''
        translates local points to global points to be used when drawn
        '''
        points = []
        for p in self._local_points:
            points.append(self.position + pygame.Vector2(p).rotate(-self.angle))
        return points

    def draw(self, screen):
        # Use velocity-based coloring
        velocity_color = get_velocity_color(self.velocity)
        pygame.draw.polygon(screen, (*velocity_color,self.fill_alpha), self.asteroid_shape())

        overlay = pygame.transform.rotate(self._detail_surface, self.angle)
        rect = overlay.get_rect(center=(self.position.x, self.position.y))
        screen.blit(overlay, rect.topleft)

    def update(self, dt):
        self.position += self.velocity * dt
        self.angle += self.spin * dt
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
                asteroid1 = Asteroid(self.position.x, self.position.y, new_radius, 128)
                #asteroid1.thick *= 5
                asteroid1.velocity = velocity1 * random.uniform(1.2, 1.8)
                asteroid2 = Asteroid(self.position.x, self.position.y, new_radius, 128)
                #asteroid2.thick *= 5
                asteroid2.velocity = velocity2 * random.uniform(1.2, 1.8)
            else:
                # Smallest asteroids: fastest (2.0x to 2.5x)
                asteroid1 = Asteroid(self.position.x, self.position.y, new_radius, 64)
                #asteroid1.thick *= 5
                asteroid1.velocity = velocity1 * random.uniform(2.0, 2.5)
                asteroid2 = Asteroid(self.position.x, self.position.y, new_radius, 64)
                #asteroid2.thick *= 5
                asteroid2.velocity = velocity2 * random.uniform(2.0, 2.5)

    def __build_detail_surface(self):
        """
        Returns a transparent detail OVERLAY (no base fill).
        It's intentionally subtle so the main color shows through:
        - faint inset bands (alpha only)
        - gentle edge light/shadow (very low alpha)
        - few speckles
        - no craters, no radial vignette
        """
        RING_LIGHT_ALPHA = 14      # 12 → 14 (slightly stronger)
        RING_DARK_ALPHA  = 8      # 10 → 12

        EDGE_HI_MAX_ALPHA = 50     # 36 → 80 (way more visible)
        EDGE_SH_MAX_ALPHA = 40     # 26 → 60
        EDGE_INSET_SCALE  = 0.96   # 0.965 → 0.96 (hug the outline more)
        EDGE_THICK        = 3      # 1px; switch to 2 if you want bolder

        SPECK_DENSITY     = 1.2    # radius * 0.8 → radius * 1.1 (more dots)
        SPECK_LIGHT_ALPHA = 26     # 12 → 26
        SPECK_DARK_ALPHA  = 30     # new (some darker specks)
        SPECK_RADIUS_MIN  = 1      # still tiny
        SPECK_RADIUS_MAX  = 5      # a few slightly bigger pixels

        SPOKE_ALPHA = 12           # darkness of spokes
        SPOKE_THICK = 4            #1..2
        SPOKE_START_SCALE = 0.98   # Start inside the other edge

        diameter = int(self.radius * 2) + 4
        surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        center = pygame.Vector2(diameter // 2, diameter // 2)

        # polygon in local surface space
        poly_pts = [center + p for p in self._local_points]

        # helper: inset polygon
        def inset(points, s: float):
            out = []
            for q in points:
                v = q - center
                out.append(center + v * s)
            return out

        # ---- 1) very light inset bands (alpha-only) ----
        layers = 7
        for i in range(1, layers + 1):
            s = 1.0 - 0.09 * i
            s += random.uniform(-0.008, 0.008)
            inner = inset(poly_pts, s)
            # alternate tiny light/dark; keep ALPHA TINY
            if i % 2:
                col = (128, 128, 128, RING_LIGHT_ALPHA)   # subtle light
            else:
                t = (i - 2)/(layers - 2)
                dr = 0
                dg = 0
                db = 0
                lr = 255
                lg = 255
                lb = 255
                r = int(dr + (lr - dr)*t)
                g = int(dg + (lg - dg)*t)
                b = int(db + (lb - db)*t)
                col = (r,g,b,RING_LIGHT_ALPHA)         # subtle dark
            pygame.draw.polygon(surf, col, inner)
            if i == layers: innermost_pts = inner

        # --- SPOKES from each vertex to the innermost ring ---
        # Map vertex i to its inset counterpart i (inset() preserves ordering)
        for i, outer_pt in enumerate(poly_pts):
            if i % 3:
                continue
            
            start = center + (outer_pt - center) * SPOKE_START_SCALE
            end   = innermost_pts[i]
            pygame.draw.line(surf, (128, 128, 128, RING_LIGHT_ALPHA), start, end, width=SPOKE_THICK)

        # --- Optional spoke highlights ---
        light_dir = pygame.Vector2(1.0, -0.35).normalize()
        for i, outer_pt in enumerate(poly_pts):
            start = center + (outer_pt - center) * SPOKE_START_SCALE
            end   = innermost_pts[i]
            mid = start.lerp(end, 0.5)
            tip = mid + light_dir * 0.6  # small offset toward light
            pygame.draw.line(surf, (255, 255, 255, 12), mid, tip, 1)


        # ---- 2) gentle edge lighting (alpha-only) ----
        light_dir = pygame.Vector2(1.0, -0.35).normalize()
        edge_overlay = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        n = len(poly_pts)
        for i in range(n):
            a = poly_pts[i]
            b = poly_pts[(i + 1) % n]
            edge = (b - a)
            if edge.length_squared() == 0:
                continue
            normal = pygame.Vector2(-edge.y, edge.x).normalize()
            facing = normal.dot(light_dir)  # >0 highlight, <0 shadow

            a_in = center + (a - center) * EDGE_INSET_SCALE
            b_in = center + (b - center) * EDGE_INSET_SCALE

            if facing > 0.12:
                alpha = int(EDGE_HI_MAX_ALPHA * min(1.0, facing))   # very low
                color = (255, 255, 255, alpha)
                pygame.draw.line(edge_overlay, color, a_in, b_in, width=EDGE_THICK)
            elif facing < -0.12:
                alpha = int(26 * min(1.0, -facing))  # very low
                color = (0, 0, 0, alpha)
                pygame.draw.line(edge_overlay, color, a_in, b_in, width=EDGE_THICK)

        surf.blit(edge_overlay, (0, 0))

        # ---- 3) faint speckles (alpha-only) ----
        mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), poly_pts)

        speck_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        specks = int(1000)#self.radius * SPECK_DENSITY)
        for _ in range(specks):
            x = random.randint(int(center.x - self.radius), int(center.x + self.radius))
            y = random.randint(int(center.y - self.radius), int(center.y + self.radius))
            if 0 <= x < diameter and 0 <= y < diameter and mask.get_at((x, y))[3] > 0:
                if random.random() < 0.45:
                    col = (255, 255, 255, SPECK_LIGHT_ALPHA)
                else:
                    col = (0, 0, 0, SPECK_DARK_ALPHA)
                r = random.randint(SPECK_RADIUS_MIN, SPECK_RADIUS_MAX)
                pygame.draw.circle(speck_surf, col, (x, y), r)

        speck_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(speck_surf, (0, 0))

        # No baked outline here (we’ll draw the outline on screen)
        return surf

        