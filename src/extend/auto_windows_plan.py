import ctypes
import os
import sys
import subprocess
from datetime import datetime
from pathlib import Path

from src.utils.log import Log
from src.utils.utils import Utils, tasks_json


def get_command_prefix():
    if hasattr(sys, '_MEIPASS'):
        exe_path = get_current_exe_path()
        exe_path = Path(exe_path).absolute()
        Log.info(exe_path)
        if not exe_path.exists():
            message = f"Error: exe file do not exist: {exe_path}"
            Log.error(message)
            raise Exception(message)
        return str(exe_path)
    else:
        return f"{Path(__file__).parent.parent / "entry.py"}"

def get_operation(operation_type):
    prefix = get_command_prefix()

    suffix = " --"
    if operation_type == "Auto Clock":
        suffix += "auto"
    elif operation_type == "Shut Down Windows":
        suffix += "shutdown"
    elif operation_type == "Windows Sleep":
        suffix += "sleep"
    else:
        message = "Unknow operation type!"
        Log.error(message)
        raise Exception(message)

    return f"{prefix}{suffix}"

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
    operation = get_operation(operation)

    cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", f'"{operation}"'.strip(),
        "/sc", trigger_type,
        "/f", # 强制覆盖同名任务
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
            Log.info(f"执行命令：{operation}")
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

# def add_trigger(task_name, date, time):
#     add_trigger_cmd = [
#         "schtasks", "/change",
#         "/tn", task_name,
#         "/sc", "once",
#         "/sd", date,
#         "/st", time,
#         "/f"
#     ]
#
#     result = subprocess.run(add_trigger_cmd, capture_output=True, text=True, encoding="gbk")
#     if result.returncode == 0:
#         Log.info(f"成功追加触发器：{date} {time}")
#         return True
#     else:
#         Log.error(f"追加触发器失败（{date} {time}）：{result.stderr}")
#         raise Exception(f"Append trigger failed:({date} {time}):{result.stderr}")

def delete_invalid_plan(plan_dict):
    if not isinstance(plan_dict, dict): return False
    if plan_dict.get("trigger_type") == "Once" and plan_dict.get("execute_day") is not None:
        execute_day = plan_dict.get("execute_day")
        execute_date = datetime.strptime(execute_day, "%Y-%m-%d").date()
        if execute_date < datetime.today().date():
            plan_name = plan_dict.get("plan_name")
            Log.info(f"Plan: {plan_name} has been invalid, it will be deleted.")
            delete_scheduled_task(plan_name)
            return True

    elif plan_dict.get("trigger_type") == "Multiple":
        deleted_day = []
        for execute_day in plan_dict.get("plan_name"):
            execute_date = datetime.strptime(execute_day, "%Y-%m-%d").date()
            if execute_date < datetime.today().date():
                deleted_day.append(execute_day)

        for execute_day in deleted_day:
            plan_name = plan_dict.get("plan_name")[execute_day]
            Log.info(f"Plan: {plan_name} has been invalid, it will be deleted.")
            delete_scheduled_task(plan_name)
            plan_dict.get("plan_name").pop(execute_day)

        if len(plan_dict.get("plan_name")) == 0:
            return True
        else:
            return False

    return False

def clear_windows_plan():
    dict_list = Utils.read_dict_from_json(tasks_json)
    if dict_list is None: return

    if isinstance(dict_list, list):
        delete_dict = []
        for plan_dict in dict_list:
            deleted = delete_invalid_plan(plan_dict)
            if deleted:
                delete_dict.append(plan_dict)
        for deleted in delete_dict:
            dict_list.remove(deleted)
    elif isinstance(dict_list, dict):
        deleted = delete_invalid_plan(dict_list)
        if deleted:
            Utils.write_dict_to_file(tasks_json, [])
            return

    Utils.write_dict_to_file(tasks_json, dict_list)

def delete_scheduled_task(task_name: str):
    """删除计划任务"""
    try:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", task_name, "/f"],
            shell=True, encoding="gbk", capture_output=True
        )
        if "成功" in result.stdout or result.returncode == 0:
            Log.info(f"已删除计划任务：{task_name}")
            return True, None
        else:
            message = f"Delete task failed: {result.stderr.strip()}"
            Log.info(message)
            return False, message
    except Exception as e:
        message = f"Delete task error: {str(e)}"
        Log.error(message)
        return False, message

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
        # if ui_trigger_type == "Multipl":
        #     execute_days = task.get("execute_days")
        #     if not execute_days: raise Exception("execute_days is empty")
        #     first_ok = create_scheduled_task(
        #         task_name=task.get("plan_name"),
        #         operation=task.get("operation"),
        #         trigger_type="ONCE",
        #         day=execute_days[0],
        #         time=task.get("execute_time")
        #     )
        #     if not first_ok:
        #         delete_scheduled_task(task.get("plan_name"))
        #     else:
        #         for i in range(1, len(execute_days)):
        #             ret = add_trigger(task_name=task.get("plan_name"),date=execute_days[i],time=task.get("execute_time"))
        #             if not ret: raise Exception("Add trigger failed")
        #         ok = True
        elif ui_trigger_type == "Daily":
            ok = create_scheduled_task(
                task_name=task.get("plan_name"),
                operation=task.get("operation"),
                trigger_type="Daily",
                day=None,
                time=task.get("execute_time")
            )
        elif ui_trigger_type == "Weekly":
            ok = create_scheduled_task(
                task_name=task.get("plan_name"),
                operation=task.get("operation"),
                trigger_type="Weekly",
                day=task.get("weekly"),
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
        delete_scheduled_task(task.get("plan_name"))
        return False, e