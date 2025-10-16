# src/settings.py

# 屏幕尺寸
WIDTH = 800
HEIGHT = 600

# 颜色定义
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
GREEN = (0, 255, 0)

# 玩家设置
PLAYER_WIDTH = 90
PLAYER_HEIGHT = 90
PLAYER_SPEED = 5

# 投掷物设置
DROP_SIZE = 48
DROP_TYPES = ["bomb", "coin", "health_pack"]
# Weights for DROP_TYPES selection. Higher means more likely.
# Default suggestion: bombs more frequent, coins medium, health packs rare.
DROP_WEIGHTS = [20, 5, 0.5]

# Drop speed settings (base random range and increase over time in pixels/frame)
# Drops will choose a base speed between DROP_BASE_SPEED_MIN and DROP_BASE_SPEED_MAX,
# then increase by DROP_SPEED_INCREASE_PER_MIN (pixels/frame) per minute of elapsed play time.
DROP_BASE_SPEED_MIN = 3
DROP_BASE_SPEED_MAX = 6
# Increase per-minute speed to make difficulty ramp faster
DROP_SPEED_INCREASE_PER_MIN = 1.5

# Multiplier applied to bomb speed (only bombs). Increase to make bombs fall noticeably faster.
BOMB_SPEED_MULTIPLIER = 1.8

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

# Spawn interval tuning (higher value => rarer spawns). This is used as the
# upper bound in `random.randint(1, interval)` where a result of 1 spawns a drop.
# The interval decreases over time to increase spawn frequency.
DROP_SPAWN_INTERVAL_BASE = 30
DROP_SPAWN_INTERVAL_MIN = 8
# Decrease the interval by this many units per minute (so smaller => more frequent)
DROP_SPAWN_DECREASE_PER_MIN = 3
