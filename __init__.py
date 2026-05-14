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
from . import preferences
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

@bpy.app.handlers.persistent
def apply_preferences_defaults(_):
    """Apply global preference defaults and restore session state when a file is loaded"""
    try:
        # Give Blender a moment to fully initialize
        context = bpy.context
        scene = context.scene
        if not scene: return

        # 1. Apply global preference for Auto Master (only if it's a new session/state)
        try:
            prefs = preferences.get_preferences(context)
            if prefs.auto_master_default:
                if hasattr(scene, "sync_options"):
                    scene.sync_options.auto_master = True
        except:
            pass

        # 2. Restore Real Time Sync if it was saved as ON
        if scene.real_time_sync:
            # Trigger the update function manually to restart timers/modals
            real_time_sync_update(scene, context)
        
        # 3. Ensure Auto Master modal is running if it's ON
        if hasattr(scene, "sync_options") and scene.sync_options.auto_master:
            # Import here to avoid circular dependency
            from .operators.op_auto_master import auto_master_update
            auto_master_update(scene.sync_options, context)

    except Exception as e:
        # Silent fail to avoid disrupting Blender startup
        print(f"K-Tools Restore Error: {e}")
        pass

def auto_update_view_count_timer():
    """Timer to automatically update view list when windows/areas change"""
    try:
        from .operators import op_sync_operators
        import time
        
        # Only run if the panel was recently drawn (visible)
        if time.time() - op_sync_operators.last_panel_draw_time > 2.0:
            return 2.0 # Check less frequently when panel is closed
            
        update_view_properties(None, bpy.context)
    except:
        pass
    return 1.0 # Check every second when panel is open

# Keymap For Pan in Camera Mode
addon_keymaps = []

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    properties.register()       
    preferences.register()
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
    bpy.app.handlers.load_post.append(apply_preferences_defaults)
    bpy.app.handlers.load_post.append(on_window_change)
    bpy.app.handlers.save_post.append(on_window_change)

    # Register automatic view count timer
    if not bpy.app.timers.is_registered(auto_update_view_count_timer):
        bpy.app.timers.register(auto_update_view_count_timer)

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
    preferences.unregister()
    op_view_index.unregister()
    # Remove timer if active
    if bpy.app.timers.is_registered(real_time_sync_timer):
        bpy.app.timers.unregister(real_time_sync_timer)
    
    if bpy.app.timers.is_registered(auto_update_view_count_timer):
        bpy.app.timers.unregister(auto_update_view_count_timer)
    
    # Remove properties
    del bpy.types.Scene.real_time_sync
    # LOCK VIEW
    del bpy.types.WindowManager.show_gizmo_special

    # Remove handlers
    if apply_preferences_defaults in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(apply_preferences_defaults)
    if on_window_change in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.remove(on_window_change)
    if on_window_change in bpy.app.handlers.save_post:
        bpy.app.handlers.save_post.remove(on_window_change)

    # Remove dynamic view properties
    for attr in dir(bpy.types.Scene):
        if attr.startswith("sync_view_"):
            delattr(bpy.types.Scene, attr)

    bpy.app.translations.unregister(__name__)            

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()