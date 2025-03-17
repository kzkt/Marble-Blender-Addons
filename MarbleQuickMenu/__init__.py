#MarbleQuickMenu-Core

#Libraries
import bpy
import os
import importlib
import ast
import json

## bpy Alias
###Types
AddonPreferences = bpy.types.AddonPreferences
Operator = bpy.types.Operator
PropertyGroup = bpy.types.PropertyGroup
UIList = bpy.types.UIList
Menu = bpy.types.Menu
###Props
StringProperty = bpy.props.StringProperty

CollectionProperty = bpy.props.CollectionProperty
BoolProperty = bpy.props.BoolProperty

## GLOBAL VARS
_SUBMODULES : list = []
_JSONDATA : dict = []
'''
{submodules:[]}
'''

def popup_sender(message,type="INFO"):

    def draw(self,context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw,title=type,icon="INFO")
    return

'''
---------------------------------------------------------------------------------------------------
SUBMODULE LOADER AND JSON FILE LIBRARY
---------------------------------------------------------------------------------------------------
'''
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
            # file.flush()
            # os.fsync(file.fileno())

    def init_json_file(self):
        if not os.path.exists(self.JSON_PATH):
            default_data = {"submodules": []}
            with open(self.JSON_PATH, 'w') as file:
                json.dump(default_data, file, indent=4)
                file.flush()
                os.fsync(file.fileno())



'''
---------------------------------------------------------------------------------------------------
ADDON PREFERENCES OBJECTS
---------------------------------------------------------------------------------------------------
'''

#BUTTON OPEN SCRIPT FOLDER IN EXPLORER
class OpenScriptsFolderInExplorer(Operator):
    bl_idname = "mqm.open_scripts_folder"
    bl_label = "Open in Explorer"
    bl_options= {"INTERNAL"}

    def execute(self, context):
        dir_ = bpy.context.preferences.addons[__name__].preferences.scripts_path

        # Open the file explorer based on the operating system
        if os.path.exists(dir_):
            if os.name == 'nt':  # Windows
                os.startfile(dir_)
            elif os.name == 'posix':  # macOS or Linux
                if os.uname().sysname == 'Darwin':  # macOS
                    subprocess.run(['open', dir_])
                else:  # Linux
                    subprocess.run(['xdg-open', dir_])
            self.report({'INFO'}, f"Opened directory: {dir_}")
        else:
            self.report({'ERROR'}, f"Directory does not exist: {dir_}")

        return {'FINISHED'}

#IMPORTED SUBMODULE LIST

## ListItem

## FUNC TO EXECUTE WHEN ENABLED PROPERTY UPDATED
def enabled_state_updated(self,context): #self传入的是当前ModuleListItem的实例
    addon_prefs = bpy.context.preferences.addons[__name__].preferences
    print(f"Enabled State Updated: Submodule {self.name} State {self.enabled}")
    if hasattr(addon_prefs,'on_submodule_enabled_toggled'):
        addon_prefs.on_submodule_enabled_toggled(target_property_group=self)

class ModulesUIListItem(PropertyGroup):
    enabled: BoolProperty(
        default=True,
        update=enabled_state_updated
    ) # type: ignore

    name: StringProperty(default="") # type: ignore
    description: StringProperty(default="") # type: ignore
    category: StringProperty(default="") # type: ignore
    version: StringProperty(default="") # type: ignore

## Create Module UIList
class MQM_UL_ModuleList(UIList):
    def draw_item(self,context,layout,data,item,icon,active_data,active_propname,index):
        if self.layout_type in {'DEFAULT','COMPACT'}:
            layout.prop(item,"enabled",text="")
            layout.label(text=item.name)
            layout.label(text=item.description)
            layout.label(text=item.category)
            layout.label(text=item.version)

## GET AND STORAGE MODULE MATADATA FROM MQM_META
class ModuleMetadata:
    def __init__(self):
        self.name = ""
        self.category = ""
        self.classes = []
        self.menu_items = []

    def get(self,module):
        self.name = module.MQM_META.get("name")
        self.category = module.MQM_META.get("category")
        self.classes = module.MQM_META.get("classes")
        self.menu_items = module.MQM_META.get("menu_items")
        print(f'Metadata of Module {self.name} Initialized.')
        return self #Return Init



