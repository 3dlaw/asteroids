import pygame

def wrap_offsets(obj_rect: pygame.Rect, cam_rect: pygame.Rect, world_w: int, world_h: int):
    """
    Return the (ox, oy) offsets that make an object's rect overlap the camera rect. 
    basically handling the seams between tiles
    """
    offsets = []
    for ox in (0, -world_w, world_w):
        for oy in (0, -world_h, world_h):
            if obj_rect.move(ox, oy).colliderect(cam_rect):
                offsets.append((ox, oy))
    return offsets

def screen_positions_wrapped(world_pos: pygame.Vector2, cam_rect: pygame.Rect, world_w: int, world_h: int, radius: int):
    sx = (world_pos.x - cam_rect.left) % world_w
    sy = (world_pos.y - cam_rect.top) % world_h
    base = pygame.Vector2(sx, sy)

    out = [base]
    if base.x < radius:
        out.append(pygame.Vector2(base.x + world_w, base.y))
    if base.x > cam_rect.w - radius:
        out.append(pygame.Vector2(base.x-world_w, base.y))

    extra = []
    if base.y < radius:
        extra.append((0, world_h))
    if base.y > cam_rect.h - radius:
        extra.append((0, -world_h))

    if extra:
        current = list(out)
        out.clear()
        for p in current:
            out.append(p)
            for dx, dy in extra:
                out.append(pygame.Vector2(p.x + dx, p.y + dy))

    return out

def is_on_screen_wrapped(world_pos: pygame.Vector2, cam_rect: pygame.Rect, world_w: int, world_h: int, radius: int, buffer: int=0) -> bool:
    view = pygame.Rect(-buffer, -buffer, cam_rect.w + 2*buffer, cam_rect.h + 2*buffer)

    for p in screen_positions_wrapped(world_pos, cam_rect, world_w, world_h, radius):
        if view.collidepoint(p.x, p.y):
            return True
    return False