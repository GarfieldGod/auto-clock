import os
import platform
import subprocess
import re
import pwd
import spwd
from datetime import datetime
from src.utils.log import Log
from src.utils.const import AppPath

def throw_exception(message):
    Log.error(message)
    raise Exception(message)

def backup_config_file(config_path, backup_dir):
    """
    备份配置文件
    :param config_path: 配置文件路径
    :param backup_dir: 备份目录
    :return: 备份文件路径
    """
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
    
    backup_file = os.path.join(backup_dir, f"linux_login_backup_{datetime.now().strftime('%Y-%m-%d_%H_%M_%S.%f')}.conf")
    
    try:
        # 如果配置文件存在，则备份
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
            
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(config_content)
            
            Log.info(f"配置文件备份成功：{backup_file}")
        return backup_file
    except Exception as e:
        throw_exception(f"备份配置文件失败：{str(e)}")

def detect_display_manager():
    """
    检测系统使用的显示管理器
    :return: 显示管理器名称（'lightdm', 'gdm', 'sddm' 或 'unknown'）
    """
    try:
        # 尝试检测正在运行的显示管理器进程
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        
        if 'lightdm' in result.stdout:
            return 'lightdm'
        elif 'gdm' in result.stdout or 'gdm3' in result.stdout:
            return 'gdm'
        elif 'sddm' in result.stdout:
            return 'sddm'
        else:
            # 如果没有检测到运行中的显示管理器，尝试检查已安装的包
            try:
                if os.path.exists('/etc/lightdm/lightdm.conf'):
                    return 'lightdm'
                elif os.path.exists('/etc/gdm3/gdm.conf') or os.path.exists('/etc/gdm/gdm.conf'):
                    return 'gdm'
                elif os.path.exists('/etc/sddm.conf'):
                    return 'sddm'
            except:
                pass
        return 'unknown'
    except Exception as e:
        Log.error(f"检测显示管理器失败：{str(e)}")
        return 'unknown'

def get_lightdm_config_path():
    """
    获取LightDM配置文件路径
    :return: 配置文件路径
    """
    config_paths = ['/etc/lightdm/lightdm.conf', '/etc/lightdm/lightdm.conf.d/50-autologin.conf']
    for path in config_paths:
        if os.path.exists(path):
            return path
    # 如果没有找到配置文件，使用默认路径
    return '/etc/lightdm/lightdm.conf.d/50-autologin.conf'

def get_gdm_config_path():
    """
    获取GDM配置文件路径
    :return: 配置文件路径
    """
    config_paths = ['/etc/gdm3/custom.conf', '/etc/gdm/custom.conf']
    for path in config_paths:
        if os.path.exists(path):
            return path
    # 如果没有找到配置文件，使用默认路径
    return '/etc/gdm3/custom.conf'

def get_sddm_config_path():
    """
    获取SDDM配置文件路径
    :return: 配置文件路径
    """
    config_paths = ['/etc/sddm.conf', '/etc/sddm.conf.d/autologin.conf']
    for path in config_paths:
        if os.path.exists(path):
            return path
    # 如果没有找到配置文件，使用默认路径
    return '/etc/sddm.conf.d/autologin.conf'

def set_lightdm_auto_login(username, enabled=True):
    """
    配置LightDM自动登录
    :param username: 用户名
    :param enabled: 是否启用自动登录
    :return: 备份文件路径
    """
    config_path = get_lightdm_config_path()
    backup_file = backup_config_file(config_path, AppPath.BackupRoot)
    
    # 确保配置目录存在
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
    
    # 读取现有配置（如果存在）
    config_content = ''
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
    
    # 确保[Seat:*]部分存在
    if not re.search(r'\[Seat:.*\]', config_content):
        config_content += '\n[Seat:*]\n'
    
    # 替换或添加自动登录配置
    if enabled:
        # 设置自动登录用户
        config_content = re.sub(r'autologin-user=.*', f'autologin-user={username}', config_content)
        if 'autologin-user=' not in config_content:
            config_content = re.sub(r'\[Seat:.*\]', f'[Seat:*]\nautologin-user={username}', config_content)
        
        # 启用自动登录
        config_content = re.sub(r'autologin-user-timeout=.*', 'autologin-user-timeout=0', config_content)
        if 'autologin-user-timeout=' not in config_content:
            config_content = re.sub(r'\[Seat:.*\]', '[Seat:*]\nautologin-user-timeout=0', config_content)
        
        # 禁用访客登录
        config_content = re.sub(r'autologin-guest=.*', 'autologin-guest=false', config_content)
        if 'autologin-guest=' not in config_content:
            config_content = re.sub(r'\[Seat:.*\]', '[Seat:*]\nautologin-guest=false', config_content)
    else:
        # 禁用自动登录
        config_content = re.sub(r'autologin-user=.*\n?', '', config_content)
        config_content = re.sub(r'autologin-user-timeout=.*\n?', '', config_content)
    
    try:
        # 写入配置文件（需要root权限）
        cmd = f'echo "{config_content}" | sudo tee {config_path}'
        subprocess.run(cmd, shell=True, check=True)
        Log.info("LightDM自动登录配置已更新")
        return backup_file
    except Exception as e:
        # 恢复备份
        if os.path.exists(backup_file):
            try:
                cmd = f'sudo cp {backup_file} {config_path}'
                subprocess.run(cmd, shell=True)
                Log.info("已恢复配置文件备份")
            except:
                pass
        throw_exception(f"配置LightDM自动登录失败：{str(e)}")

