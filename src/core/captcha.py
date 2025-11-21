import os
import cv2
import numpy as np
import time, base64, io, math, random

from PIL import Image
from datetime import datetime
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait

from src.utils.log import Log
from src.utils.const import AppPath, WebPath

# ---------------------------------------------------------------------------------------------------获取图片
def dataurl_to_cv2(data_url):
    header, b64 = data_url.split(',', 1)
    img_bytes = base64.b64decode(b64)
    pil = Image.open(io.BytesIO(img_bytes)).convert('RGB')
    arr = np.array(pil)[:, :, ::-1]
    return arr

def png_bytes_to_cv2(png_bytes):
    pil = Image.open(io.BytesIO(png_bytes)).convert('RGB')
    arr = np.array(pil)[:, :, ::-1]
    return arr

def get_canvas_dataurl(driver, selector):
    script = """
    var el = document.querySelector(arguments[0]);
    if (!el) return null;
    try {
      if (el.toDataURL) return el.toDataURL('image/png');
      if (el.tagName && el.tagName.toLowerCase() === 'img') return el.src;
      return null;
    } catch(e) { return null; }
    """
    return driver.execute_script(script, selector)

def element_screenshot_bytes(driver, selector):
    try:
        we = driver.find_element(By.CSS_SELECTOR, selector)
        return we.screenshot_as_png
    except Exception:
        return None

def get_image(driver, canvas_sel):
    dataurl = get_canvas_dataurl(driver, canvas_sel)
    if dataurl:
        try:
            img = dataurl_to_cv2(dataurl)
            Log.info("使用 dataURL 获取图片")
        except Exception as e:
            Log.waring(f"dataURL 解析失败: {e}")
            img = None
    else:
        img = None

    if img is None:
        png = element_screenshot_bytes(driver, canvas_sel)
        if png:
            img = png_bytes_to_cv2(png)
            Log.info("使用元素截图获取图片")
            return img
        else:
            Log.error("无法获取验证码画面（dataURL 失败且元素截图失败）。")
            return None
    else:
        return img
# ---------------------------------------------------------------------------------------------------获取角度
def estimate_angle_pca(cv_img):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    ys, xs = np.where(edges > 0)
    if len(xs) < 20:
        return None
    coords = np.vstack([xs, ys]).T.astype(np.float32)
    coords_cent = coords - coords.mean(axis=0)
    cov = np.cov(coords_cent, rowvar=False)
    vals, vecs = np.linalg.eig(cov)
    principal = vecs[:, np.argmax(vals)]
    angle = math.degrees(math.atan2(principal[1], principal[0]))
    return angle

def estimate_angle_hough(cv_img):
    gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    lines = cv2.HoughLines(edges, 1, np.pi/180, 120)
    if lines is None:
        return None
    angles = []
    for l in lines[:,0]:
        theta = l[1]
        angle = math.degrees(theta) - 90
        angles.append(angle)
    if not angles:
        return None
    return float(np.median(angles))

def estimate_angle_normal(img):
    # 粗粒度旋转对比 (示例：按 10° 样本选择锐度最佳)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    best = None;
    best_score = -1e9
    for a in range(0, 360, 10):
        M = cv2.getRotationMatrix2D((img.shape[1] / 2, img.shape[0] / 2), a, 1.0)
        rot = cv2.warpAffine(gray, M, (img.shape[1], img.shape[0]), flags=cv2.INTER_LINEAR,
                             borderMode=cv2.BORDER_REPLICATE)
        score = cv2.Laplacian(rot, cv2.CV_64F).var()
        if score > best_score:
            best_score = score
            best = a
    angle = best
    return angle

