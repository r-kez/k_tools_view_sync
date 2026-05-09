import bpy
from bpy.props import BoolProperty
from bpy.types import Operator
import time

##
## start/stop syncing
##                
import bpy
from bpy.types import Operator

class KT_VIEW3D_OT_sync_views(Operator):
    bl_idname = "view3d.sync_views"
    bl_label = "Sync Views"
    bl_description = "Synchronize selected views"

    def execute(self, context):
        #print("Sync Views Operator Called")
        sync_views(context)
        return {'FINISHED'}

##
##
## Define what to sync based in the Sync Options Panel
def sync_views(context):
    scene = context.scene
    sync_options = scene.sync_options
    view3d_areas = [(window_index, area)
        for window_index, window in enumerate(bpy.context.window_manager.windows)
        for area in window.screen.areas if area.type == 'VIEW_3D']

    master_index = sync_options.master_view_index
    if master_index >= len(view3d_areas):
        return

    bpy.ops.view3d.update_view_count() # Force update view count, this will automatically sync the views as now the Booleans are defined as True since it's creation

    _, master_area = view3d_areas[master_index]
    master_space = master_area.spaces.active
    master_region = master_space.region_3d

    # Don't sync from a locked master view
    if master_region.lock_rotation:
        return

    for i, (_, area) in enumerate(view3d_areas):
        if i != master_index and getattr(scene, f"sync_view_{i}", False):
            space = area.spaces.active
            region = space.region_3d

            # Sync properties (even to locked views)
            if sync_options.sync_view_distance:
                region.view_distance = master_region.view_distance * sync_options.sync_view_distance_adjust
            
            if sync_options.sync_view_location:
                region.view_location = master_region.view_location
            
            if sync_options.sync_view_rotation:
                region.view_rotation = master_region.view_rotation
            
            if sync_options.sync_camera_zoom:
                region.view_camera_zoom = master_region.view_camera_zoom
            
            if sync_options.sync_camera_offset:
                region.view_camera_offset = master_region.view_camera_offset
            
            if sync_options.sync_view_perspective:
                region.view_perspective = master_region.view_perspective
            
            if sync_options.sync_clip_start:
                space.clip_start = master_space.clip_start
            
            if sync_options.sync_clip_end:
                space.clip_end = master_space.clip_end
            
            if sync_options.sync_focal_length:
                space.lens = master_space.lens


            # Force view update
            region.update()

##
## Manage Lights when Isolating Objects in all Views
##  
class KT_VIEW3D_OT_local_view_all_areas(Operator):
    bl_idname = "view3d.local_view_all_areas"
    bl_label = "Local View All Areas"
    bl_description = "Set Local View for all 3D Views (Keep lights visible if enabled in options)"

    def execute(self, context):
        selected_objects = context.selected_objects
        active_object = context.active_object
        sync_options = context.scene.sync_options

        # Select lights if option is enabled
        if sync_options.dont_exclude_lights:
            lights = [obj for obj in context.scene.objects 
                    if obj.type == 'LIGHT' and obj.visible_get()]
            for light in lights:
                light.select_set(True)

        # Apply local view to all 3D views
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    override = context.copy()
                    override['window'] = window
                    override['screen'] = window.screen
                    override['area'] = area
                    override['region'] = area.regions[-1]
                    
                    with context.temp_override(**override):
                        bpy.ops.view3d.localview()

        # Frame selected objects in each view
        bpy.ops.object.select_all(action='DESELECT')
        for obj in selected_objects:
            obj.select_set(True)

        # Frame selected in all views
        for window in bpy.context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    override = context.copy()
                    override['window'] = window
                    override['screen'] = window.screen
                    override['area'] = area
                    override['region'] = area.regions[-1]
                    
                    #with context.temp_override(**override):
                        #bpy.ops.view3d.view_selected()

        # Restore original selection
        if active_object:
            context.view_layer.objects.active = active_object

        return {'FINISHED'}

##
##
## Real-time Sync

last_interaction_time = 0
mouse_button_pressed = False
last_master_view_state = None

