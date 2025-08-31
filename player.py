import pygame
from circleshape import CircleShape
from constants import *

class Player(CircleShape):
    
    def __init__(self, x, y, muted=False, fill_alpha=200, game_stats=None):
        super().__init__(x, y, PLAYER_RADIUS)
        self.rotation = 0
        self.timer = 0.0
        self.too_many_keys = False
        self.fill_alpha = fill_alpha
        self.muted = muted
        self.game_stats = game_stats

    def triangle(self):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        right = pygame.Vector2(0, 1).rotate(self.rotation + 90) * self.radius / 1.5
        a = self.position + forward * self.radius
        b = self.position - forward * self.radius - right
        c = self.position - forward * self.radius + right
        return [a, b, c]
    
    def draw(self, screen):
        return pygame.draw.polygon(screen, (255, 255, 255, self.fill_alpha), self.triangle())
    
    def rotate(self, dt):
        self.rotation += PLAYER_TURN_SPEED * dt

    def move(self, dt):
        forward = pygame.Vector2(0, 1).rotate(self.rotation)
        self.position += forward * PLAYER_SPEED * dt

    def handle_key_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in [pygame,pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_DOWN, pygame.K_SPACE]:
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

        #wrap around screen
        if self.position.x> SCREEN_WIDTH:
            self.position.x = 0 
        elif self.position.x < 0:
            self.position.x = SCREEN_WIDTH
        elif self.position.y > SCREEN_HEIGHT:
            self.position.y = 0
        elif self.position.y < 0:
            self.position.y = SCREEN_HEIGHT

    def shoot(self):
        shot = Shot(self.position.x, self.position.y, SHOT_RADIUS)
        shot.velocity = pygame.Vector2(0, 1).rotate(self.rotation) * PLAYER_SHOOT_SPEED
        if not self.muted:
            shot_sound = pygame.mixer.Sound("assets/shot_sound.wav")
            shot_sound.set_volume(0.3)
            shot_sound.play()

        if self.game_stats:
            self.game_stats.increment_stat("shots_fired")


class Shot(CircleShape):
    def __init__(self, x, y, radius):
        super().__init__(x, y, SHOT_RADIUS)

    def draw(self, screen):
        pygame.draw.circle(screen, "white", self.position, self.radius, 2)

    def update(self, dt):
        self.position += self.velocity * dt
        buffer = 60
        
        if self.position.x> SCREEN_WIDTH + buffer:
            self.kill() 
        elif self.position.x < 0 - buffer:
            self.kill()
        elif self.position.y > SCREEN_HEIGHT + buffer:
            self.kill()
        elif self.position.y < 0 - buffer:
            self.kill()
        