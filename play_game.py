import cv2
import pyautogui 
import pygetwindow as gw
import keyboard
import numpy as np
import time
import pytesseract

from config import *

# BAR_LEFT = 90
# BAR_TOP = 40
# BAR_RIGHT = 650
# BAR_BOTTOM = 120
# LAWN_LEFT = 40
# LAWN_TOP = 115
# LAWN_GRID_W = 80
# LAWN_GRID_H = 100
# LAWN_ROWS = 5
# LAWN_COLS = 9
# ZOMBIE_DETECT_LEFT = LAWN_LEFT - 25
# ZOMBIE_DETECT_TOP = LAWN_TOP - 50
# ZOMBIE_DETECT_RIGHT = LAWN_LEFT + LAWN_GRID_W * LAWN_COLS + 50
# ZOMBIE_DETECT_BOTTOM = LAWN_TOP + LAWN_GRID_H * LAWN_ROWS + 75

# SUN_THRESHOLD = 0.75
# PLANT_CARD_THRESHOLD = 0.9
# PLANT_THRESHOLD = 0.8
# ZOMBIE_THRESHOLD = 0.75

sun_template = cv2.imread('sun_template.png')
sun_h, sun_w, _ = sun_template.shape

peashooter_card_template = cv2.imread('peashooter_card_template.png')
# peashooter_card_h, peashooter_card_w, _ = peashooter_card_template.shape
sunflower_card_template = cv2.imread('sunflower_card_template.png')
# sunflower_card_h, sunflower_card_w, _ = sunflower_card_template.shape
wall_nut_card_template = cv2.imread('wall_nut_card_template.png')
# wall_nut_card_h, wall_nut_card_w, _ = wall_nut_card_template.shape
potato_mine_card_template = cv2.imread('potato_mine_card_template.png')
# potato_mine_card_h, potato_mine_card_w, _ = potato_mine_card_template.shape
cherry_bomb_card_template = cv2.imread('cherry_bomb_card_template.png')
# cherry_bomb_card_h, cherry_bomb_card_w, _ = cherry_bomb_card_template.shape

plant_card_templates = {
    'peashooter': peashooter_card_template,
    'sunflower': sunflower_card_template,
    'wall_nut': wall_nut_card_template,
    'potato_mine': potato_mine_card_template,
    'cherry_bomb': cherry_bomb_card_template
}

zombie_head_template = cv2.imread('zombie_head_template.png')
zombie_head_h, zombie_head_w, _ = zombie_head_template.shape
zombie_head_mask = cv2.imread('zombie_head_mask.png', cv2.IMREAD_GRAYSCALE)
zombie_head_template_2 = cv2.imread('zombie_head_template_2.png')
zombie_head_h2, zombie_head_w2, _ = zombie_head_template_2.shape
zombie_head_mask_2 = cv2.imread('zombie_head_mask_2.png', cv2.IMREAD_GRAYSCALE)
zombie_templates_and_masks = [
    (zombie_head_template, zombie_head_mask),
    (zombie_head_template_2, zombie_head_mask_2)
    ]


def collect_sun(full_screen, window):
    '''
    '''
    lawn_screen = full_screen[LAWN_TOP:LAWN_TOP + LAWN_GRID_H*5, LAWN_LEFT:LAWN_LEFT + LAWN_GRID_W*9]
    result = cv2.matchTemplate(lawn_screen, sun_template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= SUN_THRESHOLD)
    clicked_locations = []
    for pt in zip(*locations[::-1]):
        too_close = False
        for clicked in clicked_locations:
            if abs(pt[0] - clicked[0]) < sun_w and abs(pt[1] - clicked[1]) < sun_h:
                too_close = True
                break
        if too_close:
            continue
        center_x = pt[0] + sun_w // 2
        center_y = pt[1] + sun_h // 2
        pyautogui.click(window.left + LAWN_LEFT + center_x, window.top + LAWN_TOP + center_y)
        pyautogui.rightClick()
        clicked_locations.append((pt[0], pt[1]))
    return len(clicked_locations)

