import os

import requests
from PyQt5.QtCore import QThread, pyqtSignal

from src.utils.log import Log
from src.utils.utils import Utils
from src.utils.const import AppPath, WebPath


def check_update():
    if not os.path.exists(AppPath.ConfigJson):
        Log.info(f"App Config File {AppPath.ConfigJson} doesn't exist")
        return False, {}
    Log.info(AppPath.ConfigJson)
    config_dict = Utils.read_dict_from_json(AppPath.ConfigJson)
    if not config_dict: return False
    local_ver = config_dict[0].get("version")
    Log.info(f"Current local version: {local_ver}")
    if not local_ver: 
        return False, {}
    try:
        try:
            response = requests.get(WebPath.AppConfigPathGitHub, timeout=1)
        except requests.exceptions.Timeout:
            response = requests.get(WebPath.AppConfigPathGitee, timeout=3)
        if not response: 
            return False, {}
        remote_info = response.json()
        if not remote_info: 
            return False, {}
        remote_ver = remote_info[0].get("version")
        Log.info(f"Current newest version: {remote_ver}")
        version = {"local": local_ver, "remote": remote_ver}

        if compare_version(remote_ver, local_ver) > 0:
            return True, version
        else:
            return False, version
    except Exception as e:
        Log.info(f"版本检测失败：{e}")
        # 返回空字典而不是None，以避免类型错误
        return False, {}

def compare_version(ver1, ver2):
    v1 = list(map(int, ver1.split(".")))
    v2 = list(map(int, ver2.split(".")))
    v2 = list(map(int, ver2.split(".")))
    max_len = max(len(v1), len(v2))
    v1 += [0] * (max_len - len(v1))
    v2 += [0] * (max_len - len(v2))
    return 1 if v1 > v2 else (-1 if v1 < v2 else 0)

class VersionCheckThread(QThread):
    check_finished = pyqtSignal(bool, dict)

    def __init__(self):
        super().__init__()

    def run(self):
        Log.info("后台执行版本检查...")
        ok, ver = check_update()
        self.check_finished.emit(ok, ver)