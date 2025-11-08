import copy
import os
import json
import sys
from datetime import datetime

from PyQt5.QtCore import Qt, QDate, QLocale, QSize
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QGroupBox,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QCheckBox,
    QPushButton, QDialogButtonBox, QSizePolicy, QFormLayout, QComboBox, QListWidgetItem
)
from platformdirs import user_data_dir

from src.core.clock_manager import ClockManager, run_clock, get_driver_path
from src.extend.auto_windows_login import auto_windows_login_on, auto_windows_login_off
from src.ui.ui_calendar import Calendar
from src.extend.auto_windows_plan import create_task, delete_scheduled_task
from src.utils.log import Log
from src.utils.utils import Utils, data_json, tasks_json

BackGround_Color = "#ffffff"
Border_Color = "#000000"
Text_Color = "grey"
Border_Width = "1px"
Border_Radius = ""

class ConfigWindow(QMainWindow):
    task_list = []

    def __init__(self):
        super().__init__()
        # 标题图标和窗口大小
        self.setFixedSize(500, 700)
        self.setWindowTitle("Auto-Clock")
        self.setWindowIcon(QIcon(Utils.get_ico_path()))
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
        self.send_email_success = QCheckBox()
        self.send_email_failed = QCheckBox()
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

        layout_sys.addWidget(QLabel("Notification Email:"))
        layout_sys.addWidget(self.captcha_failed_email)
        layout_sys.addWidget(widget_retry)

        widget_send_email = QWidget()
        layout_send_email = QHBoxLayout(widget_send_email)
        layout_send_email.addWidget(QLabel("Send Email When:"))
        layout_send_email.addStretch()
        layout_send_email.addWidget(QLabel("Failed"))
        layout_send_email.addWidget(self.send_email_failed)
        layout_send_email.addWidget(QLabel("Success"))
        layout_send_email.addWidget(self.send_email_success)
        layout_send_email.addStretch()
        layout_sys.addWidget(widget_send_email)
        # Windows Config
        group_windows_config = QGroupBox("Windows Auto Login")
        group_windows_config.setStyleSheet(self.get_group_css({}))
        layout_windows = QVBoxLayout(group_windows_config)
        self.auto_windows_login_on = QPushButton("Set Windows Auto Login")
        self.auto_windows_login_on.clicked.connect(self.auto_login_windows)
        layout_windows.addWidget(self.auto_windows_login_on)
        # Plan List
        group_plan_list = QGroupBox("Windows Plan List")
        group_plan_list.setStyleSheet(self.get_group_css({}))
        layout_plan_list = QVBoxLayout(group_plan_list)
        self.widget_plan_list = QListWidget()
        layout_plan_list.addWidget(self.widget_plan_list)
        widget_plan_list_buttons = QWidget()
        self.button_create = QPushButton("Create")
        self.button_create.clicked.connect(self.create_windows_plan)
        self.button_delete = QPushButton("Delete")
        self.button_delete.clicked.connect(self.delete_windows_plan)
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
        layout_global.addWidget(group_windows_config)
        layout_global.addWidget(group_plan_list)
        layout_global.addWidget(widget_confirm)
        self.setCentralWidget(widget_global)
