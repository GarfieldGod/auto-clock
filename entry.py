import sys
import argparse

from PyQt5.QtWidgets import QApplication

from src.ui import ConfigWindow
from src.clock_manager import run_clock

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="auto-clock")
    parser.add_argument("--auto", action="store_true")
    args = parser.parse_args()

    if args.auto:
        run_clock()
    else:
        app = QApplication(sys.argv)
        window = ConfigWindow()
        window.show()
        app.exec_()