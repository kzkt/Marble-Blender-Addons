import bpy
from bpy.app.handlers import persistent
import datetime

bl_info = {
    "name": "One Click Backup Pro",
    "blender": (4, 2, 3),
    "version": (0, 0, 1),
    "category": "Object",
}

#UI

## UILISTS

### BACKUPED OBJECTS LIST

#### DATA STRUCTURE
class OCBP_Object_Item(bpy.types.PropertyGroup):
    name:str = "Object"
    backupscount:int = 0

class OCBP_UL_BackupedObjectsList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.name)
            layout.label(text=item.backupscount)

# class BackupedObjects(bpy.types.PropertyGroup):
#     _dynamic_objects_list: list = []

#### PANEL

class OCBP_PT_MainPanel(bpy.types.Panel):
    bl_label = "One Click Backup Pro"
    bl_idname = "OCBP_PT_MainPanel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'OCBPro'

    def draw(self,context):
        layout = self.layout
        layout.label(text=f'Version: {".".join(map(str, bl_info["version"]))}')
        layout.operator("ocbp.oneclickbackup")

        box_objlist = layout.box()
        box_objlist.label(text="Backuped Objects")

        #CHECK BACKUPED OBJECTS
        ocbp_collection = bpy.data.collections.get("OCBP")
        if not ocbp_collection or len(ocbp_collection.children) == 0:
            box_objlist.label(icon="QUESTION",text="No Backuped Objects")
        else:
            box_objlist.template_list(
                "OCBP_UL_BackupedObjectsList",
                "",
                context.scene,
                "ocbp_backuped_object_list",
                context.scene,
                "ocbp_backuped_object_list_index"
            )

#Detect Scene Update and Update Object List
previous_scene_object_pointers = {}

@persistent
def scene_update_handler(scene,depsgraph):


def update_object_list(scene=None):
    """Only Update Object List PropertyGroup in Scene"""
    if scene is None:
        scene = bpy.context.scene
    if scene is None: #Second Check if bpy.context.scene is None
        return
    
    print(f'Current Scene Objects Count: {len(scene.objects)}')

    scene.ocbp_backuped_object_list.clear()

    ocbp_collection = bpy.data.collections.get("OCBP")
    if not ocbp_collection:
        return
    else:
        for bak_obj in ocbp_collection.children:
            new_list_obj = scene.ocbp_backuped_object_list.add()
            new_list_obj.name = bak_obj.name
            new_list_obj.backupscount = len(bak_obj.children)

#FUNC
class OCBP_OT_OneClickBackup(bpy.types.Operator):
    bl_idname = "ocbp.oneclickbackup"
    bl_label = "One Click Backup (Pro)"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        #Get current time
        current_time = datetime.datetime.now().strftime("%y%m%d_%H%M%S")

        #Get Active Item
        active_obj = context.active_object
        active_obj_name = active_obj.name
    
        #Get OCBP Collection
        ocbp_collection = bpy.data.collections.get("OCBP")
        if not ocbp_collection:
            ocbp_collection = bpy.data.collections.new("OCBP")
            context.scene.collection.children.link(ocbp_collection)

        #Create Sub Collection
        bak_obj_col_name = f'{active_obj_name}_BAK'
        bak_obj_col = bpy.data.collections.get(bak_obj_col_name)
        if not bak_obj_col:
            bak_obj_col = bpy.data.collections.new(bak_obj_col_name)
            ocbp_collection.children.link(bak_obj_col)

        #Copy Active Object
        new_obj = active_obj.copy()
        new_obj.data = active_obj.data.copy()
        new_obj.name = f'{active_obj_name}_OCBP_{current_time}'
        bak_obj_col.objects.link(new_obj)

        #Hide Backup Object
        new_obj.hide_viewport = True
        new_obj.hide_set(state=True,view_layer=bpy.context.view_layer) 
        new_obj.hide_render = True

        self.report(
            {'INFO'},
            f'Successfully created backup of {active_obj_name} as {new_obj.name}'
        )
        
        return {'FINISHED'}
    

#REG/UNREG
RegClass = bpy.utils.register_class
unRegClass = bpy.utils.unregister_class

_REG_LIST = [
OCBP_Object_Item,
OCBP_UL_BackupedObjectsList,
OCBP_PT_MainPanel,
OCBP_OT_OneClickBackup
]

def register():
    for i in _REG_LIST:
        RegClass(i)

    # REGISTER SCENE PROPERTIES
    bpy.types.Scene.ocbp_backuped_object_list = bpy.props.CollectionProperty(type=OCBP_Object_Item)
    bpy.types.Scene.ocbp_backuped_object_list_index = bpy.props.IntProperty(default=0)

    # bpy.app.handlers.load_post.append(load_handler)
    # bpy.app.timers.register(initialize_addon, first_interval=0.1)



def unregister():
    global initialization_done, msgbus_owner
    initialization_done = False
    
    #CLEAR MSGBUS SUBS
    # bpy.msgbus.clear_by_owner(msgbus_owner)

    # # Remove handlers
    # if load_handler in bpy.app.handlers.load_post:
    #     bpy.app.handlers.load_post.remove(load_handler)
    
    # if bpy.app.timers.is_registered(initialize_addon):
    #     bpy.app.timers.unregister(initialize_addon)

    # if bpy.app.timers.is_registered(delayed_update_once):
    #     bpy.app.timers.unregister(delayed_update_once)
    
    # Unregister properties
    del bpy.types.Scene.ocbp_backuped_object_list_index
    del bpy.types.Scene.ocbp_backuped_object_list

    for i in _REG_LIST:
        unRegClass(i)

if __name__ == "__main__":
    register()