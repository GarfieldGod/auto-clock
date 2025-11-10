import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.log import Log
from src.utils.const import WebPath

def clock(driver, sign_in_button_selector = ".kq-btn.pt43.clear a:first-child", wait=2):
    if driver.current_url == WebPath.NeusoftKQPath:
        Log.info("开始进行最终Clock操作...")
        try:
            waiter = WebDriverWait(driver, max(15, wait))
            login_btn = waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sign_in_button_selector)))
            Log.info("定位Clock成功")
            login_btn.click()
            Log.info("点击Clock成功")
        except TimeoutException:
            Log.waring("定位超时，尝试使用备选 XPath 定位并点击...")
            try:
                btn = waiter.until(EC.element_to_be_clickable((By.XPATH,
                                                               "//input[@type='button' and (contains(@value,'打') or contains(@value,'打卡') or contains(@value,'sign in'))]")))
                btn.click()
            except TimeoutException:
                Log.error("定位失败，操作未执行。")
                return False
        time.sleep(5)
        return True
    else:
        return False