def real_time_sync_timer():
    global last_master_view_state
    context = bpy.context
    scene = context.scene
    sync_options = scene.sync_options

    if not scene.real_time_sync:
        last_master_view_state = None
        return None

    view3d_areas = [area for window in context.window_manager.windows 
                    for area in window.screen.areas if area.type == 'VIEW_3D']
    
    master_index = sync_options.master_view_index
    if master_index >= len(view3d_areas):
        return sync_options.sync_refresh_rate

    master_area = view3d_areas[master_index]
    master_space = master_area.spaces.active
    master_region = master_space.region_3d
    sync_options = scene.sync_options

    current_state = (
        master_region.view_location.copy() if sync_options.sync_view_location else -1,
        master_region.view_rotation.copy() if sync_options.sync_view_rotation else -1,
        master_region.view_distance if sync_options.sync_view_distance else -1,
        sync_options.sync_view_distance_adjust if sync_options.sync_view_distance else -1,

        master_region.view_camera_zoom if sync_options.sync_camera_zoom else -1,
        tuple(master_region.view_camera_offset) if sync_options.sync_camera_offset else -1,
        master_region.view_perspective if sync_options.sync_view_perspective else -1,
        
        master_space.clip_start if sync_options.sync_clip_start else -1,
        master_space.clip_end if sync_options.sync_clip_end else -1,
        master_space.lens if sync_options.sync_focal_length else -1,
    )

    if last_master_view_state != current_state:
        bpy.ops.view3d.sync_views()
        last_master_view_state = current_state

    return sync_options.sync_refresh_rate


def real_time_sync_update(self, context):
    if self.real_time_sync:
        if not bpy.app.timers.is_registered(real_time_sync_timer):
            bpy.app.timers.register(real_time_sync_timer)
            bpy.ops.view3d.real_time_sync_modal('INVOKE_DEFAULT')
    else:
        if bpy.app.timers.is_registered(real_time_sync_timer):
            bpy.app.timers.unregister(real_time_sync_timer)


class KT_VIEW3D_OT_real_time_sync_modal(bpy.types.Operator):
    bl_idname = "view3d.real_time_sync_modal"
    bl_label = "Real Time Sync Modal"
    
    def modal(self, context, event):
        global mouse_button_pressed
        
        real_time_sync_timer.release_time = time.time()

        return {'PASS_THROUGH'}
        
    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

##
##
## Update View Properties (View Couunt List)
def update_view_properties(self, context):
    # Get ALL views from ALL windows
    view3d_areas = [area for window in bpy.context.window_manager.windows 
                    for area in window.screen.areas if area.type == 'VIEW_3D']
    view3d_count = len(view3d_areas)

    # Clean up old properties
    for i in range(view3d_count, 20):  # Reasonable limit
        if hasattr(bpy.types.Scene, f"sync_view_{i}"):
            delattr(bpy.types.Scene, f"sync_view_{i}")
    
    # Create new properties for all views
    for i in range(view3d_count):
        if not hasattr(bpy.types.Scene, f"sync_view_{i}"):
            setattr(bpy.types.Scene, f"sync_view_{i}", BoolProperty(
                name=f"Sync View {i}",
                description=f"Synchronize View3D {i}",
                default=True
            ))

    # Update master view index limit
    scene = context.scene
    sync_options = scene.sync_options
    
    sync_options.master_view_index = min(sync_options.master_view_index, max(0, view3d_count - 1))

# Manually update the view count
class KT_VIEW3D_OT_update_view_count(Operator):
    bl_idname = "view3d.update_view_count"
    bl_label = "Update View List"
    bl_description = "Update the count of View3D areas and refresh boolean buttons"

    def execute(self, context):
        update_view_properties(self, context)
        
        # Force interface update
        for area in context.screen.areas:
            area.tag_redraw()
        return {'FINISHED'}

##
## Classes
##    
classes = (
    KT_VIEW3D_OT_sync_views,
    KT_VIEW3D_OT_local_view_all_areas,
    KT_VIEW3D_OT_update_view_count,
    KT_VIEW3D_OT_real_time_sync_modal,
    )