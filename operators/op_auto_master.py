import bpy
from bpy.types import Operator

# Global variables for monitoring state
monitoring_active = False
active_viewport_id = "None"
last_active_area = None

class KT_VIEW3D_OT_auto_master_modal(Operator):
    """Deprecated: Auto Master is now handled safely by timers/view detection without blocking Blender's autosave"""
    bl_idname = "view3d.auto_master_modal"
    bl_label = "Auto Master Modal"
    bl_description = "Monitor active viewport for Auto Master"

    def execute(self, context):
        return {'FINISHED'}

    def invoke(self, context, event):
        return self.execute(context)


def auto_master_update(self, context):
    """Handler for auto_master property updates"""
    # Force UI update without spawning a modal operator
    if context and hasattr(context, "screen") and context.screen:
        for area in context.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()
            
    return None


class KT_VIEW3D_OT_set_current_as_master(Operator):
    bl_idname = "view3d.set_current_as_master"
    bl_label = "Set As Master"
    bl_description = "Set current view as master view"

    def execute(self, context):
        scene = context.scene
        sync_options = scene.sync_options
        
        try:
            # Get current view index
            active_area = context.area
            allowed_2d_types = {'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR'}
            
            if not active_area or (active_area.type != 'VIEW_3D' and active_area.type not in allowed_2d_types):
                self.report({'WARNING'}, "Not in a supported editor (3D View, Timeline, Dopesheet, NLA, Graph Editor)")
                return {'CANCELLED'}

            if active_area.type == 'VIEW_3D':
                # Calculate current view index
                view3d_count = 0
                current_index = -1
                
                for window in context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type == 'VIEW_3D':
                            if area == active_area:
                                current_index = view3d_count
                            view3d_count += 1

                if current_index == -1:
                    self.report({'WARNING'}, "Couldn't determine view index")
                    return {'CANCELLED'}

                # Set new master index
                sync_options.master_view_index = current_index
                self.report({'INFO'}, f"Set master to view {current_index}")
            else:
                # Calculate current 2D view index
                view2d_count = 0
                current_index = -1
                
                for window in context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.type in allowed_2d_types:
                            if area == active_area:
                                current_index = view2d_count
                            view2d_count += 1

                if current_index == -1:
                    self.report({'WARNING'}, "Couldn't determine 2D view index")
                    return {'CANCELLED'}

                # Set new master index
                sync_options.master_2d_view_index = current_index
                self.report({'INFO'}, f"Set master 2D view to index {current_index}")
            
            # Force UI update
            for area in context.screen.areas:
                area.tag_redraw()

            return {'FINISHED'}

        except Exception as e:
            #print(f"Error: {e}")
            self.report({'ERROR'}, f"Error: {str(e)}")
            return {'CANCELLED'}




# Test operator for debugging
class KT_VIEW3D_OT_test_view_index(Operator):
    bl_idname = "view3d.test_view_index"
    bl_label = "Test Current View Index"
    bl_description = "Test the current view index calculation"

    def execute(self, context):
        active_area = context.area
        scene = context.scene
        sync_options = scene.sync_options

        if not active_area or active_area.type != 'VIEW_3D':
            self.report({'INFO'}, "Not in a 3D View")
            return {'CANCELLED'}

        view3d_count = 0
        current_index = -1
        
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    if area == active_area:
                        current_index = view3d_count
                    view3d_count += 1

        self.report({'INFO'}, f"Current View: {current_index} of {view3d_count} views")
        #print(f"Current View: {current_index} of {view3d_count} views")  # Debug print
        
        # Force update the master index
        if sync_options.auto_master:
            sync_options.master_view_index = current_index
            
        return {'FINISHED'}
classes = (
    
    KT_VIEW3D_OT_test_view_index,
    KT_VIEW3D_OT_set_current_as_master,    
    KT_VIEW3D_OT_auto_master_modal,
    
)