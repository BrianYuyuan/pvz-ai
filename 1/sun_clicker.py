import cv2
import pyautogui 
import pygetwindow as gw
import keyboard
import numpy as np
import time

windows = gw.getWindowsWithTitle('Plants vs. Zombies')
# print(windows)

if not windows:
    print('未找到PvZ窗口')
else:
    window = windows[0]
    # print (f"找到PvZ窗口: {window}")
    
template = cv2.imread('sun_template.png')
template_h, template_w, _ = template.shape

THRESHOLD = 0.75

print("请切换到PvZ窗口")
time.sleep(3)

while not keyboard.is_pressed('esc'):

    screenshot = pyautogui.screenshot(region=(window.left, window.top, window.width, window.height))
    screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)

    result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
    locations = np.where(result >= THRESHOLD)

    clicked_locations = []

    for pt in zip(*locations[::-1]):
        too_close = False
        for clicked in clicked_locations:
            if abs(pt[0] - clicked[0]) < template_w and abs(pt[1] - clicked[1]) < template_h:
                too_close = True
                break
        if too_close:
            continue
        center_x = pt[0] + template_w // 2
        center_y = pt[1] + template_h // 2

        pyautogui.click(center_x + window.left, center_y + window.top)
        clicked_locations.append((pt[0], pt[1]))
        print(f"点击阳光: ({center_x}, {center_y})")

    time.sleep(0.5)

print("程序已退出")