import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT
import re

FONTCOLORS = {
    "title_game_over": (255, 80, 80),
    "shadow": (30, 0, 0),
    "score": (255, 210, 120),
    "retry": (80, 220, 80),
    "quit": (255, 130, 130),
    "stats": (140, 180, 255),
    "title_stats": (80, 255, 240),
    "gold": (255, 215, 0),
    "menu_title": (255, 215, 0),
    "menu_quit": (255, 120, 120)
}

def render_text_with_shadow(text, font, text_color, shadow_color=(0, 0, 0), offset=(2, 2), shadow_alpha=None):
    """Render text with a drop shadow."""
    text_surf = font.render(text, True, text_color)
    shadow_surf = font.render(text, True, shadow_color)

    if shadow_alpha is not None:
        shadow_surf = shadow_surf.convert_alpha()
        shadow_surf.set_alpha(shadow_alpha)

    w = text_surf.get_width() + abs(offset[0])
    h = text_surf.get_height() + abs(offset[1])
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    out.blit(shadow_surf, offset)
    out.blit(text_surf, (0, 0))
    return out

def render_text_with_outline(text, font, text_color, outline_color=(0, 0, 0), thickness=2):
    """Chunky arcade outline (optional)."""
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)

    w, h = base.get_width() + thickness * 2, base.get_height() + thickness * 2
    out = pygame.Surface((w, h), pygame.SRCALPHA)
    # 8 directions around the text
    for dx, dy in [(-thickness, 0), (thickness, 0), (0, -thickness), (0, thickness),
                   (-thickness, -thickness), (-thickness, thickness), (thickness, -thickness), (thickness, thickness)]:
        out.blit(outline, (dx + thickness, dy + thickness))
    out.blit(base, (thickness, thickness))
    return out

