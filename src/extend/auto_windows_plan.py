import ctypes
import os
import sys
import subprocess
from pathlib import Path

def create_scheduled_task(
    task_name: str,
    trigger_type: str,  # 触发类型：daily=每天，onlogon=登录后，weekly=每周
    day: str = None,
    time: str = None,          # 仅 trigger_type=daily/weekly 有效，格式 HH:MM
) -> bool:
    """
    创建 Windows 计划任务，自动定时运行 exe

    :param exe_path: exe 文件的绝对路径
    :param task_name: 计划任务名称（唯一）
    :param trigger_type: 触发类型：daily(每天)/onlogon(登录后)/weekly(每周)
    :param day: 执行日期 (仅 once 需指定)
    :param time: 执行时间（仅 daily/weekly 需指定，格式 HH:MM）
    :return: 创建成功返回 True，失败返回 False
    """
    arguments: str = "--auto"
    run_as_admin: bool = True

    exe_path = get_current_exe_path()
    print(exe_path)
    exe_path = Path(exe_path).absolute()
    if not exe_path.exists():
        print(f"错误：exe 文件不存在 → {exe_path}")
        return False

    cmd = [
        "schtasks", "/create",
        "/tn", task_name,
        "/tr", f'"{exe_path}" {arguments}'.strip(),
        "/sc", trigger_type,
        "/f" # 强制覆盖同名任务（避免重复创建报错）
    ]

    if trigger_type == "ONCE" and day is not None and time is not None:
        cmd.extend(["/d", day])
        if not time or len(time.split(":")) != 2:
            print(f"错误：时间格式无效 → {time}（正确格式 HH:MM，如 08:30）")
            return False
        cmd.extend(["/st", time])

    if trigger_type in ["daily", "weekly"]:
        if not time or len(time.split(":")) != 2:
            print(f"错误：时间格式无效 → {time}（正确格式 HH:MM，如 08:30）")
            return False
        cmd.extend(["/st", time])

    if run_as_admin:
        cmd.extend(["/rl", "highest"])  # /rl highest = 以最高权限运行

    try:
        result = subprocess.run(
            cmd,
            shell=True,
            encoding="utf-8",
            errors="ignore",
            capture_output=True,
            timeout=30
        )

        if result.stdout:
            print(f"命令输出：{result.stdout.strip()}")
        if result.stderr:
            print(f"命令警告：{result.stderr.strip()}")

        check_cmd = ["schtasks", "/query", "/tn", task_name, "/fo", "list"]
        check_result = subprocess.run(
            check_cmd, shell=True, encoding="utf-8", capture_output=True
        )

        if "任务名称" in check_result.stdout:
            print(f"\n计划任务创建成功！")
            print(f"任务名：{task_name}")
            print(f"触发类型：{trigger_type}")
            if trigger_type in ["daily", "weekly"]:
                print(f"执行时间：{time}")
            print(f"执行命令：{exe_path} {arguments}")
            print(f"管理员权限：{'是' if run_as_admin else '否'}")
            return True
        else:
            print(f"\n计划任务创建失败！")
            return False

    except subprocess.TimeoutExpired:
        print(f"错误：创建任务超时")
        return False
    except Exception as e:
        print(f"错误：创建任务异常 → {str(e)}")
        return False

def delete_scheduled_task(task_name: str) -> bool:
    """删除计划任务（如需重新创建时使用）"""
    try:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", task_name, "/f"],
            shell=True, encoding="utf-8", capture_output=True
        )
        if "成功" in result.stdout or result.returncode == 0:
            print(f"已删除计划任务：{task_name}")
            return True
        else:
            print(f"删除任务失败 → {result.stderr.strip()}")
            return False
    except Exception as e:
        print(f"删除任务异常 → {str(e)}")
        return False

def get_task_day(target_date):
    try:
        year, month, day = target_date.split("-")
        windows_date = f"{month}/{day}/{year}"
        return windows_date
    except Exception as e:
        print(f"日期格式错误！请输入 'YYYY-MM-DD'，错误：{e}")
        return None

def get_current_exe_path():
    current_dir = None
    if getattr(sys, 'frozen', False):
        exe_path = sys.executable
        current_dir = os.path.dirname(exe_path)
    return current_dir

if __name__ == "__main__":
    # -------------------------- 请修改以下配置 --------------------------
    TASK_ID = 0
    TASK_NAME = f"AutoClockTask_{TASK_ID}"
    EXECUTE_DAY = get_task_day("2025-11-4")
    EXECUTE_TIME = "18:30"
    # 触发类型：once=一次, daily=每天, onlogon=登录后
    TRIGGER_TYPE = "ONCE"
    # ----------------------------------------------------------------------

    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("请以管理员身份运行！")
        sys.exit(1)

    # （可选）先删除旧任务（避免冲突）
    # delete_scheduled_task(TASK_NAME)

    create_scheduled_task(
        task_name=TASK_NAME,
        trigger_type=TRIGGER_TYPE,
        day=EXECUTE_DAY,
        time=EXECUTE_TIME
    )