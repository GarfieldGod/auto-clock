import os
import json
import sys

from platformdirs import user_data_dir
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.utils.log import Log
from test.test import run_test
from src.core.auto_clock import AutoClock, Config
from src.utils.const import Key

DataRoot = user_data_dir("data", "auto-clock")

class ClockManager:
    def __init__(self):
        try:
            if not os.path.exists(f"{DataRoot}\\data.json"):
                self.status = False
                self.error = f"{DataRoot}\\data.json does not exist."
                return

            with open(f"{DataRoot}\\data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                ok = ClockManager.check_data(data)
                if not ok:
                    raise Exception("Unknow Error")
                self.user_name = data[Key.UserName]
                self.user_password = data[Key.UserPassword]
                self.driver_path = data[Key.DriverPath]
                if self.driver_path is None:
                    self.driver_path = get_driver_path()
                if self.driver_path is None:
                    Log.error("Driver Path Error")
                    raise Exception("No driver path")

                self.always_retry_check_box = data[Key.AlwaysRetry]
                retry_times = None
                tolerance_angle = None
                try:
                    retry_times = int(data.get(Key.CaptchaRetryTimes))
                    tolerance_angle = int(data.get(Key.CaptchaToleranceAngle))
                except Exception as e:
                    Log.error(e)
                self.captcha_retry_times = None if retry_times is None else retry_times
                self.captcha_tolerance_angle = None if tolerance_angle is None else tolerance_angle
                self.captcha_failed_email = data.get(Key.NotificationEmail)

                self.status = True
        except Exception as e:
            Log.error(f"ClockManager initialization error: {e}")
            self.status = False
            self.error = str(e)

    def clock(self):
        config = Config(
            self.driver_path,
            "https://kq.neusoft.com/login",
            self.user_name,
            self.user_password,
            captcha_attempts=self.captcha_retry_times if self.captcha_retry_times > 0 else 5,
            tolerance=self.captcha_tolerance_angle if self.captcha_tolerance_angle > 0 else 5,
            wait_time=2,
        )

        auto_clock = AutoClock(config)
        result = auto_clock.run()
        auto_clock.quit()

        return result

    def run(self):
        while True:
            if not self.status:
                return False
            if self.clock():
                return True
            else:
                self.send_email()

            if not self.always_retry_check_box:
                break

        return False

    def send_email(self):
        pass

    @staticmethod
    def check_data(data):
        Log.info(f"user_name: [{data[Key.UserName]}]")
        if data[Key.UserName] == Key.Empty:
            Log.error("[username] is empty.")
            raise Exception("[username] is empty.")

        if data[Key.UserPassword] == Key.Empty :
            Log.error("[password] is empty.")
            raise Exception("[password] is empty.")

        if data[Key.DriverPath] == Key.Empty:
            Log.error("[driver path] is empty.")
            raise Exception("[driver path] is empty.")

        if not os.path.exists(data[Key.DriverPath]):
            Log.error("[driver path] is invalid.")
            raise Exception("[driver path] is invalid.")

        return True

def run_clock(is_test=False):
    try:
        if not is_test:
            clock = ClockManager()
            if clock.status:
                clock.run()
                return True, None
            else:
                Log.error(clock.error)
                return False, clock.error
        else:
            run_test()
            return True, None
    except Exception as e:
        return False, str(e)

def get_driver_path(driver_name="Edge_Driver/msedgedriver.exe"):
    if hasattr(sys, "_MEIPASS"):
        Log.info("Release mode")
        driver_dir = os.path.join(sys._MEIPASS, "drivers")
    else:
        Log.info("Debug mode")
        return None

    driver_path = os.path.join(driver_dir, driver_name)

    if not os.path.exists(driver_path):
        raise FileNotFoundError(f"驱动文件不存在：{driver_path}")

    return driver_path