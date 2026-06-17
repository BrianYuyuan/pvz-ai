import cv2
import pyautogui 
import pygetwindow as gw
import keyboard
import numpy as np
import time

LAWN_LEFT_EDGE = 40
LAWN_TOP_EDGE = 115
LAWN_GRID_W = 80
LAWN_GRID_H = 100

BAR_LEFT_EDGE = 90
BAR_TOP_EDGE = 40
BAR_RIGHT_EDGE = 530
BAR_BOTTOM_EDGE = 120

PLANT_MATCH_THRESHOLD = 0.9

sun_template = cv2.imread('sun_template.png')
sun_h, sun_w, _ = sun_template.shape

peashooter_card_template = cv2.imread('peashooter_card_template.png')
peashooter_card_h, peashooter_card_w, _ = peashooter_card_template.shape
sunflower_card_template = cv2.imread('sunflower_card_template.png')
sunflower_card_h, sunflower_card_w, _ = sunflower_card_template.shape

def locate_lawn_coordinates(window, row, col):
    '''
    根据行列号计算格子中心坐标
    
    window: PvZ窗口对象
    row: 行号（0-4）
    col: 列号（0-8）

    return: 格子中心坐标 (x, y)
    '''
    grid_center_x = window.left + LAWN_LEFT_EDGE + (col)*LAWN_GRID_W + LAWN_GRID_W//2
    grid_center_y = window.top + LAWN_TOP_EDGE + (row)*LAWN_GRID_H + LAWN_GRID_H//2
    return grid_center_x, grid_center_y

def locate_bar_coordinates(window, index):
    pass

def choose_plant(window, plant_template):
    '''
    在工具栏中找到植物图标并点击选择
    
    window: PvZ窗口对象
    plant_template: 植物图标的模板图像
    '''
    bar_screenshot = pyautogui.screenshot(region=(window.left + BAR_LEFT_EDGE, window.top + BAR_TOP_EDGE, BAR_RIGHT_EDGE - BAR_LEFT_EDGE, BAR_BOTTOM_EDGE - BAR_TOP_EDGE))
    bar_screen = cv2.cvtColor(np.array(bar_screenshot), cv2.COLOR_RGB2BGR)
    result = cv2.matchTemplate(bar_screen, plant_template, cv2.TM_CCOEFF_NORMED)
    _, value, _, location = cv2.minMaxLoc(result)
    print(f"最高相似度: {value}")
    if value < PLANT_MATCH_THRESHOLD:
        print("未找到植物图标")
        return False
    else:
        return window.left + location[0] + BAR_LEFT_EDGE + plant_template.shape[1]//2, window.top + location[1] + BAR_TOP_EDGE + plant_template.shape[0]//2


windows = gw.getWindowsWithTitle('Plants vs. Zombies')
if not windows:
    print("未找到PvZ窗口")
else:
    window = windows[0]

print("请切换到PvZ窗口")
time.sleep(5)

# for row in range(0, 5):
#     for col in range(0, 9):
#         x, y = locate_coordinates(window, row, col)
#         pyautogui.moveTo(x, y)
#         time.sleep(0.5)

while not keyboard.is_pressed('esc'):

    sunflower_pos = choose_plant(window, sunflower_card_template)
    if sunflower_pos:
        pyautogui.click(sunflower_pos[0], sunflower_pos[1])
        time.sleep(0.1)
        x, y = locate_lawn_coordinates(window, 2, 2)
        pyautogui.click(x, y)
        print(f"种植向日葵: ({x}, {y})")

    time.sleep(1)
        
print("程序已退出")