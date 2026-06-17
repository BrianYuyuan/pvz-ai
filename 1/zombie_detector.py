import cv2
import pyautogui 
import pygetwindow as gw
import keyboard
import numpy as np
import time

from config import *

LAWN_LEFT_EDGE = 40
LAWN_TOP_EDGE = 115
LAWN_GRID_W = 80
LAWN_GRID_H = 100

BAR_LEFT_EDGE = 90
BAR_TOP_EDGE = 40
BAR_RIGHT_EDGE = 650
BAR_BOTTOM_EDGE = 120

ZOMBIE_MATCH_THRESHOLD = 0.75

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

def find_zombies(window):
    '''
    在游戏区域内寻找普通僵尸
    window: PvZ窗口对象

    '''
    lawn_screenshot = pyautogui.screenshot(region=(window.left + LAWN_LEFT_EDGE - 25, window.top + LAWN_TOP_EDGE - 50, LAWN_GRID_W*9 + 50, LAWN_GRID_H*5 + 100))
    lawn_screen = cv2.cvtColor(np.array(lawn_screenshot), cv2.COLOR_RGB2BGR)
    combined_result = None
    for template, mask in zombie_templates_and_masks:
        result = cv2.matchTemplate(lawn_screen, template, cv2.TM_CCOEFF_NORMED, mask=mask)
        combined_result = np.maximum(combined_result, result) if combined_result is not None else result
    locations = np.where(combined_result >= ZOMBIE_MATCH_THRESHOLD)
    zombie_locations = []

    _, value, _, _ = cv2.minMaxLoc(combined_result)
    print(f"匹配到的僵尸最高相似度: {value}")

    for pt in zip(*locations[::-1]):
        same_zombie = False
        for zombie in zombie_locations:
            if abs(pt[0] - zombie[0]) < 100 and abs(pt[1] - zombie[1]) < 150:
                same_zombie = True
                break
        if same_zombie:
            continue
        center_x = pt[0] + 25
        center_y = pt[1] + 25
        zombie_locations.append((center_x, center_y))

    return zombie_locations

def convert_to_lawn_coordinates(location):
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
        lawn_coordinates = convert_to_lawn_coordinates(location)
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
            detected_zombies.append({'x': location[0], 'y': location[1], 'row': lawn_coordinates[0], 'col': lawn_coordinates[1], 'last_seen': time.time()})

    detected_zombies[:] = [z for z in detected_zombies if time.time() - z['last_seen'] < 5]

windows = gw.getWindowsWithTitle('Plants vs. Zombies')
if not windows:
    print("未找到PvZ窗口")
else:
    window = windows[0]

print("请切换到PvZ窗口")
time.sleep(3)

lawn_screenshot = pyautogui.screenshot(region=(window.left + LAWN_LEFT_EDGE - 25, window.top + LAWN_TOP_EDGE - 50, LAWN_GRID_W*9 + 50, LAWN_GRID_H*5 + 100))
lawn_screenshot.save('lawn_screenshot.png') # debug: 保存截图查看

bar_screenshot = pyautogui.screenshot(region=(window.left + BAR_LEFT_EDGE, window.top + BAR_TOP_EDGE, BAR_RIGHT_EDGE - BAR_LEFT_EDGE, 8))
bar_screenshot.save('bar_screenshot.png')

detected_zombies = []
# detected_zombies.append({'x': 500, 'y': 200, 'row': 2, 'col': 3, 'last_seen': time.time()})

while not keyboard.is_pressed('esc'):

    zombie_locations = find_zombies(window)
    update_zombies_tracker(zombie_locations, detected_zombies)
    print(detected_zombies)
    time.sleep(0.5)

print("程序已退出")


