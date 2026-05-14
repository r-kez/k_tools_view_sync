import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty

def update_auto_master_default(self, context):
    """Update current scene immediately when preference changes"""
    try:
        if hasattr(context.scene, "sync_options"):
            context.scene.sync_options.auto_master = self.auto_master_default
    except:
        pass

class KT_ViewSync_Preferences(AddonPreferences):
    bl_idname = __package__

    auto_master_default: BoolProperty( # type: ignore
        name="Auto Master On by Default",
        description="When enabled, Auto Master will be turned on automatically when starting Blender or a new file",
        default=False,
        update=update_auto_master_default
    )

    def draw(self, context):
        layout = self.layout
        box = layout.box()
        box.label(text="Global Defaults:", icon='SETTINGS')
        
        row = box.row()
        row.prop(self, "auto_master_default")

def get_preferences(context=None):
    if context is None:
        context = bpy.context
    return context.preferences.addons[__package__].preferences

def register():
    bpy.utils.register_class(KT_ViewSync_Preferences)

def unregister():
    bpy.utils.unregister_class(KT_ViewSync_Preferences)
