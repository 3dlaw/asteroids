import pygame
from constants import *
from player import Player, Shot
from asteroid import Asteroid, get_velocity_color
from asteroidfield import AsteroidField
from menus import *
from stats import GameStats
from objectives import Objective
import os
from worldgrid import *
from camera import Camera
from menu_bg import MenuBackground

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
    
    font = pygame.font.Font("assets/fonts/PressStart2P-Regular.ttf", 20)
    big_font = pygame.font.Font("assets/fonts/Orbitron-Black.ttf", 96)
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    begin_wait = True

    music = pygame.mixer.Sound("assets/new_music.wav")
    music.set_volume(0.0)
    music.play(loops=-1)
    muted = False
    
    menu_bg = MenuBackground(SCREEN_WIDTH, SCREEN_HEIGHT, seed=None, n_asteroids=10, planets=True)
    grid = BackgroundGrid(SCREEN_WIDTH, SCREEN_HEIGHT, make_tile_fn=make_tile, nrows=5, ncols=5)
    world_w, world_h = grid.world_w, grid.world_h

    cam = Camera(SCREEN_WIDTH, SCREEN_HEIGHT, world_w, world_h, wrap=True)
    cam.set_deadzone(int(SCREEN_WIDTH*0.25), int(SCREEN_HEIGHT*0.25))
    
    while True:
        
        while begin_wait:
            start = draw_main_menu(screen, font, big_font, menu_bg, clock)
            if not start:
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
       
        cam.push_follow(player.position.x, player.position.y)
        updateable.update(dt)

        

        grid.draw(screen, cam.rect, wrap=cam.wrap)
 
        for sprite in drawable:
            try: 
                sprite.draw(screen, cam.rect)
            except TypeError:
                sprite.draw(screen)

        game_snapshot = screen.copy()
        draw_hud(screen, font, score, game_stats.stats["Stars_collected"])
        cols = world_w // SCREEN_WIDTH
        rows = world_h // SCREEN_HEIGHT
        tile_x = int(player.position.x // SCREEN_WIDTH) % cols
        tile_y = int(player.position.y // SCREEN_HEIGHT) % rows
        tile_y_disp = (rows - 1) - tile_y
        offset_x = int(player.position.x % SCREEN_WIDTH)
        offset_y = int(player.position.y % SCREEN_HEIGHT)
        offset_y_disp = SCREEN_HEIGHT - 1 - offset_y
        sector_line = f"Sector: ({tile_x}, {tile_y_disp})"
        coord_line = f"Local: ({offset_x}, {offset_y_disp})"
        coord_surf = font.render(coord_line, True, "white")
        coord_rect = coord_surf.get_rect(topleft=(20, SCREEN_HEIGHT - 40))
        sector_surf = font.render(sector_line, True, "white")
        sector_rect = sector_surf.get_rect(bottomleft=(coord_rect.left, coord_rect.top -2))
        screen.blit(coord_surf, coord_rect)
        screen.blit(sector_surf, sector_rect)

        for objective in objectives:
            if player.collision(objective):
                objective.kill()
                if objective.type == ObjectiveType.STAR:
                    game_stats.increment_stat("Stars_collected")
                    score += 2000

                

        for asteroid in asteroids:
            if player.collision(asteroid):
                action = draw_game_over_menu(screen, font, big_font, score, menu_bg, clock, game_snapshot)
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
                    stat_action = draw_stats_menu(screen, font, big_font, game_stats, menu_bg, clock, game_snapshot)
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
