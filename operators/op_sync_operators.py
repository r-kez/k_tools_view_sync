import bpy
from bpy.props import BoolProperty, EnumProperty
from bpy.types import Operator
import time
from ..properties.properties import shading_preset_items

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
    
    # 3D views sync
    view3d_areas = [(window_index, area)
        for window_index, window in enumerate(bpy.context.window_manager.windows)
        for area in window.screen.areas if area.type == 'VIEW_3D']

    master_index = sync_options.master_view_index
    if master_index < len(view3d_areas):
        bpy.ops.view3d.update_view_count() # Force update view count

        _, master_area = view3d_areas[master_index]
        master_space = master_area.spaces.active
        master_region = master_space.region_3d

        # Don't sync from a locked master view
        if not master_region.lock_rotation:
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
                    area.tag_redraw()

    # 2D views sync
    if sync_options.sync_2d_editors:
        allowed_2d_types = {'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR'}
        view2d_areas = [area for window in context.window_manager.windows 
                        for area in window.screen.areas if area.type in allowed_2d_types]
        
        master_2d_index = sync_options.master_2d_view_index
        
        # Update show_locked_time dynamically based on sync_2d_horizontal
        for idx, area in enumerate(view2d_areas):
            space = area.spaces.active
            # Guard: not all 2D editor types expose show_locked_time
            if space and hasattr(space, 'show_locked_time'):
                is_sync_enabled = (idx == master_2d_index) or getattr(scene, f"sync_2d_view_{idx}", False)
                target_locked = bool(sync_options.sync_2d_horizontal and is_sync_enabled)
                if space.show_locked_time != target_locked:
                    space.show_locked_time = target_locked

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
        
        # Select lights if option is enabled in preferences
        from ..preferences import get_preferences
        prefs = get_preferences(context)
        dont_exclude = prefs.dont_exclude_lights

        if dont_exclude:
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
                    override['region'] = area.regions[-1]  # WINDOW region
                    
                    with context.temp_override(**override):
                        try:
                            bpy.ops.view3d.localview()
                        except Exception as e:
                            print(f"Error calling localview: {e}")

        # Restore original selection (exclude lights we temporarily selected)
        if dont_exclude:
            pass

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
last_all_view_states = {}

def get_3d_view_state(area, sync_options):
    """Helper to extract a comparable state tuple from a 3D view area"""
    try:
        space = area.spaces.active
        region = space.region_3d
        return (
            tuple(region.view_location) if sync_options.sync_view_location else -1,
            tuple(region.view_rotation) if sync_options.sync_view_rotation else -1,
            region.view_distance if sync_options.sync_view_distance else -1,
            sync_options.sync_view_distance_adjust if sync_options.sync_view_distance else -1,
            region.view_camera_zoom if sync_options.sync_camera_zoom else -1,
            tuple(region.view_camera_offset) if sync_options.sync_camera_offset else -1,
            region.view_perspective if sync_options.sync_view_perspective else -1,
            space.clip_start if sync_options.sync_clip_start else -1,
            space.clip_end if sync_options.sync_clip_end else -1,
            space.lens if sync_options.sync_focal_length else -1,
        )
    except Exception:
        return None

