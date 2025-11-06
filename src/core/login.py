from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.log import Log

def login(driver, user, pwd, wait=2):
    # 定位器
    username_selector = "input.textfield.userName"
    password_selector = "input.textfield.password"
    login_button_selector = "#loginButton"

    # 定位用户名和密码输入框
    waiter = WebDriverWait(driver, max(15, wait))
    try:
        username_el = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, username_selector)))
        password_el = waiter.until(EC.presence_of_element_located((By.CSS_SELECTOR, password_selector)))
    except TimeoutException:
        Log.waring("定位【用户名或密码输入框】超时，尝试使用备选 XPath 定位...")
        try:
            username_el = waiter.until(EC.presence_of_element_located((By.XPATH, "//input[contains(@class,'userName') or contains(@placeholder,'用户名') or contains(@title,'用户名')]")))
            password_el = waiter.until(EC.presence_of_element_located((By.XPATH, "//input[@type='password']")))
        except TimeoutException:
            Log.error("定位【用户名或密码输入框】失败。")
            raise Exception("定位【用户名或密码输入框】失败。")

    # 填写用户名和密码
    username_el.clear()
    username_el.send_keys(user)
    password_el.clear()
    password_el.send_keys(pwd)
    Log.info("填写用户名和密码成功.")

    # 点击登录按钮
    try:
        login_btn = waiter.until(EC.element_to_be_clickable((By.CSS_SELECTOR, login_button_selector)))
        login_btn.click()
    except TimeoutException:
        Log.waring("定位【登录按钮】超时，尝试使用备选 XPath 定位并点击...")
        try:
            btn = waiter.until(EC.element_to_be_clickable((By.XPATH, "//input[@type='button' and (contains(@value,'登') or contains(@value,'登录') or contains(@value,'登入'))]")))
            btn.click()
        except TimeoutException:
            Log.error("定位【登录按钮】失败，登录未执行。")
            raise Exception("定位【登录按钮】失败，登录未执行。")

    return True
