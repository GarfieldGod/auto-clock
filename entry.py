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

        try:
            if args.auto:
                operation = "Auto Clock"
                ok, error = run_clock()
            elif args.shutdown:
                operation = "Shut Down Windows"
                ok, error = run_windows_shutdown(30)
            elif args.sleep:
                operation = "Windows Sleep"
                ok, error = run_windows_sleep()
            else:
                ok = False
                error = "No operation specified."
                quit()
        except Exception as e:
            ok = False
            error = str(e)

        if not error: error = "Unknow Error"

        if ok:
            if send_email_success and email:
                send_email_by_auto_clock(email, subject="Auto Clock Success", title=f"{operation} Success", message=f"Your [{operation}] operation completed successfully.")
        else:
            if send_email_failed and email:
                send_email_by_auto_clock(email, subject="Auto Clock Failed", title=f"{operation} Failed", message=f"Your [{operation}] operation failed. Error: [{error}]")

    Log.close()
