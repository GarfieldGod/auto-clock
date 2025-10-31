import os
import time
import http.server
import socketserver
from dataclasses import dataclass
from threading import Thread
from src.auto_clock import AutoClock, Config

@dataclass
class TestConfig:
    driver_path: str
    web_root: str
    page: str
    port: int
    test_times: int
    captcha_attempts: int = 3
    user_name: str = "testName"
    user_password: str = "123"

class Test:
    def __init__(self, config: TestConfig):
        self.server = None
        self.server_thread = None

        self.web_root = config.web_root
        self.page = config.page
        self.port = config.port
        self.driver_path = config.driver_path
        self.test_times = config.test_times
        self.user_name = config.user_name
        self.user_password = config.user_password
        self.captcha_attempts = config.captcha_attempts

    def run_server(self):
        """启动本地服务器（在子线程中运行）"""
        os.chdir(self.web_root)
        handler = http.server.SimpleHTTPRequestHandler
        self.server = socketserver.TCPServer(("", self.port), handler)
        print(f"本地服务器启动：http://localhost:{self.port}")
        try:
            self.server.serve_forever()  # 持续运行，直到 shutdown() 被调用
        except Exception as e:
            print(f"服务器异常停止：{e}")

    def stop_server(self):
        """关闭服务器并释放资源"""
        if self.server:
            print("正在关闭服务器...")
            self.server.shutdown()
            self.server.server_close()
            self.server = None
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=5)  # 等待线程结束（最多等5秒）
            self.server_thread = None
        print("服务器已关闭")

    def run(self):
        self.server_thread = Thread(target=self.run_server, daemon=True)
        self.server_thread.start()
        time.sleep(1)

        test_config = Config(
            self.driver_path,
            f"http://localhost:{self.port}/{self.page}",
            self.user_name,
            self.user_password,
            self.captcha_attempts
        )

        pass_case = 0
        failed_case = 0
        for i in range(self.test_times):
            test_clock = AutoClock(test_config)
            result = test_clock.run()
            print(f"result {i} is {result}.")
            if result:
                pass_case += 1
            else:
                failed_case +=1
            test_clock.quit()
            time.sleep(2)

        self.stop_server()

        print(f"Final result PASS: {pass_case/self.test_times} Failed: {failed_case/self.test_times}.")

def run_test():
    test_config = TestConfig(
        "C:/Application/Edge_Driver/msedgedriver.exe",
        "test/page",
        "test_page.html",
        8000,
        10,
        3
    )
    test_clock = Test(test_config)
    test_clock.run()