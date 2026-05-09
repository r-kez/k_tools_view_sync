import bpy
import time
import gpu
from gpu_extras.batch import batch_for_shader
import blf




# Global variables to manage the text overlay
_draw_handlers = []
_start_time = 0
_display_duration = 3.0  # 3 seconds
_view_ids = {}
_window_info = {}  # New: store window information for each view

def draw_view_id_overlay():
    """Draw function that renders the view ID text in each viewport"""
    global _start_time, _display_duration, _view_ids, _window_info
    
    current_time = time.time()
    if current_time - _start_time > _display_duration:
        # Time expired, remove handlers
        remove_view_id_handlers()
        return
    
    # Get current context
    context = bpy.context
    if not context.area or context.area.type != 'VIEW_3D':
        return
    
    # Get the current area to find its ID
    current_area_id = None
    current_window_id = None
    for area_id, area in _view_ids.items():
        if area == context.area:
            current_area_id = area_id
            current_window_id = _window_info.get(area_id, 0)
            break
    
    if current_area_id is None:
        return
    
    # Calculate fade effect
    elapsed = current_time - _start_time
    if elapsed > _display_duration - 0.5:  # Fade out in last 0.5 seconds
        alpha = (_display_duration - elapsed) / 0.5
    else:
        alpha = 1.0
    
    # Set up text properties
    font_id = 0
    blf.size(font_id, 48)  # Large font size
    blf.color(font_id, 1.0, 1.0, 1.0, alpha)  # White with alpha
    
    # Get viewport dimensions
    region = context.region
    width = region.width
    height = region.height
    
    # Create text with window and view information
    text = f"Window {current_window_id}, View {current_area_id}"
    
    # Get text dimensions for centering
    text_width, text_height = blf.dimensions(font_id, text)
    
    # Calculate position (center of viewport)
    x = (width - text_width) / 2
    y = (height - text_height) / 2
    
    # Enable blend mode for transparency
    gpu.state.blend_set('ALPHA')
    
    # Draw background rectangle (optional, for better text visibility)
    bg_padding = 20
    bg_vertices = [
        (x - bg_padding, y - bg_padding),
        (x + text_width + bg_padding, y - bg_padding),
        (x + text_width + bg_padding, y + text_height + bg_padding),
        (x - bg_padding, y + text_height + bg_padding)
    ]
    
    bg_indices = [(0, 1, 2), (2, 3, 0)]
    
    # Create background shader
    bg_shader = gpu.shader.from_builtin('UNIFORM_COLOR')
    bg_batch = batch_for_shader(bg_shader, 'TRIS', {"pos": bg_vertices}, indices=bg_indices)
    
    # Draw semi-transparent background
    bg_shader.bind()
    bg_shader.uniform_float("color", (0.0, 0.0, 0.0, 0.5 * alpha))
    bg_batch.draw(bg_shader)
    
    # Draw the text
    blf.position(font_id, x, y, 0)
    blf.draw(font_id, text)
    
    # Reset blend state
    gpu.state.blend_set('NONE')

def remove_view_id_handlers():
    """Remove all draw handlers"""
    global _draw_handlers
    
    for handler in _draw_handlers:
        try:
            bpy.types.SpaceView3D.draw_handler_remove(handler, 'WINDOW')
        except:
            pass  # Handler might have been already removed
    
    _draw_handlers.clear()
    
    # Force redraw all areas
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

def setup_view_id_handlers():
    """Setup draw handlers for all 3D viewports"""
    global _draw_handlers, _start_time, _view_ids, _window_info
    
    # Clear any existing handlers first
    remove_view_id_handlers()
    
    # Reset time
    _start_time = time.time()
    
    # Get all 3D views and assign IDs with window information
    _view_ids.clear()
    _window_info.clear()
    global_view_index = 0
    
    windows = bpy.context.window_manager.windows
    for window_index, window in enumerate(windows):
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                _view_ids[global_view_index] = area
                _window_info[global_view_index] = window_index  # Store window index
                global_view_index += 1
    
    # Add a single draw handler that will work for all viewports
    # The handler will automatically be called for each viewport when they redraw
    handler = bpy.types.SpaceView3D.draw_handler_add(
        draw_view_id_overlay, (), 'WINDOW', 'POST_PIXEL'
    )
    _draw_handlers.append(handler)
    
    # Force redraw all 3D viewports to trigger the handler
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                area.tag_redraw()

