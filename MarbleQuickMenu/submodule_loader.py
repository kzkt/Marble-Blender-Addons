#Libraries
import json
import os
import bpy
import ast
#Submodules
from ReportHelper import popup_sender

class submodule_loader:
    def __init__(self, submodules_path):
        self.data = json_library().read_json()
        self.submodules = []
        self.invalid_modules = []

    def init_submodule(self,path):
        self._clear_previous()
        self._load_files(path)

    def _clear_previous(self):
        self.submodules.clear()
        self.invalid_modules.clear()

    def _load_files(self,path):
        if not os.path.exists(path):
            popup_sender(f"Path does not exist: {path}", "ERROR")
            return
        for file in os.listdir(path):
            if file.endswith(".py") and not file.startswith("__init__"):
                metainfo = self._get_metadata(file)

    def _get_metadata(self,file):
        tree = ast.parse(file)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "MQM_META":
                    if isinstance(node.value, ast.Dict):
                        keys = [ast.literal_eval(key) for key in node.value.keys]
                        values = [ast.literal_eval(value) for value in node.value.values]
                        return dict(zip(keys, values))

class json_library:
    def __init__(self):
        self.JSON_PATH = "submodule_datas.json"

    def read_json(self):
        with open(self.JSON_PATH, 'r') as file:
            data = json.load(file)    
        return data
    
    def write_json(self,data):
        with open(self.JSON_PATH, 'w') as file:
            json.dump(data, file, indent=4)