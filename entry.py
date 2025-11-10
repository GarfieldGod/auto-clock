import sys
import argparse
import webbrowser

from PyQt5.QtWidgets import QApplication, QDialog

from src.utils import update
from src.utils.log import Log
from src.utils.utils import Utils
from src.ui.ui import ConfigWindow
from src.ui.ui_message import MessageBox
from src.core.clock_manager import run_clock
from src.utils.const import Key, AppPath, WebPath
from src.extend.email_server import send_email_by_result
from src.extend.auto_windows_plan import clean_invalid_windows_plan
from src.extend.auto_windows_operation import run_windows_shutdown, run_windows_sleep

if __name__ == '__main__':
    Log.open()

    parser = argparse.ArgumentParser(description="auto-clock")
    parser.add_argument("--task_id")
    args = parser.parse_args()

    clean_invalid_windows_plan()

    use_gui = not any(vars(args).values())
    if use_gui:
        app = QApplication(sys.argv)

        ret = update.check_update()
        if ret and ret[0]:
            is_update = MessageBox(
                f"There is a new version for the app:\t\n\n"
                f"Local: {ret[1].get("local")} Newest: {ret[1].get("remote")}\t\n\n"
                f"Do you want to download new ?\t\n\n",
                need_check=True, message_only=False)
            if is_update.exec_() == QDialog.Accepted:
                webbrowser.open_new(WebPath.AppProjectPath)
                exit()

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
                    ok, error = run_windows_sleep()
                else:
                    error = "No operation specified."

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