class KT_VIEW3D_OT_ShowViewID_GPU(bpy.types.Operator):
    """Show the Global Index for All 3D Views using GPU text overlay"""
    bl_idname = "view3d.show_all_view_ids_gpu"
    bl_label = "Show All View 3D IDs (GPU Overlay)"
    bl_description = "Display Window and View ID numbers on all 3D viewports"

    def execute(self, context):
        # Setup the GPU text overlay system
        setup_view_id_handlers()
        
        # Count total views for report
        view_count = len([area for window in bpy.context.window_manager.windows 
                        for area in window.screen.areas if area.type == 'VIEW_3D'])
        
        self.report({'INFO'}, f"Displaying IDs for {view_count} 3D viewport(s)")
        
        return {'FINISHED'}

# Timer function to clean up handlers automatically
def cleanup_timer():
    """Timer function to ensure handlers are cleaned up"""
    global _start_time, _display_duration
    
    current_time = time.time()
    if current_time - _start_time > _display_duration + 0.5:  # Add small buffer
        remove_view_id_handlers()
        return None  # Stop timer
    
    return 0.1  # Check again in 0.1 seconds

# Enhanced version that also starts a cleanup timer
class KT_VIEW3D_OT_ShowViewID_GPU_Enhanced(bpy.types.Operator):
    """Enhanced version with automatic cleanup timer"""
    bl_idname = "view3d.show_all_view_ids_gpu_enhanced"
    bl_label = "Show All View 3D IDs (GPU Enhanced)"
    bl_description = "Display Window and View ID numbers on all 3D viewports"

    def execute(self, context):
        # Setup the GPU text overlay system
        setup_view_id_handlers()

        bpy.ops.view3d.update_view_count()
        
        # Start cleanup timer
        if not bpy.app.timers.is_registered(cleanup_timer):
            bpy.app.timers.register(cleanup_timer)
        
        # Count total views for report
        view_count = len([area for window in bpy.context.window_manager.windows 
                        for area in window.screen.areas if area.type == 'VIEW_3D'])
        
        self.report({'INFO'}, f"Available 3D Views: {view_count}.")
        
        return {'FINISHED'}

# Operator to manually clear the overlay (if needed)
class KT_VIEW3D_OT_ClearViewID_GPU(bpy.types.Operator):
    """Clear View ID GPU overlay"""
    bl_idname = "view3d.clear_view_ids_gpu"
    bl_label = "Clear View ID Overlay"
    bl_description = "Manually clear the GPU text overlay"

    def execute(self, context):
        remove_view_id_handlers()
        self.report({'INFO'}, "View ID overlay cleared")
        return {'FINISHED'}

# Keep the original popup-based operator for compatibility
def ShowMessageBox(message="", title="Message Box", icon='INFO'):
    def draw(self, context):
        self.layout.label(text=message)
    bpy.context.window_manager.popup_menu(draw, title=title, icon=icon)

class KT_VIEW3D_OT_ShowViewID(bpy.types.Operator):
    """Show the Global Index for the Current 3D View and Window"""
    bl_idname = "view3d.show_current_view_id"
    bl_label = "Show Current Window and Global View 3D ID"
    bl_description = "Display current viewport's Window and View ID in a popup"
    
    def execute(self, context):
        # Get all open windows
        windows = bpy.context.window_manager.windows
        current_window_index = -1
        current_view_index = -1  # Global view index
        global_view_index = -1   # Continuous global index of views
        
        for window_index, window in enumerate(windows):
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    global_view_index += 1  # Increase global index
                    if area == context.area:
                        current_window_index = window_index
                        current_view_index = global_view_index
                        break
            if current_window_index != -1:
                break
        
        if current_window_index != -1 and current_view_index != -1:
            # Set indices in scene context
            context.scene.view_3d_index = current_view_index
            message = f"Window {current_window_index}, View {current_view_index}"
        else:
            message = "No active 3D View."
        
        # Show message in console and dialog box
        self.report({'INFO'}, message)
        ShowMessageBox(message, title="Current View 3D ID", icon='INFO')
        return {'FINISHED'}

classes = (
    # View Identification
    KT_VIEW3D_OT_ShowViewID_GPU,
    KT_VIEW3D_OT_ShowViewID_GPU_Enhanced,
    KT_VIEW3D_OT_ClearViewID_GPU,
    KT_VIEW3D_OT_ShowViewID,  # Original popup-based operator
    )


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    remove_view_id_handlers()
    
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)