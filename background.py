import pygame, random

# very dark blue-black (looks deeper than pure black)
SPACE = (5, 7, 12)

def _make_starfield(size, n_small=450, n_med=110, n_big=28, seed=None):
    '''
    Creates surface of randomly placed stars
    Args:
        size - surface size
        n_small - number of small stars
        n_med - number of medium stars
        n_big - number of big stars
        seed - if want to reproduce same output

    returns surface of star placements
    '''
    if seed is not None:
        rnd = random.Random(seed)
        randrange = rnd.randrange
    else:
        randrange = random.randrange

    w, h = size
    surf = pygame.Surface(size).convert()
    surf.fill((0, 0, 0)) 

    # small stars - single pixel
    for _ in range(n_small):
        x, y = randrange(w), randrange(h)
        surf.set_at((x, y), (60, 70, 95))

    # medium stars - 1 pixel radius
    for _ in range(n_med):
        x, y = randrange(w), randrange(h)
        pygame.draw.circle(surf, (120, 135, 170), (x, y), 1)

    # big stars + faint halo - 2 pixel radius with 4 pixel radius halo
    for _ in range(n_big):
        x, y = randrange(w), randrange(h)
        pygame.draw.circle(surf, (200, 220, 255), (x, y), 2)
        pygame.draw.circle(surf, (40, 60, 120), (x, y), 4, width=1)

    return surf

def _make_nebula(size, blobs=10, hue=(18, 26, 48), alpha=10, seed=None):
    '''
    Add Layers to create nebula
    Args:
        size - surface size
        blobs - number of "blobs" aka clouds
        hue - base color
        alpha - transparency
        seed - if want repeatable output
    returns surface with the nebulas
    '''
    if seed is not None:
        rnd = random.Random(seed)
        randrange = rnd.randrange
        randint = rnd.randint
    else:
        randrange = random.randrange
        randint = random.randint

    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)

    #overlay the clouds
    for _ in range(blobs):
        #cloud radius
        r = randint(140, 260)
        #cloud position 
        x, y = randrange(-r, w + r), randrange(-r, h + r)

        # layered circles for a soft cloud. Concentric circles for gradient
        for k in range(6, 0, -1):
            a = max(1, alpha - 2 * (6 - k))
            pygame.draw.circle(surf, (*hue, a), (x, y), int(r * k / 6))
    return surf

def create_space_background(width, height, *, darker=True, seed=None, planets=True, planet_prob=0.40):
    """
    Returns the combined surfaces
    Args:
        width, height - screen dims
        darker - makes it a bit darker lol
        seed - allows repeatability
    """
    # base canvas
    bg = pygame.Surface((width, height)).convert()
    bg.fill((3, 4, 8) if darker else SPACE)

    # subtle nebula under stars
    neb = _make_nebula((width, height), blobs=12, hue=(18, 26, 48), alpha=10, seed=seed)
    bg.blit(neb, (0, 0))

    # star layer (added so stars "glow" over dark base without washing sprites)
    stars = _make_starfield((width, height), seed=seed)
    bg.blit(stars, (0, 0), special_flags=pygame.BLEND_ADD)

    if planets:
        rng = random.Random(seed) if seed is not None else random.Random()
        overlay = _make_planet_overlay((width, height), rng, prob=planet_prob)
        if overlay is not None:
            bg.blit(overlay, (0,0))

    return bg

def _radial_grad_circle(size, center, radius, inner_col, outer_col, alpha=200):
    surf = pygame.Surface(size, pygame.SRCALPHA)
    steps = max(24, int(radius))
    for i in range(steps, 0, -1):
        t = i / steps
        r = int(inner_col[0]*t + outer_col[0]*(1-t))
        g = int(inner_col[1]*t + outer_col[1]*(1-t))
        b = int(inner_col[2]*t + outer_col[2]*(1-t))
        a = int(alpha*t)
        pygame.draw.circle(surf, (r,g,b,a), center, int(radius*t))
    return surf

def _make_planet_overlay(size, rng: random.Random, prob:float = 0.35, *, ref_dim=None):
    if rng.random() > prob:
        return None
    
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)

    min_dim = ref_dim if ref_dim is not None else min(w, h)

    rad = rng.randint(int(min_dim*0.02), int(min_dim*0.05))

    margin = max(40, int(rad * 0.8))
    cx = rng.randint(rad+margin, w - rad - margin)
    cy = rng.randint(rad+margin, h - rad - margin)

    palettes = [
        ((180,  90,  70), (20, 10, 12)),   # warm/red
        (( 60,  90, 170), (10, 14, 26)),   # cool/blue
        ((110, 150, 120), ( 8, 20, 14)),   # greenish
        ((160, 140, 210), (18, 16, 30)),   # purpley
    ]
    inner, outer = rng.choice(palettes)

    #Planet Core
    pygame.draw.circle(surf, (*inner, 255), (cx,cy), rad)

    #darken around edge
    ring_thickness = max(2, int(rad * 0.25))
    for i in range(ring_thickness):
        t = i / (ring_thickness - 1) if ring_thickness > 1 else 1.0
        shade = 0.88 - 0.18*t
        col = (int(inner[0] * shade), int(inner[1] * shade), int(inner[2] * shade))
        alpha = int(100 + 120*t)
        pygame.draw.circle(surf, (*col,alpha), (cx,cy), rad-i)

    #terminator (light direction)
    light = pygame.Vector2(1, -0.35).normalize()
    shadow = pygame.Surface(size, pygame.SRCALPHA)

    for k in range(1, 4):
        a = 14 + 10*k
        pygame.draw.circle(
            shadow, (0,0,0,a),
            (int(cx - light.x * rad * 0.3), int(cy - light.y *rad * 0.3)),
            int(rad * (1.02 + 0.2 * k))
        )
        surf.blit(shadow, (0,0), special_flags=pygame.BLEND_RGB_SUB)

    if rng.random() < 0.35:
        ring = pygame.Surface(size, pygame.SRCALPHA)
        rx, ry = rad*1.5, rad*0.5
        angle = rng.uniform(-20,20)
        rect = pygame.Rect(0, 0,int(rx*2), int(ry*2)); rect.center = (cx, cy+rng.randint(-6,6))
        ellipse = pygame.Surface(rect.size, pygame.SRCALPHA)
        pygame.draw.ellipse(ellipse, (200,200,230,70), ellipse.get_rect(), width=6)
        ellipse = pygame.transform.rotate(ellipse, angle)
        ring.blit(ellipse, ellipse.get_rect(center=(cx,cy)))
        surf.blit(ring, (0,0))

    return surf

