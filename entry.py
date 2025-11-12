import sys
import os
import argparse

from PyQt5.QtWidgets import QApplication

from src.utils.log import Log
from src.utils.utils import Utils
from src.ui.ui import ConfigWindow
from src.core.clock_manager import run_clock
from src.utils.const import Key, AppPath
from src.extend.email_server import send_email_by_result
from src.extend.network_manager import disconnect_network, connect_network

# 根据操作系统类型导入相应的模块
system_name = os.name
if system_name == 'nt':  # Windows
    from src.extend.auto_windows_plan import clean_invalid_windows_plan
    from src.extend.auto_windows_operation import run_windows_shutdown, run_windows_sleep
else:  # Linux和其他系统
    # 尝试导入Linux专用模块，如果不存在则使用占位符
    try:
        from src.extend.auto_linux_operation import run_linux_shutdown as run_windows_shutdown
        from src.extend.auto_linux_operation import run_linux_sleep as run_windows_sleep
        # 之后可以添加Linux计划任务管理模块
        def clean_invalid_windows_plan():
            Log.info("Linux系统无需清理Windows计划任务")
    except ImportError:
        # 定义Linux系统的相应函数占位符
        def clean_invalid_windows_plan():
            Log.info("Linux系统无需清理Windows计划任务")
        
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
        config_data = Utils.read_dict_from_json(AppPath.DataJson)
        send_email_success = False
        send_email_failed = False
        email = None
        if config_data and config_data.get(Key.NotificationEmail):
            email = config_data.get(Key.NotificationEmail)
            send_email_success = config_data.get(Key.SendEmailWhenSuccess, False)
            send_email_failed = config_data.get(Key.SendEmailWhenFailed, False)

        ok = False
        error = None
        task = None
        try:
            if args.task_id:
                task = Utils.find_task(args.task_id)
                Log.info(f"Auto Clock Get Task Id: {task}")
                if not task:
                    raise Exception(f"Task ID: {args.task_id} not found.")
                operation = task.get(Key.Operation)

                Log.info(f"Task ID: {args.task_id} has found, Task Name: {task.get(Key.TaskName)} Operation: {operation}")
                if operation == Key.AutoClock:
                    ok, error = run_clock()
                elif operation == Key.ShutDownWindows:
                    ok, error = run_windows_shutdown(30)
                elif operation == Key.WindowsSleep:
                    ok, error = run_windows_sleep(30)
                elif operation == Key.DisconnectNetwork:
                    ok, error = disconnect_network(30)
                elif operation == Key.ConnectNetwork:
                    ok, error = connect_network()
                else:
                    error = f"No operation specified for: {operation}"

                Log.info("Finish Task.")
            else:
                exit()
        except Exception as e:
            error = str(e)

        if not error: error = "Unknow Error"
        Log.info(f"task: {task}")
        Log.info(f"ok: {ok} error: {error}")
        Log.info(f"email: {email} send_email_success: {send_email_success} send_email_failed: {send_email_failed}")
        send_email_by_result(task=task, email=email, send_email_success=send_email_success,
                             send_email_failed=send_email_failed, ok=ok, error=error)
    Log.close()
