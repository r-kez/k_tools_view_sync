import bpy
from bpy.types      import Panel
from .pt_sync_panel import KT_PT_SyncPanel
from .pt_lock_panel import KT_PT_LockPanel

class KT_VIEW3D_PT_SyncLock_MainPanel(Panel):
    bl_idname = 'KT_VIEW3D_PT_SyncLock_MainPanel'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "K-Tools"
    bl_label = "Sync | Lock Viewport"
    bl_options = {"DEFAULT_CLOSED"}
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="UV_SYNC_SELECT")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sync_options = scene.sync_options
        mode = sync_options.addon_mode

        row = layout.row()
        row.scale_y = 1.25
        row.prop(sync_options, "addon_mode", expand=True)

        row = layout.row(align=False)
        row.scale_y = 0.32
        row.alert=True
        row.alignment = "CENTER"
        row.label(text='———————————')
        row.alert=False

        if mode == 'SYNC_VIEW':
            row = layout.row()
            row.popover(panel="KT_VIEW3D_PT_sync_options", text="Settings")            
            KT_PT_SyncPanel().draw(context, layout)
        elif mode == 'LOCK_VIEW':
            KT_PT_LockPanel().draw(context, layout)
