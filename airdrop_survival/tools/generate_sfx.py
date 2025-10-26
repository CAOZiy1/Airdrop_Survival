import os
import math
import wave
import struct
from typing import Iterable

import numpy as np

SR = 44100  # sample rate
AMP = 0.9   # max amplitude (fraction of int16)


def _ensure_out_dir() -> str:
    base = os.path.join(os.path.dirname(__file__), '..', 'assets', 'sounds')
    base = os.path.normpath(base)
    os.makedirs(base, exist_ok=True)
    return base


def _to_int16(x: np.ndarray) -> np.ndarray:
    x = np.clip(x, -1.0, 1.0)
    return (x * 32767.0).astype(np.int16)


def _normalize(x: np.ndarray, target: float = AMP) -> np.ndarray:
    peak = float(np.max(np.abs(x)) or 1.0)
    return x * (target / peak)


def _write_wav(path: str, samples: np.ndarray, sr: int = SR) -> None:
    data = _to_int16(samples)
    with wave.open(path, 'wb') as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)  # 16-bit
        wf.setframerate(sr)
        wf.writeframes(data.tobytes())


# --- SFX builders ---

def sfx_coin_pickup() -> np.ndarray:
    """Short rising blip: sine sweep 800->1600 Hz with quick ADSR."""
    dur = 0.15
    n = int(SR * dur)
    t = np.linspace(0, dur, n, endpoint=False)
    f0, f1 = 800.0, 1600.0
    # exponential sweep
    k = math.log(f1 / f0) / dur
    phase = 2 * math.pi * f0 * (np.exp(k * t) - 1.0) / k
    tone = np.sin(phase)
    # envelope (fast attack, medium decay)
    attack = int(0.01 * SR)
    release = int(0.04 * SR)
    sustain = n - attack - release
    env = np.concatenate([
        np.linspace(0, 1, attack, endpoint=False),
        np.ones(max(sustain, 0)),
        np.linspace(1, 0, release, endpoint=False),
    ])[:n]
    out = tone * env
    return _normalize(out)


def sfx_heal_pickup() -> np.ndarray:
    """Pleasant two-step chime: 600Hz then 900Hz, short crossfade."""
    d1, d2 = 0.12, 0.12
    n1, n2 = int(SR * d1), int(SR * d2)
    t1 = np.linspace(0, d1, n1, endpoint=False)
    t2 = np.linspace(0, d2, n2, endpoint=False)
    a1, a2 = 600.0, 900.0
    tone1 = np.sin(2 * np.pi * a1 * t1)
    tone2 = np.sin(2 * np.pi * a2 * t2)
    # envelopes
    def env(n: int) -> np.ndarray:
        a = int(0.01 * SR)
        r = int(0.04 * SR)
        s = n - a - r
        return np.concatenate([
            np.linspace(0, 1, max(a, 1), endpoint=False),
            np.ones(max(s, 0)),
            np.linspace(1, 0, max(r, 1), endpoint=False),
        ])[:n]
    y = np.concatenate([tone1 * env(n1), tone2 * env(n2)])
    return _normalize(y)


def sfx_bomb_explosion() -> np.ndarray:
    """Noise burst with exponential decay and mild low-pass smoothing."""
    dur = 0.5
    n = int(SR * dur)
    # white noise
    rng = np.random.default_rng(0)  # deterministic
    noise = rng.normal(0, 1, n)
    # exponential decay envelope
    tau = 0.25
    t = np.linspace(0, dur, n, endpoint=False)
    env = np.exp(-t / tau)
    y = noise * env
    # simple low-pass: moving average filter
    k = 200  # window size ~ low-pass
    if k > 1:
        kernel = np.ones(k) / k
        y = np.convolve(y, kernel, mode='same')
    return _normalize(y)


if __name__ == '__main__':
    out_dir = _ensure_out_dir()
    sounds = [
        ("coin_pickup.wav", sfx_coin_pickup()),
        ("heal_pickup.wav", sfx_heal_pickup()),
        ("bomb_explosion.wav", sfx_bomb_explosion()),
    ]
    for name, y in sounds:
        path = os.path.join(out_dir, name)
        _write_wav(path, y)
        print(f"wrote {path}")
