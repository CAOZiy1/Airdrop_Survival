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
PLAYER_WIDTH = 64
PLAYER_HEIGHT = 64
PLAYER_SPEED = 5

# 投掷物设置
DROP_SIZE = 48
DROP_TYPES = ["bomb", "coin", "health_pack"]
# Weights for DROP_TYPES selection. Higher means more likely.
# Default suggestion: bombs more frequent, coins medium, health packs rare.
DROP_WEIGHTS = [8, 3, 1]
