"""Central game configuration.

Keep names stable; other modules import these directly. Values aim for clear, minimal knobs.
"""

# Screen
WIDTH = 800
HEIGHT = 600

# Player
PLAYER_WIDTH = 90
PLAYER_HEIGHT = 90
PLAYER_SPEED = 5
# Only affects drawing (not collision)
PLAYER_DRAW_SCALE = 1.25
# Shift player a bit upward on spawn for nicer framing
PLAYER_VERTICAL_RAISE = 25

# Drops
DROP_SIZE = 48
DROP_TYPES = ["bomb", "coin", "health_pack"]
# Relative spawn likelihood by type order above
DROP_WEIGHTS = [6, 4, 0.5]

# Base fall speed range (px/frame), then ramp per minute of play
DROP_BASE_SPEED_MIN = 2.2
DROP_BASE_SPEED_MAX = 4.4
DROP_SPEED_INCREASE_PER_MIN = 0.8

# Simple, explicit per-type speed multipliers
PER_TYPE_SPEED_MULTIPLIER = {
    "bomb": 1.5,
    "coin": 1.2,
    "health_pack": 1.4,
}

# Time scaling for early game: start slower, ramp to 1.0
DROP_TIME_SCALE_START = 0.8
DROP_TIME_SCALE_RAMP_SEC = 180
# Optional very-slow opening stage
DROP_TIME_STAGE1_SEC = 120
DROP_TIME_STAGE1_SCALE = 0.6

# Per-level overall speed multiplier increment (level 0 => 1.0)
LEVEL_SPEED_INCREASE_PER_LEVEL = 0.10

# Spawn frequency: higher interval => fewer spawns; decays over time
DROP_SPAWN_INTERVAL_BASE = 40
DROP_SPAWN_INTERVAL_MIN = 10
DROP_SPAWN_DECREASE_PER_MIN = 3

# Level(s)
LEVELS = [
    {
        "name": "Level 1",
        "time_seconds": 60,
        "coins_required": 20,
        "reward": {"type": "food can", "image": "can.png"},
    }
]
CAN_IMAGE = "can.png"

# Intro animation tuning
INTRO_DROP_PAUSE = True
INTRO_DROP_PAUSE_MS = 100
INTRO_DROP_TRIGGER_ADVANCE = 90

# Audio
SOUND_VOLUME = 1.0  # 0.0..1.0 master volume
SOUND_MUTED = False

# UX flow
REPLAY_INTRO_ON_RETURN = False
