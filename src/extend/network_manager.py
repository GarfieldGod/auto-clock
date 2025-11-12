import subprocess

from src.utils.log import Log

def disconnect_network():
    """
    断开网络连接
    """
    try:
        # 使用netsh命令禁用所有网络适配器
        result = subprocess.run(["netsh", "interface", "show", "interface"], 
                                capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            return False, f"Failed to get network interfaces: {result.stderr}"
        
        # 解析输出获取网络接口名称
        lines = result.stdout.strip().split('\n')
        if len(lines) <= 2:  # 没有找到网络接口
            return False, "No network interfaces found"
        
        # 跳过前两行标题行，处理每个接口
        for i in range(2, len(lines)):
            if lines[i].strip():
                parts = lines[i].split()
                if len(parts) >= 4 and parts[0] == "Enabled":  # 只禁用已启用的接口
                    interface_name = " ".join(parts[3:])  # 接口名称可能包含空格
                    disable_result = subprocess.run([
                        "netsh", "interface", "set", "interface", 
                        f"name={interface_name}", "admin=disable"
                    ], capture_output=True, text=True, shell=True)
                    
                    if disable_result.returncode != 0:
                        Log.error(f"Failed to disable interface {interface_name}: {disable_result.stderr}")
                        return False, f"Failed to disable interface {interface_name}"
        
        Log.info("Network disconnected successfully")
        return True, None
    except Exception as e:
        Log.error(f"Error disconnecting network: {str(e)}")
        return False, str(e)

def connect_network():
    """
    连接网络
    """
    try:
        # 使用netsh命令启用所有网络适配器
        result = subprocess.run(["netsh", "interface", "show", "interface"], 
                                capture_output=True, text=True, shell=True)
        if result.returncode != 0:
            return False, f"Failed to get network interfaces: {result.stderr}"
        
        # 解析输出获取网络接口名称
        lines = result.stdout.strip().split('\n')
        if len(lines) <= 2:  # 没有找到网络接口
            return False, "No network interfaces found"
        
        # 跳过前两行标题行，处理每个接口
        for i in range(2, len(lines)):
            if lines[i].strip():
                parts = lines[i].split()
                if len(parts) >= 4 and parts[0] == "Disabled":  # 只启用已禁用的接口
                    interface_name = " ".join(parts[3:])  # 接口名称可能包含空格
                    enable_result = subprocess.run([
                        "netsh", "interface", "set", "interface", 
                        f"name={interface_name}", "admin=enable"
                    ], capture_output=True, text=True, shell=True)
                    
                    if enable_result.returncode != 0:
                        Log.error(f"Failed to enable interface {interface_name}: {enable_result.stderr}")
                        return False, f"Failed to enable interface {interface_name}"
        
        Log.info("Network connected successfully")
        return True, None
    except Exception as e:
        Log.error(f"Error connecting network: {str(e)}")
        return False, str(e)