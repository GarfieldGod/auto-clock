import copy
from datetime import datetime

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QDate, QLocale
from PyQt5.QtWidgets import QDialogButtonBox, QVBoxLayout, QComboBox, QWidget, QHBoxLayout, QLineEdit, QDialog

from src.utils.log import Log
from src.utils.const import Key
from src.ui.ui_calendar import Calendar
from src.utils.utils import Utils, QtUI
from src.ui.ui_message import MessageBox


class WindowsPlanDialog(QDialog):
    trigger_types = [Key.Once, Key.Multiple, Key.Daily, Key.Weekly, Key.Monthly]
    operation_types = [Key.AutoClock, Key.ShutDownWindows, Key.WindowsSleep]

    def __init__(self, parent=None):
        super().__init__(parent)
        try:
            self.setMinimumWidth(500)
            self.setWindowTitle("Create Windows Plan")
            self.setWindowIcon(QIcon(Utils.get_ico_path()))
            self.plan_name_edit = QLineEdit()
            self.plan_name_edit.setText(Key.DefaultWindowsPlanName)
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
            widget_line_1.addWidget(QtUI.create_label("Plan Name:"))
            widget_line_1.addWidget(self.plan_name_edit)
            widget_line_2 = QHBoxLayout()
            # 选择Trigger Type
            widget_line_2.addWidget(QtUI.create_label("Trigger Type:"))
            widget_line_2.addWidget(self.trigger_type)
            # 选择Operation
            widget_line_3 = QHBoxLayout()
            widget_line_3.addWidget(QtUI.create_label("Operation:"))
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
            self.layout_day_time_selector.addWidget(QtUI.create_label("DayTime:"))
            self.layout_day_time_selector.addStretch()
            self.layout_day_time_selector.addWidget(QtUI.create_label("Hours:", size=10, length=50))
            self.layout_day_time_selector.addWidget(self.hour_sel)
            self.layout_day_time_selector.addWidget(QtUI.create_label("Minute:", size=10, length=50))
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
            self.layout_one_day_selector.addWidget(QtUI.create_label("Year:", size=10, length=50))
            self.layout_one_day_selector.addWidget(self.year_sel)
            self.layout_one_day_selector.addWidget(QtUI.create_label("Month:", size=10, length=50))
            self.layout_one_day_selector.addWidget(self.month_sel)
            self.layout_one_day_selector.addWidget(QtUI.create_label("Day:", size=10, length=50))
            self.layout_one_day_selector.addWidget(self.day_sel)
            # 每日
            self.widget_daily_selector = QWidget()
            # 指定每周
            self.widget_weekly_selector = QWidget()
            self.layout_weekly_selector = QHBoxLayout(self.widget_weekly_selector)
            self.weekly_day_sel = QComboBox()
            for i in range(1, 8):
                self.weekly_day_sel.addItem(self.locale.dayName(int(i), QLocale.LongFormat))
            self.layout_weekly_selector.addWidget(QtUI.create_label("The Day:"))
            self.layout_weekly_selector.addWidget(self.weekly_day_sel)
            self.weekly_day_sel.setCurrentIndex(QDate.currentDate().dayOfWeek() - 1)
            # 指定每月
            self.widget_monthly_selector = QWidget()
            self.layout_monthly_selector = QHBoxLayout(self.widget_monthly_selector)
            self.monthly_day_sel = QComboBox()
            self.monthly_day_sel.addItems(Utils.get_nums_array(1,31))
            self.layout_monthly_selector.addWidget(QtUI.create_label("The Day:"))
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
            Key.WindowsPlanName: self.plan_name_edit.text().strip(),
            Key.TriggerType: self.trigger_type.currentText().strip(),
            Key.Operation: self.operation.currentText().strip() ,
            Key.Year: self.year_sel.currentText().strip(),
            Key.Month: self.month_sel.currentText().strip(),
            Key.Day: self.day_sel.currentText().strip(),
            Key.Hour: self.hour_sel.currentText().strip(),
            Key.Minute: self.minute_sel.currentText().strip(),
            Key.ExecuteDays: selected_dates,
            Key.Weekly: self.weekly_day_sel.currentText().strip()[0:3],
            Key.Monthly: self.monthly_day_sel.currentText().strip()
        }