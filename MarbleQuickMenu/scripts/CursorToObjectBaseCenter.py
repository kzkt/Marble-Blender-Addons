import bpy
from mathutils import Vector #Convert float list to vector

MQM_META = {
    "name": "CursorToObjectBaseCenter",
    "category": "Snap",
    "version": "1.0",
    "desc": "Snap selected object to floor",
    "classes": [
        "MQM_OT_CursorToObjectBaseCenter"
    ],
    "menu_items": [
        "MQM_OT_CursorToObjectBaseCenter"
    ]
}

class MQM_OT_CursorToObjectBaseCenter(bpy.types.Operator):
    bl_idname = "mqm.cursor_to_object_base_center"
    bl_label = "Cursor to Object Base Center"
    bl_description = "Move 3D cursor to the base center of the active object"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        
        # Get cursor
        cursor = bpy.context.scene.cursor
        
        # Get Active Object
        if bpy.context.selected_objects == None:
            self.report({'WARNING'},"No Active Object")
            return{'CANCELLED'}
        target_obj = bpy.context.active_object
        if not target_obj.type == 'MESH':
            self.report({'WARNING'},"Not Supported Object Type")
            return {'CANCELLED'}

        # Set Object Origin to Center of Mass (Surface)
        saved_origin = target_obj.location.copy()
        
        #Get the first 3D Viewport area
        view3d = next((area for area in context.screen.areas if area.type == "VIEW_3D"),None)
        if view3d:
            with context.temp_override(area=view3d):

                # world_verts = (target_obj.matrix_world @ target_obj.data.vertices) #.co means coordinate

                world_matrix = target_obj.matrix_world
                verts = target_obj.data.vertices
                local_coords = [0.0] * (len(verts)*3) #Create a float list with 3x the number of vertices
                verts.foreach_get("co", local_coords) #Get the local coordinates of the vertices into the list

                world_coords = [
                    world_matrix @ Vector((x,y,z)) for x,y,z in zip(local_coords[::3],local_coords[1::3],local_coords[2::3])
                ]

                x_vals = [v.x for v in world_coords]
                y_vals = [v.y for v in world_coords]
                z_vals = [v.z for v in world_coords]

                min_co = Vector((min(x_vals),min(y_vals),min(z_vals)))
                max_co = Vector((max(x_vals),max(y_vals),max(z_vals)))

                mid_pt = (min_co + max_co) / 2
                final_pt = Vector((mid_pt.x,mid_pt.y,min_co.z))

                cursor.location = final_pt
        else:
            self.report({'WARNING'}, "No 3D Viewport Found!")
            return {'CANCELLED'}

        return {'FINISHED'}