# 功能---------------------------------------------------------------------------------------------
        self.button_confirm.clicked.connect(self.confirm)
        self.button_try.clicked.connect(self.try_now)

        self.load()
        self.update_windows_plan_list()

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
            "always_retry_check_box": self.always_retry_check_box.isChecked(),
            "send_email_failed": self.send_email_failed.isChecked(),
            "send_email_success": self.send_email_success.isChecked()
        }
        if self.captcha_failed_email.text() != "":
            data["captcha_failed_email"] = self.captcha_failed_email.text()
        if retry_times is not None:
            data["captcha_retry_times"] = retry_times
        if tolerance_angle is not None:
            data["captcha_tolerance_angle"] = tolerance_angle

        try:
            ok = ClockManager.check_data(data)
            if not ok:
                raise Exception("Unknow Error")
        except Exception as e:
            raise Exception(e)

        Utils.write_dict_to_file(data_json, data)

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

            if not os.path.exists(data_json):
                return False

            data = Utils.read_dict_from_json(data_json)

            self.user_name.setText(data.get("user_name", ""))
            self.user_password.setText(data.get("user_password", ""))
            self.captcha_retry_times.setText(str(data.get("captcha_retry_times", "")))
            self.captcha_tolerance_angle.setText(str(data.get("captcha_tolerance_angle", "")))
            self.always_retry_check_box.setChecked(data.get("always_retry_check_box", False))
            self.send_email_failed.setChecked(data.get("send_email_failed", False))
            self.send_email_success.setChecked(data.get("send_email_success", False))
            self.captcha_failed_email.setText(data.get("captcha_failed_email", ""))
            if inner_driver is None:
                self.driver_path.setText(data.get("driver_path", ""))
            return True
        except Exception as e:
            MessageBox(f"Load Data Failed!\nError: {e}")
            Log.info(e)
            return False

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
        try:
            plan_ui = WindowsPlanDialog(self)
            if plan_ui.exec_() == QDialog.Accepted:
                value = plan_ui.values()
                Log.info(f"create windows plan value: {value}")
                plan_name = value.get("plan_name")
                trigger_type = value.get("trigger_type")
                operation = value.get("operation")
                if not value or not trigger_type or not operation:
                    return

                execute_time = value.get("hour") + ":" + value.get("minute")
                task_name = operation + "_Type_" + trigger_type
                task = {
                    "short_name": task_name if not plan_name else plan_name,
                    "operation": operation,
                    "trigger_type": trigger_type,
                    "execute_time": execute_time
                }

                plan_id = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
                task["plan_id"] = plan_id

                if trigger_type == "Multiple":
                    days = value.get("calendar")
                    ret = True
                    error_message = ""
                    tasks = {}
                    for day in days:
                        task["multiple_name"] = plan_name
                        task["plan_name"] = plan_name
                        execute_day = str(day.year()) + "-" + str(Utils.get_nums_array(day.month(),day.month(),2)[0]) + "-" + str(Utils.get_nums_array(day.day(),day.day(),2)[0])
                        task["execute_day"] = execute_day
                        temp_name = task_name
                        temp_name += execute_day
                        if task.get("plan_name") is None or task.get("plan_name") == "" or task.get("plan_name") == "Default":
                            task["plan_name"] = temp_name + "_" + execute_time
                        else:
                            task["plan_name"] += "_" + execute_day
                        task["plan_name"] += "_id_" + plan_id
                        task["plan_name"] = task["plan_name"].replace(":", "_").replace(" ", "_").replace("-", "_")
                        tasks[execute_day] = task["plan_name"]
                        Log.info(task)
                        ok, error = create_task(task)
                        if error:
                            error_message += str(error) + "\n"
                        if ok is False: ret = False
                    if ret:
                        MessageBox("Create Task Success!")
                        task["plan_name"] = tasks
                        tasks["execute_day"] = None
                    else:
                        raise Exception(error_message)
                else:
                    task["plan_name"] = plan_name
                    if trigger_type == "Once":
                        date = QDate(int(value.get("year")), int(value.get("month")), int(value.get("day")))
                        execute_day = value.get("year") + "-" + value.get("month") + "-" + value.get("day")
                        if date < QDate.currentDate():
                            raise Exception(f"Invalid Date: {execute_day} Early than Today!")
                        task["execute_day"] = execute_day
                        task_name += "_" + execute_day
                    # elif trigger_type == "Multipl":
                    #     days = value.get("calendar")
                    #     execute_days = []
                    #     for day in days:
                    #         execute_day = str(day.year()) + "-" + str(
                    #             Utils.get_nums_array(day.month(), day.month(), 2)[0]) + "-" + str(
                    #             Utils.get_nums_array(day.day(), day.day(), 2)[0])
                    #         execute_days.append(execute_day)
                    #     task["execute_days"] = execute_days
                    #     Log.info(f"execute_days {execute_days}")
                    #     task_name += execute_days[0] + "-" + execute_days[len(execute_days)-1]
                    elif trigger_type == "Weekly":
                        task["weekly"] = value.get("weekly")
                        task_name += "_" + value.get("weekly")
                    elif trigger_type == "Monthly":
                        task["monthly"] = value.get("monthly")
                        task_name += "_" + value.get("monthly")
                    task_name += "_" + execute_time
                    if task.get("plan_name") is None or task.get("plan_name") == "" or task.get("plan_name") == "Default":
                        task["plan_name"] = task_name
                    task["plan_name"] += "_id_" + plan_id
                    task["plan_name"] = task["plan_name"].replace(":", "_").replace(" ", "_").replace("-", "_")
                    Log.info(task)
                    ok, error = create_task(task)
                    if error:
                        raise Exception(error)
                    else:
                        MessageBox("Create Task Success!")
                self.add_windows_plan(task)
                Log.info(f"create windows plan task: {task}")
            else:
                return
        except Exception as e:
            Log.error(str(e))
            MessageBox(str(e))

    def update_windows_plan_list(self):
        try:
            dict_list = Utils.read_dict_from_json(tasks_json)
            if dict_list is None: return

            self.widget_plan_list.clear()
            if isinstance(dict_list, list):
                self.task_list = dict_list
                for plan_dict in self.task_list:
                    self.add_windows_plan_ui(plan_dict)
            elif isinstance(dict_list, dict):
                self.task_list.append(dict_list)
                self.add_windows_plan_ui(dict_list)
            else:
                raise Exception("Load tasks failed!")

        except Exception as e:
            message = f"Update windows plan list failed: {e}"
            Log.error(message)
            MessageBox(message)

    def add_windows_plan(self, task):
        self.task_list.append(task)
        Utils.write_dict_to_file(tasks_json, self.task_list)
        self.update_windows_plan_list()

    def add_windows_plan_ui(self, task):
        widget_plan_line = QWidget()
        widget_plan_line.setObjectName(task["plan_id"])
        layout_plan_line = QHBoxLayout(widget_plan_line)
        layout_plan_line.setContentsMargins(0, 0, 0, 0)
        layout_plan_line.setAlignment(Qt.AlignCenter | Qt.AlignLeft)
        front_size = 8
        label_alignment = Qt.AlignLeft
        label_p = create_label(Utils.truncate_text(task["plan_name"] if not isinstance(task["plan_name"], dict) else task.get("multiple_name", ""), 15),size=front_size, fixed_width=140)
        layout_plan_line.addWidget(label_p)
        label_o = create_label(Utils.truncate_text(task["operation"], 10),size=front_size, alignment=label_alignment, fixed_width=80)
        layout_plan_line.addWidget(label_o)
        label_t = create_label(task["trigger_type"], size=front_size, alignment=label_alignment, fixed_width=50)
        layout_plan_line.addWidget(label_t)
        label_et = create_label(task["execute_time"],size=front_size, alignment=Qt.AlignCenter, fixed_width=50)
        layout_plan_line.addWidget(label_et)
        if task["trigger_type"] == "Once":
            layout_plan_line.addWidget(create_label(task["execute_day"],size=front_size, alignment=Qt.AlignCenter, fixed_width=80))
        elif task["trigger_type"] == "Weekly":
            layout_plan_line.addWidget(create_label(task["weekly"],size=front_size, alignment=Qt.AlignCenter, fixed_width=80))
        elif task["trigger_type"] == "Monthly":
            layout_plan_line.addWidget(create_label(task["monthly"],size=front_size, alignment=Qt.AlignCenter, fixed_width=80))
        elif task["trigger_type"] == "Multiple":
            layout_plan_line.addWidget(create_label("[······]",size=front_size, alignment=Qt.AlignCenter, fixed_width=80))
            pass

        item = QListWidgetItem()
        item.setSizeHint(QSize(0, 40))
        self.widget_plan_list.addItem(item)
        self.widget_plan_list.setItemWidget(item, widget_plan_line)

    def delete_windows_plan(self):
        try:
            selected_item = self.widget_plan_list.currentItem()
            selected_widget = self.widget_plan_list.itemWidget(selected_item)
            if not selected_widget:
                Log.error("选中项未绑定Plan")
                return

            plan_id = selected_widget.objectName()
            Log.info(f"删除Plan: {plan_id}")

            delete_task = None
            for task in self.task_list:
                if task["plan_id"] == plan_id:
                    delete_task = task
                    break
            if delete_task is None:
                raise Exception(f"Delete plan failed, no plan id: {plan_id}")
            plan_name = delete_task["plan_name"]

            dlg = MessageBox(f"\nAre you really want to delete this Plan:\n\n{plan_name}\n", need_check=True, message_only=False, message_name="Delete Plan")
            if dlg.exec_() != QDialog.Accepted:
                return

            if delete_task["trigger_type"] == "Multiple":
                for task_name in plan_name:
                    ok, error = delete_scheduled_task(task_name)
                    if not ok: raise Exception(error)
            else:
                ok, error = delete_scheduled_task(plan_name)
                if not ok: raise Exception(error)
            self.task_list.remove(delete_task)
            Utils.write_dict_to_file(tasks_json, self.task_list)
            self.update_windows_plan_list()

        except Exception as e:
            Log.error(e)
            MessageBox(e)

class WindowsLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Set Windows Auto Login")
        self.setWindowIcon(QIcon(Utils.get_ico_path()))
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
    trigger_types = ["Once", "Multiple", "Daily", "Weekly", "Monthly"]
    operation_types = ["Auto Clock", "Shut Down Windows"]

    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.setMinimumWidth(500)
            self.setWindowTitle("Create Windows Plan")
            self.setWindowIcon(QIcon(Utils.get_ico_path()))
            self.plan_name_edit = QLineEdit()
            self.plan_name_edit.setText("Default")
            self.trigger_type = QComboBox()
            self.trigger_type.addItems(self.trigger_types)
            self.trigger_type.currentTextChanged.connect(self.trigger_type_changed)
            self.operation = QComboBox()
            self.operation.addItems(self.operation_types)
            self.locale = QLocale(QLocale.English)

            widget_layout = QVBoxLayout(self)

            # 常规设置
            widget_setting = QWidget()
            layout_setting = QVBoxLayout(widget_setting)
            widget_line_1 = QHBoxLayout()
            # 选择Plan Name
            widget_line_1.addWidget(create_label("Plan Name:"))
            widget_line_1.addWidget(self.plan_name_edit)
            widget_line_2 = QHBoxLayout()
            # 选择Trigger Type
            widget_line_2.addWidget(create_label("Trigger Type:"))
            widget_line_2.addWidget(self.trigger_type)
            # 选择Operation
            widget_line_3 = QHBoxLayout()
            widget_line_3.addWidget(create_label("Operation:"))
            widget_line_3.addWidget(self.operation)
            layout_setting.addLayout(widget_line_1)
            layout_setting.addLayout(widget_line_2)
            layout_setting.addLayout(widget_line_3)
            widget_layout.addWidget(widget_setting)
            # 选择DayTime
            self.widget_day_time_selector = QWidget()
            self.layout_day_time_selector = QHBoxLayout(self.widget_day_time_selector)
            self.hour_sel = QComboBox()
            self.hour_sel.addItems(Utils.get_nums_array(0,23))
            self.hour_sel.setCurrentIndex(datetime.now().hour)
            self.minute_sel = QComboBox()
            self.minute_sel.addItems(Utils.get_nums_array(0,59))
            self.minute_sel.setCurrentIndex(datetime.now().minute)
            self.layout_day_time_selector.addWidget(create_label("DayTime:"))
            self.layout_day_time_selector.addStretch()
            self.layout_day_time_selector.addWidget(create_label("Hours:", size=10, length=50))
            self.layout_day_time_selector.addWidget(self.hour_sel)
            self.layout_day_time_selector.addWidget(create_label("Minute:", size=10, length=50))
            self.layout_day_time_selector.addWidget(self.minute_sel)
            widget_layout.addWidget(self.widget_day_time_selector)

            widget_layout.addStretch()

            # 批量选择
            self.calendar_selector = Calendar()

            # 指定日
            self.widget_one_day_selector = QWidget()
            self.layout_one_day_selector = QHBoxLayout(self.widget_one_day_selector)
            self.year_sel = QComboBox()
            self.year_sel.addItems([str(QDate.currentDate().year()), str(QDate.currentDate().addYears(1).year())])
            self.year_sel.currentIndexChanged.connect(self.year_changed)
            self.month_sel = QComboBox()
            self.month_sel.addItems(Utils.get_nums_array(1,12))
            self.month_sel.setCurrentIndex(datetime.now().month - 1)
            self.month_sel.currentIndexChanged.connect(self.month_changed)
            self.day_sel = QComboBox()
            self.day_sel.addItems(Utils.get_nums_array(1, 31))
            self.day_sel.setCurrentIndex(datetime.now().day - 1)
            self.layout_one_day_selector.addWidget(create_label("Year:", size=10, length=50))
            self.layout_one_day_selector.addWidget(self.year_sel)
            self.layout_one_day_selector.addWidget(create_label("Month:", size=10, length=50))
            self.layout_one_day_selector.addWidget(self.month_sel)
            self.layout_one_day_selector.addWidget(create_label("Day:", size=10, length=50))
            self.layout_one_day_selector.addWidget(self.day_sel)
            # 每日
            self.widget_daily_selector = QWidget()
            # 指定每周
            self.widget_weekly_selector = QWidget()
            self.layout_weekly_selector = QHBoxLayout(self.widget_weekly_selector)
            self.weekly_day_sel = QComboBox()
            for i in range(1, 8):
                self.weekly_day_sel.addItem(self.locale.dayName(int(i), QLocale.LongFormat))
            self.layout_weekly_selector.addWidget(create_label("The Day:"))
            self.layout_weekly_selector.addWidget(self.weekly_day_sel)
            self.weekly_day_sel.setCurrentIndex(QDate.currentDate().dayOfWeek() - 1)
            # 指定每月
            self.widget_monthly_selector = QWidget()
            self.layout_monthly_selector = QHBoxLayout(self.widget_monthly_selector)
            self.monthly_day_sel = QComboBox()
            self.monthly_day_sel.addItems(Utils.get_nums_array(1,31))
            self.layout_monthly_selector.addWidget(create_label("The Day:"))
            self.layout_monthly_selector.addWidget(self.monthly_day_sel)
            self.monthly_day_sel.setCurrentIndex(datetime.now().day - 1)

            # 预留变化区
            self.space_area = QVBoxLayout()
            self.space_area.addWidget(self.widget_one_day_selector)
            self.space_area.addWidget(self.calendar_selector)
            self.space_area.addWidget(self.widget_daily_selector)
            self.space_area.addWidget(self.widget_weekly_selector)
            self.space_area.addWidget(self.widget_monthly_selector)
            widget_layout.addLayout(self.space_area)
            self.space_area_hide_all_content()
            self.widget_one_day_selector.show()

            # 按键
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(self.accept)
            buttons.rejected.connect(self.reject)
            widget_layout.addWidget(buttons)
        except Exception as e:
            Log.error(e)
            MessageBox(e)

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
        self.day_sel.addItems(Utils.get_nums_array(1, day))
        self.day_sel.setCurrentIndex(0)

    def space_area_hide_all_content(self):
        for i in range(self.space_area.count()):
            item = self.space_area.itemAt(i)
            widget = item.widget()
            if widget is not None:
                widget.hide()

    def trigger_type_changed(self):
        self.space_area_hide_all_content()
        if self.trigger_type.currentText() == self.trigger_types[1]:
            self.calendar_selector.show()
        elif self.trigger_type.currentText() == self.trigger_types[0]:
            self.widget_one_day_selector.show()
        elif self.trigger_type.currentText() == self.trigger_types[3]:
            self.widget_weekly_selector.show()
        elif self.trigger_type.currentText() == self.trigger_types[4]:
            self.widget_monthly_selector.show()
        else:
            self.widget_daily_selector.show()

        self.adjustSize()

    def values(self):
        selected_dates = copy.deepcopy(self.calendar_selector.selected_dates)
        self.calendar_selector.selected_dates.clear()
        return {
            "plan_name": self.plan_name_edit.text().strip(),
            "trigger_type": self.trigger_type.currentText().strip(),
            "operation": self.operation.currentText().strip() ,
            "year": self.year_sel.currentText().strip(),
            "month": self.month_sel.currentText().strip(),
            "day": self.day_sel.currentText().strip(),
            "hour": self.hour_sel.currentText().strip(),
            "minute": self.minute_sel.currentText().strip(),
            "calendar": selected_dates,
            "weekly": self.weekly_day_sel.currentText().strip()[0:3],
            "monthly": self.monthly_day_sel.currentText().strip()
        }

class MessageBox(QDialog):
    def __init__(self, message, message_name="Message", parent=None, need_check=False, message_only=True):
        super().__init__(parent)
        self.setWindowTitle(message_name)
        self.setWindowIcon(QIcon(Utils.get_ico_path()))

        label = QLabel(str(message))
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
        if need_check:
            button = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button.rejected.connect(self.reject)
        else:
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
        if message_only:
            self.exec_()

def create_label(message, size=11, length=150, family="Arial", width_policy=None, height_policy=None, alignment=None, fixed_width=None, fixed_height=None):
    label = QLabel(message)
    font = QFont()
    font.setFamily(family)
    font.setPointSize(size)
    label.setFont(font)
    label.setFixedWidth(length)
    if width_policy is not None and height_policy is not None:
        label.setSizePolicy(width_policy, height_policy)
    if alignment is not None:
        label.setAlignment(alignment)
    if fixed_width is not None:
        label.setFixedWidth(fixed_width)
    if fixed_height is not None:
        label.setFixedHeight(fixed_height)
    return label