def real_time_sync_timer():
    global last_master_view_state, last_all_view_states
    context = bpy.context
    scene = context.scene
    if not scene or not hasattr(scene, "sync_options"):
        return 0.1
    sync_options = scene.sync_options

    if not getattr(scene, "real_time_sync", False) and not getattr(sync_options, "sync_2d_editors", False) and not getattr(sync_options, "keep_playhead_centered", False):
        last_master_view_state = None
        last_all_view_states.clear()
        return None

    # --- 3D viewports sync ---
    if getattr(scene, "real_time_sync", False):
        view3d_areas = [area for window in context.window_manager.windows 
                        for area in window.screen.areas if area.type == 'VIEW_3D']
        
        master_index = sync_options.master_view_index

        # Auto Master: automatically detect if the user navigated a non-master viewport
        if sync_options.auto_master and len(view3d_areas) > 1:
            for idx, area in enumerate(view3d_areas):
                ptr = area.as_pointer()
                curr_area_state = get_3d_view_state(area, sync_options)
                if curr_area_state is not None and ptr in last_all_view_states:
                    if last_all_view_states[ptr] != curr_area_state and idx != master_index:
                        # Non-master view was navigated, make it the new master
                        sync_options.master_view_index = idx
                        master_index = idx
                        area.tag_redraw()
                        break

        if master_index < len(view3d_areas):
            master_area = view3d_areas[master_index]
            current_state = get_3d_view_state(master_area, sync_options)

            if last_master_view_state != current_state:
                bpy.ops.view3d.sync_views()
                last_master_view_state = current_state

        # Cache states for all viewports for subsequent navigation detection
        for area in view3d_areas:
            state = get_3d_view_state(area, sync_options)
            if state is not None:
                last_all_view_states[area.as_pointer()] = state

    # --- 2D animation editors sync ---
    allowed_2d_types = {'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR'}
    
    # Get all 2D areas across all windows
    view2d_areas_all = []
    for window in context.window_manager.windows:
        for area in window.screen.areas:
            if area.type in allowed_2d_types:
                view2d_areas_all.append(area)
                
    if getattr(sync_options, "sync_2d_editors", False):
        master_2d_index = sync_options.master_2d_view_index
        
        # Update show_locked_time based on sync_2d_horizontal
        # Guard: not all 2D editor types expose show_locked_time
        for idx, area in enumerate(view2d_areas_all):
            space = area.spaces.active
            if space and hasattr(space, 'show_locked_time'):
                is_sync_enabled = (idx == master_2d_index) or getattr(scene, f"sync_2d_view_{idx}", False)
                target_locked = bool(sync_options.sync_2d_horizontal and is_sync_enabled)
                if space.show_locked_time != target_locked:
                    space.show_locked_time = target_locked
    else:
        # If disabled, ensure all show_locked_time are False
        for area in view2d_areas_all:
            space = area.spaces.active
            if space and hasattr(space, 'show_locked_time') and space.show_locked_time:
                space.show_locked_time = False

    # --- Keep playhead centered during playback ---
    if getattr(sync_options, "keep_playhead_centered", False) and getattr(context.screen, "is_animation_playing", False):
        for idx, area in enumerate(view2d_areas_all):
            is_enabled = True
            if getattr(sync_options, "sync_2d_editors", False):
                master_2d_index = getattr(sync_options, "master_2d_view_index", 0)
                is_enabled = (idx == master_2d_index) or getattr(scene, f"sync_2d_view_{idx}", False)
            
            if is_enabled:
                region = next((r for r in area.regions if r.type == 'WINDOW'), None)
                if region:
                    target_window = None
                    for window in context.window_manager.windows:
                        if any(a == area for a in window.screen.areas):
                            target_window = window
                            break
                    if target_window:
                        override = context.copy()
                        override['window'] = target_window
                        override['screen'] = target_window.screen
                        override['area'] = area
                        override['region'] = region
                        with context.temp_override(**override):
                            try:
                                bpy.ops.anim.view_frame()
                            except Exception as e:
                                pass

    return sync_options.sync_refresh_rate


def real_time_sync_update(self, context):
    scene = context.scene if context else bpy.context.scene
    if not scene or not hasattr(scene, "sync_options"):
        return
        
    sync_options = scene.sync_options
    should_run = getattr(scene, "real_time_sync", False) or getattr(sync_options, "sync_2d_editors", False) or getattr(sync_options, "keep_playhead_centered", False)

    if should_run:
        if not bpy.app.timers.is_registered(real_time_sync_timer):
            bpy.app.timers.register(real_time_sync_timer)
    else:
        if bpy.app.timers.is_registered(real_time_sync_timer):
            bpy.app.timers.unregister(real_time_sync_timer)

    # Clean up all 2D locked time if 2D sync is disabled/off
    if not getattr(sync_options, "sync_2d_editors", False) or not should_run:
        allowed_2d_types = {'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR'}
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type in allowed_2d_types:
                    space = area.spaces.active
                    if space and hasattr(space, 'show_locked_time') and space.show_locked_time:
                        try:
                            space.show_locked_time = False
                        except:
                            pass


