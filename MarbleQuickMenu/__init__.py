import bpy
import os
import importlib
import ast

#GLOBAL VARS

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

## GLOBAL VARS
_METAINFOS = []
_SUBMODULES = []

#MISC FUNCTIONS

## ReportSender
def popup_sender(message,type="INFO"):
    
    def draw(self,context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw, title=type, icon='INFO')
    return

## Open in Explorer
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

## Test Button
class MQM_TestButton(Operator):
    bl_idname = "mqm.testbutton"
    bl_label = "Test Button"
    bl_description = "Test Button"
    bl_icon = 'PINNED'
    bl_options = {'REGISTER'}

    def execute(self,context):
        popup_sender("Test Button", "INFO")
        return {'FINISHED'}

#IMPORTED SUBMODULE LIST

## ListItem
class ModulesListItem(PropertyGroup):
    name: StringProperty(default="") # type: ignore
    description: StringProperty(default="") # type: ignore
    category: StringProperty(default="") # type: ignore
    version: StringProperty(default="") # type: ignore
    classes_name: StringProperty(default="") # type: ignore
    menu_items: StringProperty(default="") # type: ignore

    def set_classes(self,classes_list):
        return self._list_to_str(classes_list)
    
    def get_classes(self):
        return self._str_to_list(self.classes_name)
    
    def set_menu_items(self,menu_items_list):
        return self._list_to_str(menu_items_list)

    def get_menu_items(self):
        return self._str_to_list(self.menu_items)

    def _list_to_str(self,list_):
        if type(list_) == None:
            list_ = []
            print(f'The Class or Menu Item Missed: {self.name}. Nothing will be initialized. Please check the meta info of your submodule.')
        if not type(list_) == list:
            list_ = [list_]
            print(f'The Classes or Menu Items are not a list: {self.name}.__init__ will convert it to a list but it may cause errors. Please check the meta info of your submodule.')
        return list_
    
    def _str_to_list(self,str_):
        if str_ == "":
            return []
        else: 
            return str_.split(",")

## Create Module UIList
class MQM_UL_ModuleList(UIList):
    def draw_item(self,context,layout,data,item,icon,active_data,active_propname,index):
        if self.layout_type in {'DEFAULT','COMPACT'}:
            layout.label(text=item.name)
            layout.label(text=item.description)
            layout.label(text=item.category)
            layout.label(text=item.version)
            layout.label(text=item.classes_draw_)

#ADDON PREFS
class MQMPreferences(AddonPreferences):
    bl_idname = __name__

    scripts_path: StringProperty(
        name="Scripts Folder Path",
        subtype="DIR_PATH",
        default=os.path.join(os.path.dirname(__file__),"scripts"),
        update=lambda self, context: self.load_modules(context)
    ) # type: ignore

    submodules_collection: bpy.props.CollectionProperty(type=ModulesListItem) # type: ignore

    submodule_index: bpy.props.IntProperty(
        name = "Index of Submodule",
        default = -1
    ) # type: ignore

    submodules: list[any] = []  

    invalid_modules_info: bpy.props.StringProperty(default="") # type: ignore

    def load_modules(self,context):
        self.submodules_collection.clear()
        self.submodules.clear()
        self.invalid_modules_info = ""

        loader = MQM_SubmoduleLoader(scripts_path=self.scripts_path)
        self.submodules, invalid_modules = loader.load()

        self.invalid_modules_info = ",".join(invalid_modules)

        for m in self.submodules:
            list_item = self.submodules_collection.add()
            list_item.name = m.MQM_META.get("name")
            list_item.description = m.MQM_META.get("desc")
            list_item.category = m.MQM_META.get("category")
            list_item.version = m.MQM_META.get("version")
            list_item.set_classes(m.MQM_META.get("classes"))
            list_item.set_menu_items(m.MQM_META.get("menu_items"))

        print(f'{self.submodules_collection} Loaded.')
        print(f'Invalid Modules: {self.invalid_modules_info}')


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
            "submodules_collection",
            self,
            "submodule_index",
        )

        box2 = box.box()
        box2.label(text=f"Invalid Modules: {self.invalid_modules_info}",icon='ERROR')

#LOADING SUBMODULES

