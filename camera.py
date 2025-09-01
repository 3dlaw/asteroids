# camera.py
import pygame

class Camera:
    def __init__(self, view_w: int, view_h: int, world_w: int, world_h: int, wrap: bool = True):
        self.rect = pygame.Rect(0, 0, view_w, view_h)
        self.world_w = world_w
        self.world_h = world_h
        self.wrap = wrap

    # defines where the player starts to push the camera/view
    def set_deadzone(self, margin_x: int, margin_y: int):
        self.margin_x, self.margin_y = margin_x, margin_y

    #defines the camera movements
    def move(self, dx: float, dy: float):
        self.rect.x += dx
        self.rect.y += dy
        self._post_update()

    #where to center camera
    def center_on(self, x: float, y: float):
        self.rect.center = (x, y)
        self._post_update()

    #calculates coords for the wrapping accross edge tiles
    def _nearest_on_torus(self, coord: float, ref: float, size: float) -> float:
        # map coord to torus 
        d = coord - ref
        if d > size * 0.5: coord -= size
        if d < -size * 0.5: coord += size
        return coord

    def push_follow(self, target_x: float, target_y: float):
        '''
        Only moves the camera when close to margin
        wraps on torus
        '''
        tx, ty = target_x, target_y
        if self.wrap:
            cx, cy = self.rect.centerx, self.rect.centery
            tx = self._nearest_on_torus(tx, cx, self.world_w)
            ty = self._nearest_on_torus(ty, cy, self.world_h)

        left = self.rect.left + self.margin_x
        right = self.rect.right - self.margin_x
        top = self.rect.top + self.margin_y
        bottom = self.rect.bottom - self.margin_y

        dx = 0
        dy = 0

        if tx < left: dx = tx - left
        elif tx > right: dx = tx -right

        if ty < top: dy = ty - top
        elif ty > bottom: dy = ty - bottom

        if dx or dy:
            self.move(dx, dy)

    def _post_update(self):
        if self.wrap:
            # Keep camera coords in [0, world) so tile math stays simple
            self.rect.x %= self.world_w
            self.rect.y %= self.world_h
        else:
            # Clamp to the 3x3 edges
            self.rect.x = max(0, min(self.rect.x, self.world_w - self.rect.w))
            self.rect.y = max(0, min(self.rect.y, self.world_h - self.rect.h))
