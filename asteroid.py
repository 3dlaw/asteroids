from pty import spawn
from textwrap import wrap
import pygame
from circleshape import CircleShape
from constants import *
import random
from wrapdraw import wrap_offsets

def get_velocity_color(velocity):
    """
    Get a color based on velocity.length(), creating a gradient from red (fastest) to blue (slowest).
    
    Args:
        velocity: vector
    
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
        return level3    # Level 3 Yellow for medium-fast (200-280)
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
    
    def __init__(self, x, y, radius, fill_alpha=200, *, world_w=None, world_h=None, wrap_world=True):
        super().__init__(x, y, radius)
        self.thick = 2
        self._local_points = self._make_polygon()
        self.angle = random.uniform(0,360)
        self.spin = random.uniform(-60, 60)
        self.fill_alpha = fill_alpha

        self.wrap_world = wrap_world
        self.world_w = world_w
        self.world_h = world_h

        self._detail_surface = self.__build_detail_surface()

    def _make_polygon(self, min_sides = 6, max_sides = 12, angle_jitter = 0.35, radial_jitter = 0.30):
        '''
        creates local points for random polygons

        optional args:
            min_sides - change minimum number of sides from 6
            max_sides - change maximum number of sides from 12
            angle_jitter - step angle variance
            angle_radial - vertex position variance

        returns local points of polygon
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


    def draw(self, screen, cam_rect):
        # Use velocity-based coloring
        velocity_color = get_velocity_color(self.velocity)
        r = self.radius
        bounding_rect = pygame.Rect(self.position.x - r, self.position.y - r, 2*r, 2*r)

        union_rect = None

        for ox, oy in wrap_offsets(bounding_rect, cam_rect, self.world_w, self.world_h):
            pts_world = self.asteroid_shape()
            pts_screen = [(pt.x + ox - cam_rect.left, pt.y + oy - cam_rect.top) for pt in pts_world]
            poly_rect = pygame.draw.polygon(screen, (*velocity_color, self.fill_alpha), pts_screen)

            overlay = pygame.transform.rotate(self._detail_surface, self.angle)
            center_screen = (self.position.x + ox - cam_rect.left, self.position.y + oy - cam_rect.top)
            overlay_rect = overlay.get_rect(center=center_screen)
            screen.blit(overlay, overlay_rect.topleft)

            union_rect = poly_rect if union_rect is None else union_rect.union(poly_rect)
            union_rect = union_rect.union(overlay_rect)

        return union_rect

    def update(self, dt):
        self.position += self.velocity * dt
        self.angle += self.spin * dt
        
        if self.wrap_world and self.world_w and self.world_h:
            self.position.x %= self.world_w
            self.position.y %= self.world_h
        elif self.world_w and self.world_h:
            buffer = 120
            if (self.position.x < -buffer or
                self.position.x > self.world_w + buffer or
                self.position.y < -buffer or
                self.position.y > self.world_h + buffer):
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
            def spawn_child(vel, alpha, speed_min, speed_max):
                a = Asteroid(self.position.x, self.position.y, new_radius, alpha, world_w=self.world_w, world_h=self.world_h, wrap_world=self.wrap_world)
                a.velocity = vel * random.uniform(speed_min, speed_max)
                return a
            if new_radius > ASTEROID_MIN_RADIUS:
                spawn_child(velocity1, 128, 1.2, 1.8)
                spawn_child(velocity2, 128, 1.2, 1.8)
     
            else:
                spawn_child(velocity1, 64, 2.0, 2.5)
                spawn_child(velocity2, 64, 2.0, 2.5)

    def __build_detail_surface(self):
        """
        Returns a transparent detail OVERLAY
        - rings, speckles, craters, spokes as an attempt at depth lol 
        """
        #constants to make tweaking easier
        RING_LIGHT_ALPHA = 14      # higher = brighter
        RING_DARK_ALPHA  = 8       # higher = darker

        EDGE_HI_MAX_ALPHA = 50     # attempt at highlights
        EDGE_SH_MAX_ALPHA = 40     # attempt at shadows
        EDGE_INSET_SCALE  = 0.96   # offset 
        EDGE_THICK        = 3      # thickness

        SPECK_DENSITY     = 1.2    # more dots
        SPECK_LIGHT_ALPHA = 26     # higher = brighter
        SPECK_DARK_ALPHA  = 30     # higher = darker 
        SPECK_RADIUS_MIN  = 1      # tiny
        SPECK_RADIUS_MAX  = 5      # a few slightly bigger pixels

        SPOKE_ALPHA = 12           # darkness of spokes
        SPOKE_THICK = 4            # thickness
        SPOKE_START_SCALE = 0.98   # Start inside the other edge

        CRATER_DENSITY    = 0.05   # number of craters ≈ radius * this
        CRATER_MIN_SCALE  = 0.08   # crater min radius ≈ self.radius * this
        CRATER_MAX_SCALE  = 0.40   # crater max radius ≈ self.radius * this
        CRATER_EDGE_INSET = 0.88   # keep centers this fraction inside to avoid edges
        CRATER_TRIES      = 20     # attempts to find an in-polygon point
        # opacities (keep subtle)
        CRATER_BASE_ALPHA   = 30   
        CRATER_SHADOW_ALPHA = 35
        CRATER_DARKRIM_ALPHA= 50
        CRATER_LIGHtrim_ALPHA= 40

        diameter = int(self.radius * 2) + 4
        surf = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        center = pygame.Vector2(diameter // 2, diameter // 2)

        # polygon in local surface space
        poly_pts = [center + p for p in self._local_points]

        mask = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        pygame.draw.polygon(mask, (255, 255, 255, 255), poly_pts)

        # helper: inset polygon
        def inset(points, s: float):
            out = []
            for q in points:
                v = q - center
                out.append(center + v * s)
            return out

        # number of rings/bands
        layers = 7
        for i in range(1, layers + 1):
            s = 1.0 - 0.09 * i
            s += random.uniform(-0.008, 0.008)
            inner = inset(poly_pts, s)
            # alternate tiny light/dark; keep ALPHA TINY
            if i % 2:
                col = (128, 128, 128, RING_LIGHT_ALPHA)
            #my attempt at lerping from dark to light for smooth transition in middle   
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
                col = (r,g,b,RING_LIGHT_ALPHA)         
            pygame.draw.polygon(surf, col, inner)
            if i == layers: innermost_pts = inner

        # "Spokes" = lines going from outside to inner ring on the corners
        # Map vertex i to its inset counterpart i
        for i, outer_pt in enumerate(poly_pts):
            #skip some corners bc too much looked goofy
            if i % 3:
                continue
            
            start = center + (outer_pt - center) * SPOKE_START_SCALE
            end   = innermost_pts[i]
            pygame.draw.line(surf, (128, 128, 128 , RING_LIGHT_ALPHA), start, end, width=SPOKE_THICK)

        # Spoke highlights? honestly have no idea chatGPT suggest it though. 
        light_dir = pygame.Vector2(1.0, -0.35).normalize()
        for i, outer_pt in enumerate(poly_pts):
            start = center + (outer_pt - center) * SPOKE_START_SCALE
            end   = innermost_pts[i]
            mid = start.lerp(end, 0.5)
            tip = mid + light_dir * 0.6  
            pygame.draw.line(surf, (255, 255, 255, 12), mid, tip, 1)


        #again, not sure what this does. I don't see how shadow does anything when I don't have a light source? 
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
            facing = normal.dot(light_dir)

            a_in = center + (a - center) * EDGE_INSET_SCALE
            b_in = center + (b - center) * EDGE_INSET_SCALE

            if facing > 0.12:
                alpha = int(EDGE_HI_MAX_ALPHA * min(1.0, facing))   
                color = (255, 255, 255, alpha)
                pygame.draw.line(edge_overlay, color, a_in, b_in, width=EDGE_THICK)
            elif facing < -0.12:
                alpha = int(26 * min(1.0, -facing))  
                color = (0, 0, 0, alpha)
                pygame.draw.line(edge_overlay, color, a_in, b_in, width=EDGE_THICK)

        surf.blit(edge_overlay, (0, 0))

        #craters take two
        crater_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        light_dir = pygame.Vector2(1.0, -0.35).normalize()

        crater_count = max(1, int(self.radius * CRATER_DENSITY))
        cr_min = max(2, int(self.radius * CRATER_MIN_SCALE))
        cr_max = max(cr_min + 1, int(self.radius * CRATER_MAX_SCALE))

        #makes an irregular cicle shape so craters don't look too much lik bubbles lol 
        def irregular_circle_points(center, radius, jaggedness=0.35, points=10):
            pts = []
            for i in range(points):
                angle = (i / points) * 360
                r = radius * (1 + random.uniform(-jaggedness, jaggedness))
                pt = pygame.Vector2(0, -r).rotate(angle) + center
                pts.append(pt)
            return pts

        for _ in range(crater_count):
            # pick a center inside the polygon, away from edges
            pos = None
            for _try in range(CRATER_TRIES):
                x = random.randint(int(center.x - self.radius * CRATER_EDGE_INSET),
                                int(center.x + self.radius * CRATER_EDGE_INSET))
                y = random.randint(int(center.y - self.radius * CRATER_EDGE_INSET),
                                int(center.y + self.radius * CRATER_EDGE_INSET))
                if 0 <= x < crater_surf.get_width() and 0 <= y < crater_surf.get_height():
                    if mask.get_at((x, y))[3] > 0:  # inside polygon
                        pos = pygame.Vector2(x, y)
                        break
            if pos is None:
                continue

            r = random.randint(cr_min, cr_max)

            # another chatgpt sugggestion for getting some shadow 
            # base depression (very soft)
            pygame.draw.polygon(crater_surf, (0, 0, 0, CRATER_BASE_ALPHA), irregular_circle_points(pos, int(r * 0.9)))

            # inner shadow (away from light)
            shadow_pos = pos - light_dir * (r * 0.15)
            pygame.draw.polygon(crater_surf, (0, 0, 0, CRATER_SHADOW_ALPHA), irregular_circle_points(shadow_pos, int(r * 0.6)))

            # dark rim on far side
            rim_back = pos - light_dir * (r * 0.25)
            pygame.draw.polygon(
                crater_surf, (0, 0, 0, CRATER_DARKRIM_ALPHA), irregular_circle_points(rim_back, r), width=max(1, int(r * 0.25))
            )

            # bright rim on near side
            rim_front = pos + light_dir * (r * 0.20)
            pygame.draw.circle(
                crater_surf, (255, 255, 255, CRATER_LIGHtrim_ALPHA), rim_front, int(r * 0.85),
                width=max(1, int(r * 0.18))
            )

        # clip craters to polygon and bake into overlay
        crater_surf.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MIN)
        surf.blit(crater_surf, (0, 0))

        speck_surf = pygame.Surface(surf.get_size(), pygame.SRCALPHA)
        specks = int(1000)
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

        return surf

        