import pygame
from constants import *
from player import Player, Shot
from asteroid import Asteroid
from asteroidfield import AsteroidField

def main():
    pygame.init()
    clock = pygame.time.Clock()
    dt = 0
    score = 0

    updateable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()

    Asteroid.containers = (asteroids, updateable, drawable)
    Player.containers = (updateable, drawable)
    AsteroidField.containers = (updateable)
    Shot.containers = (shots, updateable, drawable)

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
    AsteroidField()

    font = pygame.font.Font(None, 36)

    while True:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            
        text_surface = font.render(f"Score: {score}", True, "white")
        text_rect = text_surface.get_rect()
        text_rect.centerx = SCREEN_WIDTH // 2
        text_rect.centery = 20
        
        screen.fill((0,0,0))

        screen.blit(text_surface, text_rect)
    
        updateable.update(dt)
 
        for sprite in drawable:
            sprite.draw(screen)

        for asteroid in asteroids:
            if player.collision(asteroid):
                screen.fill((0,0,0))
                end_game = font.render(f"Game Over", True, "red")
                restart = font.render(f"Press R to Retry", True, "green")
                game_quit = font.render(f"Press Q to Quit", True, "red")
                screen.blit(end_game, (SCREEN_WIDTH//2 - end_game.get_width()//2, 200))
                screen.blit(restart, (SCREEN_WIDTH//2 - restart.get_width()//2, 300))
                screen.blit(game_quit, (SCREEN_WIDTH//2 - game_quit.get_width()//2, 360))
                pygame.display.flip()
                wait = True
                while wait:
                    for event in pygame.event.get():
                        if event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_q:
                                return
                            if event.key == pygame.K_r:
                                score = 0
                                for g in (updateable, drawable, asteroids, shots):
                                    g.empty()
                                #screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
                                player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
                                AsteroidField()
                                wait = False
                    #clock.tick(60)
            
            for shot in shots:
                if shot.collision(asteroid):
                    shot.kill()
                    if asteroid.radius == ASTEROID_MAX_RADIUS:
                        score += 20
                    elif ASTEROID_MIN_RADIUS < asteroid.radius < ASTEROID_MAX_RADIUS:
                        score += 50
                    elif asteroid.radius <= ASTEROID_MIN_RADIUS:
                        score += 100
                    asteroid.split()
        
        pygame.display.flip()

        dt = clock.tick(60)/1000
        

if __name__ == "__main__":
    main()
