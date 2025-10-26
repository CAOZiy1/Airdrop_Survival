# src/drop.py

from __future__ import annotations

import os
import random
from typing import Optional

import pygame

from settings import (
    WIDTH,
    DROP_SIZE,
    DROP_TYPES,
    DROP_WEIGHTS,
    DROP_BASE_SPEED_MIN,
    DROP_BASE_SPEED_MAX,
    DROP_SPEED_INCREASE_PER_MIN,
    DROP_TIME_SCALE_START,
    DROP_TIME_SCALE_RAMP_SEC,
    DROP_TIME_STAGE1_SEC,
    DROP_TIME_STAGE1_SCALE,
)
from settings import PER_TYPE_SPEED_MULTIPLIER

# Module-level image cache (originals)
_IMG_BOMB: Optional[pygame.Surface] = None
_IMG_COIN: Optional[pygame.Surface] = None
_IMG_HEALTH: Optional[pygame.Surface] = None

# Module-level scaled cache (resized to current DROP_SIZE)
_SCALED_SIZE: Optional[int] = None
_BOMB_SCALED: Optional[pygame.Surface] = None
_COIN_SCALED: Optional[pygame.Surface] = None
_HEALTH_SCALED: Optional[pygame.Surface] = None

# Module-level sound cache (initialized by init_sounds)
_COIN_SOUND: Optional[pygame.mixer.Sound] = None
_BOMB_SOUND: Optional[pygame.mixer.Sound] = None
_HEAL_SOUND: Optional[pygame.mixer.Sound] = None
_SUCCESS_SOUND: Optional[pygame.mixer.Sound] = None
_FAIL_SOUND: Optional[pygame.mixer.Sound] = None

def init_sounds() -> None:
    """Initialize mixer (if needed) and load pickup/explosion sounds from assets/sounds."""
    global _COIN_SOUND, _BOMB_SOUND, _HEAL_SOUND, _SUCCESS_SOUND, _FAIL_SOUND

    if not pygame.mixer.get_init():
        try:
            pygame.mixer.init()
        except Exception:
            # If mixer fails to init, leave sounds as None.
            return

    base = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sounds')

    # apply global volume/mute from settings
    try:
        from settings import SOUND_VOLUME, SOUND_MUTED
        sound_volume = float(SOUND_VOLUME)
        sound_muted = bool(SOUND_MUTED)
    except Exception:
        sound_volume = 1.0
        sound_muted = False

    def _vol(v: float) -> float:
        return 0.0 if sound_muted else max(0.0, min(1.0, float(v) * sound_volume))

    def _load(name: str, vol: float = 0.8) -> Optional[pygame.mixer.Sound]:
        for ext in ('.wav', '.mp3'):
            p = os.path.join(base, name + ext)
            if os.path.exists(p):
                try:
                    s = pygame.mixer.Sound(p)
                    s.set_volume(vol)
                    return s
                except Exception:
                    continue
        return None

    _COIN_SOUND = _load('coin_pickup', vol=_vol(0.7))
    _BOMB_SOUND = _load('bomb_explosion', vol=_vol(1.0))
    _HEAL_SOUND = _load('heal_pickup', vol=_vol(0.8))
    # optional end-of-level stingers (short sfx; main ending music is handled in game.py)
    _SUCCESS_SOUND = _load('success', vol=_vol(0.9))
    _FAIL_SOUND = _load('failure', vol=_vol(0.9))

def play_coin() -> None:
    if _COIN_SOUND:
        try:
            _COIN_SOUND.play()
        except Exception:
            pass

def play_bomb() -> None:
    if _BOMB_SOUND:
        try:
            _BOMB_SOUND.play()
        except Exception:
            pass

def play_heal() -> None:
    if _HEAL_SOUND:
        try:
            _HEAL_SOUND.play()
        except Exception:
            pass

def play_success() -> None:
    if _SUCCESS_SOUND:
        try:
            _SUCCESS_SOUND.play()
        except Exception:
            pass


def play_failure() -> None:
    if _FAIL_SOUND:
        try:
            _FAIL_SOUND.play()
        except Exception:
            pass

