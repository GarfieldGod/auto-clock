import os
os.system("chcp 65001 >nul")

def create_windows_task(script_path, time, task_name):
    """
    Windows：创建计划任务，每天指定时间执行 Python 脚本
    :param script_path: 脚本绝对路径（如 "D:\\script.py"）
    :param time: 执行时间（如 "08:30"）
    :param task_name: 任务名称
    """
    # Python 解释器路径（需替换为你的 python.exe 路径，可通过 where python 查找）
    python_path = r"C:\Python39\python.exe"
    # schtasks 命令：/create 创建任务，/tn 任务名，/tr 执行命令，/sc 触发频率（daily 每天），/st 执行时间
    command = (
        f'schtasks /create /tn "{task_name}" '
        f'/tr "{python_path} "{script_path}"" '  # 注意脚本路径的引号嵌套
        f'/sc daily /st {time} /rl highest'  # /rl highest 以管理员权限运行
    )
    try:
        os.system(command)
        print(f"计划任务创建成功！任务名：{task_name}，每天 {time} 执行")
    except Exception as e:
        print(f"创建任务失败：{e}")

# 调用：每天 8:30 执行 D:\auto_clock.py
create_windows_task(script_path=r"D:\auto_clock.py", time="08:30", task_name="AutoRunScript")

# 查看任务
os.system('schtasks /query /tn "AutoRunScript"')
# 删除任务
os.system('schtasks /delete /tn "AutoRunScript" /f')  # /f 强制删除