def set_gdm_auto_login(username, enabled=True):
    """
    配置GDM自动登录
    :param username: 用户名
    :param enabled: 是否启用自动登录
    :return: 备份文件路径
    """
    config_path = get_gdm_config_path()
    backup_file = backup_config_file(config_path, AppPath.BackupRoot)
    
    # 确保配置目录存在
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
    
    # 读取现有配置（如果存在）
    config_content = ''
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
    
    # 确保[daemon]部分存在
    if not re.search(r'\[daemon\]', config_content):
        config_content = '[daemon]\n' + config_content
    
    # 确保[security]部分存在
    if not re.search(r'\[security\]', config_content):
        config_content += '\n[security]\n'
    
    # 替换或添加自动登录配置
    if enabled:
        # 启用自动登录
        config_content = re.sub(r'#?AutomaticLoginEnable=.*', 'AutomaticLoginEnable=True', config_content)
        if 'AutomaticLoginEnable=' not in config_content:
            config_content = re.sub(r'\[daemon\]', '[daemon]\nAutomaticLoginEnable=True', config_content)
        
        # 设置自动登录用户
        config_content = re.sub(r'#?AutomaticLogin=.*', f'AutomaticLogin={username}', config_content)
        if 'AutomaticLogin=' not in config_content:
            config_content = re.sub(r'\[daemon\]', f'[daemon]\nAutomaticLogin={username}', config_content)
    else:
        # 禁用自动登录
        config_content = re.sub(r'AutomaticLoginEnable=.*', '#AutomaticLoginEnable=False', config_content)
        config_content = re.sub(r'AutomaticLogin=.*', '', config_content)
    
    try:
        # 写入配置文件（需要root权限）
        cmd = f'echo "{config_content}" | sudo tee {config_path}'
        subprocess.run(cmd, shell=True, check=True)
        Log.info("GDM自动登录配置已更新")
        return backup_file
    except Exception as e:
        # 恢复备份
        if os.path.exists(backup_file):
            try:
                cmd = f'sudo cp {backup_file} {config_path}'
                subprocess.run(cmd, shell=True)
                Log.info("已恢复配置文件备份")
            except:
                pass
        throw_exception(f"配置GDM自动登录失败：{str(e)}")

def set_sddm_auto_login(username, enabled=True):
    """
    配置SDDM自动登录
    :param username: 用户名
    :param enabled: 是否启用自动登录
    :return: 备份文件路径
    """
    config_path = get_sddm_config_path()
    backup_file = backup_config_file(config_path, AppPath.BackupRoot)
    
    # 确保配置目录存在
    config_dir = os.path.dirname(config_path)
    if not os.path.exists(config_dir):
        os.makedirs(config_dir, exist_ok=True)
    
    # 读取现有配置（如果存在）
    config_content = ''
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            config_content = f.read()
    
    # 确保[Autologin]部分存在
    if not re.search(r'\[Autologin\]', config_content):
        config_content += '\n[Autologin]\n'
    
    # 替换或添加自动登录配置
    if enabled:
        # 启用自动登录
        config_content = re.sub(r'#?Session=.*', 'Session=plasma.desktop', config_content)
        if 'Session=' not in config_content:
            config_content = re.sub(r'\[Autologin\]', '[Autologin]\nSession=plasma.desktop', config_content)
        
        # 设置自动登录用户
        config_content = re.sub(r'#?User=.*', f'User={username}', config_content)
        if 'User=' not in config_content:
            config_content = re.sub(r'\[Autologin\]', f'[Autologin]\nUser={username}', config_content)
        
        # 启用自动登录
        config_content = re.sub(r'#?Relogin=.*', 'Relogin=false', config_content)
        if 'Relogin=' not in config_content:
            config_content = re.sub(r'\[Autologin\]', '[Autologin]\nRelogin=false', config_content)
    else:
        # 禁用自动登录
        config_content = re.sub(r'User=.*\n?', '', config_content)
        config_content = re.sub(r'Relogin=.*\n?', '', config_content)
    
    try:
        # 写入配置文件（需要root权限）
        cmd = f'echo "{config_content}" | sudo tee {config_path}'
        subprocess.run(cmd, shell=True, check=True)
        Log.info("SDDM自动登录配置已更新")
        return backup_file
    except Exception as e:
        # 恢复备份
        if os.path.exists(backup_file):
            try:
                cmd = f'sudo cp {backup_file} {config_path}'
                subprocess.run(cmd, shell=True)
                Log.info("已恢复配置文件备份")
            except:
                pass
        throw_exception(f"配置SDDM自动登录失败：{str(e)}")

