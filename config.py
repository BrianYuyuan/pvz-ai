# ============================================================
# 窗口和游戏区域坐标（相对于窗口左上角）
# ============================================================
# 植物栏
BAR_LEFT = 90
BAR_TOP = 40
BAR_RIGHT = 650
BAR_BOTTOM = 120
BAR_CARD_W = 50
BAR_CARD_H = 70

# 草坪网格（用于种植定位）
LAWN_LEFT = 40
LAWN_TOP = 115
LAWN_GRID_W = 80
LAWN_GRID_H = 100
LAWN_ROWS = 5
LAWN_COLS = 9

# 僵尸检测区域（比草坪略大，因为僵尸会从右边走进来、走过左边）
ZOMBIE_DETECT_LEFT = LAWN_LEFT - 25
ZOMBIE_DETECT_TOP = LAWN_TOP - 50
ZOMBIE_DETECT_RIGHT = LAWN_LEFT + LAWN_GRID_W * LAWN_COLS + 50
ZOMBIE_DETECT_BOTTOM = LAWN_TOP + LAWN_GRID_H * LAWN_ROWS + 75

# 阳光计数显示区域（OCR用，V2再说）
# SUN_COUNT_X = ...
# SUN_COUNT_Y = ...

# ============================================================
# 模板匹配阈值
# ============================================================
CARD_BRIGHTNESS_THRESHOLD = 130
SUN_THRESHOLD = 0.75
PLANT_CARD_THRESHOLD = 0.7
PLANT_THRESHOLD = 0.8
ZOMBIE_THRESHOLD = 0.75

# ============================================================
# 僵尸追踪参数
# ============================================================
ZOMBIE_SAME_DISTANCE = 100      # 像素，小于这个距离认为是同一个僵尸
ZOMBIE_CLEANUP_TIME = 3         # 秒，超过没更新就从tracker删除

# ============================================================
# 主循环参数
# ============================================================
LOOP_SLEEP = 0.5                 # 秒，每轮主循环的间隔

# ============================================================
# 游戏常量（PvZ游戏固定的事实）
# ============================================================
SUN_VALUE = 25           # 单个阳光的默认价值
SUN_COUNT_INITIAL = 50           # 游戏开始时的阳光数

PLANT_COSTS = {
    'sunflower': 50,
    'peashooter': 100,
    'wall_nut': 50,
    'potato_mine': 25,
    'cherry_bomb': 150,
    'chomper': 150,
    'snow_pea': 175,
    'repeater': 200
}

PLANT_EXPIRY = {
    'potato_mine': 30,
    'squash': 15,
    'cherry_bomb': 2,
    'jalapeno': 2
}

SUN_PLANTS = ('sunflower', 'sun_shroom', 'twin_sunflower')
RANGE_ATTACK_PLANTS = ('peashooter', 'snow_pea', 'repeater')
ASH_PLANTS = ('cherry_bomb', 'potato_mine', 'doom_shroom', 'squash','jalapeno')
DEFENSE_PLANTS = ('wall_nut', 'tall_nut', 'pumpkin')
CLOSE_COMBAT_PLANTS = ('chomper', 'spikeweed', 'spikerock')

WAIT_MARGIN = 15
