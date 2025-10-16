# src/drop.py

import pygame
import random
import os
from settings import WIDTH, DROP_SIZE, DROP_TYPES, DROP_WEIGHTS, DROP_BASE_SPEED_MIN, DROP_BASE_SPEED_MAX, DROP_SPEED_INCREASE_PER_MIN, BOMB_SPEED_MULTIPLIER, DROP_TIME_SCALE_START, DROP_TIME_SCALE_RAMP_SEC, DROP_TIME_STAGE1_SEC, DROP_TIME_STAGE1_SCALE
from settings import USE_PER_TYPE_SPEED_MULTIPLIERS, COIN_SPEED_MULTIPLIER, HEALTH_SPEED_MULTIPLIER

# Module-level image cache
_IMG_BOMB = None
_IMG_COIN = None
_IMG_HEALTH = None

def _load_images():
    global _IMG_BOMB, _IMG_COIN, _IMG_HEALTH
    base = os.path.join(os.path.dirname(__file__), '..', 'assets')
    base = os.path.normpath(base)
    try:
        p = os.path.join(base, 'bomb.png')
        print(f"drop: loading bomb image from {p}")
        _IMG_BOMB = pygame.image.load(p).convert_alpha()
    except Exception:
        import traceback
        print(f"drop: failed loading bomb image from {p}")
        traceback.print_exc()
        _IMG_BOMB = None
    try:
        p = os.path.join(base, 'coin.png')
        print(f"drop: loading coin image from {p}")
        _IMG_COIN = pygame.image.load(p).convert_alpha()
    except Exception:
        import traceback
        print(f"drop: failed loading coin image from {p}")
        traceback.print_exc()
        _IMG_COIN = None
    try:
        p = os.path.join(base, 'health_pack.png')
        print(f"drop: loading health image from {p}")
        _IMG_HEALTH = pygame.image.load(p).convert_alpha()
    except Exception:
        import traceback
        print(f"drop: failed loading health image from {p}")
        traceback.print_exc()
        _IMG_HEALTH = None


class Drop:
    def __init__(self, elapsed_seconds=0, level_speed_multiplier=1.0):
        if _IMG_BOMB is None and _IMG_COIN is None and _IMG_HEALTH is None:
            _load_images()

        self.x = random.randint(0, WIDTH - DROP_SIZE)
        self.y = 0
        # base speed random in range, then increase with elapsed minutes
        base = random.uniform(DROP_BASE_SPEED_MIN, DROP_BASE_SPEED_MAX)
        increase = (elapsed_seconds / 60.0) * DROP_SPEED_INCREASE_PER_MIN
        # apply time-scaling: start slightly slower, ramp to 1.0 by DROP_TIME_SCALE_RAMP_SEC
        time_scale = 1.0
        try:
            # piecewise: stage1 constant scale, then ramp from stage1_scale -> DROP_TIME_SCALE_START -> 1.0
            if elapsed_seconds <= DROP_TIME_STAGE1_SEC:
                time_scale = DROP_TIME_STAGE1_SCALE
            else:
                # after stage1, interpolate between DROP_TIME_SCALE_START and 1.0 over remaining ramp
                if DROP_TIME_SCALE_RAMP_SEC > DROP_TIME_STAGE1_SEC:
                    t_after = max(0.0, elapsed_seconds - DROP_TIME_STAGE1_SEC)
                    ramp_duration = float(DROP_TIME_SCALE_RAMP_SEC - DROP_TIME_STAGE1_SEC)
                    frac_t = min(1.0, t_after / ramp_duration) if ramp_duration > 0 else 1.0
                    time_scale = DROP_TIME_SCALE_START + (1.0 - DROP_TIME_SCALE_START) * frac_t
                else:
                    time_scale = 1.0
        except Exception:
            time_scale = 1.0
        self.speed = (base + increase) * time_scale
        try:
            # use weighted random choices if weights are provided
            self.type = random.choices(DROP_TYPES, weights=DROP_WEIGHTS, k=1)[0]
        except Exception:
            self.type = random.choice(DROP_TYPES)
        # apply configured multipliers: either per-type or a single global multiplier
        try:
            if USE_PER_TYPE_SPEED_MULTIPLIERS:
                if self.type == 'coin':
                    self.speed *= COIN_SPEED_MULTIPLIER
                elif self.type == 'health_pack':
                    self.speed *= HEALTH_SPEED_MULTIPLIER
                else:
                    self.speed *= BOMB_SPEED_MULTIPLIER
            else:
                # legacy: apply single bomb multiplier to all
                self.speed *= BOMB_SPEED_MULTIPLIER
        except Exception:
            pass
        # apply per-level multiplier last so it scales the final speed
        try:
            self.speed *= float(level_speed_multiplier)
        except Exception:
            pass
        self.rect = pygame.Rect(self.x, self.y, DROP_SIZE, DROP_SIZE)

    def update(self):
        self.y += self.speed
        self.rect.y = self.y

    def draw(self, screen):
        # Choose image based on type and blit scaled to DROP_SIZE
        img = None
        if self.type == "bomb":
            img = _IMG_BOMB
        elif self.type == "coin":
            img = _IMG_COIN
        else:
            img = _IMG_HEALTH

        if img:
            surf = pygame.transform.smoothscale(img, (DROP_SIZE, DROP_SIZE))
            screen.blit(surf, (self.x, self.y))
        else:
            # Fallback: draw a simple circle if image missing
            color = (200, 0, 0) if self.type == "bomb" else (212, 175, 55) if self.type == "coin" else (0, 200, 0)
            pygame.draw.circle(screen, color, self.rect.center, DROP_SIZE // 2)
