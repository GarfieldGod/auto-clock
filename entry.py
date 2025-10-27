import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.auto_clock import AutoClock, Config
from test.test import Test, TestConfig

DRIVER_PATH = "C:/Application/Edge_Driver/msedgedriver.exe"
if __name__ == '__main__':
    isTest = False

    if not isTest:
        remote_config = Config(
            DRIVER_PATH, # 浏览器驱动路径
            "https://kq.neusoft.com/login",
            "your username", # 用户名
            "your password", # 密码
            5 # 验证码重试次数
        )
        remote_clock = AutoClock(remote_config)
        remote_clock.run()
        time.sleep(5)
    else:
        test_config = TestConfig(
            DRIVER_PATH,
            "test/page",
            "test_page.html",
            8000,
            10,
            3
        )
        test_clock = Test(test_config)
        test_clock.run()