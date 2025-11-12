import os
import sys
from pathlib import Path
from dataclasses import dataclass

from platformdirs import user_data_dir


@dataclass
class Key:
    TaskName: str = "task_name"
    TaskID: str = "task_id"
    TriggerType: str = "trigger_type"
    Operation: str = "operation"
    WindowsPlanName: str = "windows_plan_name"
    ExecuteTime: str = "execute_time"
    ExecuteDay: str = "execute_day"
    ExecuteDays: str = "execute_days"

    Year: str = "year"
    Month: str = "month"
    Day: str = "day"
    Hour: str = "hour"
    Minute: str = "minute"

    Once: str = "Once"
    Multiple: str = "Multiple"
    Daily: str = "Daily"
    Weekly: str = "Weekly"
    Monthly: str = "Monthly"

    NotificationEmail: str = "notification_email"
    SendEmailWhenSuccess: str = "send_email_success"
    SendEmailWhenFailed: str = "send_email_failed"

    UserName: str = "user_name"
    UserPassword: str = "user_password"
    DriverPath: str = "driver_path"
    CaptchaRetryTimes: str = "captcha_retry_times"
    CaptchaToleranceAngle: str = "captcha_tolerance_angle"
    AlwaysRetry: str = "always_retry"
    ShowWebPage: str = "show_web_page"

    AutoClock: str = "Auto Clock"
    ShutDownWindows: str = "Shut Down Windows"
    WindowsSleep: str = "Windows Sleep"
    # 新增断网和联网操作类型
    DisconnectNetwork: str = "Disconnect Network"
    ConnectNetwork: str = "Connect Network"

    DefaultWindowsPlanName: str = "AutoClock_Windows_Plan"
    Unknown: str = "Unknown"
    Empty: str = ""

@dataclass
class AppPath:
    LogRoot = user_data_dir("log", "auto-clock")
    DataRoot = user_data_dir("data", "auto-clock")
    BackupRoot = user_data_dir("backup", "auto-clock")
    ScreenshotRoot = user_data_dir("screenshot", "auto-clock")
    DataJson: str = f"{DataRoot}\\data.json"
    TasksJson: str = f"{DataRoot}\\tasks.json"
    if hasattr(sys, '_MEIPASS'):
        ProjectRoot = sys._MEIPASS
    else:
        ProjectRoot = os.path.abspath(".")
    ConfigJson: str = f"{ProjectRoot}\\config.json"

@dataclass
class WebPath:
    AppConfigPathGitee: str = "https://gitee.com/garfieldgod/auto-clock/raw/master/config.json"
    AppConfigPathGitHub: str = "https://github.com/garfieldgod/auto-clock/raw/master/config.json"
    AppProjectPath: str = "https://github.com/GarfieldGod/auto-clock"
    NeusoftKQPath: str = "https://kq.neusoft.com/"
    NeusoftKQLoginPath: str = "https://kq.neusoft.com/login"