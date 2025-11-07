import sys
import argparse

from PyQt5.QtWidgets import QApplication

from src.extend.auto_windows_plan import clear_windows_plan
from src.ui.ui import ConfigWindow
from src.core.clock_manager import run_clock
from src.extend.auto_windows_operation import run_windows_shutdown, run_windows_sleep
from src.utils.utils import Utils

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="auto-clock")
    parser.add_argument("--auto", action="store_true")
    parser.add_argument("--shutdown", action="store_true")
    parser.add_argument("--sleep", action="store_true")
    args = parser.parse_args()

    clear_windows_plan()

    if args.auto:
        run_clock()
    if args.shutdown:
        run_windows_shutdown(30)
    if args.sleep:
        run_windows_sleep()
    else:
        app = QApplication(sys.argv)
        window = ConfigWindow()
        window.show()
        app.exec_()