import bpy
from bpy_extras.io_utils import ExportHelper

MQM_META = {
    "name": "VRCArmatureExporter",
    "category": "VRChat",
    "version": "1.0",
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
    bl_options = {'REGISTER', 'UNDO'}
    
    filename_ext = ".fbx"

    armature: bpy.props.StringProperty() #type: ignore

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
        return {'FINISHED'}

    def _collect_export_objects(self,context):
        export_objects = []
        
        armature = context.scene.objects.get(self.armature)

        if armature.type != 'ARMATURE':
            self.report({'WARNING'}, "Please select an Armature")
            return {'CANCELLED'}
        export_objects.append(armature)

        export_objects.extend(self._get_all_children(armature))

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
        layout.label(text="Select an armature to export:",icon='EXPORT')
        layout.separator()
        self._get_all_armatures(context,layout)
        
    def _get_all_armatures(self,context,layout):
        armatures = [
            obj for obj in context.scene.objects if obj.type == 'ARMATURE'
        ]
        if not armatures:
            layout.label(text="No armatures found in the scene")
            return

        for a in armatures:
            print(a)
            row = layout.row()
            row.operator("mqm.export_armature",text=f'{a.name}').armature = a.name
            


    
    
