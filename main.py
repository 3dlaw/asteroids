import pygame
from constants import *
from player import Player, Shot
from asteroid import Asteroid, get_velocity_color
from asteroidfield import AsteroidField
from menus import *
from stats import GameStats

def main():
    game_stats = GameStats()
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
    
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 100)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    begin_wait = True
    
    while True:

        while begin_wait:
            if not draw_main_menu(screen, font, big_font):
                return
            score = 0
            player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
            AsteroidField()
            begin_wait = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_stats.increment_stat("shots_fired")
            
        screen.fill((0,0,0))
        draw_hud(screen, font, score)
    
        updateable.update(dt)
 
        for sprite in drawable:
            sprite.draw(screen)

        for asteroid in asteroids:
            if player.collision(asteroid):
                action = draw_game_over_menu(screen, font, big_font, score)
                if action == 'quit':
                    return
                elif action == 'retry':
                    score = 0
                    for g in (updateable, drawable, asteroids, shots):
                        g.empty()
                    player = Player(SCREEN_WIDTH/2, SCREEN_HEIGHT/2)
                    AsteroidField()
                elif action == 'main_menu':
                    for g in (updateable, drawable, asteroids, shots):
                        g.empty()
                    begin_wait = True
                elif action == 'stats':
                    for g in (updateable, drawable, asteroids, shots):
                        g.empty()
                    stat_action = draw_stats_menu(screen, font, big_font, game_stats)
                    if stat_action == 'quit':
                        return
                    if stat_action == 'main_menu':
                        for g in (updateable, drawable, asteroids, shots):
                            g.empty()
                        begin_wait = True
           
            for shot in shots:
                if shot.collision(asteroid):
                    shot.kill()
                    asteroid_color = get_velocity_color(asteroid.velocity)
                    if asteroid_color == (255, 255, 255):
                        game_stats.increment_stat("White_asteroids_destroyed")
                        score += 50
                    elif asteroid_color == (0, 0, 255):
                        game_stats.increment_stat("Blue_asteroids_destroyed")
                        score += 100
                    elif asteroid_color == (0, 255, 0):
                        game_stats.increment_stat("Green_asteroids_destroyed")
                        score += 200
                    elif asteroid_color == (255, 255, 0):
                        game_stats.increment_stat("Yellow_asteroids_destroyed")
                        score += 250
                    elif asteroid_color == (255, 128, 0):
                        game_stats.increment_stat("Orange_asteroids_destroyed")
                        score += 350
                    elif asteroid_color == (255, 0, 0):
                        game_stats.increment_stat("Red_asteroids_destroyed")
                        score += 500
                    #score += asteroid.thick + int(asteroid.velocity.length())
                    asteroid.split()
        
        pygame.display.flip()

        dt = clock.tick(60)/1000

if __name__ == "__main__":
    main()
