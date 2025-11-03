import os
import sys
import json

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QGroupBox,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QCheckBox,
    QPushButton, QDialogButtonBox, QSizePolicy
)
from platformdirs import user_data_dir

from src.clock_manager import ClockManager, run_clock, get_driver_path

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
        # Plan List
        group_plan_list = QGroupBox("Plan List")
        group_plan_list.setStyleSheet(self.get_group_css({}))
        layout_plan_list = QVBoxLayout(group_plan_list)
        self.widget_plan_list = QListWidget()
        layout_plan_list.addWidget(self.widget_plan_list)
        widget_plan_list_buttons = QWidget()
        self.button_create = QPushButton("Create")
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

class MessageBox(QDialog):
    def __init__(self, message, message_name="Massage", parent=None):
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