import json
import os
import sys
from pathlib import Path

from platformdirs import user_data_dir

from src.utils.const import Key
from src.utils.log import Log

DataRoot = user_data_dir("data", "auto-clock")
data_json = f"{DataRoot}\\data.json"
tasks_json = f"{DataRoot}\\tasks.json"

class Utils:
    @staticmethod
    def get_nums_array(start, end, bit=2):
        num_array = []
        for i in range(start, end + 1):
            num_str = str(i)
            if len(num_str) < bit:
                num_str = "0" * (bit - len(num_str)) + num_str
            num_array.append(num_str)
        return num_array

    @staticmethod
    def truncate_text(text, max_length=15):
        if len(text) > max_length:
            return text[:max_length] + "..."
        return text

    @staticmethod
    def write_dict_to_file(file_path, data):
        if not os.path.exists(Path(file_path).parent):
            os.makedirs(Path(file_path).parent)

        with open(f"{file_path}", "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @staticmethod
    def read_dict_from_json(file_path):
        if not os.path.exists(file_path):
            return None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                dict_list = json.load(f)
                return dict_list
        except Exception as e:
            Log.info(f"Load {file_path} failed. error: {e}")
            return None

    @staticmethod
    def get_ico_path():
        if hasattr(sys, '_MEIPASS'):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.abspath(".")
        return os.path.join(base_path, "icon.ico")

    @staticmethod
    def find_task(task_id):
        tasks_data = Utils.read_dict_from_json(tasks_json)
        if not tasks_data:
            return None
        if isinstance(tasks_data, list):
            for task in tasks_data:
                if str(task.get(Key.TaskID)) == str(task_id):
                    return task
        elif isinstance(tasks_data, dict):
            if str(tasks_data.get(Key.TaskID)) == str(task_id):
                return tasks_data
        return None
