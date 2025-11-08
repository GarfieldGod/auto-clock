import subprocess
from src.utils.log import Log

def run_windows_sleep():
    cmd = ["shutdown.exe", "/h", "/f"]
    try:
        subprocess.run(cmd, check=True, shell=True, encoding="gbk")
        Log.info("已触发睡眠...")
        return True, None
    except subprocess.CalledProcessError:
        Log.error("睡眠失败: 请以管理员身份运行脚本")
        return False, "睡眠失败: 请以管理员身份运行脚本"

def run_windows_shutdown(delay_seconds=0):
    cmd = ["shutdown.exe", "/s", "/t", str(delay_seconds)]
    try:
        subprocess.run(cmd, check=True, shell=True)
        message = f"关机命令已提交，将在 {delay_seconds} 秒后关机"
        Log.info(message)
        return True, None
    except subprocess.CalledProcessError:
        message = "关机失败: 请以管理员身份运行脚本"
        Log.info(message)
        return False, message