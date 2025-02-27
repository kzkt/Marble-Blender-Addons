import bpy

def popup_sender(message,type="INFO"):

    def draw(self,context):
        self.layout.label(text=message)

    bpy.context.window_manager.popup_menu(draw,title=type,icon="INFO")
    return