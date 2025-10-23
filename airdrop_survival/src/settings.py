# src/settings.py

# 屏幕尺寸
WIDTH = 800
HEIGHT = 600


# 玩家设置
PLAYER_WIDTH = 90
PLAYER_HEIGHT = 90
PLAYER_SPEED = 5

# Visual tuning for player rendering (does not change collision rect)
# Multiply the drawn sprite size by this factor (1.0 = draw at rect size)
PLAYER_DRAW_SCALE = 1.25
# Vertical raise in pixels from the bottom when spawning the player (higher => player appears higher)
PLAYER_VERTICAL_RAISE = 25

MAX_HEALTH = 3

# 投掷物设置
DROP_SIZE = 48
DROP_TYPES = ["bomb", "coin", "health_pack"]
# Weights for DROP_TYPES selection. Higher means more likely.
# Adjusted to make bombs less frequent so player can prioritize coins.
# Order: [bomb, coin, health_pack]
# Previously bombs were very common; lower that weight relative to coins.
DROP_WEIGHTS = [6, 4, 0.5]

# Drop speed settings (base random range and increase over time in pixels/frame)
# Drops will choose a base speed between DROP_BASE_SPEED_MIN and DROP_BASE_SPEED_MAX,
# then increase by DROP_SPEED_INCREASE_PER_MIN (pixels/frame) per minute of elapsed play time.
DROP_BASE_SPEED_MIN = 2.2
DROP_BASE_SPEED_MAX = 4.4
# Increase per-minute speed to make difficulty ramp faster
# Lower ramp so drops speed up more gently over time
DROP_SPEED_INCREASE_PER_MIN = 0.8

# Multiplier applied to bomb speed (only bombs). Increase to make bombs fall noticeably faster.
BOMB_SPEED_MULTIPLIER = 1.5

# Speed multiplier behavior: if True, each drop type can have its own multiplier.
# If False, the single BOMB_SPEED_MULTIPLIER is applied to all drop types (legacy behavior).
USE_PER_TYPE_SPEED_MULTIPLIERS = True

# Per-type multipliers (used when USE_PER_TYPE_SPEED_MULTIPLIERS is True)
# These allow finer tuning: coins can be slightly slower or faster than bombs, etc.
COIN_SPEED_MULTIPLIER = 1.2
HEALTH_SPEED_MULTIPLIER = 1.4

# Time-scaling for drop speeds: start slightly slower and ramp to full speed
# DROP_TIME_SCALE_START: multiplier at t=0 (e.g. 0.8 => 80% speed at start)
# DROP_TIME_SCALE_RAMP_SEC: number of seconds to ramp to 1.0 (default 180s = 3min)
DROP_TIME_SCALE_START = 0.8
DROP_TIME_SCALE_RAMP_SEC = 180
# First stage: make the first N seconds even slower (e.g. 1-2 minutes)
# DROP_TIME_STAGE1_SEC: duration of the initial slower stage (seconds)
# DROP_TIME_STAGE1_SCALE: multiplier used during stage1 (e.g. 0.6 => 60% speed)
DROP_TIME_STAGE1_SEC = 120
DROP_TIME_STAGE1_SCALE = 0.6

# Per-level base speed increase (e.g. 0.10 means +10% base speed per level)
LEVEL_SPEED_INCREASE_PER_LEVEL = 0.10

# Spawn interval tuning (higher value => rarer spawns). This is used as the
# upper bound in `random.randint(1, interval)` where a result of 1 spawns a drop.
# The interval decreases over time to increase spawn frequency.
# Spawn interval tuning: higher value => rarer spawns. Increase base to
# reduce overall spawn frequency slightly so coins are easier to notice.
DROP_SPAWN_INTERVAL_BASE = 40
DROP_SPAWN_INTERVAL_MIN = 10
# Decrease the interval by this many units per minute (so smaller => more frequent)
DROP_SPAWN_DECREASE_PER_MIN = 3


# Level configuration: list of dicts with 'name', 'time_seconds', 'coins_required', 'reward'
# reward can be a dict describing what the player receives when meeting the coin goal
# First level: collect 20 coins before time runs out to get a food can
LEVELS = [
	{
		'name': 'Level 1',
		'time_seconds': 60,  # 60 seconds for first level
		'coins_required': 20,
		'reward': {
			'type': 'food_can',
			'image': 'can.png'
		}
	}
]

# Name of can image in assets (UI will try to load this)
CAN_IMAGE = 'can.png'

# Intro animation tuning
# If True, the plane will pause at each drop node so drops have time to fall
INTRO_DROP_PAUSE = True
# Pause duration in milliseconds when the plane reaches a drop node
INTRO_DROP_PAUSE_MS = 100
# Advance drop triggers by this many pixels (positive = trigger earlier)
INTRO_DROP_TRIGGER_ADVANCE = 90

# Global sound settings
# Master volume applied to all sounds (0.0 = silent, 1.0 = full)
SOUND_VOLUME = 1.0
# Mute flag: when True all sounds will be silenced regardless of SOUND_VOLUME
SOUND_MUTED = False