#ADDON PREFS
class MQMPreferences(AddonPreferences):
    bl_idname = __name__
    '''
    ---------------------------
    PROPERTIES
    ---------------------------
    '''

    scripts_path: StringProperty(
        name="Scripts Folder Path",
        subtype="DIR_PATH",
        default=os.path.join(os.path.dirname(__file__),"scripts"),
        update=lambda self, context: self.load_modules(context)
    ) # type: ignore

    modules_ui_list_collection: bpy.props.CollectionProperty(type=ModulesUIListItem) # type: ignore

    submodule_index: bpy.props.IntProperty(
        name = "Index of Submodule",
        default = -1
    ) # type: ignore

    invalid_modules_info: StringProperty(default="") # type: ignore

    debug_string: StringProperty(name="Debug String",default="") # type: ignore

    submodules: list[any] = []

    '''
    ---------------------------
    FUNCTIONS
    ---------------------------
    '''  

    def on_submodule_enabled_toggled(self,target_property_group):
        global _JSONDATA        
        def get_metadata_index(data_list,target_name):
            return next((i for i, d in enumerate(data_list) if d.get('name') == target_name ),-1)
        target_index = get_metadata_index(_JSONDATA['submodules'],target_property_group.name)
        
        _JSONDATA['submodules'][target_index]["enabled"] = target_property_group.enabled

        print(f"UPDATED JSONDATA GLOBAL VAR: {_JSONDATA}")
        json_library().write_json(_JSONDATA)
        _JSONDATA = json_library().read_json()

        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'PREFERENCES':
                    area.tag_redraw()        

    def load_modules(self,context):
        self.modules_ui_list_collection.clear()
        self.submodules.clear()
        self.invalid_modules_info = ""

        #IMPORT MODULE WITH IMPORTLIB LIBRARY
        loader = MQM_SubmoduleLoader(scripts_path=self.scripts_path) #只负责import submodules
        self.submodules, invalid_modules = loader.load()

        self.parse_json_to_uilist(context)

        self.invalid_modules_info = ",".join(invalid_modules)

        # ##Append Metadata to Global Variable
        # for m in self.submodules:
        #     global _METAINFOS
        #     metadata = ModuleMetadata().get(m)
        #     _METAINFOS.append(metadata)

        print(f'Invalid Modules: {self.invalid_modules_info}')

    def parse_json_to_uilist(self,context):
        global _JSONDATA
        for data in _JSONDATA['submodules']:
            list_item = self.modules_ui_list_collection.add()
            list_item.enabled = data['enabled']
            list_item.name = data['name']
            list_item.description = data['desc']
            list_item.category = data['category']
            list_item.version = data['version']

    #Draw UI
    def draw(self, context):
        layout = self.layout

        #ROW1
        #COLUMN1
        row1 = layout.row()
        column1 = row1.column()
        column1.prop(self, "scripts_path")
        #COLUMN2
        column2 = row1.column()
        column2.operator(operator="mqm.open_scripts_folder", text="Open In Explorer")

        box = layout.box()
        box.label(text="Installed Modules",icon='SCRIPT')

        box.template_list(
            "MQM_UL_ModuleList",
            "",
            self,
            "modules_ui_list_collection",
            self,
            "submodule_index",
        )

        box2 = box.box()
        box2.label(text=f"Invalid Modules: {self.invalid_modules_info}",icon='ERROR')

'''
---------------------------------------------------------------------------------------------------
SUBMODULE LOADER
---------------------------------------------------------------------------------------------------
'''

