# background_grid.py
import pygame
from typing import Callable

class BackgroundGrid:
    """
    Keeps a 3x3 grid of background Surfaces and draws whichever tiles
    overlap the camera. With wrapping ON, the 3x3 pattern repeats infinitely.
    """
    def __init__(self, tile_w: int, tile_h: int, make_tile_fn: Callable[[int, int, int], pygame.Surface]):
        self.tile_w = tile_w
        self.tile_h = tile_h

        # Pre-generate nine tiles with distinct seeds so they aren’t identical
        self.tiles = []
        seed_base = 10_000
        for j in range(3):
            row = []
            for i in range(3):
                seed = seed_base + j * 3 + i
                row.append(make_tile_fn(tile_w, tile_h, seed))
            self.tiles.append(row)

        # World size if you want to clamp (exactly 3x3 tiles)
        self.world_w = tile_w * 3
        self.world_h = tile_h * 3

    def draw(self, screen: pygame.Surface, camera_rect: pygame.Rect, wrap: bool = True):
        tw, th = self.tile_w, self.tile_h

        # Which tile indices does the camera cover?
        start_i = camera_rect.left // tw
        start_j = camera_rect.top  // th

        # Draw up to 4 tiles to cover the viewport
        for dj in range(2):
            for di in range(2):
                world_i = start_i + di
                world_j = start_j + dj

                if wrap:
                    ti = world_i % 3
                    tj = world_j % 3
                    tile = self.tiles[tj][ti]
                else:
                    # Only draw if inside the fixed 3x3 bounds
                    if not (0 <= world_i < 3 and 0 <= world_j < 3):
                        continue
                    tile = self.tiles[world_j][world_i]

                world_x = world_i * tw
                world_y = world_j * th

                # Position relative to camera
                blit_x = world_x - camera_rect.left
                blit_y = world_y - camera_rect.top
                screen.blit(tile, (blit_x, blit_y))
