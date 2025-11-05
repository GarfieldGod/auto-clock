import sys

from PyQt5.QtGui import QPalette, QColor, QTextCharFormat, QFont
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout,
                             QCalendarWidget, QLabel, QPushButton, QDialog, QHBoxLayout, QDialogButtonBox, QHeaderView,
                             QTableView, QToolButton)
from PyQt5.QtCore import QDate, Qt, QLocale

COLOR_UNSELECTED_BACKGROUND = QColor(255, 255, 255)
COLOR_UNSELECTED_TEXT = QColor(0, 0, 0)
COLOR_SELECTED_BACKGROUND = QColor(255, 100, 100)
COLOR_TODAY_BACKGROUND = QColor(200, 200, 255)
COLOR_GRAY = QColor(245, 245, 245)
COLOR_DARK_GRAY = QColor(64, 64, 64)

class Calendar(QWidget):
    selected_dates = set()

    def __init__(self):
        super().__init__()
        # self.setWindowTitle("Select date")
        self.resize(600, 400)

        layout = QVBoxLayout()

        self.calendar = QCalendarWidget(self)
        self.calendar.setGridVisible(True)
        self.calendar.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.calendar.setMinimumDate(QDate.currentDate())
        self.calendar.setMaximumDate(QDate.currentDate().addMonths(1))
        self.calendar.setLocale(QLocale(QLocale.English, QLocale.UnitedStates))
        self.calendar.clicked.connect(self.on_date_clicked)

        layout.addWidget(self.calendar)

        self.setLayout(layout)
        self.set_calendar_qss()

    def setHighLightColor(self, color):
        palette = self.calendar.palette()
        palette.setColor(QPalette.Highlight, color)
        self.calendar.setPalette(palette)

    def on_date_clicked(self, selected_date):
        try:
            selected_format = QTextCharFormat()

            if selected_date not in self.selected_dates:
                self.lastDate = selected_date
                self.selected_dates.add(selected_date)
                selected_format.setBackground(COLOR_SELECTED_BACKGROUND)
            else:
                if self.lastDate is not None:
                    self.calendar.setSelectedDate(self.lastDate)
                self.selected_dates.remove(selected_date)
                selected_format.setBackground(COLOR_UNSELECTED_BACKGROUND)

            self.calendar.setDateTextFormat(selected_date, selected_format)

            selected_count = len(self.selected_dates)
            print(f"已选中：{selected_count} 个日期 | 选中列表：{self.selected_dates}")
        except Exception as e:
            print(e)

    def set_calendar_qss(self):
        qss = """
            QCalendarWidget {
                border: 1px solid black;
            }

            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #ffffff;
            }

            QCalendarWidget QToolButton {
                background-color: transparent;
                color: #000000;
                border: none;
            }

            QTableView::item:disabled {
                background-color: white;
                color: grey;
            }
        """
        self.calendar.setStyleSheet(qss)

    def values(self):
        return self.selected_dates

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Calendar()
    window.show()
    sys.exit(app.exec_())