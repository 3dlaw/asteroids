import pygame
from constants import *
from player import Player, Shot
from asteroid import Asteroid, get_velocity_color
from asteroidfield import AsteroidField
from menus import *
from stats import GameStats
from powerups import Objective
import os
from background import create_space_background
from worldgrid import BackgroundGrid
from camera import Camera

def make_tile(width, height, seed):
    return create_space_background(width, height, seed=seed)

def main():
    os.environ["SDL_AUDIODRIVER"] = "pulse"
    os.environ["PULSE_LATENCY_MSEC"] = "200"

    pygame.mixer.pre_init(frequency=44100, size=-16,channels=1,buffer=2048)
    pygame.init()

    game_stats = GameStats()
    clock = pygame.time.Clock()
    dt = 0
    score = 0

    updateable = pygame.sprite.Group()
    drawable = pygame.sprite.Group()
    asteroids = pygame.sprite.Group()
    shots = pygame.sprite.Group()
    objectives = pygame.sprite.Group()

    Asteroid.containers = (asteroids, updateable, drawable)
    Player.containers = (updateable, drawable)
    AsteroidField.containers = (updateable,)
    Shot.containers = (shots, updateable, drawable)
    Objective.containers = (updateable, drawable, objectives)
    
    font = pygame.font.Font(None, 36)
    big_font = pygame.font.Font(None, 100)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    begin_wait = True

    music = pygame.mixer.Sound("assets/new_music.wav")
    music.set_volume(0.0)
    music.play(loops=-1)
    muted = False
    
    tile_w, tile_h = SCREEN_WIDTH, SCREEN_HEIGHT
    grid = BackgroundGrid(tile_w, tile_h, make_tile)
    world_w, world_h = grid.world_w, grid.world_h

    cam = Camera(tile_w, tile_h, world_w, world_h, wrap=True)
    #background = create_space_background(SCREEN_WIDTH, SCREEN_HEIGHT)
    cam.set_deadzone(int(SCREEN_WIDTH*0.25), int(SCREEN_HEIGHT*0.25))

    #bonus = Objective(2*world_w, 2*world_h, 20, world_w=world_w, world_h=world_h, cam=cam, obj_type=None)
    
    while True:
        
        while begin_wait:
            if not draw_main_menu(screen, font, big_font):
                return
            score = 0
            game_stats = GameStats()
            player = Player(world_w/2, world_h/2, world_w=world_w, world_h=world_h, wrap_world=True, muted=muted, fill_alpha=200, game_stats=game_stats, cam=cam)
            field = AsteroidField(world_w=world_w, world_h=world_h, cam=cam, wrap_world=True)
            begin_wait = False

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    muted = not muted
                    if muted:
                        music.set_volume(0.0)
                        player.muted = muted
                    else:
                        music.set_volume(0.3)
                        player.muted = muted
            
        #screen.fill((0,0,0))
        #screen.blit(background, (0, 0))
       
    
        updateable.update(dt)

        cam.push_follow(player.position.x, player.position.y)

        grid.draw(screen, cam.rect, wrap=cam.wrap)
 
        for sprite in drawable:
            try: 
                sprite.draw(screen, cam.rect)
            except TypeError:
                sprite.draw(screen)

        draw_hud(screen, font, score, game_stats.stats["Stars_collected"])

        for objective in objectives:
            if player.collision(objective):
                objective.kill()
                if objective.type == ObjectiveType.STAR:
                    game_stats.increment_stat("Stars_collected")
                    score += 2000

                

        for asteroid in asteroids:
            if player.collision(asteroid):
                action = draw_game_over_menu(screen, font, big_font, score)
                if action == 'quit':
                    return
                elif action == 'retry':
                    score = 0
                    game_stats = GameStats()
                    for g in (updateable, drawable, asteroids, shots, objectives):
                        g.empty()
                    player = Player(world_w/2, world_h/2, world_w=world_w, world_h=world_h, wrap_world=True, muted=muted, fill_alpha=200, game_stats=game_stats, cam=cam)
                    field = AsteroidField(world_w=world_w, world_h=world_h, cam=cam, wrap_world=True)
                    
                elif action == 'main_menu':
                    for g in (updateable, drawable, asteroids, shots, objectives):
                        g.empty()
                    begin_wait = True
                elif action == 'stats':
                    for g in (updateable, drawable, asteroids, shots, objectives):
                        g.empty()
                    stat_action = draw_stats_menu(screen, font, big_font, game_stats)
                    if stat_action == 'quit':
                        return
                    elif stat_action == 'main_menu':
                        for g in (updateable, drawable, asteroids, shots, objectives):
                            g.empty()
                        begin_wait = True
                    elif stat_action == 'retry':
                        score = 0
                        game_stats = GameStats()
                        for g in (updateable, drawable, asteroids, shots, objectives):
                            g.empty()
                        player = Player(world_w/2, world_h/2, world_w=world_w, world_h=world_h, wrap_world=True, muted=muted, fill_alpha=200, game_stats=game_stats, cam=cam)
                        field = AsteroidField(world_w=world_w, world_h=world_h, cam=cam, wrap_world=True)
                        
           
            for shot in shots:
                if shot.collision(asteroid):
                    shot.kill()
                    asteroid_color = get_velocity_color(asteroid.velocity)
                    if asteroid_color == (25, 38, 56):
                        game_stats.increment_stat("Level0_asteroids_destroyed")
                        score += 50
                    elif asteroid_color == (64, 119, 142):
                        game_stats.increment_stat("Level1_asteroids_destroyed")
                        score += 100
                    elif asteroid_color == (108, 66, 133):
                        game_stats.increment_stat("Level2_asteroids_destroyed")
                        score += 200
                    elif asteroid_color == (196, 107, 44):
                        game_stats.increment_stat("Level3_asteroids_destroyed")
                        score += 250
                        new_star = Objective(world_w/2, world_h/2, 20,world_w=world_w, world_h=world_h, cam=cam,obj_type=ObjectiveType.STAR)
                        new_star.spawn_in_view(margin=24)
                    elif asteroid_color == (178, 40, 85):
                        game_stats.increment_stat("Level4_asteroids_destroyed")
                        score += 350
                        new_star = Objective(world_w/2, world_h/2, 20,world_w=world_w, world_h=world_h, cam=cam,obj_type=ObjectiveType.STAR)
                        new_star.spawn_in_view(margin=24)
                        #print(f"{bonus.position}")
                    elif asteroid_color == (0, 222, 173):
                        game_stats.increment_stat("Level5_asteroids_destroyed")
                        score += 500
                        new_star = Objective(world_w/2, world_h/2, 20,world_w=world_w, world_h=world_h, cam=cam,obj_type=ObjectiveType.STAR)
                        new_star.spawn_in_view(margin=24)
                        #print(f"{bonus.position}")
                    #score += asteroid.thick + int(asteroid.velocity.length())
                    asteroid.split()
        
        pygame.display.flip()

        dt = clock.tick(60)/1000

if __name__ == "__main__":
    main()
