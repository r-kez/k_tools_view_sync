import bpy

class KT_OT_create_analytic_window(bpy.types.Operator):
    """Open a dedicated analysis window with multiple synced views"""
    bl_idname = "view3d.kt_create_analytic_window"
    bl_label = "Open Analytic Window"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        # 1. Store original workspace to switch back
        original_workspace = context.workspace
        
        # 2. Create or setup the Analysis Workspace
        ws_name = "K-Tools Analysis"
        if ws_name in bpy.data.workspaces:
            new_ws = bpy.data.workspaces[ws_name]
        else:
            bpy.ops.workspace.duplicate()
            new_ws = context.workspace
            new_ws.name = ws_name
            
        # 3. Open a new window on this workspace
        # We temporarily set the main window to the new workspace so window_new clones it
        context.window.workspace = new_ws
        bpy.ops.wm.window_new()
        
        # Restore main window workspace
        context.window.workspace = original_workspace
        
        # 4. Target the new window for layout configuration
        target_window = context.window_manager.windows[-1]
        
        # Split logic
        with context.temp_override(window=target_window, screen=target_window.screen):
            # Find initial 3D area
            area_3d = next((a for a in target_window.screen.areas if a.type == 'VIEW_3D'), None)
            
            if area_3d:
                # Vertical split
                with context.temp_override(area=area_3d):
                    bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
                
                # Now we have 2 areas, split both horizontally
                areas_after_v = [a for a in target_window.screen.areas if a.type == 'VIEW_3D']
                for a in areas_after_v:
                    with context.temp_override(area=a):
                        bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.5)
                
                # 5. Setup Presets for the 4 final areas
                # We'll identify them by their position (X, Y)
                final_areas = sorted([a for a in target_window.screen.areas if a.type == 'VIEW_3D'], 
                                    key=lambda a: (a.x, a.y))
                
                # Order will be: Bottom-Left, Top-Left, Bottom-Right, Top-Right (approx)
                presets = ['SILHOUETTE', 'TOPOLOGY', 'NORMALS', 'HIGH_DETAIL']
                
                # We need access to apply_shading_preset. 
                # Since it's in another module, we'll import it here to avoid circular imports
                from .op_sync_operators import apply_shading_preset
                
                # Find all 3D areas globally to get the correct indices for the sync system
                all_3d_areas = [a for w in context.window_manager.windows 
                               for a in w.screen.areas if a.type == 'VIEW_3D']
                
                for i, area in enumerate(final_areas):
                    # Find global index
                    try:
                        global_idx = all_3d_areas.index(area)
                        preset = presets[i % len(presets)]
                        apply_shading_preset(context, global_idx, preset)
                        
                        # Set dynamic property so UI reflects it
                        prop_name = f"sync_view_preset_{global_idx}"
                        setattr(context.scene, prop_name, preset)
                        
                        # Enable sync for this specific view
                        sync_toggle_name = f"sync_view_{global_idx}"
                        setattr(context.scene, sync_toggle_name, True)
                    except:
                        pass
        
        # 6. Enable Real-time Sync if off
        context.scene.real_time_sync = True
        
        self.report({'INFO'}, "Analytic Window Created!")
        return {'FINISHED'}

class KT_OT_close_analytic_sessions(bpy.types.Operator):
    """Remove temporary analysis workspaces"""
    bl_idname = "view3d.kt_close_analytic_sessions"
    bl_label = "Clean Analysis Sessions"
    bl_options = {'REGISTER', 'UNDO'}
    
    def execute(self, context):
        to_remove = [ws for ws in bpy.data.workspaces if ws.name == "K-Tools Analysis"]
        for ws in to_remove:
            # Make sure we are not in it
            if context.workspace == ws:
                context.window.workspace = bpy.data.workspaces[0]
            bpy.data.workspaces.remove(ws)
        return {'FINISHED'}

class KT_VIEW3D_OT_call_sync_lock_popup(bpy.types.Operator):
    """Open a floating popup dialog for K-Tools View Sync"""
    bl_idname = "view3d.call_sync_lock_popup"
    bl_label = "K-Tools View Sync Menu"
    bl_options = {'REGISTER', 'UNDO'}
    
    def draw(self, context):
        layout = self.layout
        
        # Add spacing at the top of the popup
        layout.separator(factor=1.2)
        
        scene = context.scene
        sync_options = scene.sync_options
        mode = sync_options.addon_mode

        row = layout.row()
        row.scale_y = 1.25
        row.prop(sync_options, "addon_mode", expand=True)

        row = layout.row(align=False)
        row.scale_y = 0.32
        row.alert = True
        row.alignment = "CENTER"
        row.label(text='———————————')
        row.alert = False

        if mode == 'SYNC_VIEW':
            row = layout.row()
            row.popover(panel="KT_VIEW3D_PT_sync_options", text="Settings")            
            from ..panels.pt_sync_panel import KT_PT_SyncPanel
            KT_PT_SyncPanel().draw(context, layout)
        elif mode == 'LOCK_VIEW':
            from ..panels.pt_lock_panel import KT_PT_LockPanel
            KT_PT_LockPanel().draw(context, layout)

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.invoke_popup(self, width=280)
        return {'RUNNING_MODAL'}

classes = (
    KT_OT_create_analytic_window,
    KT_OT_close_analytic_sessions,
    KT_VIEW3D_OT_call_sync_lock_popup,
)
