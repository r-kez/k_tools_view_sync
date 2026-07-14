import bpy

class KT_PT_LockPanel:
    def draw(self, context, layout):
        wm = context.window_manager
        scene = context.scene
        sync_options = scene.sync_options

        # --- Group 1: View & Gizmo Controls ---
        col = layout.column(align=True)

        # Set Clean View
        col.operator("view3d.toggle_gizmos", text="Set Clean View")
        col.prop(wm, "show_gizmo_special", text="Special Gizmos", toggle=True)

        # Camera Pan Controls
        col.prop(sync_options, "enable_camera_pan", text="Enable Camera Pan", toggle=True)
        col.prop(sync_options, "enable_pan_on_lock", text="Enable Pan on Lock", toggle=True)
        col.prop(sync_options, "auto_lock_ortho", text="Auto Lock Ortho", toggle=True)

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
                region_3d = area.spaces.active.region_3d

                row = col.row(align=True)
                row.prop(
                    region_3d,
                    "lock_rotation",
                    text=f"View {view_index}",
                    icon='LOCKED' if region_3d.lock_rotation else 'UNLOCKED'
                )

                props = row.operator_menu_enum(
                    "view3d.lock_view_preset",
                    "preset",
                    text="",
                    icon='DOWNARROW_HLT'
                )
                props.view_index = view_index
                props.window_index = window_index
