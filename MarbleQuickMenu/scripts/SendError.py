import bpy

MQM_META = {
    "name": "SendError",
    "category": "Debug",
    "version": "0.0.1",
    "desc": "Report an error",
    "classes": ["SEND_ERROR"],
    "menu_items": [
        "SEND_ERROR"
    ]
}

class SEND_ERROR(bpy.types.Operator):
    bl_idname = "mqm.send_error"
    bl_label = "Send Error"
    bl_description = "Report an error to the user"
    bl_icon = 'ERROR'
    bl_options = {'REGISTER'}

    def execute(self, context):
        self.report({'ERROR'}, "这只是一个测试")
        return {'CANCELLED'}

