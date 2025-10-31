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

from entry import ClockManager, run_clock

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

        # System Config
        group_sys = QGroupBox("Optional Config")
        group_sys.setStyleSheet(self.get_group_css({}))
        layout_sys = QVBoxLayout(group_sys)

        widget_retry = QWidget()
        layout_retry = QHBoxLayout(widget_retry)
        layout_retry.setContentsMargins(0, 0, 0, 0)
        widget_retry_a = QWidget()
        layout_retry_a = QVBoxLayout(widget_retry_a)
        layout_retry_a.setContentsMargins(0, 0, 0, 0)
        layout_retry_a.addWidget(QLabel("Captcha Retry Times:"))
        layout_retry_a.addWidget(self.captcha_retry_times)
        widget_retry_b = QWidget()
        layout_retry_b = QVBoxLayout(widget_retry_b)
        layout_retry_a.setContentsMargins(0, 0, 0, 0)
        layout_retry_b.addWidget(QLabel("Always Retry:"))
        layout_retry_b.addWidget(self.always_retry_check_box)
        layout_retry.addWidget(widget_retry_a)
        layout_retry.addWidget(widget_retry_b)

        layout_sys.addWidget(QLabel("Captcha Failed Email:"))
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
        data = {
            "user_name": self.user_name.text(),
            "user_password": self.user_password.text(),
            "captcha_retry_times": int(self.captcha_retry_times.text()),
            "always_retry_check_box": self.always_retry_check_box.isChecked(),
            "captcha_failed_email": self.captcha_failed_email.text(),
            "driver_path": self.driver_path.text()
        }
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
            quit()
        except Exception as e:
            MessageBox(f"Confirmation Failed!\nError: {e}")

    def load(self):
        try:
            if not os.path.exists(f"{DataRoot}\\data.json"):
                return False

            with open(f"{DataRoot}\\data.json", "r", encoding="utf-8") as f:
                data = json.load(f)
                self.user_name.setText(data["user_name"])
                self.user_password.setText(data["user_password"])
                self.captcha_retry_times.setText(str(data["captcha_retry_times"]))
                self.always_retry_check_box.setChecked(data["always_retry_check_box"])
                self.captcha_failed_email.setText(data["captcha_failed_email"])
                self.driver_path.setText(data["driver_path"])
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

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ConfigWindow()
    window.show()
    app.exec_()