def correct_angle_with_semantics(cv_img, angle):
    h, w = cv_img.shape[:2]
    top_half = cv_img[:h // 2, :]
    bottom_half = cv_img[h // 2:, :]

    # 计算图片上下两部分亮度均值, 区别天空与地面）
    top_brightness = cv2.cvtColor(top_half, cv2.COLOR_BGR2GRAY).mean()
    bottom_brightness = cv2.cvtColor(bottom_half, cv2.COLOR_BGR2GRAY).mean()

    if top_brightness < bottom_brightness - 10:
        angle = (angle + 180) % 360
    return angle

def normalize_angle(angle):
    return ((angle + 180) % 360) - 180

def estimate_angle(img):
    angle = estimate_angle_pca(img)
    Log.info(f"PCA 检测角度: {angle}")
    if angle is None:
        angle = estimate_angle_hough(img)
        Log.info(f"Hough 检测角度: {angle}")
    if angle is None:
        angle = estimate_angle_normal(img)
        Log.info(f"normal 检测角度: {angle}")

    angle = correct_angle_with_semantics(img, angle)
    Log.info(f"根据亮度分布修正角度: {angle}")

    angle = normalize_angle(angle)
    Log.info(f"估计图像主方向角度: {angle}")
    return angle

# ---------------------------------------------------------------------------------------------------执行滑动
def dynamic_adjust_drag(actions, driver, slider_elem, track_sel, canvas_sel, max_steps=20, tolerance=3):
    actions.click_and_hold(slider_elem).perform()
    moved = 0
    track_w = driver.execute_script("var el=document.querySelector(arguments[0]); if(!el) return 0; return el.getBoundingClientRect().width;",track_sel)
    max_possible_x = int(track_w) if track_w else 300  # 轨道最大宽度
    correct_direction = 1  # 1:向右为正确方向；-1:向左为正确方向（默认向右）

    for step in range(max_steps):
        # 计算当前角度
        current_angle = None
        try:
            img = get_image(driver, canvas_sel)
            current_angle = estimate_angle(img)
        except Exception as e:
            Log.waring(f"角度计算失败：{e}")

        # 角度达标则停止
        if current_angle is not None and abs(current_angle) <= tolerance:
            Log.info(f"角度已达标（{current_angle:.1f}°），停止拖动")
            break
        else:
            Log.info(f"角度未达标（{current_angle:.1f}°），进行拖动")

        if current_angle is not None:
            abs_angle = abs(current_angle)
            # 步长基数：角度越大，步长越大
            if abs_angle > 30:
                step_base = random.randint(10, 15)
            elif abs_angle > 20:
                step_base = random.randint(5, 10)
            elif abs_angle > 10:
                step_base = random.randint(2, 5)
            elif abs_angle > 5:
                step_base = random.randint(1, 2)
            else:
                step_base = 1
            # 步长方向：基于首次滑动判断的正确方向
            step_dx = correct_direction * step_base
        else:
            # 角度未知，按正确方向滑动
            step_dx = correct_direction * random.randint(5, 10)

        # 限制步长范围（不超过轨道边界）
        step_dx = max(-moved, min(step_dx, max_possible_x - moved))  # 不超出轨道
        step_dx = step_dx if abs(step_dx) >= 1 else correct_direction * 1  # 至少1px

        # 执行拖动
        actions.move_by_offset(step_dx, random.uniform(-2, 2)).perform()
        moved += step_dx

        img = get_image(driver, canvas_sel)
        new_angle = estimate_angle(img)
        # 判断方向（基于角度变化）（仅为低角度时判断）
        if new_angle is not None and current_angle is not None and abs(new_angle) < 10:
            Log.info("进入低角度检测")
            # 计算首次滑动后的角度变化（绝对值）
            angle_change = abs(current_angle) - abs(new_angle)
            if angle_change < 0:
                # 向右滑动后角度变大→正确方向为向左（-1）
                correct_direction = -1
                Log.info(f"滑动后角度增大（{abs(current_angle):.1f}°→{abs(new_angle):.1f}°），正确方向为向左")
            else:
                # 向右滑动后角度变小→正确方向为向右（1）
                correct_direction = 1
                Log.info(f"滑动后角度减小（{abs(current_angle):.1f}°→{abs(new_angle):.1f}°），正确方向为向右")

        # 动态调整延迟（角度小则延迟长）
        if current_angle is not None:
            base_delay = 0.03
            max_delay = 0.2
            max_angle = 90
            normalized_angle = min(abs(current_angle), max_angle)
            sleep_per_step = base_delay + (max_angle - normalized_angle) / max_angle * (max_delay - base_delay)
        else:
            sleep_per_step = 0.05 + random.uniform(0, 0.03)
        sleep_per_step += random.uniform(-0.01, 0.02)
        sleep_per_step = max(0.02, sleep_per_step)
        time.sleep(sleep_per_step)

    return moved

# ---------------------------------------------------------------------------------------------------执行验证流程
@dataclass
class Selectors:
    canvas: str
    slider: str
    track: str

def captcha(driver, selectors, max_attempts=3, tolerance=3):
    Log.info(f"进入验证流程...")
    canvas_sel=selectors.canvas
    slider_sel=selectors.slider
    track_sel=selectors.track

    try:
        wait = WebDriverWait(driver, 20)
        wait.until(lambda d: d.execute_script("return !!document.querySelector(arguments[0])", canvas_sel))
        Log.info(f"已定位验证码画布...")
    except Exception as e:
        info = f"验证失败, 未查询到画布:{e}"
        Log.error(info)
        return False, info

    for attempt in range(max_attempts):
        Log.info(f"----------------------------[({attempt + 1}/{max_attempts}) 尝试获取验证码图片...]----------------------------")

        # 执行人类样式拖动
        actions = ActionChains(driver)
        slider = driver.find_element(By.CSS_SELECTOR, slider_sel)
        actual_x = dynamic_adjust_drag(
            actions,
            driver,
            slider,
            track_sel,
            canvas_sel,
            max_steps=50,
            tolerance=tolerance
        )

        screenshot_file_name = f"{datetime.now().strftime('%Y_%m_%d_%H_%M_%S_%f')}_debug_canvas_attempt_{attempt + 1}"
        screenshot_file_path = f"{AppPath.ScreenshotRoot}/{screenshot_file_name}.png"
        try:
            if not os.path.exists(AppPath.ScreenshotRoot):
                os.makedirs(AppPath.ScreenshotRoot, exist_ok=True)
            driver.find_element(By.CSS_SELECTOR, canvas_sel).screenshot(screenshot_file_path)
        except Exception as e:
            Log.error(f"验证码截图失败: {e}")

        # 松开滑块前停顿
        time.sleep(0.1 + random.random() * 0.15)
        actions.release().perform()

        Log.info(f"实际拖动距离：{actual_x}px")

        time.sleep(2)
        time.sleep(1.2 + random.random()*0.8)

        result = False
        Log.info(f"当前页面为: {driver.current_url}")
        if driver.current_url == WebPath.NeusoftKQPath:
            result = True

        # 自定义检测方法：检查成功 DOM class 或 AJAX 返回（可扩展）
        # result = driver.execute_script("return (!!document.querySelector('.captcha-state .captcha-state-icon-success') && document.querySelector('.captcha-state .captcha-state-icon-success').offsetParent !== null);")
        Log.info(f"检测验证结果: {result}")
        if result:
            Log.info(f"----------------------------[({attempt + 1}/{max_attempts}) 验证码通过，继续后续流程]----------------------------")
            if os.path.exists(screenshot_file_path):
                os.rename(screenshot_file_path, f"{AppPath.ScreenshotRoot}/{screenshot_file_name + 'success'}.png")
            return True, None
        else:
            Log.info(f"----------------------------[({attempt + 1}/{max_attempts}) 此次尝试未通过，保存截图供分析并重试]----------------------------")
            if os.path.exists(screenshot_file_path):
                os.rename(screenshot_file_path, f"{AppPath.ScreenshotRoot}/{screenshot_file_name + 'failed'}.png")

    Log.error("重试结束，未通过验证码。请查看保存的截图与后端日志。")
    return False, "重试结束，未通过验证码。请查看保存的截图与后端日志。"