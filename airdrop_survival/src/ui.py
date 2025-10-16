# src/ui.py

import pygame
import os
from settings import BLACK, RED, GREEN, WIDTH, HEIGHT, MAX_HUNGER, COINS_PER_FOOD, MAX_HEALTH

# Cached icon surfaces
_HEART_ICON = None
_COIN_ICON = None
_IMG_COIN = None
_IMG_HEALTH = None
_IMG_STOMACH = None
_STOMACH_ICON = None
_IMG_BACKGROUND = None
_IMG_CAN = None

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
    # can image for level reward
    try:
        can_path = os.path.join(base, 'can.png')
        if os.path.exists(can_path):
            _IMG_CAN = pygame.image.load(can_path).convert_alpha()
        else:
            _IMG_CAN = None
    except Exception:
        _IMG_CAN = None

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


def draw_status(screen, font, hearts, coins, hunger=None, time_left_seconds=None):
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

    # Hunger is now shown as a single icon beside the top countdown; we no longer render multiple stomach icons here.

    # (time display moved to centered message; draw_status no longer renders it)


def draw_gameover(screen, font, message, color):
    text = font.render(message, True, color)
    screen.blit(text, (400 - text.get_width() // 2, 300))
    pygame.display.flip()
    pygame.time.wait(3000)


def draw_level_result(screen, font, message, success=True, reward_image=None):
    """Display an end-of-level message. If success, show the reward_image (surface or None).

    Blocks briefly to let the player read the message.
    """
    # darken background slightly
    overlay = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
    overlay.fill((0, 0, 0, 180))
    screen.blit(overlay, (0, 0))

    color = GREEN if success else RED
    text = font.render(message, True, color)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 40))

    if success and reward_image is not None:
        try:
            img_s = pygame.transform.smoothscale(reward_image, (96, 96))
            screen.blit(img_s, (WIDTH // 2 - img_s.get_width() // 2, HEIGHT // 2 + 10))
        except Exception:
            pass

    pygame.display.flip()
    pygame.time.wait(2500)


def draw_level_start_hint(screen, font, coins_required, reward_text, reward_image=None, duration_ms=2000):
    """Show a brief level-start hint like '30 coins for a can' with optional image.

    Blocks for duration_ms milliseconds to ensure player sees the objective.
    """
    overlay = pygame.Surface((WIDTH, HEIGHT)).convert_alpha()
    overlay.fill((0, 0, 0, 160))
    screen.blit(overlay, (0, 0))

    text = f"{coins_required} coins for {reward_text}"
    txt = font.render(text, True, (255, 230, 180))
    screen.blit(txt, (WIDTH // 2 - txt.get_width() // 2, HEIGHT // 2 - 30))

    if reward_image is not None:
        try:
            img_s = pygame.transform.smoothscale(reward_image, (72, 72))
            screen.blit(img_s, (WIDTH // 2 - img_s.get_width() // 2, HEIGHT // 2 + 10))
        except Exception:
            pass

    pygame.display.flip()
    pygame.time.wait(duration_ms)


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


def draw_center_countdown(screen, font, seconds_left):
    """Draw a centered countdown message in English: 'XX seconds until starvation'"""
    try:
        text = f"{seconds_left} seconds until starvation"
        txt = font.render(text, True, (10, 10, 10))
        # render a small stomach icon to the left of the text for clarity
        icon_size = 20
        gap = 8
        # compute combined width (icon + gap + text)
        total_w = icon_size + gap + txt.get_width()
        x0 = WIDTH // 2 - total_w // 2
        y = 10
        # draw icon
        if _IMG_STOMACH:
            try:
                icon_s = pygame.transform.smoothscale(_IMG_STOMACH, (icon_size, icon_size))
                screen.blit(icon_s, (x0, y + (txt.get_height() - icon_size) // 2))
            except Exception:
                # fallback to simple ellipse
                pygame.draw.ellipse(screen, (100, 150, 200), (x0, y + (txt.get_height() - icon_size) // 2, icon_size, icon_size))
        else:
            pygame.draw.ellipse(screen, (100, 150, 200), (x0, y + (txt.get_height() - icon_size) // 2, icon_size, icon_size))
        # draw text to the right of the icon
        screen.blit(txt, (x0 + icon_size + gap, y))
    except Exception:
        pass
