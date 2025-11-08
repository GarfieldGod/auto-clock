import sys
import argparse

from PyQt5.QtWidgets import QApplication

from src.extend.auto_windows_plan import clean_invalid_windows_plan
from src.extend.email_server import send_email_by_auto_clock
from src.ui.ui import ConfigWindow
from src.core.clock_manager import run_clock
from src.extend.auto_windows_operation import run_windows_shutdown, run_windows_sleep
from src.utils.const import Key
from src.utils.log import Log
from src.utils.utils import Utils, data_json

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
        config_data = Utils.read_dict_from_json(data_json)
        send_email_success = False
        send_email_failed = False
        email = None
        operation = None
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
                Log.info(f"Auto Clock Get Task: {task}")
                if task and task.get(Key.Operation):
                    operation = task.get(Key.Operation)

                if operation == Key.AutoClock:
                    ok, error = run_clock()
                elif operation == Key.ShutDownWindows:
                    ok, error = run_windows_shutdown(30)
                elif operation == Key.WindowsSleep:
                    ok, error = run_windows_sleep()
                else:
                    error = "No operation specified."
        except Exception as e:
            error = str(e)

        if not error: error = "Unknow Error"
        if not operation: operation = Key.Unknown
        if not task: task = {}

        if ok:
            if send_email_success and email:
                send_email_by_auto_clock(email, subject="Auto Clock Success", title=f"Task: {operation} Success",
                                         message=f"Your [{operation}] operation completed successfully.<br>"
                                                 f"Task Name: {task.get(Key.ShortName, Key.Unknown) if task.get(Key.TriggerType) != Key.Multiple else task.get(Key.ShortName, Key.Unknown)}<br>"
                                                 f"Trigger Type: {task.get(Key.TriggerType, Key.Unknown)}<br>"
                                                 f"Execute Time: {task.get(Key.ExecuteTime, Key.Unknown)}<br>")
        else:
            if send_email_failed and email:
                send_email_by_auto_clock(email, subject="Auto Clock Failed", title=f"Task: {operation} Failed",
                                         message=f"Your [{operation}] operation failed. Error: [{error}]<br>"
                                                 f"Task Name: {task.get(Key.ShortName, Key.Unknown) if task.get(Key.TriggerType) != Key.Multiple else task.get(Key.ShortName, Key.Unknown)}<br>"
                                                 f"Trigger Type: {task.get(Key.TriggerType, Key.Unknown)}<br>"
                                                 f"Execute Time: {task.get(Key.ExecuteTime, Key.Unknown)}<br>")

    Log.close()
