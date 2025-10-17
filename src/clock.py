from paddleocr import PaddleOCR
from PIL import ImageGrab
import cv2
import numpy as np
import pyautogui
import random
import time

# -------------------------- 初始化配置 --------------------------
# 初始化 PaddleOCR（使用中英文模型，关闭可视化）
ocr = PaddleOCR(use_textline_orientation=True, lang="ch")  # lang="ch" 支持中英文

# 随机延迟和鼠标操作参数（模拟人类行为，参考之前的防检测逻辑）
MIN_DELAY = 0.8
MAX_DELAY = 2.5
CLICK_OFFSET_RANGE = 3


# -------------------------- 工具函数 --------------------------
def capture_screen():
    """捕获全屏截图，返回 OpenCV 格式的图像（BGR 通道）"""
    time.sleep(random.uniform(MIN_DELAY / 2, MIN_DELAY))  # 截图前随机延迟
    screenshot = ImageGrab.grab()  # 全屏截图（PIL 格式，RGB 通道）
    screen_cv = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)  # 转为 OpenCV 的 BGR 格式
    return screen_cv


def find_text_positions(screen_img, target_text="打卡"):
    """使用 PaddleOCR 识别文字并定位目标文本的中心坐标"""
    # 调用 OCR 识别（返回结果为列表，每个元素包含文字和坐标）
    # 结果格式：[[[文本框坐标], [识别文字, 置信度]], ...]
    result = ocr.predict(screen_img)
    print("ORC END")

    positions = []
    if result is not None:
        for line in result:
            if line is None:
                continue
            # line 格式：[[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], (text, score)]
            text_box, (text, score) = line[0], line[1]
            # 筛选包含目标文本的结果（支持模糊匹配，如“打卡按钮”也会被识别）
            if target_text in text:
                # 计算文本框中心坐标（取四边形的中心）
                x_coords = [point[0] for point in text_box]
                y_coords = [point[1] for point in text_box]
                center_x = int((min(x_coords) + max(x_coords)) / 2)
                center_y = int((min(y_coords) + max(y_coords)) / 2)
                # 添加随机偏移，模拟人类点击偏差
                center_x += random.randint(-CLICK_OFFSET_RANGE, CLICK_OFFSET_RANGE)
                center_y += random.randint(-CLICK_OFFSET_RANGE, CLICK_OFFSET_RANGE)
                positions.append((center_x, center_y))
    return positions


def human_click(x, y):
    """模拟人类点击（平滑移动+随机延迟，复用之前的防检测逻辑）"""
    # 平滑移动鼠标（可复用之前的 smooth_move_mouse 函数）
    pyautogui.moveTo(x, y, duration=random.uniform(0.3, 0.8), tween=pyautogui.easeInOutQuad)
    # 点击前延迟
    time.sleep(random.uniform(0.2, 0.5))
    # 模拟按下/松开
    pyautogui.mouseDown()
    time.sleep(random.uniform(0.05, 0.15))
    pyautogui.mouseUp()
    # 点击后延迟
    time.sleep(random.uniform(MIN_DELAY, MAX_DELAY))


# -------------------------- 主逻辑 --------------------------
if __name__ == "__main__":
    try:
        # 1. 模拟人类操作前的延迟
        time.sleep(random.uniform(1.5, 3.0))
        # 2. 全屏截图
        screen_img = capture_screen()
        print("Get screen shoot.")
        # 3. 定位“打卡”文字
        target_positions = find_text_positions(screen_img, target_text="打卡")

        if not target_positions:
            print("未找到“打卡”文字")
        else:
            print(f"找到 {len(target_positions)} 处“打卡”，开始模拟点击...")
            for pos in target_positions:
                human_click(pos[0], pos[1])
    except Exception as e:
        print(f"操作异常：{e}")