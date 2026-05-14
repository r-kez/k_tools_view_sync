import bpy
from bpy.types import Operator

# Global variables for monitoring state
monitoring_active = False
active_viewport_id = "None"
last_active_area = None

class KT_VIEW3D_OT_auto_master_modal(Operator):
    bl_idname = "view3d.auto_master_modal"
    bl_label = "Auto Master Modal"
    bl_description = "Monitor active viewport for Auto Master"

    timer = None

    def modal(self, context, event):
        global active_viewport_id, last_active_area
        scene = context.scene
        sync_options = scene.sync_options
        
        if not sync_options.auto_master:
            global monitoring_active
            monitoring_active = False
            # Remove timer when monitoring is stopped
            if self.timer:
                context.window_manager.event_timer_remove(self.timer)
                self.timer = None
            return {'CANCELLED'}

        # Update active viewport based on context
        if event.type == 'MOUSEMOVE':
            # Use mouse coordinates to find the area under the mouse
            # Blender's context.area is fixed in modal operators
            found_area = None
            found_window = None
            
            # Check current window first (most common case)
            for area in context.window.screen.areas:
                if (area.x <= event.mouse_x <= area.x + area.width and
                    area.y <= event.mouse_y <= area.y + area.height):
                    found_area = area
                    found_window = context.window
                    break
            
            # If not found in current window, check others (multi-window support)
            if not found_area:
                for window in context.window_manager.windows:
                    if window == context.window: continue
                    # Translate coordinates for other windows
                    wx = event.mouse_x + context.window.x - window.x
                    wy = event.mouse_y + context.window.y - window.y
                    if 0 <= wx <= window.width and 0 <= wy <= window.height:
                        for area in window.screen.areas:
                            if (area.x <= wx <= area.x + area.width and
                                area.y <= wy <= area.y + area.height):
                                found_area = area
                                found_window = window
                                break
                    if found_area: break

            # If we found a 3D area under the mouse
            if found_area and found_area.type == 'VIEW_3D' and found_area != last_active_area:
                last_active_area = found_area
                active_viewport_id = f"View ID: {found_area.as_pointer()} (Window: {found_window.screen.name})"

                # Calculate the global index across all windows
                correct_global_index = 0
                found_match = False
                
                for w in context.window_manager.windows:
                    for a in w.screen.areas:
                        if a.type == 'VIEW_3D':
                            if a.as_pointer() == found_area.as_pointer():
                                # Update index without toggling real_time_sync 
                                # to avoid spawning multiple sync modals
                                sync_options.master_view_index = correct_global_index
                                found_area.tag_redraw()
                                found_match = True
                                break
                            correct_global_index += 1
                    if found_match:
                        break

        # Handle direct viewport interaction (clicks)
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE', 'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # Find area under mouse for clicks as well
            click_area = None
            for area in context.window.screen.areas:
                if (area.x <= event.mouse_x <= area.x + area.width and
                    area.y <= event.mouse_y <= area.y + area.height):
                    click_area = area
                    break
            
            if click_area and click_area.type == 'VIEW_3D':
                # Update ID for visual feedback
                window_name = context.window.screen.name
                active_viewport_id = f"View ID: {click_area.as_pointer()} (Window: {window_name})"

        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        global monitoring_active
        if not context.scene.sync_options.auto_master:
            return {'CANCELLED'}
            
        # Prevent multiple instances of the modal operator
        if monitoring_active:
            # Check if timer is actually registered? 
            # In Blender it's hard to check specific operator instances, 
            # so we rely on this flag.
            return {'CANCELLED'}
        
        self.timer = context.window_manager.event_timer_add(0.1)
        context.window_manager.modal_handler_add(self)
        monitoring_active = True
        return {'RUNNING_MODAL'}



def auto_master_update(self, context):
    """Handler for auto_master property updates"""
    global monitoring_active
    
    if self.auto_master:
        if not monitoring_active:
            bpy.ops.view3d.auto_master_modal('INVOKE_DEFAULT')
    else:
        # The modal will catch this via sync_options.auto_master check 
        # and set monitoring_active to False itself.
        pass
    
    # Force UI update
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
            if not active_area or active_area.type != 'VIEW_3D':
                self.report({'WARNING'}, "Not in a 3D View")
                return {'CANCELLED'}

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