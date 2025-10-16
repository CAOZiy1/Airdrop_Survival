# src/player.py

import pygame
import os
from settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, HEIGHT

_PLAYER_IMG = None

def _load_player_image():
    global _PLAYER_IMG
    base = os.path.join(os.path.dirname(__file__), '..', 'assets')
    base = os.path.normpath(base)
    try:
        _PLAYER_IMG = pygame.image.load(os.path.join(base, 'player.png')).convert_alpha()
    except Exception:
        _PLAYER_IMG = None


class Player:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, PLAYER_WIDTH, PLAYER_HEIGHT)
        if _PLAYER_IMG is None:
            _load_player_image()

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < 800:
            self.rect.x += PLAYER_SPEED

    def draw(self, screen, color):
        if _PLAYER_IMG:
            surf = pygame.transform.smoothscale(_PLAYER_IMG, (self.rect.width, self.rect.height))
            screen.blit(surf, (self.rect.x, self.rect.y))
        else:
            pygame.draw.rect(screen, color, self.rect)
