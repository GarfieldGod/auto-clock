import os
import subprocess
import time

from src.utils.log import Log


def run_linux_shutdown(delay=30):
    """
    在Linux系统上执行关机操作
    
    Args:
        delay: 延迟关机的秒数
    
    Returns:
        tuple: (success, error_message)
    """
    try:
        Log.info(f"Linux系统执行关机操作，延迟{delay}秒")
        # 使用subprocess执行关机命令，需要sudo权限
        # 注意：在实际运行时，应用程序需要以管理员权限运行
        command = ["sudo", "shutdown", "-h", f"+{delay // 60}"]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            Log.info(f"关机命令已成功执行，系统将在{delay}秒后关机")
            return True, None
        else:
            error_msg = f"执行关机命令失败: {result.stderr}"
            Log.error(error_msg)
            return False, error_msg
    except Exception as e:
        error_msg = f"关机操作异常: {str(e)}"
        Log.error(error_msg)
        return False, error_msg


def run_linux_sleep(delay=30):
    """
    在Linux系统上执行睡眠/挂起操作
    
    Args:
        delay: 延迟睡眠的秒数
    
    Returns:
        tuple: (success, error_message)
    """
    try:
        Log.info(f"Linux系统执行睡眠操作，延迟{delay}秒")
        
        # 先等待指定的延迟时间
        time.sleep(delay)
        
        # 尝试多种方式执行睡眠操作
        # 1. 使用systemctl suspend
        try:
            command = ["sudo", "systemctl", "suspend"]
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                Log.info("睡眠命令已成功执行，系统将进入睡眠状态")
                return True, None
        except:
            pass
        
        # 2. 如果systemctl方式失败，尝试使用pm-suspend
        try:
            command = ["sudo", "pm-suspend"]
            result = subprocess.run(command, capture_output=True, text=True)
            
            if result.returncode == 0:
                Log.info("pm-suspend命令已成功执行，系统将进入睡眠状态")
                return True, None
        except:
            pass
        
        error_msg = "无法执行睡眠操作，可能需要安装相关软件包或配置权限"
        Log.error(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"睡眠操作异常: {str(e)}"
        Log.error(error_msg)
        return False, error_msg


def cancel_linux_shutdown():
    """
    取消Linux系统的关机计划
    
    Returns:
        tuple: (success, error_message)
    """
    try:
        Log.info("取消Linux系统的关机计划")
        command = ["sudo", "shutdown", "-c"]
        result = subprocess.run(command, capture_output=True, text=True)
        
        if result.returncode == 0:
            Log.info("关机计划已成功取消")
            return True, None
        else:
            error_msg = f"取消关机计划失败: {result.stderr}"
            Log.error(error_msg)
            return False, error_msg
    except Exception as e:
        error_msg = f"取消关机计划异常: {str(e)}"
        Log.error(error_msg)
        return False, error_msg


def is_linux_command_available(command):
    """
    检查Linux命令是否可用
    
    Args:
        command: 要检查的命令
    
    Returns:
        bool: 命令是否可用
    """
    try:
        subprocess.run(["which", command], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False