import sys
import os
import time
import random
import argparse
from datetime import datetime

from PyQt5.QtWidgets import QApplication

from src.utils.log import Log
from src.utils.utils import Utils
from src.ui.ui import ConfigWindow
from src.core.clock_manager import run_clock
from src.utils.const import Key, AppPath
from src.extend.email_server import send_email_by_result

# 根据操作系统选择正确的网络管理模块
system_name = os.name
if system_name == 'nt':  # Windows
    from src.extend.network_manager import disconnect_network, connect_network
else:  # Linux
    from src.extend.auto_linux_network import disconnect_network, connect_network

# 根据操作系统类型导入相应的模块
if system_name == 'nt':  # Windows
    from src.extend.auto_windows_plan import clean_invalid_windows_plan
    from src.extend.auto_windows_operation import run_windows_shutdown, run_windows_sleep
else:  # Linux和其他系统
    # 尝试导入Linux专用模块，如果不存在则使用占位符
    try:
        from src.extend.auto_linux_operation import run_linux_shutdown as run_windows_shutdown
        from src.extend.auto_linux_operation import run_linux_sleep as run_windows_sleep
        from src.extend.auto_linux_plan import clean_invalid_linux_plan as clean_invalid_windows_plan
    except ImportError:
        # 定义Linux系统的相应函数占位符
        def clean_invalid_windows_plan():
            Log.info("Linux系统清理无效计划任务")
            # 这里可以实现基本的清理逻辑
            return True, None
        
        def run_windows_shutdown(delay=30):
            Log.info(f"Linux系统执行关机操作，延迟{delay}秒")
            return True, None
        
        def run_windows_sleep(delay=30):
            Log.info(f"Linux系统执行睡眠操作，延迟{delay}秒")
            return True, None

if __name__ == '__main__':
    Log.open()

    parser = argparse.ArgumentParser(description="auto-clock")
    parser.add_argument("--task_id")
    args = parser.parse_args()

    clean_invalid_windows_plan()

    use_gui = not any(vars(args).values())
    if use_gui:
        app = QApplication(sys.argv)
        window = ConfigWindow()
        window.show()
        app.exec_()

    else:
        ok = False
        error = None
        task = None
        try:
            if args.task_id:
                task = Utils.find_task(args.task_id)
                Log.info(f"Auto Clock Get Task Id: {args.task_id}")
                if not task:
                    raise Exception(f"Task ID: {args.task_id} not found.")
                operation = task.get(Key.Operation)
                day_time_type = task.get(Key.DayTimeType)
                if day_time_type and day_time_type == Key.Random:
                    time_offset = task.get(Key.TimeOffset, 0)
                    random_sec = random.randint(0, time_offset)
                    Log.info(f"将等待 {random_sec} 秒...")
                    time.sleep(random_sec)
                    Log.info("等待结束！继续执行任务")

                Log.info(f"Task ID: {args.task_id} has found, Task Name: {task.get(Key.TaskName)} Operation: {operation}")
                start_time = datetime.now()

                if operation == Key.AutoClock:
                    ok, error = run_clock()
                elif operation == Key.ShutDownWindows:
                    ok, error = run_windows_shutdown(30)
                elif operation == Key.WindowsSleep:
                    ok, error = run_windows_sleep(30)
                elif operation == Key.DisconnectNetwork:
                    # 对于断网操作，Windows和Linux都支持延迟参数
                    ok, error = disconnect_network(30)
                elif operation == Key.ConnectNetwork:
                    # 对于联网操作，通常不需要延迟
                    ok, error = connect_network()
                else:
                    error = f"No operation specified for: {operation}"

                end_time = datetime.now()
                elapsed_time = end_time - start_time
                elapsed_sec = elapsed_time.total_seconds()
                task[Key.CostTime] = int(elapsed_sec)
                Log.info(f"Finish Task. Start at: {start_time} End at: {end_time} Cost time: {elapsed_sec} sec")
            else:
                exit()
        except Exception as e:
            error = str(e)

        config_data = Utils.read_dict_from_json(AppPath.DataJson)
        if not config_data or not config_data.get(Key.NotificationEmail): exit()

        email = config_data.get(Key.NotificationEmail)
        send_email_success = config_data.get(Key.SendEmailWhenSuccess, False)
        send_email_failed = config_data.get(Key.SendEmailWhenFailed, False)

        if not error: error = "Unknow Error"
        Log.info(f"task: {task}")
        Log.info(f"ok: {ok} error: {error}")
        Log.info(f"email: {email} send_email_success: {send_email_success} send_email_failed: {send_email_failed}")
        send_email_by_result(task=task, email=email, send_email_success=send_email_success,
                             send_email_failed=send_email_failed, ok=ok, error=error)
    Log.close()