class KT_VIEW3D_OT_real_time_sync_modal(bpy.types.Operator):
    """Deprecated: Real-time sync is handled safely via bpy.app.timers without blocking Blender's autosave"""
    bl_idname = "view3d.real_time_sync_modal"
    bl_label = "Real Time Sync Modal"
    
    def execute(self, context):
        return {'FINISHED'}

##
##
# Storage for original viewport states before applying presets
viewport_states = {}

def capture_viewport_state(space):
    shading = space.shading
    overlay = space.overlay
    
    state = {
        'shading': {
            'type': shading.type,
            'light': shading.light,
            'color_type': shading.color_type,
            'background_type': shading.background_type,
            'background_color': tuple(shading.background_color),
            'show_xray': shading.show_xray,
            'xray_alpha': shading.xray_alpha,
            'show_object_outline': shading.show_object_outline,
            'studio_light': shading.studio_light,
            'single_color': tuple(shading.single_color),
            'show_cavity': shading.show_cavity,
            'cavity_type': shading.cavity_type,
            'cavity_ridge_factor': shading.cavity_ridge_factor,
            'cavity_valley_factor': shading.cavity_valley_factor,
        },
        'overlay': {
            'show_overlays': overlay.show_overlays,
            'show_wireframes': overlay.show_wireframes,
            'wireframe_threshold': overlay.wireframe_threshold,
            'show_face_orientation': overlay.show_face_orientation,
            'show_stats': overlay.show_stats,
            'show_cursor': overlay.show_cursor,
        },
        'space': {
            'show_gizmo': space.show_gizmo,
            'show_region_header': space.show_region_header,
        }
    }
    return state

def restore_viewport_state(space, state):
    shading = space.shading
    overlay = space.overlay
    
    # Shading
    s_state = state['shading']
    shading.type = s_state['type']
    shading.light = s_state['light']
    shading.color_type = s_state['color_type']
    shading.background_type = s_state['background_type']
    shading.background_color = s_state['background_color']
    shading.show_xray = s_state['show_xray']
    shading.xray_alpha = s_state['xray_alpha']
    shading.show_object_outline = s_state['show_object_outline']
    shading.studio_light = s_state['studio_light']
    shading.single_color = s_state['single_color']
    shading.show_cavity = s_state['show_cavity']
    shading.cavity_type = s_state['cavity_type']
    shading.cavity_ridge_factor = s_state['cavity_ridge_factor']
    shading.cavity_valley_factor = s_state['cavity_valley_factor']
    
    # Overlay
    o_state = state['overlay']
    overlay.show_overlays = o_state['show_overlays']
    overlay.show_wireframes = o_state['show_wireframes']
    overlay.wireframe_threshold = o_state['wireframe_threshold']
    overlay.show_face_orientation = o_state['show_face_orientation']
    overlay.show_stats = o_state['show_stats']
    overlay.show_cursor = o_state['show_cursor']
    
    # Space
    space.show_gizmo = state['space']['show_gizmo']
    space.show_region_header = state['space']['show_region_header']

def set_viewport_clean_state(space, keep_wireframe=False, keep_normals=False):
    """Utility to turn off most overlays and gizmos for a clean look"""
    overlay = space.overlay
    
    # Always turn off gizmos and header in presets unless it's 'NONE'
    space.show_gizmo = False
    space.show_region_header = False
    
    # If we don't need any specific overlay, just turn off the master switch
    if not keep_wireframe and not keep_normals:
        overlay.show_overlays = False
        return

    # If we need specific overlays, we must keep the master switch ON
    # but we disable all the other distracting sub-overlays
    overlay.show_overlays = True
    
    # Shading/Topology related
    overlay.show_wireframes = keep_wireframe
    overlay.show_face_orientation = keep_normals
    
    # Distractions to hide
    overlay.show_cursor = False
    overlay.show_floor = False
    overlay.show_axis_x = False
    overlay.show_axis_y = False
    overlay.show_axis_z = False
    overlay.show_text = False
    overlay.show_stats = False
    overlay.show_extras = False
    overlay.show_relationship_lines = False
    overlay.show_object_origins = False
    overlay.show_outline_selected = False
    overlay.show_bones = False
    overlay.show_annotation = False

