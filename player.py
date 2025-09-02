from textwrap import wrap
import pygame
from circleshape import CircleShape
from constants import *
from wrapdraw import *

class Player(CircleShape):
    
    def __init__(self, x, y, *, world_w, world_h, wrap_world=True, muted=False, fill_alpha=200, game_stats=None, cam=None):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.timer = 0.0
        self.too_many_keys = False
        self.fill_alpha = fill_alpha
        self.muted = muted
        self.game_stats = game_stats

        self.world_w = world_w
        self.world_h = world_h
        self.wrap_world = wrap_world
        self.cam = cam

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def draw(self, screen, cam_rect):
        r = self.radius
        bounding_rect = pygame.Rect(self.position.x - r, self.position.y - r, 2*r, 2*r)

        union_rect = None
        for ox, oy in wrap_offsets(bounding_rect, cam_rect, self.world_w, self.world_h):
            pts = [self.position + pygame.Vector2(p).rotate(0) for p in ()]
            pts = self.triangle()
            pts = [(p.x + ox - cam_rect.left, p.y + oy - cam_rect.top) for p in pts]
            last_rect = pygame.draw.polygon(screen, (255, 255, 255, self.fill_alpha), pts)
            union_rect = last_rect if union_rect is None else union_rect.union(last_rect)

        #cam_pts = [ (p.x - cam_rect.left, p.y -cam_rect.top) for p in self.triangle()]
        return union_rect
    
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt

    def handle_key_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_SPACE]:
                self.input_queue.append(event.key)
        elif event.type == pygame.KEYUP:
            if event.key in self.input_queue:
                self.input_queue.remove(event.key)

    def update(self, dt):
        keys = pygame.key.get_pressed()
        #self.shot_release = True
        movement_count = sum([
            keys[pygame.K_LEFT],
            keys[pygame.K_RIGHT],
            keys[pygame.K_UP],
            keys[pygame.K_DOWN]
        ])

        if keys[pygame.K_LSHIFT]:
            movement_count += 1

        self.too_many_keys = (movement_count > 3)

        if keys[pygame.K_LEFT]:
            self.rotate(-dt)
        if keys[pygame.K_RIGHT]:
            self.rotate(dt)
        if keys[pygame.K_UP]:
            self.move(dt)
        if keys[pygame.K_DOWN]:
            self.move(-dt)

        
        if keys[pygame.K_LSHIFT] and not self.too_many_keys:
            if self.timer <= 0.0: # and self.shot_release:
                self.shoot()
                self.timer = PLAYER_COOL_DOWN
        
        self.timer -= dt

        if self.wrap_world:
            self.position.x %= self.world_w
            self.position.y %= self.world_h
        else:
            self.position.x = max(0, min(self.position.x, self.world_w))
            self.position.y = max(0, min(self.position.y, self.world_h))

        '''
        #wrap around screen
        if self.position.x> SCREEN_WIDTH:
            self.position.x = 0 
        elif self.position.x < 0:
            self.position.x = SCREEN_WIDTH
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = SCREEN_HEIGHT
        '''

    def shoot(self):
        shot = Shot(self.position.x, self.position.y, SHOT_RADIUS, cam = self.cam, world_w = self.world_w, world_h=self.world_h)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
        if not self.muted:
            shot_sound = pygame.mixer.Sound("assets/shot_sound.wav")
            shot_sound.set_volume(0.1)
            shot_sound.play()

        if self.game_stats:
            self.game_stats.increment_stat("shots_fired")


class Shot(CircleShape):
    def __init__(self, x, y, radius, *, cam=None, world_w=None, world_h=None):
        super().__init__(x, y, SHOT_RADIUS)
        self.cam = cam
        self.world_w = world_w
        self.world_h = world_h
        self.age = 0.0

    def _is_visible(self, buffer: int = 60) -> bool:
        if self.cam is None or self.world_w is None or self.world_h is None:
            r = self.radius
            return (0 - buffer <= self.position.x - r <= SCREEN_WIDTH + buffer and
                    0 - buffer <= self.position.y - r <= SCREEN_HEIGHT + buffer)

        cam_rect = self.cam.rect.inflate(buffer*2, buffer*2)
        r = self.radius
        bounding_rect = pygame.Rect(self.position.x - r, self.position.y - r, 2*r, 2*r)
        return len(wrap_offsets(bounding_rect, cam_rect, self.world_w, self.world_h)) > 0

    def draw(self, screen, cam_rect):
        if self.cam and self.world_w and self.world_h:
            for p in screen_positions_wrapped(self.position, cam_rect, self.world_w, self.world_h, self.radius + 2):
                pygame.draw.circle(screen, "white", (int(p.x), int(p.y)), self.radius, 2)
        else:
            cam_pts = (self.position.x - cam_rect.left, self.position.y - cam_rect.top)
            pygame.draw.circle(screen, "white", cam_pts, self.radius, 2)

    def update(self, dt):
        self.age += dt
        self.position += self.velocity * dt
        buffer = 90
        if self.cam and self.world_w and self.world_h:
            if self.age > 0.05:
                if not is_on_screen_wrapped(self.position, self.cam.rect, self.world_w, self.world_h, self.radius, buffer):
                    self.kill()

        else:
        
            if self.position.x > SCREEN_WIDTH + buffer:
                self.kill() 
            elif self.position.x < 0 - buffer:
                self.kill()
            elif self.position.y > SCREEN_HEIGHT + buffer:
                self.kill()
            elif self.position.y < 0 - buffer:
                self.kill()
        