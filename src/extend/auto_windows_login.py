import os
import winreg

from datetime import datetime
from platformdirs import user_data_dir
from src.utils.log import Log

DataRoot = user_data_dir("backup", "auto-clock")

def throw_exception(message):
    Log.error(message)
    raise Exception(message)

def backup_registry_key(key_path, backup_file):
    try:
        result = os.system(f'reg export "{key_path}" "{backup_file}" /y')
        if result == 0:
            Log.info(f"注册表备份成功：{backup_file}")
            return True
        else:
            throw_exception(f"Registry backup failed.")
    except Exception as e:
        throw_exception(f"Backup exception：{str(e)}")

def set_auto_login(username=None, password=None, enabled=False):
    """
    配置 Windows 自动登录（修改注册表）
    :param username: Windows 用户名（本地账户/微软账户前缀）
    :param password: Windows 登录密码
    :param enabled: 开启或关闭自动登录
    """
    reg_path = r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\Winlogon"
    backup_file = os.path.join(DataRoot, f"windows_logon_backup_{datetime.now().strftime("%Y-%m-%d_%H_%M_%S.%f")}.reg")

    if not backup_registry_key(f"HKEY_LOCAL_MACHINE\\{reg_path}", backup_file):
        throw_exception("Backup failed, canceling automatic login configuration.")

    try:
        with winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                reg_path,
                0,
                winreg.KEY_WRITE | winreg.KEY_WOW64_64KEY
        ) as key:

            if username is not None:
                winreg.SetValueEx(key, "DefaultUserName", 0, winreg.REG_SZ, username)
                Log.info(f"设置 DefaultUserName = {username}")

            if password is not None:
                winreg.SetValueEx(key, "DefaultPassword", 0, winreg.REG_SZ, password)
                Log.info(f"设置 DefaultPassword = {password}")

            winreg.SetValueEx(key, "AutoAdminLogon", 0, winreg.REG_SZ, "1" if enabled else "0")
            Log.info(f"设置 AutoAdminLogon = {"1" if enabled else "0"}")

        Log.info("\n自动登录配置完成！重启电脑后生效")
        Log.info(f"注册表备份文件已保存到：{backup_file}（若需恢复，双击该文件导入即可）")
        return backup_file

    except PermissionError:
        throw_exception("\nInsufficient permissions! Please run as an administrator.")
    except Exception as e:
        # 恢复注册表（失败时回滚）
        os.system(f'reg import "{backup_file}"')
        Log.error(f"已自动恢复注册表到修改前状态")
        throw_exception(f"\nConfiguration failed: {str(e)}")

def auto_windows_login_on(user_name, user_password):
    if not user_name:
        raise Exception("Error: Username cannot be empty.")

    return set_auto_login(user_name, user_password, enabled=True)

def auto_windows_login_off():
    return set_auto_login(None, None, enabled=False)