def find_zombies(full_screen):
    '''
    '''
    zombie_detection_screen = full_screen[ZOMBIE_DETECT_TOP:ZOMBIE_DETECT_BOTTOM, ZOMBIE_DETECT_LEFT:ZOMBIE_DETECT_RIGHT]
    combined_result = None
    for template, mask in zombie_templates_and_masks:
        result = cv2.matchTemplate(zombie_detection_screen, template, cv2.TM_CCOEFF_NORMED, mask=mask)
        combined_result = np.maximum(combined_result, result) if combined_result is not None else result
    locations = np.where(combined_result >= ZOMBIE_THRESHOLD)
    zombie_locations = []
    # _, value, _, _ = cv2.minMaxLoc(combined_result)

    for pt in zip(*locations[::-1]):
        same_zombie = False
        for zombie in zombie_locations:
            if abs(pt[0] - zombie[0]) < 100 and abs(pt[1] - zombie[1]) < 150:
                same_zombie = True
                break
        if same_zombie:
            continue
        center_x = pt[0] + 30
        center_y = pt[1] + 50
        zombie_locations.append((center_x, center_y))

    return zombie_locations

def convert_location_to_lawn_coordinates(location):
    '''
    将像素位置转换为坐标
    location: 僵尸在游戏区域内的坐标

    return: 僵尸在屏幕上的坐标列表
        row: 行号（0-4）
        col: 列号（0-8）
    '''
    row = location[1] // LAWN_GRID_H
    col = location[0] // LAWN_GRID_W
    return (row, col)

def update_zombies_tracker(zombie_locations, detected_zombies):
    '''
    '''
    for location in zombie_locations:
        same = False
        lawn_coordinates = convert_location_to_lawn_coordinates(location)
        for known_zombie in detected_zombies:
            if abs(location[0]-known_zombie['x']) < 100 and abs(location[1]-known_zombie['y']) < 100:
                same = True
                known_zombie['x'] = location[0]
                known_zombie['y'] = location[1]
                known_zombie['row'] = lawn_coordinates[0]
                known_zombie['col'] = lawn_coordinates[1]
                known_zombie['last_seen'] = time.time()
                break
        if not same:
            print(f"[ZOMBIE+] row={lawn_coordinates[0]} col={lawn_coordinates[1]} "
                f"at pixel=({location[0]}, {location[1]})")
            detected_zombies.append({'x': location[0], 'y': location[1], 
                'row': lawn_coordinates[0], 'col': lawn_coordinates[1], 
                'last_seen': time.time()
            })

    now = time.time()
    still_alive = []
    for z in detected_zombies:
        if now - z['last_seen'] >= ZOMBIE_CLEANUP_TIME:
            print(f"[ZOMBIE-] row={z['row']} col={z['col']} "
                f"last_seen={now - z['last_seen']:.1f}s ago")
        else:
            still_alive.append(z)
    detected_zombies[:] = still_alive

def initialize_plant_card_positions(full_screen, plant_card_templates):
    '''
    '''
    bar_screen = full_screen[BAR_TOP:BAR_BOTTOM, BAR_LEFT:BAR_RIGHT]
    top_left_positions = {}
    for plant_name, template in plant_card_templates.items():
        result = cv2.matchTemplate(bar_screen, template, cv2.TM_CCOEFF_NORMED)
        _, val, _, loc = cv2.minMaxLoc(result)
        # print(f"{plant_name}卡牌最高相似度: {val}") # debug
        if val >= PLANT_CARD_THRESHOLD:
            top_left_positions[plant_name] = (loc[0] + BAR_LEFT, loc[1] + BAR_TOP)
    return top_left_positions

