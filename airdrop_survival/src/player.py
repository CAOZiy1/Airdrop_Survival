# src/player.py

import pygame
from settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, HEIGHT

class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < 800:
            self.rect.x += PLAYER_SPEED

    def draw(self, screen, color):
        pygame.draw.rect(screen, color, self.rect)
