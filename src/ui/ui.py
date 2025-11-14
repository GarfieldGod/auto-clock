import os
import webbrowser
from datetime import datetime

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QDate, QSize
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QDialog, QGroupBox,
    QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QListWidget, QCheckBox,
    QPushButton, QSizePolicy, QListWidgetItem
)

from src.utils.log import Log
from src.utils.const import Key, AppPath, WebPath
from src.ui.ui_message import MessageBox
from src.ui.ui_windows_plan import WindowsPlanDialog
from src.ui.ui_windows_login import WindowsLoginDialog
from src.utils.update import VersionCheckThread
from src.utils.utils import Utils, QtUI
from src.extend.auto_windows_login import auto_windows_login_on
from src.core.clock_manager import ClockManager, run_clock, get_driver_path
from src.extend.auto_windows_plan import create_task, delete_scheduled_task
from src.extend.network_manager import connect_network, disconnect_network


Text_Color = "grey"
Border_Width = "1px"
Border_Color = "#000000"
Border_Radius = Key.Empty
BackGround_Color = "#ffffff"

class ConfigWindow(QMainWindow):
    task_list = []

    def __init__(self):
        super().__init__()
        self.setFixedSize(500, 800)
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
        screen_geometry = QApplication.desktop().screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)
# 布局---------------------------------------------------------------------------------------------
        # User Information
        self.user_name = QLineEdit()
        self.user_password = QLineEdit()
        self.user_password.setEchoMode(QLineEdit.Password)  # 设置密码框隐藏输入
        
        # 创建密码可见性切换按钮
        self.show_password_btn = QPushButton()
        self.show_password_btn.setFixedSize(24, 24)
        self.show_password_btn.setStyleSheet("border: none; background-color: transparent;")
        
        # 使用锁图标作为默认状态（密码隐藏）
        self.show_password_btn.setText("🔒")
        self.show_password_btn.setToolTip("显示密码")
        self.show_password_btn.clicked.connect(self.toggle_password_visibility)
        self.captcha_retry_times = QLineEdit()
        self.notification_email = QLineEdit()
        self.captcha_tolerance_angle = QLineEdit()
        self.driver_path = QLineEdit()
        self.always_retry_check_box = QCheckBox()
        self.send_email_success = QCheckBox()
        self.send_email_failed = QCheckBox()
        self.show_web_page = QCheckBox()
        # Must Config
        group_user = QGroupBox("Login Config")
        group_user.setStyleSheet(self.get_group_css({"Text_Color":"#D32F2F"}))
        layout_function = QVBoxLayout(group_user)
        layout_username = QVBoxLayout()
        layout_username.addWidget(QLabel("UserName:"))
        layout_username.addWidget(self.user_name)
        # 创建密码输入的垂直布局
        layout_password = QVBoxLayout()
        layout_password.addWidget(QLabel("Password:"))
        
        # 创建水平布局来容纳密码输入框和眼睛图标按钮
        password_input_layout = QHBoxLayout()
        password_input_layout.addWidget(self.user_password)
        password_input_layout.addWidget(self.show_password_btn)
        password_input_layout.setContentsMargins(0, 0, 0, 0)
        
        layout_password.addLayout(password_input_layout)
        layout_user = QVBoxLayout()
        layout_user.addLayout(layout_username)
        layout_user.addLayout(layout_password)
        layout_function.addLayout(layout_user)
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
        widget_retry_d = QWidget()
        layout_retry_d = QVBoxLayout(widget_retry_d)
        layout_retry_d.setContentsMargins(0, 0, 0, 0)
        layout_retry_d.addWidget(QLabel("Show Web:"))
        layout_retry_d.addWidget(self.show_web_page)

        layout_retry.addWidget(widget_retry_a)
        layout_retry.addWidget(widget_retry_c)
        layout_retry.addWidget(widget_retry_b)
        layout_retry.addWidget(widget_retry_d)
        layout_sys.addWidget(widget_retry)

        # Notification Config
        group_notification = QGroupBox("Notification Config")
        group_notification.setStyleSheet(self.get_group_css({}))
        layout_notification = QVBoxLayout(group_notification)

        layout_email = QVBoxLayout()
        layout_email.addWidget(QLabel("Notification Email:"))
        layout_email.addWidget(self.notification_email)

        layout_send_email = QHBoxLayout()
        layout_send_email.addWidget(QLabel("Send Email When:"))
        layout_send_email.addStretch()
        layout_send_email_checkbox = QHBoxLayout()
        layout_send_email_checkbox.addWidget(QLabel("Failed"))
        layout_send_email_checkbox.addWidget(self.send_email_failed)
        layout_send_email_checkbox.addWidget(QLabel("Success"))
        layout_send_email_checkbox.addWidget(self.send_email_success)
        layout_send_email.addLayout(layout_send_email_checkbox)
        layout_send_email.addStretch()
        layout_notification.addLayout(layout_email)
        layout_notification.addLayout(layout_send_email)

        # Windows Config
        group_windows = QGroupBox("Windows Config")
        group_windows.setStyleSheet(self.get_group_css({}))
        layout_plan_list = QVBoxLayout(group_windows)

        self.auto_windows_login_on = QPushButton("Set Windows Auto Login")
        self.auto_windows_login_on.clicked.connect(self.auto_login_windows)
        layout_plan_list.addWidget(self.auto_windows_login_on)
        
        self.widget_plan_list = QListWidget()
        layout_plan_list.addWidget(QLabel("Windows Plan List:"))
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

        # Confirm or Try
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
        layout_global.addWidget(group_notification)
        layout_global.addWidget(group_windows)
        layout_global.addWidget(widget_confirm)
        self.setCentralWidget(widget_global)
