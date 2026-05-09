import bpy


viewport_states = {}  


class KT_PT_SyncPanel:
    def draw(self, context, layout):
        scene = context.scene
        sync_options = scene.sync_options

        # --- Group 1: Main Sync Controls ---
        col = layout.column(align=True)
        row = col.row(align=True)
        row.operator("view3d.sync_views", text='Single Match')
        row.prop(scene, "real_time_sync", text="Real Time Sync", toggle=True)

        row = col.row(align=True)
        row.prop(sync_options, "sync_refresh_rate", text="Refresh Rate")

        # --- Group 2: Master Controls ---
        col.separator()
        row = col.row(align=True)
        row.prop(sync_options, "auto_master", text="Auto Master", toggle=True)
        if not sync_options.auto_master:
            row.operator("view3d.set_current_as_master", text="Current As Master")

        row = col.row(align=True)
        row.prop(sync_options, "master_view_index", text="Master View")

        # --- Local View Controls ---
        col.separator()
        row = col.row(align=True)
        row.operator("view3d.local_view_all_areas", text='Set Local View')

        # --- Available Views Box ---
        col.separator()
        box = layout.box()
        row = box.row(align=False)
        row.label(text="Available Views:")
        row.operator("view3d.show_all_view_ids_gpu_enhanced", text='Identify Views')
        row.operator("view3d.update_view_count", text="", icon='FILE_REFRESH')

        # Get views organized by windows
        windows = bpy.context.window_manager.windows
        view3d_areas = [
            (window_index, area)
            for window_index, window in enumerate(windows)
            for area in window.screen.areas if area.type == 'VIEW_3D'
        ]

        window_views = {}
        global_view_index = 0
        for window_index, area in view3d_areas:
            if window_index not in window_views:
                window_views[window_index] = []
            window_views[window_index].append((global_view_index, area))
            global_view_index += 1

        # Create grid inside box
        grid = box.grid_flow(columns=len(window_views), even_columns=True, even_rows=False)
        for window_index, areas in window_views.items():
            col = grid.column()
            col.label(text=f"Window {window_index}")

            for view_index, area in areas:
                if hasattr(scene, f"sync_view_{view_index}"):
                    row = col.row(align=True)
                    row.prop(
                        scene,
                        f"sync_view_{view_index}",
                        text=f"View {view_index}",
                        icon='LOCKVIEW_ON' if getattr(scene, f"sync_view_{view_index}") else 'LOCKVIEW_OFF'
                    )
                    row.prop(scene, f"sync_view_preset_{view_index}", text="")



class KT_VIEW3D_PT_sync_options(bpy.types.Panel):
    bl_label = "Sync Options"
    bl_idname = "KT_VIEW3D_PT_sync_options"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'HIDE_HEADER'}
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="", icon="OPTIONS")

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        sync_options = scene.sync_options
        view = context.space_data

        box = layout.box()
        box.label(text='View Sync Options:') 

        grid = box.grid_flow(row_major=False, columns=1, align=True)         
        # View Clipping
        grid.prop(view, "clip_start", text="Clip Start:")
        grid.prop(view, "clip_end", text="Clip End:")     
        grid.prop(view, "lens", text="Focal Length:")  

        grid = box.grid_flow(row_major=False, columns=2, align=True)
        grid.prop(sync_options, "sync_view_distance_adjust", text='Distance Adjust:')  
        
        use_toggle = {"toggle": False}
                
        grid = box.grid_flow(row_major=False, columns=2, align=True)         
        grid.prop(sync_options, "sync_view_distance", text='Distance', **use_toggle)
        grid.prop(sync_options, "sync_view_location", text='Location', **use_toggle)
        grid.prop(sync_options, "sync_view_rotation", text='Rotation', **use_toggle)
        grid.prop(sync_options, "sync_camera_zoom", text='Zoom', **use_toggle)
        grid.prop(sync_options, "sync_camera_offset", text='Offset', **use_toggle)
        grid.prop(sync_options, "sync_view_perspective", text='Perspective', **use_toggle)
        grid.prop(sync_options, "sync_clip_start", text='Clip Start', **use_toggle)
        grid.prop(sync_options, "sync_clip_end", text='Clip End', **use_toggle)
        grid.prop(sync_options, "sync_focal_length", text='Focal Length', **use_toggle)

        box.label(text='Local View:')
        box.prop(sync_options, "dont_exclude_lights", text="Keep Lights when in Local View", **use_toggle)
