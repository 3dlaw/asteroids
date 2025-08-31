import pygame

def wrap_offsets(obj_rect: pygame.Rect, cam_rect: pygame.Rect, world_w: int, world_h: int):
    """
    Return the (ox, oy) offsets (subset of {0,±world_w}×{0,±world_h}) that make
    the object's rect overlap the camera rect. Typically 1 (normal), or up to 4.
    """
    offsets = []
    for ox in (0, -world_w, world_w):
        for oy in (0, -world_h, world_h):
            if obj_rect.move(ox, oy).colliderect(cam_rect):
                offsets.append((ox, oy))
    return offsets
