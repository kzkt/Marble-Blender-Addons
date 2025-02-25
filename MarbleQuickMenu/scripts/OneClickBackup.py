import bpy
import datetime

MQM_META = {
    "name": __name__,
    "category": "Objects",
    "version": "1.0",
    "desc": "Backup selected objects",
    "classes": ["MQM_OT_backup_selected"],
    "menu_items": [
        "MQM_OT_backup_selected"
    ]
}

class MQM_OT_backup_selected(bpy.types.Operator):


    bl_idname = "mqm.backup_selected"
    bl_label = "Backup Selected Objects"
    bl_description = "Create a copy of the selected objects and put them in the disabled collection"
    bl_icon = 'EVENT_NDOF_BUTTON_SAVE_V1'
    bl_options = {'REGISTER', 'UNDO'}

    

    def execute(self, context):

        #Get current time
        current_time = datetime.datetime.now().strftime("%y%m%d_%H%M%S")

        # 获取当前选中对象
        selected_objects = context.selected_objects
        if not selected_objects:
            self.report({'WARNING'}, "No objects selected")
            return {'CANCELLED'}


        # 获取当前激活对象名称用于集合命名
        active_obj_name = context.active_object.name if context.active_object else "Backup"
        collection_name = f"{active_obj_name}_BAK_{current_time}"

        # 创建或获取备份集合
        backup_collection = bpy.data.collections.get(collection_name)
        if not backup_collection:
            backup_collection = bpy.data.collections.new(collection_name)
            context.scene.collection.children.link(backup_collection)

        # 隐藏集合
        # backup_collection.hide_viewport = True
        # backup_collection.hide_render = True

        # 复制对象并添加到集合
        for obj in selected_objects:
            # 创建副本
            new_obj = obj.copy()
            new_obj.data = obj.data.copy()
            new_obj.name = f"{obj.name}_BAK_{current_time}"

            # 链接到场景并移动到备份集合
            backup_collection.objects.link(new_obj)

        def exclude_collection(view_layer: bpy.types.ViewLayer, collecion: bpy.types.Collection):
            for layer_collection in view_layer.layer_collection.children:
                if layer_collection.name == collecion.name:
                    layer_collection.exclude = True
                    return
                
        current_viewlayer = bpy.context.view_layer

        exclude_collection(current_viewlayer,backup_collection)
        self.report({'INFO'},f'Successfully Backup to {backup_collection.name}')

        return {'FINISHED'}