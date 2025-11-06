import time
import traceback

from selenium import webdriver
from dataclasses import dataclass
from selenium.webdriver.common.by import By
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from src.utils.log import Log
from src.core.clock import clock
from src.core.login import login
from src.core.captcha import captcha, Selectors

@dataclass
class Config:
    driver_path: str
    remote_url: str
    user_name: str
    user_password: str
    captcha_attempts: int = 3
    tolerance: int = 5
    wait_time: int = 2

class AutoClock:
    def __init__(self, config: Config):
        self.driver_path = config.driver_path
        self.user_name = config.user_name
        self.user_password = config.user_password
        self.wait_time = config.wait_time
        self.captcha_attempts = config.captcha_attempts
        self.tolerance = config.tolerance
        self.remote_url = config.remote_url

        try:
            self.driver = self.create_driver()
        except Exception as e:
            Log.error(f"Create driver error: {e}")

    def create_driver(self):
        # 创建浏览器驱动
        opts = Options()
        opts.add_argument("--start-maximized")
        opts.add_argument("--enable-logging")
        opts.add_argument("--v=1")
        service = Service(executable_path=self.driver_path)
        driver = webdriver.Edge(service=service)

        Log.info("create driver successfully")
        return driver

    def auto_login(self):
        try:
            Log.info("DO AUTO CLOCK")
            self.driver.get(self.remote_url)
            Log.info(f"打开URL：{self.remote_url}")
            result = login(self.driver, self.user_name, self.user_password, wait=self.wait_time)
            if result:
                Log.info("已尝试提交登录表单。")
            else:
                info = "自动登录执行失败，请检查选择器或页面加载。"
                Log.error(info)
                raise Exception(info)

            time.sleep(2)
            WebDriverWait(self.driver, 3).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, "#loginButton")))
            Log.info("登录表单已消失，可能登录成功。")
            return True

        except TimeoutException as e:
            Log.error(f"等待到元素消失超时，登录状态未知")
            return False
        except Exception as e:
            info = f"登录失败: {e}"
            Log.error(info)
            raise Exception(info)
        finally:
            Log.info("登录流程结束; 保留浏览器窗口。")

    def auto_captcha(self):
        try:
            selectors = Selectors(
                canvas='#captchaImage',
                slider='.captcha-root .captcha-control-button',
                track='.captcha-control-wrap'
            )
            result = captcha(self.driver, selectors=selectors, max_attempts=self.captcha_attempts,tolerance=self.tolerance)
            if result:
                Log.info(f"识别验证码成功。")
                return True
            else:
                Log.error(f"尝试自动通过验证码失败。请手动进行操作或重试！")
                return False

        except Exception as e:
            tb = traceback.extract_tb(e.__traceback__)
            # 堆栈信息的最后一条是错误发生的位置
            if tb:
                last_frame = tb[-1]  # 最后一个栈帧是错误源头
                error_file = last_frame.filename  # 错误发生的文件名
                error_line = last_frame.lineno  # 错误发生的行号
                error_code = last_frame.line  # 错误发生的代码行
            else:
                error_file = "未知文件"
                error_line = "未知行号"
                error_code = "未知代码"

            # 记录包含错误行号的日志
            Log.error(f"验证码验证失败：{str(e)} | 错误位置：{error_file}:{error_line} | 代码：{error_code}")

            info = f"验证码验证失败。请手动进行操作或重试！{e}"
            Log.error(info)
            raise Exception(info)

    def do_clock(self):
        try:
            Log.info("DO FINAL CLOCK")
            result = clock(self.driver)
            if result:
                return True
            else:
                return False
        except Exception as e:
            Log.error(f"auto clock failed: {e}")
            return False

    def quit(self):
        self.driver.quit()

    def auto_clock(self):
        try:
            self.auto_login()
            self.auto_captcha()
            return self.do_clock()
        except Exception as e:
            return False

    def run(self):
        result = self.auto_clock()
        Log.info("流程结束，关闭浏览器驱动。")
        self.driver.quit()
        if result:
            time.sleep(5)
            Log.info("最终结果：成功! 结束运行。")
            return True
        else:
            Log.error("最终结果：失败! 请重试。")
            return False