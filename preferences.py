import bpy
from bpy.types import AddonPreferences
from bpy.props import BoolProperty, EnumProperty

def update_auto_master_default(self, context):
    """Update current scene immediately when preference changes"""
    try:
        if hasattr(context.scene, "sync_options"):
            context.scene.sync_options.auto_master = self.auto_master_default
    except:
        pass

def update_auto_lock_ortho_default(self, context):
    """Update current scene immediately when preference changes"""
    try:
        if hasattr(context.scene, "sync_options"):
            context.scene.sync_options.auto_lock_ortho = self.auto_lock_ortho_default
    except:
        pass

def update_replace_local_view(self, context):
    """Dynamically update keymap when preference toggle changes"""
    try:
        from . import register_keymaps
        register_keymaps()
    except Exception as e:
        print(f"Error updating keymaps: {e}")

def update_floating_panel_keymap(self, context):
    """Dynamically update keymap when preference toggle changes"""
    try:
        from . import register_keymaps
        register_keymaps()
    except Exception as e:
        print(f"Error updating keymaps: {e}")

class KT_ViewSync_Preferences(AddonPreferences):
    bl_idname = __package__

    settings_tab: EnumProperty( # type: ignore
        name="Tab",
        items=[
            ('DEFAULTS', "Global Defaults", "Configure default startup behaviors", 'SETTINGS', 0),
            ('UI', "UI Options", "Configure user interface and overlays", 'RESTRICT_VIEW_OFF', 1),
            ('KEYMAP', "Keymap Options", "Configure shortcuts and key bindings", 'KEYINGSET', 2),
            ('HELP', "Help", "Report bugs and view documentation", 'HELP', 3)
        ],
        default='DEFAULTS'
    )

    auto_master_default: BoolProperty( # type: ignore
        name="Auto Master On by Default",
        description="When enabled, Auto Master will be turned on automatically when starting Blender or a new file",
        default=True,
        update=update_auto_master_default
    )

    auto_lock_ortho_default: BoolProperty( # type: ignore
        name="Auto Lock Ortho by Default",
        description="When enabled, Auto Lock Ortho will be turned on automatically when starting Blender or a new file",
        default=False,
        update=update_auto_lock_ortho_default
    )

    show_lock_hud: BoolProperty( # type: ignore
        name="Show Lock HUD Overlay",
        description="Display a HUD card at the bottom of the viewport when rotation is locked",
        default=True
    )

    replace_local_view: BoolProperty( # type: ignore
        name="Replace Default Local View",
        description="Override Blender's default Local View key with K-Tools Global Local View (isolates objects in all 3D viewports simultaneously)",
        default=False,
        update=update_replace_local_view
    )

    use_floating_panel_keymap: BoolProperty( # type: ignore
        name="Enable Floating Panel Hotkey",
        description="Enable a global shortcut to open the View Sync / Lock floating popup menu in 3D Viewport",
        default=False,
        update=update_floating_panel_keymap
    )

    dont_exclude_lights: BoolProperty( # type: ignore
        name="Keep Lights in Local View",
        description="Keep lights visible when using Local View",
        default=True
    )

    def draw(self, context):
        layout = self.layout
        
        row = layout.row()
        row.prop(self, "settings_tab", expand=True)

        if self.settings_tab == 'DEFAULTS':
            box = layout.box()
            box.label(text="Global Defaults:", icon='SETTINGS')
            row_def = box.row()
            row_def.prop(self, "auto_master_default")
            row_def.prop(self, "auto_lock_ortho_default")

            box.prop(self, "dont_exclude_lights")
            
        elif self.settings_tab == 'UI':
            box_ui = layout.box()
            box_ui.label(text="UI Options:", icon='RESTRICT_VIEW_OFF')
            row_ui = box_ui.row()
            row_ui.prop(self, "show_lock_hud")
            
        elif self.settings_tab == 'KEYMAP':
            box_keymap = layout.box()
            box_keymap.label(text="Keymap Options:", icon='KEYINGSET')
            
            row_key = box_keymap.row(align=True)
            row_key.prop(self, "replace_local_view")
            row_key.operator("view3d.restore_default_local_view", text="Restore Default", icon='LOOP_BACK')

            box_keymap.prop(self, "use_floating_panel_keymap", text="Enable Floating Panel Hotkey")
            
            if self.use_floating_panel_keymap:
                wm = context.window_manager
                kc = wm.keyconfigs.addon
                if kc:
                    km = kc.keymaps.get('3D View')
                    if km:
                        # Find our operator keymap item
                        for kmi in km.keymap_items:
                            if kmi.idname == 'view3d.call_sync_lock_popup':
                                col = box_keymap.column()
                                col.context_pointer_set("keymap", km)
                                col.label(text="Hotkey Configuration:")
                                import rna_keymap_ui
                                rna_keymap_ui.draw_kmi([], kc, km, kmi, col, 0)
                                break

        elif self.settings_tab == 'HELP':
            box_help = layout.box()
            box_help.label(text="Help & Support:", icon='HELP')
            row = box_help.row(align=False)
            row.operator("wm.url_open", text="Report a Bug", icon='URL').url = "https://github.com/r-kez/k_tools_view_sync/issues"
            row.operator("wm.url_open", text="Documentation", icon='QUESTION').url = "https://github.com/r-kez/k_tools_view_sync/wiki"

class KT_OT_restore_default_local_view(bpy.types.Operator):
    """Restore default Blender Local View hotkey"""
    bl_idname = "view3d.restore_default_local_view"
    bl_label = "Restore Default"
    bl_description = "Restore the default Blender keymap for Local View"
    
    def execute(self, context):
        try:
            prefs = get_preferences(context)
            prefs.replace_local_view = False
            self.report({'INFO'}, "Default Local View keymap restored.")
        except Exception as e:
            self.report({'ERROR'}, f"Failed to restore: {e}")
        return {'FINISHED'}

def get_preferences(context=None):
    if context is None:
        context = bpy.context
    return context.preferences.addons[__package__].preferences

def register():
    bpy.utils.register_class(KT_ViewSync_Preferences)
    bpy.utils.register_class(KT_OT_restore_default_local_view)

def unregister():
    bpy.utils.unregister_class(KT_OT_restore_default_local_view)
    bpy.utils.unregister_class(KT_ViewSync_Preferences)
