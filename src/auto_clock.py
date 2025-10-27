import time
from logging import exception

from numpy.f2py.auxfuncs import throw_error
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from dataclasses import dataclass

from src.login import login
from src.captcha import captcha, Selectors
from src.clock import clock

@dataclass
class Config:
    driver_path: str
    remote_url: str
    user_name: str
    user_password: str
    captcha_attempts: int = 3
    wait_time: int = 2

class AutoClock:
    def __init__(self, config: Config):
        self.driver_path = config.driver_path
        self.user_name = config.user_name
        self.user_password = config.user_password
        self.wait_time = config.wait_time
        self.captcha_attempts = config.captcha_attempts
        self.remote_url = config.remote_url

        try:
            self.driver = self.create_driver()
        except Exception as e:
            print(f"Create driver error: {e}")

    def create_driver(self):
        # 创建浏览器驱动
        opts = Options()
        opts.add_argument("--start-maximized")
        opts.add_argument("--enable-logging")
        opts.add_argument("--v=1")
        service = Service(executable_path=self.driver_path)
        driver = webdriver.Edge(service=service)

        print("create driver successfully")
        return driver

    def auto_login(self):
        try:
            print("DO AUTO CLOCK")
            print(f"打开URL：{self.remote_url}")
            self.driver.get(self.remote_url)
            result = login(self.driver, self.user_name, self.user_password, wait=self.wait_time)
            if result:
                print("已尝试提交登录表单，请在浏览器中确认是否成功。")
            else:
                print("自动登录执行失败，请检查选择器或页面加载。")
                return False

            time.sleep(2)
            WebDriverWait(self.driver, 1).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "#loginButton")))
            print("登录表单已消失，可能登录成功。")
            return True

        except Exception as e:
            throw_error(f"登录失败: {e}")
        finally:
            print("已完成登录操作；保留浏览器窗口。请手动关闭浏览器。")

    def auto_captcha(self):
        try:
            selectors = Selectors(
                canvas='#captchaImage',
                slider='.captcha-root .captcha-control-button',
                track='.captcha-control-wrap'
            )
            result = captcha(self.driver, selectors=selectors, max_attempts=self.captcha_attempts)
            if result:
                print(f"识别验证码成功。")
                return True
            else:
                print(f"尝试自动通过验证码失败。请手动进行操作或重试！")
                return False

        except Exception as e:
            throw_error(f"验证码验证失败。请手动进行操作或重试！")

    def do_clock(self):
        try:
            print("DO FINAL CLOCK")
            result = clock(self.driver)
            if result:
                return True
            else:
                return False
        except Exception as e:
            print("auto clock failed", e)
            return False

    def quit(self):
        self.driver.quit()

    def auto_clock(self):
        self.auto_login()
        self.auto_captcha()
        return self.do_clock()

    def run(self):
        result = self.auto_clock()
        print("流程结束，关闭浏览器驱动。")
        self.driver.quit()
        if result:
            time.sleep(5)
            print("最终结果：成功! 结束运行。")
            self.quit()
        else:
            throw_error("最终结果：失败! 请重试。")