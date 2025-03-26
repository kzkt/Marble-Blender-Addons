import bpy

MQM_META = {
    "name": "SelectionToWorldOrigin",
    "category": "Snap",
    "version": "1.0",
    "desc": "Set origin of selected object to the world origin",
    "classes": [
        "MQM_OT_SelectionToWorldOrigin"
    ],
    "menu_items": [
        "MQM_OT_SelectionToWorldOrigin"
    ]
}

class MQM_OT_SelectionToWorldOrigin(bpy.types.Operator):
    bl_idname = "mqm.selection_to_world_origin"
    bl_label = "Selection to World Origin"
    bl_description = "Set origin of selected object to the world origin"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        #Get Cursor and copy its location
        cursor = bpy.context.scene.cursor
        saved_cursor_location = cursor.location.copy()

        #Set cursor to world origin
        cursor.location = (0, 0, 0)
        
        #Get Selected Object
        selected_objs = bpy.context.selected_objects
        if not selected_objs:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}
        
        #Focus to view3d Context
        #Get the first 3D Viewport area
        view3d = next((area for area in context.screen.areas if area.type == "VIEW_3D"),None)
        if view3d:
            with context.temp_override(area=view3d):
                context.view_layer.objects.active = selected_objs[0]
                #目前的Context需要是View3d才能成功调用该ops
                bpy.ops.object.origin_set(type='ORIGIN_CURSOR',center='MEDIAN')
        else:
            self.report({'WARNING'}, "No 3D Viewport Found!")
            return {'CANCELLED'}
        
            

        cursor.location = saved_cursor_location

        return {'FINISHED'}