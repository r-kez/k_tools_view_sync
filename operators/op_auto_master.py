import bpy
from bpy.types import Operator

# Global variables for monitoring state
monitoring_active = False
active_viewport_id = "None"
last_mouse_x, last_mouse_y = 0, 0
last_active_area = None

class KT_VIEW3D_OT_auto_master_modal(Operator):
    bl_idname = "view3d.auto_master_modal"
    bl_label = "Auto Master Modal"
    bl_description = "Monitor active viewport for Auto Master"

    timer = None

    def modal(self, context, event):
        global active_viewport_id, last_mouse_x, last_mouse_y, last_active_area
        scene = context.scene
        sync_options = scene.sync_options
        
        if not sync_options.auto_master:
            # Remove timer when monitoring is stopped
            if self.timer:
                context.window_manager.event_timer_remove(self.timer)
                self.timer = None
            return {'CANCELLED'}

        # Update mouse position
        if event.type == 'MOUSEMOVE':
            last_mouse_x, last_mouse_y = event.mouse_x, event.mouse_y
            
            # Reset view index counter
            global_view_index = -1
            found_area = None
            found_window = None
            
            # Check which area contains the mouse
            for window in context.window_manager.windows:
                for area in window.screen.areas:
                    if area.type == 'VIEW_3D':
                        global_view_index += 1  # Increment for each View3D found
                        
                        # Check if mouse is inside this area
                        if (area.x <= last_mouse_x <= area.x + area.width and
                            area.y <= last_mouse_y <= area.y + area.height):
                            found_area = area
                            found_window = window
                            break
                if found_area:
                    break

            # If we found a new active area
            if found_area and found_area != last_active_area:
                last_active_area = found_area
                
                # Update active viewport ID with window information
                active_viewport_id = f"View ID: {found_area.as_pointer()} (Window: {found_window.screen.name})"

                # Start counting from beginning for accurate global index
                correct_global_index = 0
                for w in context.window_manager.windows:
                    for a in w.screen.areas:
                        if a.type == 'VIEW_3D':
                            if a.as_pointer() == found_area.as_pointer():
                                # Create override context
                                override = context.copy()
                                override['window'] = w
                                override['screen'] = w.screen
                                override['area'] = a
                                override['region'] = a.regions[-1]
                                
                                # Update master view index
                                was_syncing = context.scene.real_time_sync
                                if was_syncing:
                                    context.scene.real_time_sync = False
                                
                                sync_options.master_view_index = correct_global_index
                                #print(f"Master view set to: {correct_global_index} in window {w.screen.name}")
                                
                                if was_syncing:
                                    context.scene.real_time_sync = True
                                
                                # Force UI update
                                found_area.tag_redraw()
                                return {'PASS_THROUGH'}
                            correct_global_index += 1

        # Handle direct viewport interaction
        if event.type in {'LEFTMOUSE', 'RIGHTMOUSE', 'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            if context.area and context.area.type == 'VIEW_3D':
                # Find the window containing the current area
                window_name = "Unknown"
                for window in context.window_manager.windows:
                    for area in window.screen.areas:
                        if area.as_pointer() == context.area.as_pointer():
                            window_name = window.screen.name
                            break
                    if window_name != "Unknown":
                        break
                
                active_viewport_id = f"View ID: {context.area.as_pointer()} (Window: {window_name})"

        return {'PASS_THROUGH'}


    def invoke(self, context, event):
        if not context.scene.sync_options.auto_master:
            return {'CANCELLED'}
            
        self.timer = context.window_manager.event_timer_add(0.1, window=context.window)
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}



def auto_master_update(self, context):
    """Handler for auto_master property updates"""
    global monitoring_active
    
    if self.auto_master:
        monitoring_active = True
        bpy.ops.view3d.auto_master_modal('INVOKE_DEFAULT')
        #print("Auto Master monitoring started")
    else:
        monitoring_active = False
        #print("Auto Master monitoring stopped")
    
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

            # Store real-time sync state
            was_syncing = context.scene.real_time_sync
            
            # Disable real-time sync temporarily
            if was_syncing:
                #print("Temporarily disabling real-time sync")
                context.scene.real_time_sync = False

            # Set new master index
            #print(f"Setting master index to: {current_index}")
            sync_options.master_view_index = current_index

            # Restore real-time sync if it was on
            if was_syncing:
                #print("Re-enabling real-time sync")
                context.scene.real_time_sync = True

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