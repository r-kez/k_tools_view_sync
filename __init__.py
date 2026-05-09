import bpy
from bpy.props import BoolProperty
from bpy.app.translations import pgettext_iface as _
# Panels
from .panels.main_panel import KT_VIEW3D_PT_SyncLock_MainPanel
from .panels.pt_sync_panel import KT_VIEW3D_PT_sync_options
# Operators: Sync
from .operators import classes as operators
from .operators.op_sync_operators import (
    update_view_properties, 
    real_time_sync_timer, 
    real_time_sync_update
    )
# Properties
from .properties import properties
# View Index
from .operators import op_view_index

from .dictionary_merge import translations_dict


def get_active_screens():
    return [window.screen for window in bpy.context.window_manager.windows]

classes = (
    *operators,
    KT_VIEW3D_PT_SyncLock_MainPanel,
    KT_VIEW3D_PT_sync_options,
    )

@bpy.app.handlers.persistent
def on_window_change(_):
    try:
        update_view_properties(None, bpy.context)
    except:
        pass

# Keymap For Pan in Camera Mode
addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    properties.register()       
    op_view_index.register()

    bpy.types.Scene.real_time_sync = BoolProperty(
        name="Real-time Sync",
        description="Enable real-time synchronization",
        default=False,
        update=real_time_sync_update
    )
    
    # LOCK VIEW   
    bpy.types.WindowManager.show_gizmo_special = BoolProperty(
        name="Show Gizmo While Lock",
        default=True,
        description='Show special gizmos in locked views'
    )
    # Register handlers
    bpy.app.handlers.load_post.append
    bpy.app.handlers.load_post.append(on_window_change)
    bpy.app.handlers.save_post.append(on_window_change)

    # Keymap for camera Pan
    # Setup keymap - using smart_pan as default
    wm = bpy.context.window_manager
    kc = wm.keyconfigs.addon
    if kc:
        # Get or create 3D View keymap
        km = kc.keymaps.get('3D View')
        if not km:
            km = kc.keymaps.new(name='3D View', space_type='VIEW_3D')
        
        # Map middle mouse button to smart pan (combines both behaviors)
        kmi = km.keymap_items.new(
            'view3d.smart_pan',
            type='MIDDLEMOUSE',
            value='PRESS'
        )
        # Set higher priority to override default behavior
        kmi.active = True
        
        addon_keymaps.append((km, kmi))

        bpy.app.translations.register(__name__, translations_dict)

def unregister():
    properties.unregister()
    op_view_index.unregister()
    # Remove timer if active
    if bpy.app.timers.is_registered(real_time_sync_timer):
        bpy.app.timers.unregister(real_time_sync_timer)
    
    # Remove properties
    del bpy.types.Scene.real_time_sync
    # LOCK VIEW
    del bpy.types.WindowManager.show_gizmo_special

    # Remove dynamic view properties
    for attr in dir(bpy.types.Scene):
        if attr.startswith("sync_view_"):
            delattr(bpy.types.Scene, attr)

    bpy.app.translations.unregister(__name__)            

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()