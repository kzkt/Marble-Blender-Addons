#Libraries
import json
import os
import bpy
import ast
#Submodules
from ReportHelper import popup_sender

JSON_DB_PATH = os.path.join(os.path.dirname(__file__), "submodule_datas.json")

class submodule_loader:
    def __init__(self,submodules_path):
        self.datas = json_library().read_json()
        self.submodules_path = submodules_path
        self.submodules = []
        self.invalid_modules = []
         
    #MAIN FUNCTION
    def init_submodule(self):
        self._clear_previous()
        scripts = self._load_submodule_files(self.submodules_path)
        self._clear_unavailable_submodules(scripts)

    def _clear_previous(self):
        self.submodules.clear()
        self.invalid_modules.clear()

    '''
    ---------------------------------------------------------------------------------------------------
    LOAD ALL SUBMODULE FILES AND UPDATE DATABASE JSON
    ---------------------------------------------------------------------------------------------------
    '''
    def _load_submodule_files(self,path):
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            popup_sender(f"Path does not exist: {path}", "ERROR")
            return
        path_content = os.listdir(path)
        for file in path_content:
            print(f"Current File Name: {file}")
            if os.path.isdir( os.path.join(path,file) ) == False:
                metainfo = self._get_metadata(file)
                if metainfo != None:
                    if self._check_if_in_database(metainfo) == False:
                        metainfo.update({"enabled":True})
                        self.datas['submodules'].append(metainfo)
                        json_library().write_json(self.datas)
                else:
                    print("Non Supported Script")
            else:
                path_content.remove(file)
        json_library().write_json(self.datas)
        return path_content

    def _get_metadata(self,file):
        file_path = os.path.join(self.submodules_path, file)
        with open(file_path, 'r', encoding='utf-8') as f:
            tree = ast.parse(f.read(),filename=file_path)
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    if len(node.targets) == 1 and isinstance(node.targets[0], ast.Name) and node.targets[0].id == "MQM_META":
                        if isinstance(node.value, ast.Dict):
                            keys = [ast.literal_eval(key) for key in node.value.keys]
                            values = [ast.literal_eval(value) for value in node.value.values]
                            return dict(zip(keys, values))

    def _check_if_in_database(self,metainfo):
        if len(self.datas["submodules"]) == 0:
            return False
        for submodule in self.datas["submodules"]:
            if submodule["name"] == metainfo["name"]:
                return True
            else:
                result = False
        return result

    '''
    ---------------------------------------------------------------------------------------------------
    COMPARE DATABASE JSON AND SUBMODULES FOLDER, DELETE DATAS THAT NO LONGER EXIST IN SUBMODULES FOLDER
    ---------------------------------------------------------------------------------------------------
    '''

    def _clear_unavailable_submodules(self,scripts_list):
        json_data = json_library().read_json()
        scripts_name = [os.path.splitext(i)[0] for i in scripts_list]

        data_to_del = []

        print(f'scripts_name : {scripts_name}')

        for submodule in json_data["submodules"]:
            if submodule["name"] not in scripts_name:
                print(f"Submodule {submodule['name']} not found in scripts folder, removing from database..")
                data_to_del.append(submodule)

        for data in data_to_del:
            json_data["submodules"].remove(data)

        json_library().write_json(json_data)

class json_library:
    def __init__(self):
        self.JSON_PATH = JSON_DB_PATH

    def read_json(self):
        self.init_json_file
        with open(self.JSON_PATH, 'r') as file:
            data = json.load(file)    
        return data
    
    def write_json(self,data):
        with open(self.JSON_PATH, 'w') as file:
            json.dump(data, file, indent=4)

    def init_json_file(self):
        if not os.path.exists(self.JSON_PATH):
            default_data = {"submodules": []}
            with open(self.JSON_PATH, 'w') as f:
                json.dump(default_data, f, indent=4)