def _load_images() -> None:
    """Load original images into cache (no scaling)."""
    global _IMG_BOMB, _IMG_COIN, _IMG_HEALTH
    base = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', 'assets'))

    def _load_img(filename: str) -> Optional[pygame.Surface]:
        path = os.path.join(base, filename)
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            return None

    _IMG_BOMB = _load_img('bomb.png')
    _IMG_COIN = _load_img('coin.png')
    _IMG_HEALTH = _load_img('health_pack.png')

def _ensure_scaled() -> None:
    """Ensure scaled surfaces match current DROP_SIZE (compute once)."""
    global _SCALED_SIZE, _BOMB_SCALED, _COIN_SCALED, _HEALTH_SCALED
    if _SCALED_SIZE == DROP_SIZE:
        return
    _SCALED_SIZE = DROP_SIZE

    def _scale(img: Optional[pygame.Surface]) -> Optional[pygame.Surface]:
        if not img:
            return None
        try:
            return pygame.transform.smoothscale(img, (DROP_SIZE, DROP_SIZE))
        except Exception:
            return None

    _BOMB_SCALED = _scale(_IMG_BOMB)
    _COIN_SCALED = _scale(_IMG_COIN)
    _HEALTH_SCALED = _scale(_IMG_HEALTH)


class Drop:
    def __init__(self, elapsed_seconds: float = 0.0, level_speed_multiplier: float = 1.0) -> None:
        # Lazy-load images and compute scaled surfaces
        if _IMG_BOMB is None and _IMG_COIN is None and _IMG_HEALTH is None:
            _load_images()
        _ensure_scaled()

        # Spawn across the width
        self.x: float = float(random.randint(0, max(0, WIDTH - DROP_SIZE)))
        self.y: float = 0.0

        # Base speed with global increase over elapsed time (per minute)
        base = random.uniform(DROP_BASE_SPEED_MIN, DROP_BASE_SPEED_MAX)
        increase = (elapsed_seconds / 60.0) * DROP_SPEED_INCREASE_PER_MIN

        # Time scaling: stage 1 fixed scale, then ramp to 1.0 by DROP_TIME_SCALE_RAMP_SEC
        if elapsed_seconds <= DROP_TIME_STAGE1_SEC:
            time_scale = DROP_TIME_STAGE1_SCALE
        else:
            if DROP_TIME_SCALE_RAMP_SEC > DROP_TIME_STAGE1_SEC:
                t_after = max(0.0, elapsed_seconds - DROP_TIME_STAGE1_SEC)
                ramp_duration = float(DROP_TIME_SCALE_RAMP_SEC - DROP_TIME_STAGE1_SEC)
                frac_t = min(1.0, t_after / ramp_duration) if ramp_duration > 0 else 1.0
                time_scale = DROP_TIME_SCALE_START + (1.0 - DROP_TIME_SCALE_START) * frac_t
            else:
                time_scale = 1.0

        speed = (base + increase) * time_scale

        # Weighted type selection (fallback to uniform if weights invalid)
        try:
            drop_type = random.choices(DROP_TYPES, weights=DROP_WEIGHTS, k=1)[0]
        except Exception:
            drop_type = random.choice(DROP_TYPES)

        # Per-type speed multiplier (defaults to 1.0 if type not found)
        try:
            speed *= float(PER_TYPE_SPEED_MULTIPLIER.get(drop_type, 1.0))
        except Exception:
            pass

        # Per-level multiplier last
        try:
            speed *= float(level_speed_multiplier)
        except Exception:
            pass

        self.speed: float = float(speed)
        self.type: str = drop_type
        self.rect = pygame.Rect(int(self.x), int(self.y), DROP_SIZE, DROP_SIZE)

    def update(self) -> None:
        self.y += self.speed
        self.rect.y = int(self.y)

    def draw(self, screen: pygame.Surface) -> None:
        # Choose cached, pre-scaled surface
        if self.type == 'bomb':
            surf = _BOMB_SCALED
            color = (200, 0, 0)
        elif self.type == 'coin':
            surf = _COIN_SCALED
            color = (212, 175, 55)
        else:
            surf = _HEALTH_SCALED
            color = (0, 200, 0)

        if surf:
            screen.blit(surf, (int(self.x), int(self.y)))
        else:
            # Fallback: simple circle if image missing
            pygame.draw.circle(screen, color, self.rect.center, DROP_SIZE // 2)
