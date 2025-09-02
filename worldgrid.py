import pygame
import math
from typing import Callable
from background import create_space_background

class BackgroundGrid:
    """
    Keeps a nxm grid of background Surfaces and draws whichever tiles
    overlap the camera. With wrapping ON, the pattern repeats infinitely.
    """
    
    def __init__(self, tile_w: int, tile_h: int, make_tile_fn: Callable[[int, int, int], pygame.Surface], nrows: int=3, ncols: int=3,seed_base: int=10000, call_convert: bool=True):
        self.tile_w = tile_w
        self.tile_h = tile_h
        self.nrows = nrows
        self.ncols = ncols

        # Pre-generate tiles with distinct seeds so they aren’t identical
        self.tiles: list[list[pygame.Surface]] = []
        
        for row in range(self.nrows):
            row_tiles = []
            for col in range(self.ncols):
                seed = seed_base + row * self.nrows + col
                surf = make_tile_fn(tile_w, tile_h, seed)
                if call_convert:
                    try:
                        surf = surf.convert() if surf.get_alpha() is None else surf.convert_alpha()
                    except pygame.error:
                        pass
                row_tiles.append(surf)
            self.tiles.append(row_tiles)

        self.world_w = tile_w * self.ncols
        self.world_h = tile_h * self.nrows

    def draw(self, screen: pygame.Surface, camera_rect: pygame.Rect, wrap: bool = True):
        tw, th = self.tile_w, self.tile_h
        view_w, view_h = camera_rect.w, camera_rect.h

        #screen-space origin for first tile
        x0 = -(camera_rect.left % tw)
        y0 = -(camera_rect.top % th)

        # Which tile indices does the camera cover?
        start_col = camera_rect.left // tw
        start_row = camera_rect.top  // th

        need_cols = (view_w // tw) + 2
        need_rows = (view_h // th) + 2

        for row in range(need_rows):
            world_row = start_row + row
            if wrap:
                trow = world_row % self.nrows
            else:
                if not (0 <= world_row < self.nrows):
                    continue
                trow = world_row
            
            screen_y = y0 + row * th

            for col in range(need_cols):
                world_col = start_col + col
                if wrap:
                    tcol = world_col % self.ncols
                else:
                    if not (0 <= world_col < self.ncols):
                        continue
                    tcol = world_col
                
                screen_x = x0 + col * tw
                tile = self.tiles[trow][tcol]
                screen.blit(tile, (screen_x, screen_y))
'''
        above is a cleaner way of doing below which works better with the new depth added to the background.
        
        #how many tiles needed to cover viewport? 
        need_cols = 1 + math.ceil((camera_rect.right - (start_col * tw)) / tw)
        need_rows = 1 + math.ceil((camera_rect.bottom - (start_row * th)) / th)

        if not wrap:
            need_cols = max(1, min(need_cols, self.ncols - start_col))
            need_rows = max(1, min(need_rows, self.nrows - start_row))

        # Draw the tiles needed to cover the viewport
        for dj in range(need_rows):
            for di in range(need_cols):
                world_col = start_col + di
                world_row = start_row + dj

                if wrap:
                    ti = world_col % self.ncols
                    tj = world_row % self.nrows
                    tile = self.tiles[tj][ti]
                else:
                    if not (0 <= world_col < self.ncols and 0 <= world_row < self.nrows):
                        continue
                    tile = self.tiles[world_row][world_col]

                world_x = world_col * tw
                world_y = world_row * th

                # Position relative to camera
                blit_x = world_x - camera_rect.left
                blit_y = world_y - camera_rect.top
                screen.blit(tile, (blit_x, blit_y))

'''

def make_tile(width, height, seed):
    surf = pygame.Surface((width, height), pygame.SRCALPHA)
    return surf.convert_alpha()
    #return create_space_background(width, height, seed=seed)
