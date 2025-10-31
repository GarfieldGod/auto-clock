import os
import json
import sys

from platformdirs import user_data_dir
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.log import Log
from test.test import run_test
from src.auto_clock import AutoClock, Config

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
                self.user_name = data["user_name"]
                self.user_password = data["user_password"]
                self.driver_path = data["driver_path"]

                self.captcha_retry_times = int(data["captcha_retry_times"])
                self.always_retry_check_box = data["always_retry_check_box"]
                self.captcha_failed_email = data["captcha_failed_email"]

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
            captcha_attempts=self.captcha_retry_times,
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
        Log.info(f"user_name: [{data["user_name"]}]")
        if data["user_name"] == "":
            Log.error("[username] is empty.")
            raise Exception("[username] is empty.")

        if data["user_password"] == "" :
            Log.error("[password] is empty.")
            raise Exception("[password] is empty.")

        if data["driver_path"] == "":
            Log.error("[driver path] is empty.")
            raise Exception("[driver path] is empty.")

        if not os.path.exists(data["driver_path"]):
            Log.error("[driver path] is invalid.")
            raise Exception("[driver path] is invalid.")

        return True

def run_clock():
    is_test = False
    try:
        Log.open()

        if not is_test:
            clock = ClockManager()
            if clock.status:
                clock.run()
            else:
                Log.error(clock.error)
        else:
            run_test()

        Log.close()
    except Exception as e:
        print(e)

if __name__ == '__main__':
    run_clock()