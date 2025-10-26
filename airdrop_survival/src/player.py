# src/player.py

import pygame
import os
from settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, WIDTH
from settings import PLAYER_DRAW_SCALE, PLAYER_VERTICAL_RAISE

_PLAYER_IMG = None
_HURT_IMG = None
_DEAD_IMG = None

def _load_player_images():
    global _PLAYER_IMG, _HURT_IMG, _DEAD_IMG
    base = os.path.join(os.path.dirname(__file__), '..', 'assets')
    base = os.path.normpath(base)
    try:
        _PLAYER_IMG = pygame.image.load(os.path.join(base, 'player.png')).convert_alpha()
    except Exception:
        _PLAYER_IMG = None
    try:
        # prefer user-supplied newer names, fall back to older ones
        hurt_path = os.path.join(base, 'player_hurt.png')
        if not os.path.exists(hurt_path):
            hurt_path = os.path.join(base, 'chara_hurt.png')
        _HURT_IMG = pygame.image.load(hurt_path).convert_alpha()
    except Exception:
        _HURT_IMG = None
    try:
        dead_path = os.path.join(base, 'player_dead.png')
        if not os.path.exists(dead_path):
            dead_path = os.path.join(base, 'chara_dead.png')
        _DEAD_IMG = pygame.image.load(dead_path).convert_alpha()
    except Exception:
        _DEAD_IMG = None


class Player:
    def __init__(self, x, y):
        # apply a small vertical raise so the player appears higher on screen
        # (this only shifts the rect's y; collision rect remains the same size)
        self.rect = pygame.Rect(x, y - PLAYER_VERTICAL_RAISE, PLAYER_WIDTH, PLAYER_HEIGHT)
        if _PLAYER_IMG is None and _HURT_IMG is None and _DEAD_IMG is None:
            _load_player_images()

        # overlay state (milliseconds timestamp)
        self.hurt_until = 0
        self.dead_until = 0

    def move(self, keys):
        # support arrow keys and A/D for left/right movement
        left_pressed = keys[pygame.K_LEFT] or keys[pygame.K_a]
        right_pressed = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        dx = 0
        if left_pressed:
            dx -= PLAYER_SPEED
        if right_pressed:
            dx += PLAYER_SPEED
        # apply delta then clamp inside screen bounds
        new_x = self.rect.x + dx
        max_x = WIDTH - self.rect.width
        if new_x < 0:
            new_x = 0
        elif new_x > max_x:
            new_x = max_x
        self.rect.x = new_x

    def set_hurt(self, duration_seconds):
        self.hurt_until = pygame.time.get_ticks() + int(duration_seconds * 1000)

    def set_dead(self, duration_seconds):
        self.dead_until = pygame.time.get_ticks() + int(duration_seconds * 1000)

    def draw(self, screen, color):
        # choose which sprite to draw: dead > hurt > normal
        now = pygame.time.get_ticks()
        sprite = None
        if now < self.dead_until and _DEAD_IMG:
            sprite = _DEAD_IMG
        elif now < self.hurt_until and _HURT_IMG:
            sprite = _HURT_IMG
        elif _PLAYER_IMG:
            sprite = _PLAYER_IMG

        if sprite:
            # preserve aspect ratio: scale sprite to fit inside rect
            iw, ih = sprite.get_width(), sprite.get_height()
            rw, rh = self.rect.width, self.rect.height
            # apply draw-scale multiplier so sprite can be visually larger than collision rect
            scale = min(rw / iw, rh / ih) * PLAYER_DRAW_SCALE
            target_w = max(1, int(iw * scale))
            target_h = max(1, int(ih * scale))
            surf = pygame.transform.smoothscale(sprite, (target_w, target_h))
            # center the sprite on the player's rect and draw
            dest = surf.get_rect(center=self.rect.center)
            screen.blit(surf, dest.topleft)
        else:
            pygame.draw.rect(screen, color, self.rect)
