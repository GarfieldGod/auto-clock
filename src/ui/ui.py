import os
import json

from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont, QPalette, QColor
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QGroupBox,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QCheckBox,
    QPushButton, QDialogButtonBox, QSizePolicy, QFormLayout, QComboBox, QSpacerItem
)
from platformdirs import user_data_dir

from src.core.clock_manager import ClockManager, run_clock, get_driver_path
from src.extend.auto_windows_login import auto_windows_login_on, auto_windows_login_off
from src.ui.calendar import Calendar

DataRoot = user_data_dir("data", "auto-clock")

BackGround_Color = "#ffffff"
Border_Color = "#000000"
Text_Color = "grey"
Border_Width = "1px"
Border_Radius = ""

class ConfigWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        # 标题图标和窗口大小
        self.setFixedSize(500, 700)
        self.setWindowTitle("Auto-Clock")
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {BackGround_Color};
            }}
            QMainWindow > QWidget {{
                background-color: {BackGround_Color};
            }}
        """)
        # 窗口置中
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
# 布局---------------------------------------------------------------------------------------------
        # User Information
        self.user_name = QLineEdit()
        self.user_password = QLineEdit()
        self.captcha_retry_times = QLineEdit()
        self.captcha_failed_email = QLineEdit()
        self.captcha_tolerance_angle = QLineEdit()
        self.driver_path = QLineEdit()
        self.always_retry_check_box = QCheckBox()
        group_user = QGroupBox("Must Config")
        group_user.setStyleSheet(self.get_group_css({"Text_Color":"#D32F2F"}))
        layout_function = QVBoxLayout(group_user)
        layout_function.addWidget(QLabel("UserName:"))
        layout_function.addWidget(self.user_name)
        layout_function.addWidget(QLabel("Password:"))
        layout_function.addWidget(self.user_password)
        layout_function.addWidget(QLabel("edge driver path:"))
        layout_function.addWidget(self.driver_path)

        # Captcha Config
        group_sys = QGroupBox("Captcha Config")
        group_sys.setStyleSheet(self.get_group_css({}))
        layout_sys = QVBoxLayout(group_sys)

        widget_retry = QWidget()
        layout_retry = QHBoxLayout(widget_retry)
        layout_retry.setContentsMargins(0, 0, 0, 0)
        widget_retry_a = QWidget()
        layout_retry_a = QVBoxLayout(widget_retry_a)
        layout_retry_a.setContentsMargins(0, 0, 0, 0)
        layout_retry_a.addWidget(QLabel("Retry Times:"))
        layout_retry_a.addWidget(self.captcha_retry_times)
        widget_retry_b = QWidget()
        layout_retry_b = QVBoxLayout(widget_retry_b)
        layout_retry_b.setContentsMargins(0, 0, 0, 0)
        layout_retry_b.addWidget(QLabel("Always Retry:"))
        layout_retry_b.addWidget(self.always_retry_check_box)
        widget_retry_c = QWidget()
        layout_retry_c = QVBoxLayout(widget_retry_c)
        layout_retry_c.setContentsMargins(0, 0, 0, 0)
        layout_retry_c.addWidget(QLabel("Tolerance Angle:"))
        layout_retry_c.addWidget(self.captcha_tolerance_angle)
        layout_retry.addWidget(widget_retry_a)
        layout_retry.addWidget(widget_retry_c)
        layout_retry.addWidget(widget_retry_b)

        layout_sys.addWidget(QLabel("Failure Notification Email:"))
        layout_sys.addWidget(self.captcha_failed_email)
        layout_sys.addWidget(widget_retry)
        # Windows Config
        group_windows_config = QGroupBox("Windows Config")
        group_windows_config.setStyleSheet(self.get_group_css({}))
        layout_windows = QVBoxLayout(group_windows_config)
        self.auto_windows_login_on = QPushButton("Set Windows Auto Login")
        self.auto_windows_login_on.clicked.connect(self.auto_login_windows)
        layout_windows.addWidget(self.auto_windows_login_on)
        # Plan List
        group_plan_list = QGroupBox("Plan List")
        group_plan_list.setStyleSheet(self.get_group_css({}))
        layout_plan_list = QVBoxLayout(group_plan_list)
        self.widget_plan_list = QListWidget()
        layout_plan_list.addWidget(self.widget_plan_list)
        widget_plan_list_buttons = QWidget()
        self.button_create = QPushButton("Create")
        self.button_create.clicked.connect(self.create_windows_plan)
        self.button_delete = QPushButton("Delete")
        layout_plan_list_buttons = QHBoxLayout(widget_plan_list_buttons)
        layout_plan_list_buttons.addWidget(self.button_create)
        layout_plan_list_buttons.addWidget(self.button_delete)
        layout_plan_list.addWidget(widget_plan_list_buttons)

        # confirm or try
        widget_confirm = QWidget()
        widget_confirm.setObjectName("widget_confirm")
        widget_confirm.setFixedHeight(75)
        widget_confirm.setStyleSheet(f"""
        #widget_confirm {{
            background-color: {BackGround_Color};
            color: {Text_Color};
            border: {Border_Width} solid {Border_Color};
            border-radius: 5px;
        }}
        """)
        layout_confirm = QHBoxLayout(widget_confirm)
        self.button_confirm = QPushButton("Confirm")
        self.button_confirm.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        self.button_try = QPushButton("Try")
        self.button_try.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout_confirm.addWidget(self.button_try)
        layout_confirm.addWidget(self.button_confirm)

        # Global
        widget_global = QWidget()
        layout_global = QVBoxLayout(widget_global)
        layout_global.addWidget(group_user)
        layout_global.addWidget(group_sys)
        layout_global.addWidget(group_plan_list)
        layout_global.addWidget(group_windows_config)
        layout_global.addWidget(widget_confirm)
        self.setCentralWidget(widget_global)
# 功能---------------------------------------------------------------------------------------------
        self.button_confirm.clicked.connect(self.confirm)
        self.button_try.clicked.connect(self.try_now)

        self.load()

    def write_json(self):
        retry_times = None
        tolerance_angle = None
        if self.captcha_retry_times.text() != "":
            retry_times = int(self.captcha_retry_times.text())
        if self.captcha_tolerance_angle.text() != "":
            tolerance_angle = int(self.captcha_tolerance_angle.text())
        data = {
            "user_name": self.user_name.text(),
            "user_password": self.user_password.text(),
            "driver_path": self.driver_path.text(),
            "always_retry_check_box": self.always_retry_check_box.isChecked()
        }
        if self.captcha_failed_email.text() != "":
            data["captcha_failed_email"] = self.captcha_failed_email.text()
        if retry_times is not None:
            data["captcha_retry_times"] = retry_times
        if tolerance_angle is not None:
            data["captcha_tolerance_angle"] = tolerance_angle

        if not os.path.exists(DataRoot):
            os.makedirs(DataRoot)

        try:
            ok = ClockManager.check_data(data)
            if not ok:
                raise Exception("Unknow Error")
        except Exception as e:
            raise Exception(e)

        with open(f"{DataRoot}\\data.json", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def confirm(self):
        try:
            self.write_json()

            MessageBox(f"Confirmation Success!")
        except Exception as e:
            MessageBox(f"Confirmation Failed!\nError: {e}")

    def load(self):
        try:
            inner_driver = None
            try:
                inner_driver = get_driver_path()
            except Exception as e:
                MessageBox(f"内置浏览器驱动展开失败，请自行下载并设置edge浏览器驱动位置!\nError: {e}")
            if inner_driver is not None:
                self.driver_path.setText(inner_driver)
                self.driver_path.setEnabled(False)

            if not os.path.exists(f"{DataRoot}\\data.json"):
                return False

            with open(f"{DataRoot}\\data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.user_name.setText(data.get("user_name", ""))
                self.user_password.setText(data.get("user_password", ""))
                self.captcha_retry_times.setText(str(data.get("captcha_retry_times", "")))
                self.captcha_tolerance_angle.setText(str(data.get("captcha_tolerance_angle", "")))
                self.always_retry_check_box.setChecked(data.get("always_retry_check_box", False))
                self.captcha_failed_email.setText(data.get("captcha_failed_email", ""))
                if inner_driver is None:
                    self.driver_path.setText(data.get("driver_path", ""))
                return True
        except Exception as e:
            MessageBox(f"Load Data Failed!\nError: {e}")
            print(e)

    def try_now(self):
        try:
            self.write_json()
        except Exception as e:
            MessageBox(f"Try Failed!\nError: {e}")
        run_clock()

    def get_group_css(self, css_data):
        background_color = css_data["BackGround_Color"] if css_data.get("BackGround_Color") is not None and css_data["BackGround_Color"] != "" else BackGround_Color
        text_color = css_data["Text_Color"] if css_data.get("Text_Color") is not None and css_data["Text_Color"] != "" else Text_Color
        border_color = css_data["Border_Color"] if css_data.get("Border_Color") is not None and css_data["Border_Color"] != "" else Border_Color
        border_width = css_data["Border_Width"] if css_data.get("Border_Width") is not None and css_data["Border_Width"] != "" else Border_Width
        css = f"""
            QGroupBox {{
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
                font-weight: bold;
                font-size: 16px;
                background-color: {background_color};
                color: {text_color};
                border: {border_width} solid {border_color};
                border-radius: 5px;
                margin-top: 10px;
            }}
            QGroupBox:title {{
                font-family: "Microsoft YaHei", "SimHei", sans-serif;
                font-weight: bold;
                font-size: 24px;
                subcontrol-origin: margin;
                subcontrol-position: top left;
                left: 10px;
                padding: 0 5px 0 5px;
            }}
        """
        return css

    def auto_login_windows(self):
        dlg = WindowsLoginDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            name, password = dlg.values()
            if not name or not name.strip():
                return
        else:
            return
        try:
            backup_path = auto_windows_login_on(name, password)
            MessageBox(f"Set Windows Auto Login Success!\nwindows config backup path: {backup_path}")
        except Exception as e:
            MessageBox(f"Set Windows Auto Login Failed!\nError: {e}")

    def create_windows_plan(self):
        dlg = WindowsPlanDialog(self)
        if dlg.exec_() == QDialog.Accepted:
            pass
        else:
            return

class WindowsLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Windows Auto Login")
        self.name_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.button_clear_auto_login = QPushButton("Clear")
        self.button_clear_auto_login.clicked.connect(self.clear_auto_login)

        form = QFormLayout(self)
        form.addRow("Windows User Name:", self.name_edit)
        form.addRow("Windows User Password:", self.password_edit)
        form.addRow("Clear Auto Login:", self.button_clear_auto_login)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        form.addRow(buttons)

    def values(self):
        return self.name_edit.text().strip(), self.password_edit.text().strip()

    def clear_auto_login(self):
        try:
            backup_path = auto_windows_login_off()
            MessageBox(f"Clear Success!\nbackup before clear: {backup_path}")
        except Exception as e:
            MessageBox(f"Clear Failed!\nError: {e}")

class WindowsPlanDialog(QDialog):
    trigger_types = ["Multiple", "once", "daily", "weekly", "monthly"]

    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.setWindowTitle("Create Windows Plan")
            self.plan_name_edit = QLineEdit()
            self.trigger_type = QComboBox()
            self.trigger_type.addItems(["once", "Multiple", "daily", "weekly", "monthly"])
            self.trigger_type.currentTextChanged.connect(self.trigger_type_changed)

            widget_layout = QVBoxLayout(self)

            widget_setting = QWidget()
            layout_setting = QVBoxLayout(widget_setting)
            widget_line_1 = QHBoxLayout()
            widget_line_1.addWidget(QLabel("Plan Name:"))
            widget_line_1.addWidget(self.plan_name_edit)
            widget_line_2 = QHBoxLayout()
            widget_line_2.addWidget(QLabel("Trigger Type:"))
            widget_line_2.addWidget(self.trigger_type)
            layout_setting.addLayout(widget_line_1)
            layout_setting.addLayout(widget_line_2)
            widget_layout.addWidget(widget_setting)
            widget_layout.addStretch()

            self.calendar_selector = Calendar()
            palette = self.calendar_selector.calendar.palette()
            palette.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Base, QColor(255, 0, 0))
            COLOR_GRAY = QColor(245, 245, 245)
            COLOR_DARK_GRAY = QColor(64, 64, 64)
            palette.setColor(QPalette.Highlight, COLOR_GRAY)
            palette.setColor(QPalette.HighlightedText, COLOR_DARK_GRAY)
            self.calendar_selector.calendar.setPalette(palette)

            self.widget_one_day_selector = QWidget()
            self.layout_one_day_selector = QHBoxLayout(self.widget_one_day_selector)
            self.year_sel = QComboBox()
            self.year_sel.addItems([str(QDate.currentDate().year()), str(QDate.currentDate().addYears(1).year())])
            self.year_sel.currentIndexChanged.connect(self.year_changed)
            self.month_sel = QComboBox()
            self.month_sel.addItems(self.get_nums_array(1,12))
            self.month_sel.currentIndexChanged.connect(self.month_changed)
            self.day_sel = QComboBox()
            self.day_sel.addItems(self.get_nums_array(1, 31))
            self.hour_sel = QComboBox()
            self.hour_sel.addItems(self.get_nums_array(0,23))
            self.minute_sel = QComboBox()
            self.minute_sel.addItems(self.get_nums_array(0,59))
            self.layout_one_day_selector.addWidget(self.year_sel)
            self.layout_one_day_selector.addWidget(self.month_sel)
            self.layout_one_day_selector.addWidget(self.day_sel)
            self.layout_one_day_selector.addWidget(self.hour_sel)
            self.layout_one_day_selector.addWidget(self.minute_sel)

            self.space_area = QHBoxLayout()
            self.space_area.addWidget(self.calendar_selector)
            self.space_area.addWidget(self.widget_one_day_selector)
            widget_layout.addLayout(self.space_area)
            self.space_area_hide_all_content()
            self.widget_one_day_selector.show()

            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            widget_layout.addWidget(buttons)
        except Exception as e:
            print(e)

    def year_changed(self):
        self.month_sel.setCurrentIndex(0)
        self.day_sel.setCurrentIndex(0)

    def month_changed(self):
        self.day_sel.clear()
        if self.month_sel.currentText() in ["01", "03", "05", "07", "08", "10", "12"]:
            day = 31
        elif self.month_sel.currentText() == "02":
            if QDate.isLeapYear(int(self.year_sel.currentText())):
                day = 28
            else:
                day = 29
        else:
            day = 30
        self.day_sel.addItems(self.get_nums_array(1, day))
        self.day_sel.setCurrentIndex(0)

    def get_nums_array(self, start, end, bit=2):
        num_array = []
        for i in range(start, end + 1):
            num_str = str(i)
            if len(num_str) < bit:
                num_str = "0" * (bit - len(num_str)) + num_str
            num_array.append(num_str)
        return num_array

    def space_area_hide_all_content(self):
        for i in range(self.space_area.count()):
            item = self.space_area.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.hide()

    def trigger_type_changed(self):
        self.space_area_hide_all_content()
        if self.trigger_type.currentText() == self.trigger_types[0]:
            self.calendar_selector.show()
        elif self.trigger_type.currentText() == self.trigger_types[1]:
            self.widget_one_day_selector.show()
        else:
            pass
        self.adjustSize()

    def values(self):
        return self.plan_name_edit.text().strip(), self.trigger_type.text().strip()

class MessageBox(QDialog):
    def __init__(self, message, message_name="Message", parent=None):
        super().__init__(parent)
        self.setWindowTitle(message_name)

        label = QLabel(message)
        font = QFont()
        font.setFamily("Consolas")
        font.setPointSize(10)
        label.setFont(font)
        label.setAlignment(Qt.AlignHCenter | Qt.AlignVCenter)

        layout_center_label = QHBoxLayout()
        layout_center_label.addStretch(1)
        layout_center_label.addWidget(label)
        layout_center_label.addStretch(1)

        button = QDialogButtonBox(QDialogButtonBox.Ok)
        button.accepted.connect(self.accept)
        layout_center_button = QHBoxLayout()
        layout_center_button.addStretch(1)
        layout_center_button.addWidget(button)
        layout_center_button.addStretch(1)

        layout = QVBoxLayout(self)
        layout.addStretch()
        layout.addLayout(layout_center_label)
        layout.addStretch()
        layout.addLayout(layout_center_button)
        self.exec_()