def set_auto_login(username=None, password=None, enabled=False):
    """
    配置Linux自动登录
    :param username: Linux用户名
    :param password: Linux登录密码（在Linux中通常不需要密码）
    :param enabled: 开启或关闭自动登录
    :return: 备份文件路径
    """
    if not platform.system() == 'Linux':
        throw_exception("此功能仅适用于Linux系统")
    
    dm_type = detect_display_manager()
    
    if dm_type == 'lightdm':
        return set_lightdm_auto_login(username, enabled)
    elif dm_type == 'gdm':
        return set_gdm_auto_login(username, enabled)
    elif dm_type == 'sddm':
        return set_sddm_auto_login(username, enabled)
    else:
        throw_exception(f"不支持的显示管理器：{dm_type}。请手动配置自动登录。")

def auto_linux_login_on(user_name, user_password=None):
    """
    开启Linux自动登录
    :param user_name: Linux用户名
    :param user_password: Linux登录密码（可选，大多数情况下不需要）
    :return: 备份文件路径
    """
    if not user_name:
        raise Exception("错误：用户名不能为空。")
    
    return set_auto_login(user_name, user_password, enabled=True)

def auto_linux_login_off():
    """
    关闭Linux自动登录
    :return: 备份文件路径
    """
    return set_auto_login(None, None, enabled=False)

def check_auto_login_status():
    """
    检查当前Linux自动登录状态
    :return: (bool, str) - (是否启用, 状态描述)
    """
    if not platform.system() == 'Linux':
        return None, "此功能仅适用于Linux系统"
    
    dm_type = detect_display_manager()
    
    try:
        if dm_type == 'lightdm':
            config_path = get_lightdm_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    autologin_enabled = re.search(r'autologin-user=([^\n]+)', content)
                    if autologin_enabled:
                        username = autologin_enabled.group(1)
                        status = f"自动登录已启用 (用户: {username}, 显示管理器: LightDM)"
                        return True, status
        elif dm_type == 'gdm':
            config_path = get_gdm_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    enabled = re.search(r'AutomaticLoginEnable=True', content)
                    username_match = re.search(r'AutomaticLogin=([^\n]+)', content)
                    if enabled and username_match:
                        username = username_match.group(1)
                        status = f"自动登录已启用 (用户: {username}, 显示管理器: GDM)"
                        return True, status
        elif dm_type == 'sddm':
            config_path = get_sddm_config_path()
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    username_match = re.search(r'User=([^\n]+)', content)
                    if username_match:
                        username = username_match.group(1)
                        status = f"自动登录已启用 (用户: {username}, 显示管理器: SDDM)"
                        return True, status
        
        if dm_type == 'unknown':
            return False, "无法确定显示管理器"
        else:
            return False, f"自动登录未启用 (显示管理器: {dm_type.capitalize()})"
    except Exception as e:
        Log.error(f"检查自动登录状态时出错：{str(e)}")
        return None, "无法检查状态：未知错误"


def validate_linux_credentials(username, password=None):
    """
    验证Linux账号密码的有效性
    :param username: Linux用户名
    :param password: Linux密码（可选，如果为None则只验证用户存在）
    :return: (bool, str) - (是否有效, 状态描述)
    """
    if not platform.system() == 'Linux':
        return False, "此功能仅适用于Linux系统"
    
    if not username:
        return False, "用户名不能为空"
    
    try:
        # 检查用户是否存在
        try:
            pwd.getpwnam(username)
            Log.info(f"用户 {username} 存在")
        except KeyError:
            return False, f"用户 {username} 不存在"
        
        # 如果没有提供密码，只验证用户存在性
        if not password:
            return True, f"用户 {username} 存在（密码未验证）"
        
        # 验证密码（需要root权限或当前用户权限）
        try:
            # 使用su命令验证密码
            # 注意：这个方法可能需要root权限，或者只能验证当前用户的密码
            result = subprocess.run(
                ['su', '-c', 'true', username],
                input=password,
                text=True,
                capture_output=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return True, f"用户 {username} 密码验证成功"
            else:
                return False, f"用户 {username} 密码错误"
                
        except subprocess.TimeoutExpired:
            return False, "密码验证超时"
        except Exception as e:
            Log.warning(f"密码验证失败，可能是权限问题：{str(e)}")
            # 如果密码验证失败，返回部分成功状态
            return True, f"用户 {username} 存在（密码无法验证，可能需要更高权限）"
            
    except Exception as e:
        Log.error(f"验证Linux账号时出错：{str(e)}")
        return False, f"验证失败：{str(e)}"


def get_linux_credentials_status():
    """
    获取当前存储的Linux账号状态
    :return: (bool, str) - (是否有效, 状态描述)
    """
    try:
        # 这里可以从配置文件读取存储的账号信息
        # 暂时返回未配置状态
        return False, "未配置Linux账号信息"
    except Exception as e:
        Log.error(f"获取Linux账号状态时出错：{str(e)}")
        return None, "无法获取账号状态"