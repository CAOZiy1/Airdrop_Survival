# src/player.py

import pygame
import os
from settings import PLAYER_WIDTH, PLAYER_HEIGHT, PLAYER_SPEED, HEIGHT
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
        self.outline = True  # 默认开启描边
        self.outline_color = (0, 0, 0)  # 黑色描边
        self.outline_width = 3  # 描边宽度
        self.rect = pygame.Rect(x, y - PLAYER_VERTICAL_RAISE, PLAYER_WIDTH, PLAYER_HEIGHT)
        if _PLAYER_IMG is None and _HURT_IMG is None and _DEAD_IMG is None:
            _load_player_images()

        # overlay state (milliseconds timestamp)
        self.hurt_until = 0
        self.dead_until = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= PLAYER_SPEED
        if keys[pygame.K_RIGHT] and self.rect.right < 800:
            self.rect.x += PLAYER_SPEED

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
            # center the sprite on the player's rect
            dest = surf.get_rect(center=self.rect.center)
            # optional outline: draw a slightly enlarged filled version behind the sprite
            if self.outline:
                try:
                    outline_surf = pygame.Surface((surf.get_width() + self.outline_width * 2, surf.get_height() + self.outline_width * 2), pygame.SRCALPHA)
                    # draw the sprite's alpha as a mask by blitting the sprite multiple times in the outline color
                    mask = surf.copy()
                    mask.fill(self.outline_color + (0,), special_flags=pygame.BLEND_RGBA_MULT)
                    # draw multiple shifted blits to create a solid outline
                    ox, oy = self.outline_width, self.outline_width
                    for dx in range(-self.outline_width, self.outline_width + 1, max(1, self.outline_width)):
                        for dy in range(-self.outline_width, self.outline_width + 1, max(1, self.outline_width)):
                            outline_surf.blit(mask, (ox + dx, oy + dy))
                    # then blit the outline and the sprite onto the screen
                    outline_pos = (dest.left - self.outline_width, dest.top - self.outline_width)
                    screen.blit(outline_surf, outline_pos)
                except Exception:
                    # fallback: draw a simple rect behind the player
                    back = pygame.Rect(dest.left - self.outline_width, dest.top - self.outline_width, surf.get_width() + self.outline_width * 2, surf.get_height() + self.outline_width * 2)
                    pygame.draw.rect(screen, self.outline_color, back)
            screen.blit(surf, dest.topleft)
        else:
            pygame.draw.rect(screen, color, self.rect)
