import pygame
from constants import SCREEN_WIDTH, SCREEN_HEIGHT

def draw_main_menu(screen, font, big_font):
    """
    Draw the main menu screen with start game and quit options.
    
    Args:
        screen: Pygame screen surface
        font: Regular font for smaller text
        big_font: Large font for main text
    
    Returns:
        bool: True if game should start, False if should quit
    """
    screen.fill("black")
    
    # Main title
    start_game = big_font.render("Press ENTER to Start", True, "green")
    start_rect = start_game.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(start_game, start_rect)
    
    # Quit instruction
    game_quit = font.render("Press Q to Quit", True, "red")
    quit_rect = game_quit.get_rect(center=(SCREEN_WIDTH//2, 680))
    screen.blit(game_quit, quit_rect)
    
    pygame.display.flip()
    
    # Handle input
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    return False
                if event.key == pygame.K_RETURN:
                    return True

def draw_game_over_menu(screen, font, big_font, score):
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
    screen.fill("black")
    
    # Game over title
    end_game = big_font.render("Game Over", True, "red")
    end_rect = end_game.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
    screen.blit(end_game, end_rect)
    
    # Score display
    score_text = font.render(f"Final Score: {score}", True, "white")
    score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 + 80))
    screen.blit(score_text, score_rect)
    
    # Retry option
    restart = font.render("Press R to Retry", True, "green")
    restart_rect = restart.get_rect(center=(SCREEN_WIDTH//2, 560))
    screen.blit(restart, restart_rect)
    
    # Quit option
    game_quit = font.render("Press Q to Quit", True, "red")
    quit_rect = game_quit.get_rect(center=(SCREEN_WIDTH//2, 620))
    screen.blit(game_quit, quit_rect)
    
    # Main menu option
    main_menu = font.render("Press ESC to go to Main Menu", True, "white")
    menu_rect = main_menu.get_rect(center=(SCREEN_WIDTH//2, 680))
    screen.blit(main_menu, menu_rect)
    
    pygame.display.flip()
    
    # Handle input
    while True:
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

def draw_hud(screen, font, score):
    """
    Draw the heads-up display during gameplay.
    
    Args:
        screen: Pygame screen surface
        font: Font for text rendering
        score: Current game score
    """
    text_surface = font.render(f"Score: {score}", True, "white")
    text_rect = text_surface.get_rect()
    text_rect.centerx = SCREEN_WIDTH // 2
    text_rect.centery = 20
    screen.blit(text_surface, text_rect)
