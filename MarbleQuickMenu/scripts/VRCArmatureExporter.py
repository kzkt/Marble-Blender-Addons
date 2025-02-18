import bpy
from bpy_extras.io_utils import ExportHelper

MQM_META = {
    "name": __name__,
    "category": "VRChat",
    "version": "0.0.1",
    "desc": "Export Selected Armature for VRChat",
    "classes": [
        "MQM_OT_export_armature",
        "MQM_MT_ExportToVRChat"
    ],
    "menu_items": [
        "MQM_MT_ExportToVRChat"
    ]
}

class MQM_OT_export_armature(bpy.types.Operator, ExportHelper):
    bl_idname = "mqm.export_armature"
    bl_label = "Export for VRChat"
    bl_description = "Export Selected Armature for VRChat"
    bl_icon = 'EVENT_NDOF_BUTTON_SAVE_V1'
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".fbx"

    filter_glob: bpy.props.StringProperty(
        default="*.fbx",
        options={'HIDDEN'},
        maxlen=255,
    ) #type: ignore

    def execute(self,context):
        self._collect_export_objects(context)
        
        bpy.ops.export_scene.fbx(
            filepath=self.filepath,
            use_selection=True,
            use_active_collection=False,
            apply_scale_options='FBX_SCALE_ALL',
            object_types={
                'ARMATURE',
                'MESH',
                'EMPTY'
                },
            use_mesh_modifiers=True,
            add_leaf_bones=False
        )

    def _collect_export_objects(self,context):
        export_objects = []
        
        selected_object = context.selected_objects[0]

        if selected_object.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an Armature")
            return {'CANCELLED'}
        export_objects.append(selected_object)

        export_objects.extend(self._get_all_children(selected_object))

        bpy.ops.object.select_all(action='DESELECT')
        for obj in export_objects:
            obj.hide_viewport = False
            obj.hide_render = False
            obj.select_set(True)


    def _get_all_children(self,obj):
        children = []
        for child in obj.children:
            children.append(child)
            children.extend(self._get_all_children(child))
        return children

class MQM_MT_ExportToVRChat(bpy.types.Menu):
    bl_label = "Export to VRChat"
    bl_idname = "MQM_MT_SUB_ExportToVRChat"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Export to VRChat")
        
        
        


    
    
