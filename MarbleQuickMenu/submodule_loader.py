#Libraries
import json
import os
import bpy
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