## Update View Properties (View Couunt List)
def apply_shading_preset(context, view_index, preset_type):
    view3d_areas = [area for window in context.window_manager.windows 
                    for area in window.screen.areas if area.type == 'VIEW_3D']
    
    if view_index >= len(view3d_areas):
        return

    area = view3d_areas[view_index]
    space = area.spaces.active
    if not space or space.type != 'VIEW_3D':
        return
        
    shading = space.shading
    overlay = space.overlay

    # Capture state if not already stored
    if preset_type != 'NONE':
        if view_index not in viewport_states:
            viewport_states[view_index] = capture_viewport_state(space)
        else:
            # If we already have a saved state, restore it first 
            # so the new preset starts from the clean original state
            restore_viewport_state(space, viewport_states[view_index])

    if preset_type == 'SILHOUETTE':
        shading.type = 'SOLID'
        shading.light = 'FLAT'
        shading.color_type = 'OBJECT'
        shading.background_type = 'VIEWPORT'
        shading.background_color = (0, 0, 0)
        set_viewport_clean_state(space)
    elif preset_type == 'SILHOUETTE_INV':
        shading.type = 'SOLID'
        shading.light = 'FLAT'
        shading.color_type = 'SINGLE'
        shading.single_color = (0, 0, 0)
        shading.background_type = 'VIEWPORT'
        shading.background_color = (1, 1, 1)
        set_viewport_clean_state(space)
    elif preset_type == 'TOPOLOGY':
        shading.type = 'SOLID'
        shading.light = 'STUDIO'
        set_viewport_clean_state(space, keep_wireframe=True)
        overlay.wireframe_threshold = 1.0
    elif preset_type == 'NORMALS':
        shading.type = 'SOLID'
        shading.light = 'MATCAP'
        shading.studio_light = 'check_normal+y.exr'
        set_viewport_clean_state(space, keep_normals=True)
    elif preset_type == 'HARD_SURFACE':
        shading.type = 'SOLID'
        shading.light = 'MATCAP'
        shading.studio_light = 'hard_surface_red.exr'
        set_viewport_clean_state(space)
    elif preset_type == 'REFL_H':
        shading.type = 'SOLID'
        shading.light = 'MATCAP'
        shading.studio_light = 'check_reflection_horizontal.exr'
        set_viewport_clean_state(space)
    elif preset_type == 'REFL_V':
        shading.type = 'SOLID'
        shading.light = 'MATCAP'
        shading.studio_light = 'check_reflection_vertical.exr'
        set_viewport_clean_state(space)
    elif preset_type == 'TOON_DARK':
        shading.type = 'SOLID'
        shading.light = 'MATCAP'
        shading.studio_light = 'toon_dark.exr'
        set_viewport_clean_state(space)
    elif preset_type == 'TOON_LIGHT':
        shading.type = 'SOLID'
        shading.light = 'MATCAP'
        shading.studio_light = 'toon_light.exr'
        set_viewport_clean_state(space)
    elif preset_type == 'HIGH_DETAIL':
        shading.type = 'SOLID'
        shading.light = 'MATCAP'
        shading.studio_light = 'clay_brown.exr'
        shading.show_cavity = True
        shading.cavity_type = 'BOTH'
        shading.cavity_ridge_factor = 2.0
        shading.cavity_valley_factor = 2.0
        shading.show_object_outline = True
        set_viewport_clean_state(space)
    elif preset_type == 'XRAY':
        shading.type = 'SOLID'
        shading.show_xray = True
        shading.xray_alpha = 0.5
        set_viewport_clean_state(space)
    elif preset_type == 'RANDOM':
        shading.type = 'SOLID'
        shading.color_type = 'RANDOM'
        set_viewport_clean_state(space)
    elif preset_type == 'CLEAN':
        set_viewport_clean_state(space)
    elif preset_type == 'NONE':
        # Restore original state if it exists
        if view_index in viewport_states:
            restore_viewport_state(space, viewport_states[view_index])
            del viewport_states[view_index]
        else:
            # Fallback if no state was stored
            shading.type = 'SOLID'
            shading.light = 'STUDIO'
            shading.color_type = 'MATERIAL'
            shading.background_type = 'THEME'
            shading.show_xray = False
            overlay.show_overlays = True
            overlay.show_wireframes = False
            overlay.show_face_orientation = False
            space.show_gizmo = True
    
    area.tag_redraw()

