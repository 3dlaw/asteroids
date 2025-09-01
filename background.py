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

def create_space_background(width, height, *, darker=True, seed=None):
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

    return bg