def measure_card_brightness(full_screen, top_left_position, top_sample_height=8):
    '''
    '''
    x, y = top_left_position
    region = full_screen[y : y + top_sample_height, x : x + BAR_CARD_W]
    # region_screenshot = pyautogui.screenshot(region=(window.left + x, window.top + y, BAR_CARD_W, top_sample_height)) # debug: 截图查看选取区域是否正确
    # region_screenshot.save('card_brightness_region.png') # debug: 保存截图查看
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    brightness = np.mean(hsv[:,:,2])
    return brightness

def is_card_usable(full_screen, card_position):
    '''
    '''
    return measure_card_brightness(full_screen, card_position) >= CARD_BRIGHTNESS_THRESHOLD

def convert_lawn_coordinates_to_location(window, row, col):
    '''
    根据行列号计算格子中心坐标
    
    window: PvZ窗口对象
    row: 行号（0-4）
    col: 列号（0-8）

    return: 格子中心坐标 (x, y)
    '''
    grid_center_x = window.left + LAWN_LEFT + (col)*LAWN_GRID_W + LAWN_GRID_W//2
    grid_center_y = window.top + LAWN_TOP + (row)*LAWN_GRID_H + LAWN_GRID_H//2
    return grid_center_x, grid_center_y

def click_plant_card(window, plant_name, game_state):
    '''
    '''
    x, y = game_state['card_positions'][plant_name]
    pyautogui.click(window.left + x + BAR_CARD_W//2, window.top + y + BAR_CARD_H//2)

def place_plant(window, row, col, plant_name, game_state):
    '''
    '''
    x, y = convert_lawn_coordinates_to_location(window, row, col)
    pyautogui.click(x, y)
    pyautogui.rightClick()
    expires = time.time() + PLANT_EXPIRY[plant_name] if plant_name in PLANT_EXPIRY else None
    game_state['plants'][(row, col)] = {
        'plant_name': plant_name,
        'expired_at': expires
    }
    game_state['sun_count'] -= PLANT_COSTS[plant_name]

def cleanup_expired_plants(game_state):
    '''
    '''
    now = time.time()
    expired = [pos for pos, info in game_state['plants'].items()
               if info['expired_at'] is not None and now > info['expired_at']]
    for pos in expired:
        del game_state['plants'][pos]


def score_sunflower(row, col, game_state):
    '''

    row: (0-4)
    col: (0-8)
    '''
    score = 0
    # 种在靠左侧列加分
    score += (9-col) * 10 - 60
    # 游戏前期种植加分
    if game_state['elapsed'] <= 60:
        score += 10
    # 种在没有僵尸的行加分
    if not any(z['row'] == row for z in game_state['zombies']):
        score += 10
    # 种在已有一两个阳光植物的行逐渐减分
    sunflower_in_row = sum(
        1 for (r, c), plant in game_state['plants'].items()
        if plant in SUN_PLANTS and r == row
    )
    score -= sunflower_in_row * 25
    return score

def score_peashooter(row, col, game_state):
    '''
    
    row: (0-4)
    col: (0-8)
    '''
    score = 0
    # 种在靠左侧列加分
    score += (9-col) * 10 - 60
    # 种在有僵尸的行加分
    if any(z['row'] == row for z in game_state['zombies']):
        score += 30 
    # 种在僵尸较远的列加分（已经被上面两个覆盖）
    # 种在已有一两个远程攻击植物的行逐渐减分
    range_attack_in_row = sum(
        1 for (r, c), plant in game_state['plants'].items()
        if plant in RANGE_ATTACK_PLANTS and r == row
    )
    score -= range_attack_in_row * 10
    # 种在有防御植物的行加分
    if any(plant in DEFENSE_PLANTS and r == row for (r, c), plant in game_state['plants'].items()):
        score += 10
    # 种在灰烬植物右边减分
    ash_col = [c for (r, c), p in game_state['plants'].items() if r == row and p['plant_name'] in ASH_PLANTS]
    if ash_col and col > min(ash_col):
        score -= 50 
    return score

def score_wall_nut(row, col, game_state):
    score = 0
    # 种在有多个僵尸的行加分
    if sum(1 for z in game_state['zombies'] if z['row'] == row) >=2:
        score += 20
    # 种在有僵尸的行加分
    if any(z['row'] == row for z in game_state['zombies']):
        score += 10
    # 种在已有防御植物的行减分
    if any(plant in DEFENSE_PLANTS and r == row for (r, c), plant in game_state['plants'].items()):
        score -= 50
    # 种在有攻击型植物的行加分
    if any((plant in RANGE_ATTACK_PLANTS or plant in CLOSE_COMBAT_PLANTS)and r == row for (r, c), plant in game_state['plants'].items()):
        score += 20
    # 种在中间的列加分
    if 4 <= col <= 5:
        score += 10
    # 种在灰烬植物右边减分
    ash_col = [c for (r, c), p in game_state['plants'].items() if r == row and p['plant_name'] in ASH_PLANTS]
    if ash_col and col > min(ash_col):
        score -= 50
    return score

def score_potato_mine(row, col, game_state):
    score = 0
    # 游戏前期种植加分
    if game_state['elapsed'] <= 60:
        score += 30
    # 种植在距离僵尸大于等于4格的地方加分 小于等于4格的地方减分
    zombies_in_row = [z for z in game_state['zombies'] if z['row'] == row]
    if zombies_in_row:
        score += 20
        leftest_zombie_col = min(z['col'] for z in zombies_in_row)
        if leftest_zombie_col - col >= 4 and leftest_zombie_col - col <= 5:
            score += 10
        else:
            score -= 50
    # 种在防御植物左边减分
    lefest_defense_col = [c for (r, c), p in game_state['plants'].items() if r == row and p['plant_name'] in DEFENSE_PLANTS]
    if lefest_defense_col and col <= max(lefest_defense_col):
        score -= 50
    # 种在攻击植物左边减分（未来）
    return score

def score_cherry_bomb(row, col, game_state):
    score = 0 
    # 种在离家很近的僵尸旁边加分
    if any(z['row'] == row and z['col'] < 2 for z in game_state['zombies']):
        score += 50
    # 种在周围范围僵尸多的格子加分
    nearby_zombies = sum(1 for z in game_state['zombies'] if abs(z['row'] - row) <= 1 and abs(z['col'] - col) <= 1)
    score += nearby_zombies * 20
    return score

def decision_candidates(game_state):
    candidates = []
    for plant, scoring_func in SCORING_FUNCTIONS.items():
        for row in range(LAWN_ROWS):
            for col in range(LAWN_COLS):
                if (row, col) in game_state['plants']:
                    continue
                score = scoring_func(row, col, game_state)
                if score <= 0:
                    continue
                affordable = game_state['card_status'].get(plant, False)
                candidates.append({
                    'plant_name': plant,
                    'row': row,
                    'col': col,
                    'score': score,
                    'affordable': affordable
                })
    return candidates

def decide_action(game_state):
    candidates = decision_candidates(game_state)
    if not candidates:
        print("[DECIDE] no candidates")
        return None
    
    sorted_cands = sorted(candidates, key=lambda c: c['score'], reverse=True)
    print("[DECIDE] candidates:")
    for i, c in enumerate(sorted_cands[:3]):
        mark = '✓' if c['affordable'] else '✗'
        print(f"  {i+1}. {c['plant_name']:12s} @ ({c['row']},{c['col']}) "
              f"score={c['score']:3d} affordable={mark}")
    best_overall = max(candidates, key = lambda c : c['score'])
    # print(best_overall) # debug

    affordable_candidates = [c for c in candidates if c['affordable']]
    if not affordable_candidates:
        print(f"[DECIDE] wait — no affordable candidate "
              f"(best needs '{best_overall['plant_name']}')")
        return None
    best_affordable = max(affordable_candidates, key = lambda c : c['score'])
    # print(best_affordable) # debug

    score_gap = best_overall['score'] - best_affordable['score']
    if best_overall is best_affordable or score_gap <= WAIT_MARGIN:
        print(f"[DECIDE] → {best_affordable['plant_name']} @ "
              f"({best_affordable['row']},{best_affordable['col']}) "
              f"score={best_affordable['score']} gap={score_gap}")
        return best_affordable
    else:
        print(f"[DECIDE] wait — gap={score_gap} > margin={WAIT_MARGIN}, "
              f"saving for {best_overall['plant_name']}")
        return None


SCORING_FUNCTIONS = {
    'sunflower': score_sunflower,
    'peashooter': score_peashooter,
    'wall_nut': score_wall_nut,
    'potato_mine': score_potato_mine,
    'cherry_bomb': score_cherry_bomb
}

detected_zombies = []
# detected_zombies.append({'x': 500, 'y': 200, 'row': 2, 'col': 3, 'last_seen': time.time()})

placed_plants = {}
# placed_plants = {(2, 3): {'plant_name': 'peashooter', 'expires_at': None}}

windows = gw.getWindowsWithTitle('Plants vs. Zombies')
if not windows:
    print("Couldn't find PvZ window")
else:
    window = windows[0]
print("Please switch to PvZ window")
time.sleep(3)

full_screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
full_screen = cv2.cvtColor(np.array(full_screenshot), cv2.COLOR_RGB2BGR)
full_screenshot.save('full_screenshot.png')

card_positions = initialize_plant_card_positions(full_screen, plant_card_templates)
print("Plant Card Positions:", card_positions) # debug

crop = full_screen[ZOMBIE_DETECT_TOP:ZOMBIE_DETECT_BOTTOM, ZOMBIE_DETECT_LEFT:ZOMBIE_DETECT_RIGHT]
cv2.imwrite('zombie_detection_screenshot.png', crop) #debug

game_state = {
    'sun_count': 50,
    'start_time': time.time(),
    'elapsed': 0,
    'zombies': detected_zombies,
    'plants': placed_plants,
    'card_positions': card_positions,
    'card_status': {}
}

# brightness = measure_card_brightness(full_screen, card_positions['peashooter'])
# print("豌豆射手卡牌亮度:", brightness)

while not keyboard.is_pressed('esc'):
    
    sun_clicked = collect_sun(full_screen, window)
    game_state['sun_count'] += sun_clicked * 25

    zombie_locations = find_zombies(full_screen)
    update_zombies_tracker(zombie_locations, detected_zombies)
    
    for plant_name, card_pos in card_positions.items():
        brightness = measure_card_brightness(full_screen, card_pos)
        usable = brightness >= CARD_BRIGHTNESS_THRESHOLD
        game_state['card_status'][plant_name] = usable
        # print(f"  card {plant_name:12s} brightness={brightness:.1f} usable={usable}") # debug

    cleanup_expired_plants(game_state)

    action = decide_action(game_state)
    if action:
        click_plant_card(window, action['plant_name'], game_state)
        time.sleep(0.05)
        place_plant(window, action['row'], action['col'], action['plant_name'], game_state)

    card_status_str = ' '.join(
        f"{name[:2]}{'✓' if game_state['card_status'].get(name, False) else '✗'}"
        for name in game_state['card_positions']
    )
    print(f"[t={game_state['elapsed']:5.1f}s] "
        f"sun={game_state['sun_count']:4d} "
        f"zombies={len(game_state['zombies'])} "
        f"plants={len(game_state['plants'])} "
        f"cards:[{card_status_str}]")

    time.sleep(LOOP_SLEEP)
    game_state['elapsed'] = time.time() - game_state['start_time']

    full_screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
    full_screen = cv2.cvtColor(np.array(full_screenshot), cv2.COLOR_RGB2BGR)

print("程序已退出")