def draw_main_menu(screen, font, big_font, menu_bg, clock):
    """
    Draw the main menu screen with start game and quit options.
    
    Args:
        screen: Pygame screen surface
        font: Regular font for smaller text
        big_font: Large font for main text
    
    Returns:
        bool: True if game should start, False if should quit
    """

    # Handle input
    while True:
        dt = clock.tick(60)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_RETURN:
                    return True
        
        menu_bg.update(dt)
        menu_bg.draw(screen)

        # Main title
        start_game = render_text_with_shadow("Press ENTER to Start", big_font, FONTCOLORS["menu_title"], shadow_color=FONTCOLORS["shadow"], offset=(6,6), shadow_alpha=180)
        #start_game = big_font.render("Press ENTER to Start", True, FONTCOLORS["menu_title"])
        start_rect = start_game.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(start_game, start_rect)
        
        # Quit instruction
        game_quit = font.render("Press Q to Quit", True, FONTCOLORS["menu_quit"])
        quit_rect = game_quit.get_rect(center=(SCREEN_WIDTH//2, 680))
        screen.blit(game_quit, quit_rect)
        
        pygame.display.flip()
    

def draw_game_over_menu(screen, font, big_font, score, menu_bg, clock, game_snapshot):
    """
    Draw the game over screen with retry, quit, and main menu options.
    
    Args:
        screen: Pygame screen surface
        font: Regular font for smaller text
        big_font: Large font for main text
        score: Current game score
    
    Returns:
        str: Action to take - 'retry', 'quit', or 'main_menu'
    """
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((120, 15, 15, 150))
    # Handle input
    while True:
        dt = clock.tick(60) / 1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return 'quit'
                if event.key == pygame.K_r:
                    return 'retry'
                if event.key == pygame.K_ESCAPE:
                    return 'main_menu'
                if event.key == pygame.K_s:
                    return 'stats'
                
        screen.blit(game_snapshot, (0,0))
        screen.blit(overlay, (0,0))
        #menu_bg.draw(screen)
                
            
        # Game over title
        end_game = render_text_with_outline("GAME OVER", big_font, FONTCOLORS["title_game_over"], outline_color=(20,0,0), thickness=3)
        #end_game = big_font.render("GAME OVER", True, FONTCOLORS["title_game_over"])
        end_rect = end_game.get_rect(center=(SCREEN_WIDTH//2, 80))
        screen.blit(end_game, end_rect)
        
        # Score display
        score_text = render_text_with_shadow(f"Final Score: {score}",font,FONTCOLORS["score"],shadow_color=(0,0,0), offset=(2,2), shadow_alpha=150)
        #score_text = font.render(f"Final Score: {score}", True, FONTCOLORS["score"])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
        screen.blit(score_text, score_rect)
        
        # Stats menu
        stats = font.render("Press S for Stats", True, FONTCOLORS["stats"])
        stats_rect = stats.get_rect(center=(SCREEN_WIDTH//2, 500))
        screen.blit(stats, stats_rect)

        # Retry option
        restart = font.render("Press R to Retry", True, FONTCOLORS["retry"])
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH//2, 560))
        screen.blit(restart, restart_rect)
        
        # Quit option
        game_quit = font.render("Press Q to Quit", True, FONTCOLORS["quit"])
        quit_rect = game_quit.get_rect(center=(SCREEN_WIDTH//2, 620))
        screen.blit(game_quit, quit_rect)
        
        # Main menu option
        main_menu = font.render("Press ESC to go to Main Menu", True, FONTCOLORS["menu_quit"])
        menu_rect = main_menu.get_rect(center=(SCREEN_WIDTH//2, 680))
        screen.blit(main_menu, menu_rect)
        
        pygame.display.flip()

def draw_hud(screen, font, score, collected):
    """
    Draw the heads-up display during gameplay.
    
    Args:
        screen: Pygame screen surface
        font: Font for text rendering
        score: Current game score
        collected: Stars Collected
    """
    text_surface = font.render(f"Score: {score}", True, FONTCOLORS["score"])
    text_rect = text_surface.get_rect()
    text_rect.centerx = SCREEN_WIDTH // 2
    text_rect.centery = 20
    screen.blit(text_surface, text_rect)
    if collected>0:
        star_surface = font.render(f"Stars Collected: {collected}", True, FONTCOLORS["gold"])
        star_rect = star_surface.get_rect(midtop=(text_rect.centerx, text_rect.bottom + 2))
        screen.blit(star_surface, star_rect)

def draw_stats_menu(screen, font, big_font, game_stats, menu_bg, clock, game_snapshot):
    """
    Draw the stats screen.
    
    Args:
        screen: Pygame screen surface
        font: Font for text rendering
        big_font: main text
        game_stats: GameStats object
    """
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((120, 15, 15, 150))

    #Handle input
    while True:
        dt = clock.tick(60)/1000
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return 'quit'
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return 'quit'
                if event.key == pygame.K_ESCAPE:
                    return 'main_menu'
                if event.key == pygame.K_r:
                    return 'retry'
                
        screen.blit(game_snapshot, (0,0))
        screen.blit(overlay, (0,0,))

                
        #Title
        title = big_font.render("Game Statistics", True, FONTCOLORS["title_stats"])
        title_rect = title.get_rect(center=(SCREEN_WIDTH//2, 80))
        screen.blit(title, title_rect)

        #Display stats
        y_offset = 150
        line_spacing = 40

        #Get all stats
        game_stats.accuracy()
        for stat_name, value in game_stats.stats.items():
            if value == 0:
                continue
            
            if "red" in stat_name.lower():
                color = "red"
            elif "blue" in stat_name.lower():
                color = "blue"
            elif "green" in stat_name.lower():
                color = "green"
            elif "yellow" in stat_name.lower():
                color = "yellow"
            elif "orange" in stat_name.lower():
                color = "orange"
            else:
                color = "white"

            display_name = stat_name.replace("_", " ").title()
            display_name = re.sub("Level(\d+)", r"Level \1", display_name)

            if "accuracy" in stat_name:
                display_value = f"{value:.1f}%"
            else:
                display_value = str(value)

            stat_text = font.render(f"{display_name}: {display_value}", True, FONTCOLORS["stats"])
            stat_rect = stat_text.get_rect(topleft=(title_rect.left, y_offset))
            screen.blit(stat_text, stat_rect)

            y_offset += line_spacing

        # Retry option
        restart = font.render("Press R to Retry", True, FONTCOLORS["retry"])
        restart_rect = restart.get_rect(center=(SCREEN_WIDTH//2, 560))
        screen.blit(restart, restart_rect)
        
        # Main menu option
        back_text = font.render("Press ESC to go to Main Menu", True, FONTCOLORS["menu_quit"])
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2, 680))
        screen.blit(back_text, back_rect)

        # Quit option
        game_quit = font.render("Press Q to Quit", True, FONTCOLORS["quit"])
        quit_rect = game_quit.get_rect(center=(SCREEN_WIDTH//2, 620))
        screen.blit(game_quit, quit_rect)

        pygame.display.flip()