# 功能---------------------------------------------------------------------------------------------
        self.button_confirm.clicked.connect(self.confirm)
        self.button_try.clicked.connect(self.try_now)

        self.load()
        self.update_windows_plan_list()
        self.check_app_update()

    def write_json(self):
        retry_times = None
        tolerance_angle = None
        if self.captcha_retry_times.text() != Key.Empty:
            retry_times = int(self.captcha_retry_times.text())
        if self.captcha_tolerance_angle.text() != Key.Empty:
            tolerance_angle = int(self.captcha_tolerance_angle.text())
        data = {
            Key.UserName: self.user_name.text(),
            Key.UserPassword: self.user_password.text(),
            Key.DriverPath: self.driver_path.text(),
            Key.AlwaysRetry: self.always_retry_check_box.isChecked(),
            Key.ShowWebPage: self.show_web_page.isChecked(),
            Key.SendEmailWhenFailed: self.send_email_failed.isChecked(),
            Key.SendEmailWhenSuccess: self.send_email_success.isChecked()
        }
        if self.notification_email.text() != Key.Empty:
            data[Key.NotificationEmail] = self.notification_email.text()
        if retry_times is not None:
            data[Key.CaptchaRetryTimes] = retry_times
        if tolerance_angle is not None:
            data[Key.CaptchaToleranceAngle] = tolerance_angle

        try:
            ok = ClockManager.check_data(data)
            if not ok:
                raise Exception("Unknow Error")
        except Exception as e:
            raise Exception(e)

        Utils.write_dict_to_file(AppPath.DataJson, data)

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

            if not os.path.exists(AppPath.DataJson):
                return False

            data = Utils.read_dict_from_json(AppPath.DataJson)

            self.user_name.setText(data.get(Key.UserName, Key.Empty))
            self.user_password.setText(data.get(Key.UserPassword, Key.Empty))
            self.captcha_retry_times.setText(str(data.get(Key.CaptchaRetryTimes, Key.Empty)))
            self.captcha_tolerance_angle.setText(str(data.get(Key.CaptchaToleranceAngle, Key.Empty)))
            self.always_retry_check_box.setChecked(data.get(Key.AlwaysRetry, False))
            self.show_web_page.setChecked(data.get(Key.ShowWebPage, False))
            self.send_email_failed.setChecked(data.get(Key.SendEmailWhenFailed, False))
            self.send_email_success.setChecked(data.get(Key.SendEmailWhenSuccess, False))
            self.notification_email.setText(data.get(Key.NotificationEmail, Key.Empty))
            if inner_driver is None:
                self.driver_path.setText(data.get(Key.DriverPath, Key.Empty))
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
    
    # 添加断网功能
    def toggle_password_visibility(self):
        """切换密码可见性"""
        if self.user_password.echoMode() == QLineEdit.Password:
            # 显示密码 - 使用普通眼睛图标
            self.user_password.setEchoMode(QLineEdit.Normal)
            self.show_password_btn.setText("👁")
            self.show_password_btn.setToolTip("隐藏密码")
        else:
            # 隐藏密码 - 使用闭眼睛+斜杠图标
            self.user_password.setEchoMode(QLineEdit.Password)
            self.show_password_btn.setText("🔒")
            self.show_password_btn.setToolTip("显示密码")
            
    def disconnect_network_now(self):
        try:
            success, error = disconnect_network()
            if success:
                MessageBox("Network disconnected successfully!")
            else:
                MessageBox(f"Failed to disconnect network: {error}")
        except Exception as e:
            MessageBox(f"Error disconnecting network: {str(e)}")
    
    # 添加联网功能
    def connect_network_now(self):
        try:
            success, error = connect_network()
            if success:
                MessageBox("Network connected successfully!")
            else:
                MessageBox(f"Failed to connect network: {error}")
        except Exception as e:
            MessageBox(f"Error connecting network: {str(e)}")

    def get_group_css(self, css_data):
        background_color = css_data["BackGround_Color"] if css_data.get("BackGround_Color") is not None and css_data["BackGround_Color"] != Key.Empty else BackGround_Color
        text_color = css_data["Text_Color"] if css_data.get("Text_Color") is not None and css_data["Text_Color"] != Key.Empty else Text_Color
        border_color = css_data["Border_Color"] if css_data.get("Border_Color") is not None and css_data["Border_Color"] != Key.Empty else Border_Color
        border_width = css_data["Border_Width"] if css_data.get("Border_Width") is not None and css_data["Border_Width"] != Key.Empty else Border_Width
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
                plan_name = value.get(Key.WindowsPlanName)
                operation = value.get(Key.Operation)
                trigger_type = value.get(Key.TriggerType)
                execute_time = value.get(Key.Hour) + ":" + value.get(Key.Minute)
                if not value or not trigger_type or not operation:
                    return

                task_id = datetime.now().strftime("%Y_%m_%d_%H_%M_%S_%f")
                is_no_name = plan_name is None or plan_name == Key.Empty or plan_name == Key.DefaultWindowsPlanName
                task = {
                    Key.TaskName: Key.DefaultWindowsPlanName if is_no_name else plan_name,
                    Key.TaskID: task_id,
                    Key.Operation: operation,
                    Key.TriggerType: trigger_type,
                    Key.ExecuteTime: execute_time
                }

                if trigger_type == Key.Multiple:
                    multiple_tasks = {}
                    execute_days = value.get(Key.ExecuteDays)
                    ret, error_message = True, Key.Empty
                    for execute_day in execute_days:
                        task[Key.ExecuteDay] = execute_day
                        task[Key.WindowsPlanName] = task[Key.TaskName] + "_Type_" + trigger_type + "_Date_" + execute_day + "_Time_" + execute_time + "_Id_" + task_id
                        task[Key.WindowsPlanName] = Utils.replace_signs(task[Key.WindowsPlanName])
                        ok, error = create_task(task)
                        multiple_tasks[execute_day] = task[Key.WindowsPlanName]
                        if error:
                            error_message += str(error) + "\n"
                        if ok is False: ret = False
                    if ret:
                        MessageBox(f"Create Task: {task[Key.TaskName]} Success!")
                        task[Key.WindowsPlanName] = multiple_tasks
                        task.pop(Key.ExecuteDay)
                    else:
                        raise Exception(error_message)
                else:
                    task[Key.WindowsPlanName] = plan_name
                    if trigger_type == Key.Once:
                        date = QDate(int(value.get(Key.Year)), int(value.get(Key.Month)), int(value.get(Key.Day)))
                        execute_day = value.get(Key.Year) + "-" + value.get(Key.Month) + "-" + value.get(Key.Day)
                        if date < QDate.currentDate():
                            raise Exception(f"Invalid Date: {execute_day} Early than Today!")
                        task[Key.ExecuteDay] = execute_day
                    elif trigger_type == Key.Daily:
                        pass
                    elif trigger_type == Key.Weekly:
                        dates = value.get(Key.Weekly)
                        if not dates and len(dates) == 0: return
                        dates_str = dates[0]
                        for i in range(1, len(dates)):
                            dates_str +=  "," + dates[i]
                        task[Key.ExecuteDay] = dates_str
                    elif trigger_type == Key.Monthly:
                        task[Key.ExecuteDay] = value.get(Key.Monthly)
                    else:
                        return
                    task[Key.WindowsPlanName] = (task[Key.TaskName] +
                                                 "_Type_" + trigger_type +
                                                 "_Date_" +task.get(Key.ExecuteDay, Key.Unknown if trigger_type != Key.Daily else Key.Daily) +
                                                 "_Time_" + execute_time +
                                                 "_Id_" + task_id)
                    task[Key.WindowsPlanName] = Utils.replace_signs(task[Key.WindowsPlanName])
                    ok, error = create_task(task)
                    if error:
                        raise Exception(error)
                    else:
                        MessageBox(f"Create Task: {task[Key.TaskName]} Success!")
                self.add_windows_plan(task)
                Log.info(f"create windows plan task: {task}")
        except Exception as e:
            Log.error(str(e))
            MessageBox(str(e))

    def update_windows_plan_list(self):
        try:
            dict_list = Utils.read_dict_from_json(AppPath.TasksJson)
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
        Utils.write_dict_to_file(AppPath.TasksJson, self.task_list)
        self.update_windows_plan_list()

    def add_windows_plan_ui(self, task):
        widget_plan_line = QWidget()
        widget_plan_line.setObjectName(task[Key.TaskID])
        layout_plan_line = QHBoxLayout(widget_plan_line)
        layout_plan_line.setContentsMargins(0, 0, 0, 0)
        layout_plan_line.setAlignment(Qt.AlignCenter | Qt.AlignLeft)
        front_size = 8
        label_alignment = Qt.AlignLeft
        label_p = QtUI.create_label(Utils.truncate_text(task[Key.TaskName], 15),size=front_size, fixed_width=140)
        layout_plan_line.addWidget(label_p)
        label_o = QtUI.create_label(Utils.truncate_text(task[Key.Operation], 10),size=front_size, alignment=label_alignment, fixed_width=80)
        layout_plan_line.addWidget(label_o)
        label_t = QtUI.create_label(task[Key.TriggerType], size=front_size, alignment=label_alignment, fixed_width=50)
        layout_plan_line.addWidget(label_t)
        label_et = QtUI.create_label(task[Key.ExecuteTime],size=front_size, alignment=Qt.AlignCenter, fixed_width=50)
        layout_plan_line.addWidget(label_et)
        if task[Key.TriggerType] == Key.Once:
            layout_plan_line.addWidget(QtUI.create_label(task[Key.ExecuteDay],size=front_size, alignment=Qt.AlignCenter, fixed_width=80))
        elif task[Key.TriggerType] == Key.Weekly:
            layout_plan_line.addWidget(QtUI.create_label(task[Key.ExecuteDay],size=front_size, alignment=Qt.AlignCenter, fixed_width=80))
        elif task[Key.TriggerType] == Key.Monthly:
            layout_plan_line.addWidget(QtUI.create_label(task[Key.ExecuteDay],size=front_size, alignment=Qt.AlignCenter, fixed_width=80))
        elif task[Key.TriggerType] == Key.Multiple:
            layout_plan_line.addWidget(QtUI.create_label("[······]",size=front_size, alignment=Qt.AlignCenter, fixed_width=80))
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
                if task[Key.TaskID] == plan_id:
                    delete_task = task
                    break
            if delete_task is None:
                raise Exception(f"Delete plan failed, no plan id: {plan_id}")
            short_name = delete_task[Key.TaskName]
            plan_name = delete_task[Key.WindowsPlanName]

            dlg = MessageBox(f"\nAre you really want to delete this Plan:\n\n{short_name}\n", need_check=True, message_only=False, message_name="Delete Plan")
            if dlg.exec_() != QDialog.Accepted:
                return

            if delete_task[Key.TriggerType] == Key.Multiple:
                for task_name in plan_name:
                    ok, error = delete_scheduled_task(plan_name.get(task_name))
                    if not ok: raise Exception(error)
            else:
                ok, error = delete_scheduled_task(plan_name)
                if not ok: raise Exception(error)
            self.task_list.remove(delete_task)
            Utils.write_dict_to_file(AppPath.TasksJson, self.task_list)
            self.update_windows_plan_list()

        except Exception as e:
            Log.error(e)
            MessageBox(e)

    def check_app_update(self):
        self.thread = VersionCheckThread()
        self.thread.check_finished.connect(self.on_check_done)
        self.thread.finished.connect(self.thread.deleteLater)
        self.thread.start()

    def on_check_done(self, ok, ver):
        if ok and ver:
            is_update = MessageBox(
                f"There is a new version for the app:\t\n\n"
                f"Local: {ver.get('local')} Newest: {ver.get('remote')}\t\n\n"
                f"Do you want to download new ?\t\n\n",
                need_check=True, message_only=False)
            if is_update.exec_() == QDialog.Accepted:
                webbrowser.open_new(WebPath.AppProjectPath)