# src/ui.py

import pygame
from settings import BLACK, RED, GREEN

def draw_status(screen, font, hearts, coins):
    text = font.render(f"❤️: {hearts}    💰: {coins}", True, BLACK)
    screen.blit(text, (10, 10))

def draw_gameover(screen, font, message, color):
    text = font.render(message, True, color)
    screen.blit(text, (400 - text.get_width() // 2, 300))
    pygame.display.flip()
    pygame.time.wait(3000)
