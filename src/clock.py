from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def clock(driver, sign_in_button_selector = ".kq-btn.pt43.clear a:first-child", wait=2):
    if driver.current_url == "https://kq.neusoft.com/":
        print("开始进行终局操作...")
        try:
            waiter = WebDriverWait(driver, max(15, wait))
            login_btn = waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, sign_in_button_selector)))
            print("定位成功")
            login_btn.click()
        except TimeoutException:
            print("定位超时，尝试使用备选 XPath 定位并点击...")
            try:
                btn = waiter.until(EC.element_to_be_clickable((By.XPATH,
                                                               "//input[@type='button' and (contains(@value,'打') or contains(@value,'打卡') or contains(@value,'sign in'))]")))
                btn.click()
            except TimeoutException:
                print("定位失败，操作未执行。")
                return False
        return True
    else:
        return False