# src/ui.py

import pygame
import os
from settings import BLACK, RED, GREEN

# Cached icon surfaces
_HEART_ICON = None
_COIN_ICON = None
_IMG_COIN = None
_IMG_HEALTH = None

def _load_status_images():
    global _IMG_COIN, _IMG_HEALTH
    base = os.path.join(os.path.dirname(__file__), '..', 'assets')
    base = os.path.normpath(base)
    try:
        _IMG_COIN = pygame.image.load(os.path.join(base, 'coin.png')).convert_alpha()
    except Exception:
        _IMG_COIN = None
    try:
        _IMG_HEALTH = pygame.image.load(os.path.join(base, 'health_pack.png')).convert_alpha()
    except Exception:
        _IMG_HEALTH = None

def _create_icons(size=24):
    """Create simple heart and coin icon surfaces.

    Returns (heart_surface, coin_surface)
    """
    heart = pygame.Surface((size, size), pygame.SRCALPHA)
    coin = pygame.Surface((size, size), pygame.SRCALPHA)

    # Heart: two circles + triangle-ish bottom
    circle_radius = size // 4
    pygame.draw.circle(heart, RED, (circle_radius, circle_radius), circle_radius)
    pygame.draw.circle(heart, RED, (size - circle_radius, circle_radius), circle_radius)
    points = [
        (0 + size * 0.15, circle_radius + size * 0.15),
        (size - size * 0.15, circle_radius + size * 0.15),
        (size * 0.5, size - size * 0.05),
    ]
    pygame.draw.polygon(heart, RED, points)

    # Coin: yellow/gold circle with darker border
    COIN_COLOR = (212, 175, 55)
    BORDER = (120, 90, 20)
    pygame.draw.circle(coin, COIN_COLOR, (size // 2, size // 2), size // 2 - 1)
    pygame.draw.circle(coin, BORDER, (size // 2, size // 2), size // 2 - 1, 2)
    # Add a small inner shine
    shine_rect = pygame.Rect(size * 0.55, size * 0.25, size * 0.2, size * 0.12)
    pygame.draw.ellipse(coin, (255, 230, 160), shine_rect)

    return heart, coin


def draw_status(screen, font, hearts, coins):
    global _HEART_ICON, _COIN_ICON
    global _IMG_COIN, _IMG_HEALTH
    if _IMG_COIN is None and _IMG_HEALTH is None:
        _load_status_images()

    if _HEART_ICON is None or _COIN_ICON is None:
        _HEART_ICON, _COIN_ICON = _create_icons(size=24)

    padding = 8
    x = 10
    y = 10

    # Blit heart icon and count (prefer image)
    if _IMG_HEALTH:
        heart_s = pygame.transform.smoothscale(_IMG_HEALTH, (_HEART_ICON.get_width(), _HEART_ICON.get_height()))
        screen.blit(heart_s, (x, y))
    else:
        screen.blit(_HEART_ICON, (x, y))
    text = font.render(str(hearts), True, BLACK)
    screen.blit(text, (x + _HEART_ICON.get_width() + 4, y + (_HEART_ICON.get_height() - text.get_height()) // 2))

    # Blit coin icon and count (to the right of heart group)
    x2 = x + _HEART_ICON.get_width() + text.get_width() + padding * 2
    if _IMG_COIN:
        coin_s = pygame.transform.smoothscale(_IMG_COIN, (_COIN_ICON.get_width(), _COIN_ICON.get_height()))
        screen.blit(coin_s, (x2, y))
    else:
        screen.blit(_COIN_ICON, (x2, y))
    text2 = font.render(str(coins), True, BLACK)
    screen.blit(text2, (x2 + _COIN_ICON.get_width() + 4, y + (_COIN_ICON.get_height() - text2.get_height()) // 2))


def draw_gameover(screen, font, message, color):
    text = font.render(message, True, color)
    screen.blit(text, (400 - text.get_width() // 2, 300))
    pygame.display.flip()
    pygame.time.wait(3000)
