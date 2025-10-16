# src/ui.py

import pygame
import os
from settings import BLACK, RED, GREEN, WIDTH, MAX_HUNGER, COINS_PER_FOOD, MAX_HEALTH

# Cached icon surfaces
_HEART_ICON = None
_COIN_ICON = None
_IMG_COIN = None
_IMG_HEALTH = None
_IMG_STOMACH = None
_STOMACH_ICON = None
_IMG_BACKGROUND = None

def _load_status_images():
    global _IMG_COIN, _IMG_HEALTH
    global _IMG_BACKGROUND
    global _IMG_STOMACH
    base = os.path.join(os.path.dirname(__file__), '..', 'assets')
    base = os.path.normpath(base)
    # try to load background
    try:
        pbg = os.path.join(base, 'background.png')
        print(f"ui: loading background image from {pbg}")
        _IMG_BACKGROUND = pygame.image.load(pbg).convert()
    except Exception:
        _IMG_BACKGROUND = None
    def _try_load_alpha(candidates):
        for name in candidates:
            p = os.path.join(base, name)
            try:
                if os.path.exists(p):
                    print(f"ui: loading image from {p}")
                    return pygame.image.load(p).convert_alpha()
            except Exception:
                import traceback
                print(f"ui: failed loading image from {p}")
                traceback.print_exc()
        return None

    # coin image: prefer money_icon if available, then coin
    _IMG_COIN = _try_load_alpha(['money_icon.png', 'coin.png'])

    # health/heart image: prefer heart_icon if present, then heart, life_icon, then health_pack
    _IMG_HEALTH = _try_load_alpha(['heart_icon.png', 'heart.png', 'life_icon.png', 'health_pack.png'])
    # stomach image: accept stomach.png or stomach_icon.png
    _IMG_STOMACH = _try_load_alpha(['stomach.png', 'stomach_icon.png'])

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


def draw_status(screen, font, hearts, coins, hunger=None):
    global _HEART_ICON, _COIN_ICON
    global _IMG_COIN, _IMG_HEALTH
    if _IMG_COIN is None and _IMG_HEALTH is None:
        _load_status_images()

    if _HEART_ICON is None or _COIN_ICON is None:
        _HEART_ICON, _COIN_ICON = _create_icons(size=24)

    padding = 8
    x = 10
    y = 10

    # Draw hearts: render MAX_HEALTH icons and dim ones above current hearts
    heart_w = _HEART_ICON.get_width()
    heart_h = _HEART_ICON.get_height()
    for i in range(MAX_HEALTH):
        hx = x + i * (heart_w + 4)
        if _IMG_HEALTH:
            hs = pygame.transform.smoothscale(_IMG_HEALTH, (heart_w, heart_h))
            if i < hearts:
                screen.blit(hs, (hx, y))
            else:
                tmp = hs.copy()
                tmp.fill((80, 80, 80, 150), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(tmp, (hx, y))
        else:
            if i < hearts:
                screen.blit(_HEART_ICON, (hx, y))
            else:
                tmp = _HEART_ICON.copy()
                tmp.fill((80, 80, 80, 150), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(tmp, (hx, y))

    # move coins start to right of hearts block
    text_offset = MAX_HEALTH * (heart_w + 4)

    # Blit coin icon and count (to the right of heart group)
    x2 = x + text_offset + padding * 2
    if _IMG_COIN:
        coin_s = pygame.transform.smoothscale(_IMG_COIN, (_COIN_ICON.get_width(), _COIN_ICON.get_height()))
        screen.blit(coin_s, (x2, y))
    else:
        screen.blit(_COIN_ICON, (x2, y))
    text2 = font.render(str(coins), True, BLACK)
    screen.blit(text2, (x2 + _COIN_ICON.get_width() + 4, y + (_COIN_ICON.get_height() - text2.get_height()) // 2))

    # If hunger provided, draw stomach icons to the right of coins
    if hunger is None:
        hunger = MAX_HUNGER

    x3 = x2 + _COIN_ICON.get_width() + text2.get_width() + padding * 2
    # prefer image if available
    stomach_width = _COIN_ICON.get_width()
    stomach_height = _COIN_ICON.get_height()
    for i in range(MAX_HUNGER):
        pos_x = x3 + i * (stomach_width + 4)
        if _IMG_STOMACH:
            s = pygame.transform.smoothscale(_IMG_STOMACH, (stomach_width, stomach_height))
            if i < hunger:
                screen.blit(s, (pos_x, y))
            else:
                # draw dimmed for empty stomach
                tmp = s.copy()
                tmp.fill((60, 60, 60, 140), special_flags=pygame.BLEND_RGBA_MULT)
                screen.blit(tmp, (pos_x, y))
        else:
            # fallback: draw a simple stomach-like ellipse
            stomach_surf = pygame.Surface((stomach_width, stomach_height), pygame.SRCALPHA)
            color_full = (100, 150, 200)
            color_empty = (120, 120, 120)
            pygame.draw.ellipse(stomach_surf, color_full if i < hunger else color_empty, (0, 0, stomach_width, stomach_height))
            screen.blit(stomach_surf, (pos_x, y))

    # small hint for buying food: key 'F' spends coins to buy food
    hint = font.render(f"F: {COINS_PER_FOOD} coins -> +1 food", True, BLACK)
    screen.blit(hint, (WIDTH - hint.get_width() - 10, y + (_HEART_ICON.get_height() - hint.get_height()) // 2))


def draw_gameover(screen, font, message, color):
    text = font.render(message, True, color)
    screen.blit(text, (400 - text.get_width() // 2, 300))
    pygame.display.flip()
    pygame.time.wait(3000)


def draw_background(screen, width, height):
    """Draw background: prefer loaded image, otherwise procedural gradient + ground."""
    global _IMG_BACKGROUND
    if _IMG_BACKGROUND is None:
        # attempt to load status images (which also tries background)
        _load_status_images()

    if _IMG_BACKGROUND:
        try:
            bg = pygame.transform.smoothscale(_IMG_BACKGROUND, (width, height))
            screen.blit(bg, (0, 0))
            return
        except Exception:
            pass

    # fallback: procedural gradient
    # Colors
    top_color = (135, 206, 250)   # light sky blue
    mid_color = (70, 130, 180)    # steel blue
    ground_color = (34, 139, 34)  # forest green

    sky_height = int(height * 0.75)

    # Draw sky gradient: top -> mid over sky_height
    for y in range(sky_height):
        t = y / max(sky_height - 1, 1)
        r = int(top_color[0] * (1 - t) + mid_color[0] * t)
        g = int(top_color[1] * (1 - t) + mid_color[1] * t)
        b = int(top_color[2] * (1 - t) + mid_color[2] * t)
        pygame.draw.line(screen, (r, g, b), (0, y), (width, y))

    # Ground
    pygame.draw.rect(screen, ground_color, (0, sky_height, width, height - sky_height))
