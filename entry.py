import sys
import argparse

from PyQt5.QtWidgets import QApplication

from src.extend.auto_windows_plan import clear_windows_plan
from src.extend.email_server import send_email_by_auto_clock
from src.ui.ui import ConfigWindow
from src.core.clock_manager import run_clock
from src.extend.auto_windows_operation import run_windows_shutdown, run_windows_sleep
from src.utils.log import Log
from src.utils.utils import Utils, data_json

if __name__ == '__main__':
    Log.open()

    parser = argparse.ArgumentParser(description="auto-clock")
    parser.add_argument("--auto", action="store_true")
    parser.add_argument("--shutdown", action="store_true")
    parser.add_argument("--sleep", action="store_true")
    parser.add_argument("--email_success", action="store_true")
    parser.add_argument("--email_failed", action="store_true")
    parser.add_argument("--task_id")
    args = parser.parse_args()

    clear_windows_plan()

    use_gui = not any(vars(args).values())
    if use_gui:
        app = QApplication(sys.argv)
        window = ConfigWindow()
        window.show()
        app.exec_()

    else:
        config_data = Utils.read_dict_from_json(data_json)
        send_email_success = False
        send_email_failed = False
        email = None
        operation = None
        if config_data and config_data.get("captcha_failed_email"):
            email = config_data.get("captcha_failed_email")
            send_email_success = config_data.get("send_email_success", False)
            send_email_failed = config_data.get("send_email_failed", False)

        ok = False
        error = None
        task = None
        try:
            if args.task_id:
                task = Utils.find_task(args.task_id)
                Log.info(f"Auto Clock Get Task: {task}")
                if task and task.get("operation"):
                    operation = task.get("operation")

                if operation == "Auto Clock":
                    ok, error = run_clock()
                elif operation == "Shut Down Windows":
                    ok, error = run_windows_shutdown(30)
                elif operation == "Windows Sleep":
                    ok, error = run_windows_sleep()
                else:
                    error = "No operation specified."
        except Exception as e:
            error = str(e)

        if not error: error = "Unknow Error"
        if not operation: operation = "Unknow"
        if not task: task = {}

        if ok:
            if send_email_success and email:
                send_email_by_auto_clock(email, subject="Auto Clock Success", title=f"Task: {operation} Success",
                                         message=f"Your [{operation}] operation completed successfully.<br>"
                                                 f"Task Name: {task.get("short_name", "Unknown") if task.get("trigger_type") != "Multiple" else task.get("short_name", "Unknown")}<br>"
                                                 f"Trigger Type: {task.get("trigger_type", "Unknown")}<br>"
                                                 f"Execute Time: {task.get("execute_time", "Unknown")}<br>")
        else:
            if send_email_failed and email:
                send_email_by_auto_clock(email, subject="Auto Clock Failed", title=f"Task: {operation} Failed",
                                         message=f"Your [{operation}] operation failed. Error: [{error}]<br>"
                                                 f"Task Name: {task.get("short_name", "Unknown") if task.get("trigger_type") != "Multiple" else task.get("short_name", "Unknown")}<br>"
                                                 f"Trigger Type: {task.get("trigger_type", "Unknown")}<br>"
                                                 f"Execute Time: {task.get("execute_time", "Unknown")}<br>")

    Log.close()
