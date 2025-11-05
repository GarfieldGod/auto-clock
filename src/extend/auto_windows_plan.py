import ctypes
import os
import sys
import subprocess
from pathlib import Path

from utils.log import Log

def get_operation(operation_type):
    if operation_type == "Auto Clock":
        exe_path = get_current_exe_path()
        exe_path = Path(exe_path).absolute()
        Log.info(exe_path)
        if not exe_path.exists():
            message = f"Error: exe file do not exist: {exe_path}"
            Log.error(message)
            raise Exception(message)
        return exe_path, "--auto"
    elif operation_type == "Shut Down Windows":
        return "shutdown", ""
    else:
        message = "Unknow operation type!"
        Log.error(message)
        raise Exception(message)

def create_scheduled_task(
    task_name: str,
    operation: str,
    trigger_type: str,  # 触发类型：daily=每天，onlogon=登录后，weekly=每周
    day: str = None,
    time: str = None,          # 仅 trigger_type=daily/weekly 有效，格式 HH:MM
) -> bool:
    """
    创建 Windows 计划任务，自动定时运行 exe

    :param task_name: 计划任务名称（唯一）
    :param operation: 要执行的操作
    :param trigger_type: 触发类型：daily(每天)/onlogon(登录后)/weekly(每周)
    :param day: 执行日期
    :param time: 执行时间
    :return: 创建成功返回 True，失败返回 False
    """
    run_as_admin: bool = True
    exe_path, arguments = get_operation(operation)

    cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", f'"{exe_path}" {arguments}'.strip(),
        "/sc", trigger_type,
        "/f" # 强制覆盖同名任务
    ]

    if trigger_type == "ONCE" and day is not None:
        cmd.extend(["/sd", day])

    if trigger_type in ["Weekly", "Monthly"] and day is not None:
        cmd.extend(["/d", day])

    if not time or len(time.split(":")) != 2:
        raise Exception(f"Error: Invalid time format: {time} (Valid format: HH:MM, e.g., 08:30)")
    cmd.extend(["/st", time])

    if run_as_admin:
        cmd.extend(["/rl", "highest"])

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            encoding="gbk",
            errors="ignore",
            capture_output=True,
            timeout=30
        )
        Log.info(cmd)

        if result.stdout:
            Log.info(f"命令输出：{result.stdout.strip()}")
        if result.stderr:
            Log.info(f"命令警告：{result.stderr.strip()}")

        check_cmd = ["schtasks", "/query", "/tn", task_name, "/fo", "list"]
        check_result = subprocess.run(
            check_cmd, shell=True, encoding="gbk", capture_output=True
        )

        Log.info(check_result.stdout)

        if "任务名" in check_result.stdout or result.stderr is None:
            Log.info(f"\n计划任务创建成功！")
            Log.info(f"任务名：{task_name}")
            Log.info(f"触发类型：{trigger_type}")
            if trigger_type in ["daily", "weekly"]:
                Log.info(f"执行时间：{time}")
            Log.info(f"执行命令：{exe_path} {arguments}")
            Log.info(f"管理员权限：{'是' if run_as_admin else '否'}")
            return True
        else:
            message = f"\nCreate task failed!"
            Log.error(message)
            raise Exception(message)

    except subprocess.TimeoutExpired:
        message = f"Error：Create task timeout!"
        Log.error(message)
        raise Exception(message)
    except Exception as e:
        message = f"Create task error: {str(e)}"
        Log.error(message)
        raise Exception(message)

def delete_scheduled_task(task_name: str) -> bool:
    """删除计划任务"""
    try:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", task_name, "/f"],
            shell=True, encoding="gbk", capture_output=True
        )
        if "成功" in result.stdout or result.returncode == 0:
            Log.info(f"已删除计划任务：{task_name}")
            return True
        else:
            Log.info(f"Delete task failed: {result.stderr.strip()}")
            return False
    except Exception as e:
        message = (f"Delete task error: {str(e)}")
        Log.error(message)
        raise Exception(message)

def get_task_day(target_date):
    try:
        year, month, day = target_date.split("-")
        windows_date = f"{month}/{day}/{year}"
        return windows_date
    except Exception as e:
        message = f"Invalid time format (Valid format: HH:MM, e.g., 08:30), Error: {e}"
        Log.error(message)
        raise Exception(message)

def get_current_exe_path():
    current_dir = None
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
        current_dir = os.path.dirname(exe_path)
    return current_dir

def create_task(task):
    try:
        if not ctypes.windll.shell32.IsUserAnAdmin():
            message = "No permission! Please run as an administrator!"
            Log.error(message)
            raise Exception(message)

        # 删除旧任务
        delete_scheduled_task(task.get("plan_name"))

        ui_trigger_type = task.get("trigger_type")
        ok = False
        if ui_trigger_type == "Once" or ui_trigger_type == "Multiple":
            ok = create_scheduled_task(
                task_name=task.get("plan_name"),
                operation=task.get("operation"),
                trigger_type="ONCE",
                day=task.get("execute_day"),
                time=task.get("execute_time")
            )
        elif ui_trigger_type == "Daily":
            ok = create_scheduled_task(
                task_name=task.get("plan_name"),
                operation=task.get("operation"),
                trigger_type="daily",
                day=None,
                time=task.get("execute_time")
            )
        elif ui_trigger_type == "Weekly":
            ok = create_scheduled_task(
                task_name=task.get("plan_name"),
                operation=task.get("operation"),
                trigger_type="Weekly",
                day=task.get("Weekly"),
                time=task.get("execute_time")
            )
        elif ui_trigger_type == "Monthly":
            ok = create_scheduled_task(
                task_name=task.get("plan_name"),
                operation=task.get("operation"),
                trigger_type="Monthly",
                day=task.get("monthly"),
                time=task.get("execute_time")
            )
        return ok, None
    except Exception as e:
        return False, e