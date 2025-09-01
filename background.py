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

def create_space_background(width, height, *, darker=True, seed=None, planets=True, planet_prob=0.2):
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
        rng = random.Random(seed if seed is not None else 0)
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

def _make_planet_overlay(size, rng: random.Random, prob:float = 0.2):
    if rng.random() > prob:
        return None
    
    w, h = size
    surf = pygame.Surface(size, pygame.SRCALPHA)

    rad = rng.randint(int(min(w,h)*0.12), int(min(w,h)*0.22))
    cx = rng.randint(rad+40, w - rad - 40)
    cy = rng.randint(rad+40, h - rad - 40)

    palettes = [
        ((180,  90,  70), (20, 10, 12)),   # warm/red
        (( 60,  90, 170), (10, 14, 26)),   # cool/blue
        ((110, 150, 120), ( 8, 20, 14)),   # greenish
        ((160, 140, 210), (18, 16, 30)),   # purpley
    ]
    inner, outer = rng.choice(palettes)

    body = _radial_grad_circle(size, (cx,cy), rad, inner, outer, alpha=210)
    surf.blit(body, (0,0))

    light = pygame.Vector2(1, -0.4).normalize()
    shadow = pygame.Surface(size, pygame.SRCALPHA)
    for k in range(1, 6):
        a = 18 + 9*k
        pygame.draw.circle(
            shadow, (0,0,0,a),
            (int(cx - light.x*rad*0.3), int(cy -light.y*rad*0.3)),
            int(rad*1.02 + k)
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