def _tile_blit(screen, surf, offx, offy, blend=None):
    sw, sh = surf.get_size()
    x0 = -(offx % sw)
    y0 = -(offy % sh)
    flag = 0 if blend is None else blend

    screen.blit(surf, (x0, y0), special_flags=flag)
    screen.blit(surf, (x0 + sw, y0), special_flags=flag)
    screen.blit(surf, (x0, y0 + sh), special_flags=flag)
    screen.blit(surf, (x0 + sw, y0 + sh), special_flags=flag)

class ParallaxLayer:
    def __init__(self, surface: pygame.Surface, factor: float, blend=None, drift=(0.0,0.0)):
        self.surf = surface.convert_alpha()
        self.factor = factor                # 0.0 = infinitely far, 1.0 = moves with camera
        self.blend = blend                  
        self.driftx, self.drifty = drift    #pixels/sec
        self._ox = 0.0
        self._oy = 0.0

    def update(self, dt):
        self._ox += self.driftx * dt
        self._oy += self.drifty * dt

    def draw(self, screen, base_x, base_y):
        offx = int(self._ox + base_x * self.factor)
        offy = int(self._oy + base_y * self.factor)
        _tile_blit(screen, self.surf, offx, offy, blend=(self.blend or 0))

class ParallaxBackground:
    def __init__(self, w, h, *, seed=None, make_starfield=None, make_nebula=None, make_planets=None):
        self.w, self.h = w, h
        self.rng = random.Random(seed) if seed is not None else random.Random()

        self._make_starfield = make_starfield
        self._make_nebula = make_nebula
        self._make_planets = make_planets

        self._accum_x = 0.0
        self._accum_y = 0.0
        self._prev_cam_xy = None

        TW, TH = w*2, h*2
        screen_ref = min(w, h)

        neb_surf = self._make_nebula((TW, TH), blobs=14, hue=(18, 26, 48), alpha=10, seed=self.rng.randrange(10**9))

        stars_small = self._make_starfield((TW, TH), n_small=600, n_med=0, n_big=0, seed=self.rng.randrange(10**9))

        stars_med = self._make_starfield((TW, TH), n_small=0, n_med=180, n_big=0, seed=self.rng.randrange(10**9))

        stars_big = self._make_starfield((TW, TH), n_small=0, n_med=0, n_big=38, seed=self.rng.randrange(10**9))

        planets = self._make_planets((TW, TH), self.rng, prob=1, ref_dim=screen_ref) or pygame.Surface((TW,TH), pygame.SRCALPHA)

        neb_surf = neb_surf.convert_alpha()
        stars_small = stars_small.convert_alpha()
        stars_med = stars_med.convert_alpha()
        stars_big = stars_big.convert_alpha()
        planets = planets.convert_alpha()

        self.layers = [
            ParallaxLayer(neb_surf, factor=0.08, blend=None, drift=(2.0, 4.0)),
            ParallaxLayer(stars_small, factor=0.12, blend=pygame.BLEND_ADD, drift=(6.0, 8.0)),
            ParallaxLayer(stars_med, factor=0.18, blend=pygame.BLEND_ADD, drift=(9.0, 11.0)),
            ParallaxLayer(stars_big, factor=0.22, blend=pygame.BLEND_ADD, drift=(11.0, 13.0)),
            ParallaxLayer(planets, factor=0.42, blend=None, drift=(3.0, 4.0)),
        ]

    def update(self, dt):
        for L in self.layers:
            L.update(dt)

    def draw(self, screen, cam_rect):
        bx, by = self._accum_x, self._accum_y
        for L in self.layers:
            L.draw(screen, bx, by)

    def draw_far(self, screen, cam_rect):
        bx, by = self._accum_x, self._accum_y
        for L in self.layers:
            if (L.blend or 0) == 0:
                L.draw(screen, bx, by)

    def draw_near(self, screen, cam_rect):
        bx, by = self._accum_x, self._accum_y
        for L in self.layers:
            if (L.blend or 0) != 0:
                L.draw(screen, bx, by)

    def _delta_wrap(self, curr, prev, period):
        if not period or period <= 0: return curr - prev
        half = period * 0.5
        return ((curr - prev + half) % period) - half
    
    def begin_frame(self, cam_rect, wrap_w=None, wrap_h=None):

        cx, cy = float(cam_rect.x), float(cam_rect.y)
        if self._prev_cam_xy is None:
            self._prev_cam_xy = (cx, cy)
            return
        
        px, py = self._prev_cam_xy
        dx = self._delta_wrap(cx, px, float(wrap_w) if wrap_w else None)
        dy = self._delta_wrap(cy, py, float(wrap_h) if wrap_h else None)
        self._accum_x += dx
        self._accum_y += dy
        self._prev_cam_xy = (cx, cy)

