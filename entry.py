import os
import sys
import time
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from src.auto_clock import AutoClock, Config
from test.test import Test, TestConfig

DRIVER_PATH = "C:/Application/Edge_Driver/msedgedriver.exe"
if __name__ == '__main__':
    isTest = True

    if not isTest:
        remote_config = Config(
            DRIVER_PATH,
            "https://kq.neusoft.com/login",
            "luo_zhh",
            "God1351763110?",
            5
        )
        remote_clock = AutoClock(remote_config)
        remote_clock.run()
        time.sleep(3600)
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