class MQM_SubmoduleLoader:
    def __init__(self,scripts_path):
        self.submodules = []
        self.invalid_modules = []
        self.scripts_path = scripts_path

    def load(self):
        self._clear_previous()
        self._load_files()

        info:str = f"Loaded {len(self.submodules)} modules; {len(self.invalid_modules)} is not MQM modules"
        popup_sender(info)
        print(info)

        global _SUBMODULES
        _SUBMODULES = self.submodules.copy()

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
        module_name = os.path.splitext(file)[0] # 获取文件名（不包含扩展名）
        file_path = os.path.join(self.scripts_path, file) # 获取文件路径
        try:
            # 动态导入模块
            _quick_check = self._static_mqm_check(file)
            if not _quick_check:
                self.invalid_modules.append(file)
                return

            spec = importlib.util.spec_from_file_location(module_name, file_path) # 创建模块规范
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

class MQM_SubmoduleMenuItemLoader:
    global _SUBMODULES,_METAINFOS

    def __init__(self):
        self.meta_infos = _METAINFOS
        self.categories = []
        self.modules = _SUBMODULES
        self.ops_to_register = []

    def GetClasses(self):
        ops_to_register, categories = self._Class_Checker()
        print(f'Found Classes: {ops_to_register}')
        return ops_to_register

    def GetCategories(self):
        ops_to_register, categories = self._Class_Checker()
        print(f'Found Categories: {categories}')
        return categories

    def _Class_Checker(self):
        classes_to_register = []
        categories = []
        for module, meta in zip(self.modules, self.meta_infos):
            for class_str in meta.get_classes():
                if hasattr(module, class_str):
                    class_ = getattr(module, class_str)
                    classes_to_register.append(class_)
                    if meta.category not in categories:
                        categories.append(meta.category)
                else:
                    print(f'{class_str} not found in {module.__name__}')

        return classes_to_register, categories

#MAIN MENU
class MQM_MainMenu(Menu):

    bl_label = "MQMenu"  # 菜单的显示名称
    bl_idname = "MQM_MT_MainMenu"  # 菜单的唯一ID
    modules = _SUBMODULES

    categories = MQM_SubmoduleMenuItemLoader().GetCategories()
    def draw(self, context):
        layout = self.layout
        # 添加菜单项
        layout.label(text="Marble Quick Menu",icon='SCRIPT')
        self._draw_categories(layout)
        self._draw_operators(layout)

    def _draw_categories(self,layout):
        for c in self.categories:
            varName = f"_{c}"
            layout.separator()
            setattr(self, varName, layout.column())
            getattr(self, varName).label(text=c)

    def _draw_operators(self,layout):
        for module in self.modules:
            menu_to_items = module.MQM_META.get("menu_items")

            if not type(menu_to_items) == list: #str to list
                menu_to_items = [menu_to_items]

            for class_str in menu_to_items:
                class_ = getattr(module, class_str)
                idname = class_.bl_idname
                target_category = getattr(self, f"_{module.MQM_META.get('category')}")
                if issubclass(class_, bpy.types.Operator):
                    target_category.operator(idname)
                elif issubclass(class_, bpy.types.Menu):
                    target_category.menu(idname)
                else:
                    print(f'{class_str} is not an operator or menu')
                print(f'{idname} added to menu')

## Draw to Main UI
def draw_menu(self, context):
    self.layout.menu("MQM_MT_MainMenu")

# ADDON REG/UNREG
_CORE_CLASSES = [
    ModulesListItem,
    MQMPreferences,
    MQM_UL_ModuleList,
    OpenScriptsFolderInExplorer,
    MQM_MainMenu,
    MQM_TestButton
]

_subClasses = []

RegClass = bpy.utils.register_class
unRegClass = bpy.utils.unregister_class

def register():
    for i in _CORE_CLASSES: #Register Base Classes
        RegClass(i)

    #Get Preferences
    prefs = bpy.context.preferences.addons[__name__].preferences
    prefs.load_modules(bpy.context)
    global _METAINFOS,_SUBMODULES
    _METAINFOS = prefs.submodules_collection
    
    _subClasses = MQM_SubmoduleMenuItemLoader().GetClasses()
    for i in _subClasses:
        RegClass(i)

    print(bpy.context.preferences.addons[__name__].preferences)


    bpy.types.TOPBAR_MT_editor_menus.append(draw_menu)  # 将自定义菜单添加到最上方菜单栏

def unregister():
    for i in reversed(_CORE_CLASSES):
        unRegClass(i)

    for i in _subClasses:
        unRegClass(i)


    bpy.types.TOPBAR_MT_editor_menus.remove(draw_menu)  # 从最上方菜单栏中移除自定义菜单

if __name__ == "__main__":
    register()