class MQM_SubmoduleLoader:
    def __init__(self,scripts_path):
        self.submodules = []
        self.invalid_modules = []
        self.scripts_path = scripts_path

    def load(self):
        self._clear_previous()
        self._load_files()

        global _SUBMODULES
        _SUBMODULES = self.submodules

        return self.submodules, self.invalid_modules


    def _clear_previous(self):
        self.submodules.clear()
        self.invalid_modules.clear()

    def _load_files(self):
        if not os.path.exists(self.scripts_path):
            popup_sender(f'Directory does not exist: {self.scripts_path}', "ERROR")
            return
        for file in os.listdir(self.scripts_path):
            if file.endswith(".py") and not file.startswith("__init__"):
                self._try_load_module(file)

    def _try_load_module(self,file):
        module_name = os.path.splitext(file)[0]
        file_path = os.path.join(self.scripts_path, file)
        try:
            _quick_check = self._static_mqm_check(file)
            if not _quick_check:
                self.invalid_modules.append(file)
                return

            spec = importlib.util.spec_from_file_location(module_name, file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            self.submodules.append(module)

        except Exception as e:
            popup_sender(f'Error loading module: {e}', "ERROR")


    def _static_mqm_check(self,file):
        file_path = os.path.join(self.scripts_path, file)
        try:
            with open(file_path, 'r') as f:
                tree = ast.parse(f.read(),filename=file_path)

            for node in ast.walk(tree):
                if isinstance(node,ast.Assign):
                    for target in node.targets:
                        if isinstance(target,ast.Name) and target.id == 'MQM_META':
                            if isinstance(node.value,ast.Dict):
                                return True
            return False
        except UnicodeDecodeError:
            return False

'''
---------------------------------------------------------------------------------------------------
MAIN MENU
---------------------------------------------------------------------------------------------------
'''

class MQM_MainmenuItemLoader:
    def __init__(self):
        self.categories = []
        self.ops_to_register = []

    def GetClasses(self):
        classes_to_reg, classes_to_draw, categories_to_draw = self._Class_Checker()
        print(f'Found Classes: {classes_to_reg}')
        return classes_to_reg
    
    def GetCategories(self):
        classes_to_reg, classes_to_draw, categories_to_draw = self._Class_Checker()
        print(f'Found Categories: {categories_to_draw}')
        return categories_to_draw

    def GetDrawClasses(self):
        classes_to_reg, classes_to_draw, categories_to_draw = self._Class_Checker()
        print(f'Found Draw Classes: {classes_to_draw}')
        return classes_to_draw

    def _Class_Checker(self):
        '''
        Check if submodules enabled. Check if classes avaliable. Check if Categories have been added to the draw list.
        IF TRUE APPEND TO THE CLASSES_LIST, CATEGORIES_DRAW_LIST AND THE CLASSES_DRAW_LIST
        '''
        global _SUBMODULES,_JSONDATA
        classes_to_reg = []
        avaliable_classes_str = []

        all_classes_to_draw = []
        categories_to_draw = []

        for submodule,metadata in zip(_SUBMODULES,_JSONDATA['submodules']):
            # CLASSES REGISTER BEHAVIOR DOESN'T CONTROLLED BY ENABLED STATE
            for cls_str in metadata['classes']:
                if hasattr(submodule,cls_str):
                    cls = getattr(submodule,cls_str)
                    avaliable_classes_str.append(cls_str)
                    classes_to_reg.append(cls)
                else: print(f'{cls_str} not found in {submodule.__name__}')
            if metadata['enabled']:
                if metadata['category'] not in categories_to_draw:
                    categories_to_draw.append(metadata['category'])

                for draw_cls in metadata['menu_items']:
                    submodule_classes_to_draw = {
                        "classes": [],
                        "category": "undefined"
                    }
                    if draw_cls in avaliable_classes_str:
                        submodule_classes_to_draw['classes'].append(
                            getattr(submodule,draw_cls)
                        )
                        submodule_classes_to_draw['category'] = metadata['category']
                        all_classes_to_draw.append(submodule_classes_to_draw.copy())
            else: print(f'{submodule.__name__} is disabled')

        return classes_to_reg, all_classes_to_draw, categories_to_draw


#MAIN MENU
class MQM_MainMenu(Menu):

    bl_label = "MQMenu"
    bl_idname = "MQM_MT_MainMenu"

    #!!!在这里的语句会在最开始就被执行，应将获取Categories或Classes的语句放在draw函数中!!

    def draw(self, context):
        # prefs = bpy.context.preferences.addons[__name__].preferences
        # prefs.load_modules(bpy.context) #重复加载会导致最后一个模块的enabled状态被覆盖
        layout = self.layout
        # 添加菜单项
        layout.label(text="Marble Quick Menu",icon='SCRIPT')
        self._draw_categories(layout)
        self._draw_operators(layout)

    def _draw_categories(self,layout):
        categories = MQM_MainmenuItemLoader().GetCategories()

        if "Debug" in categories:
            categories.remove("Debug")
            categories.append("Debug")

        for c in categories:
            varName = f"_{c}"
            layout.separator()
            setattr(self, varName, layout.column())
            getattr(self, varName).label(text=c)

    def _draw_operators(self,layout):
        all_classes_to_draw = MQM_MainmenuItemLoader().GetDrawClasses()

        for classes_to_draw in all_classes_to_draw:
            category = classes_to_draw['category']
            for cls in classes_to_draw['classes']:
                idname = cls.bl_idname
                target_category = getattr(self, f"_{category}")
                if issubclass(cls, bpy.types.Operator):
                    target_category.operator(idname)
                elif issubclass(cls, bpy.types.Menu):
                    target_category.menu(idname)
                else:
                    print(f'{idname} is not an operator or menu')
                print(f'{idname} added to menu')



## Draw to Main UI
def draw_menu(self, context):
    self.layout.menu("MQM_MT_MainMenu")


'''
-----------------------------------------------------------------------------------------------------------------
REG AND UNREG
-----------------------------------------------------------------------------------------------------------------
'''

RegClass = bpy.utils.register_class
unRegClass = bpy.utils.unregister_class

_CORE_CLASSES = [
    ModulesUIListItem,
    MQM_UL_ModuleList,
    MQMPreferences,
    OpenScriptsFolderInExplorer,
    MQM_MainMenu
]

_subClasses = []

def register():
    for i in _CORE_CLASSES: #Register Base Classes
        RegClass(i)

    #Get Preferences
    prefs = bpy.context.preferences.addons[__name__].preferences

    #Load Submodule to JSON
    submodule_loader(prefs.scripts_path).init_submodule()
    global _JSONDATA
    _JSONDATA = json_library().read_json()

    prefs.load_modules(bpy.context) # IMPORT Submodules
    
    _subClasses = MQM_MainmenuItemLoader().GetClasses()
    for i in _subClasses:
        RegClass(i)

    bpy.types.TOPBAR_MT_editor_menus.append(draw_menu) # Draw Main Menu

def unregister():
    for i in reversed(_CORE_CLASSES):
        unRegClass(i)

    for i in _subClasses:
        unRegClass(i)

    bpy.types.TOPBAR_MT_editor_menus.remove(draw_menu) # Remove Main Menu

if __name__ == "__main__":
    register()