def update_view_preset(self, context):
    # Find which view triggered the change (or just apply to all for simplicity)
    view3d_areas = [area for window in context.window_manager.windows 
                    for area in window.screen.areas if area.type == 'VIEW_3D']
    
    for i in range(len(view3d_areas)):
        prop_name = f"sync_view_preset_{i}"
        if hasattr(self, prop_name):
            preset_type = getattr(self, prop_name)
            apply_shading_preset(context, i, preset_type)

## Update View Properties (View Couunt List)
last_view_count = -1
last_view2d_count = -1
last_panel_draw_time = 0.0

def mark_panel_as_visible():
    """Call this from panel draw to signal the timer that it's active"""
    global last_panel_draw_time
    last_panel_draw_time = time.time()

def update_view_properties(self, context):
    global last_view_count, last_view2d_count
    
    # Get ALL views from ALL windows
    view3d_areas = [area for window in bpy.context.window_manager.windows 
                    for area in window.screen.areas if area.type == 'VIEW_3D']
    view3d_count = len(view3d_areas)

    allowed_2d_types = {'DOPESHEET_EDITOR', 'GRAPH_EDITOR', 'NLA_EDITOR'}
    view2d_areas = [area for window in bpy.context.window_manager.windows 
                    for area in window.screen.areas if area.type in allowed_2d_types]
    view2d_count = len(view2d_areas)

    # Only update if the count has changed
    if view3d_count == last_view_count and view2d_count == last_view2d_count:
        return
    
    last_view_count = view3d_count
    last_view2d_count = view2d_count

    # Clean up old properties
    for i in range(view3d_count, 20):  # Reasonable limit
        if hasattr(bpy.types.Scene, f"sync_view_{i}"):
            delattr(bpy.types.Scene, f"sync_view_{i}")
            
    for i in range(view2d_count, 20):  # Reasonable limit
        if hasattr(bpy.types.Scene, f"sync_2d_view_{i}"):
            delattr(bpy.types.Scene, f"sync_2d_view_{i}")
    
    # Create new properties for all views
    for i in range(view3d_count):
        if not hasattr(bpy.types.Scene, f"sync_view_{i}"):
            setattr(bpy.types.Scene, f"sync_view_{i}", BoolProperty(
                name=f"Sync View {i}",
                description=f"Synchronize View3D {i}",
                default=True
            ))
        
        # Preset Property
        if not hasattr(bpy.types.Scene, f"sync_view_preset_{i}"):
            setattr(bpy.types.Scene, f"sync_view_preset_{i}", EnumProperty(
                name=f"Preset View {i}",
                description=f"Shading Preset for View3D {i}",
                items=shading_preset_items,
                default='NONE',
                update=update_view_preset
            ))

    for i in range(view2d_count):
        if not hasattr(bpy.types.Scene, f"sync_2d_view_{i}"):
            setattr(bpy.types.Scene, f"sync_2d_view_{i}", BoolProperty(
                name=f"Sync 2D View {i}",
                description=f"Synchronize 2D View {i}",
                default=True
            ))

    # Update master view index limit
    scene = context.scene
    sync_options = scene.sync_options
    
    sync_options.master_view_index = min(sync_options.master_view_index, max(0, view3d_count - 1))
    sync_options.master_2d_view_index = min(sync_options.master_2d_view_index, max(0, view2d_count - 1))

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