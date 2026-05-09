import bpy
from bpy.types import GizmoGroup, Operator
from bpy.props import EnumProperty, IntProperty



# **********************************************
class KT_LockRotationProps(bpy.types.PropertyGroup):
    lock_rotation: bpy.props.BoolProperty(
        name="Lock Rotation", 
        default=False, 
        update=lambda self, 
        context: update_lock_rotation(self, context)
        ) # type: ignore

def set_lock_rotation(area, value):
    if area.type == 'VIEW_3D':
        region_3d = area.spaces.active.region_3d
        region_3d.lock_rotation = value

def update_lock_rotation(self, context):
    wm = context.window_manager
    window = wm.windows[self.window_index]
    area = [a for a in window.screen.areas if a.type == 'VIEW_3D'][self.local_view_index]
    set_lock_rotation(area, self.lock_rotation)
    
    # Start modal operator when view is locked
    if self.lock_rotation:
        bpy.ops.view3d.locked_view_modal('INVOKE_DEFAULT')


# **********************************************
class KT_CameraViewToggleGizmo(GizmoGroup):
    bl_idname = "VIEW3D_GGT_camera_view_toggle"
    bl_label = "Camera View Toggle Button"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'WINDOW'
    bl_options = {'PERSISTENT', 'SCALE'}

    @classmethod
    def poll(cls, context):
        if context.area.type == 'VIEW_3D':
            region_3d = context.space_data.region_3d
            if region_3d.lock_rotation and context.window_manager.show_gizmo_special:
                if not context.space_data.show_gizmo:
                    context.space_data.show_gizmo = True 
                return True
        return False

    def draw_prepare(self, context):
            scene = context.scene
            props = scene.sync_options
            
            # Cores para feedback visual
            active_color = (0.3, 0.8, 1.0)
            active_alpha = 0.8
            inactive_color = (0.078, 0.15, 0.23)
            inactive_alpha = 0.8
            
            # Lógica para feedback visual (Apenas Cor e Alfa)
            if self.camera_gizmo:
                if context.space_data.region_3d.view_perspective == 'CAMERA':
                    self.camera_gizmo.color = active_color
                    self.camera_gizmo.alpha = active_alpha
                else:
                    self.camera_gizmo.color = inactive_color
                    self.camera_gizmo.alpha = inactive_alpha

            if self.camera_pan_toggle:
                if props.enable_camera_pan:
                    self.camera_pan_toggle.color = active_color
                    self.camera_pan_toggle.alpha = active_alpha
                else:
                    self.camera_pan_toggle.color = inactive_color
                    self.camera_pan_toggle.alpha = inactive_alpha

            if self.lock_pan_toggle:
                if props.enable_pan_on_lock:
                    self.lock_pan_toggle.color = active_color
                    self.lock_pan_toggle.alpha = active_alpha
                else:
                    self.lock_pan_toggle.color = inactive_color
                    self.lock_pan_toggle.alpha = inactive_alpha
            
            # Lógica de posicionamento (inalterada)
            if self.move_gizmo and self.zoom_gizmo and self.camera_pan_toggle and self.lock_pan_toggle:
                region = context.region
                margin = 35
                spacing = 30
                bottom_margin = 30
                num_camera_buttons = 5
                
                shading_group_start = margin
                self.solid_gizmo.matrix_basis[0][3] = shading_group_start
                self.solid_gizmo.matrix_basis[1][3] = bottom_margin
                self.material_gizmo.matrix_basis[0][3] = shading_group_start + spacing
                self.material_gizmo.matrix_basis[1][3] = bottom_margin
                self.render_gizmo.matrix_basis[0][3] = shading_group_start + (spacing * 2)
                self.render_gizmo.matrix_basis[1][3] = bottom_margin
                self.shading_gizmo.matrix_basis[0][3] = shading_group_start + (spacing * 3)
                self.shading_gizmo.matrix_basis[1][3] = bottom_margin

                camera_group_width = (num_camera_buttons - 1) * spacing
                camera_group_start = (region.width / 2) - (camera_group_width / 2)

                self.camera_gizmo.matrix_basis[0][3] = camera_group_start
                self.camera_gizmo.matrix_basis[1][3] = bottom_margin
                self.move_gizmo.matrix_basis[0][3] = camera_group_start + spacing
                self.move_gizmo.matrix_basis[1][3] = bottom_margin
                self.zoom_gizmo.matrix_basis[0][3] = camera_group_start + (spacing * 2)
                self.zoom_gizmo.matrix_basis[1][3] = bottom_margin
                self.camera_pan_toggle.matrix_basis[0][3] = camera_group_start + (spacing * 3)
                self.camera_pan_toggle.matrix_basis[1][3] = bottom_margin
                self.lock_pan_toggle.matrix_basis[0][3] = camera_group_start + (spacing * 4)
                self.lock_pan_toggle.matrix_basis[1][3] = bottom_margin

    def setup(self, context):
        # Common gizmo properties
        def setup_gizmo(gizmo, icon):
            gizmo.draw_options = {'BACKDROP', 'OUTLINE'}
            gizmo.color = 0.078, 0.15, 0.23
            gizmo.alpha = 0.8
            gizmo.color_highlight = 0.3, 0.8, 1.0
            gizmo.alpha_highlight = 0.5
            gizmo.scale_basis = 12  # Slightly larger buttons
            gizmo.icon = icon

        # Shading group
        self.solid_gizmo = self.gizmos.new("GIZMO_GT_button_2d")
        setup_gizmo(self.solid_gizmo, 'SHADING_SOLID')
        self.solid_gizmo.target_set_operator("view3d.toggle_solid_shading_view")

        self.material_gizmo = self.gizmos.new("GIZMO_GT_button_2d")
        setup_gizmo(self.material_gizmo, 'MATERIAL')
        self.material_gizmo.target_set_operator("view3d.toggle_material_shading_view")

        self.render_gizmo = self.gizmos.new("GIZMO_GT_button_2d")
        setup_gizmo(self.render_gizmo, 'SHADING_RENDERED')
        self.render_gizmo.target_set_operator("view3d.toggle_render_shading_view")

        self.shading_gizmo = self.gizmos.new("GIZMO_GT_button_2d")
        setup_gizmo(self.shading_gizmo, 'MENU_PANEL')
        self.shading_gizmo.target_set_operator("view3d.call_shading_popover")

        # Camera controls group
        self.camera_gizmo = self.gizmos.new("GIZMO_GT_button_2d")
        setup_gizmo(self.camera_gizmo, 'CAMERA_DATA')
        self.camera_gizmo.target_set_operator("view3d.kt_toggle_camera_view")

        self.move_gizmo = self.gizmos.new("GIZMO_GT_button_2d")
        setup_gizmo(self.move_gizmo, 'VIEW_PAN')
        self.move_gizmo.target_set_operator("view3d.move")

        self.zoom_gizmo = self.gizmos.new("GIZMO_GT_button_2d")
        setup_gizmo(self.zoom_gizmo, 'ZOOM_IN')
        self.zoom_gizmo.target_set_operator("view3d.zoom")

        self.camera_pan_toggle = self.gizmos.new("GIZMO_GT_button_2d")
        setup_gizmo(self.camera_pan_toggle, 'CON_CAMERASOLVER')
        self.camera_pan_toggle.target_set_operator("view3d.toggle_camera_pan")

        self.lock_pan_toggle = self.gizmos.new("GIZMO_GT_button_2d")
        setup_gizmo(self.lock_pan_toggle, 'MOUSE_MOVE')
        self.lock_pan_toggle.target_set_operator("view3d.toggle_pan_on_lock")


# Function to disable or enable gizmos and overlays based on the boolean value
# **********************************************
def update_disable_gizmos(self, context):
    wm = context.window_manager
    for window in wm.windows:
        for area in window.screen.areas:
            if area.type == 'VIEW_3D':
                region_3d = area.spaces.active.region_3d
                # Check if lock_rotation is active
                if region_3d.lock_rotation:
                    # Disable or enable gizmos based on the value of 'disable_gizmos'
                    area.spaces.active.show_gizmo_navigate = not self.disable_gizmos
                    area.spaces.active.show_gizmo_tool = not self.disable_gizmos
                    area.spaces.active.show_gizmo_context = not self.disable_gizmos
                    area.spaces.active.show_gizmo_empty_image = not self.disable_gizmos
                    area.spaces.active.show_gizmo_empty_force_field = not self.disable_gizmos
                    area.spaces.active.show_gizmo_light_size = not self.disable_gizmos
                    area.spaces.active.show_gizmo_light_look_at = not self.disable_gizmos
                    area.spaces.active.show_gizmo_camera_lens = not self.disable_gizmos
                    area.spaces.active.show_gizmo_camera_dof_distance = not self.disable_gizmos

                    area.spaces.active.overlay.show_overlays = not self.disable_gizmos

                    area.spaces.active.show_region_header = not self.disable_gizmos



# **********************************************
class KT_VIEW3D_OT_toggle_gizmos(bpy.types.Operator):
    '''Disable/Enable some predefined items from the viewport that have Lock Rotation enabled'''
    bl_idname = "view3d.toggle_gizmos"
    bl_label = "Toggle Gizmos and Overlays"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        wm = context.window_manager
        gizmos_active = False
        
        for window in wm.windows:
            for area in window.screen.areas:

                if area.type == 'VIEW_3D':
                    region_3d = area.spaces.active.region_3d

                    if region_3d.lock_rotation:

                        gizmos_active = area.spaces.active.show_gizmo_navigate
                        
                        area.spaces.active.show_gizmo_navigate = not gizmos_active
                        area.spaces.active.show_gizmo_tool = not gizmos_active
                        area.spaces.active.show_gizmo_context = not gizmos_active
                        area.spaces.active.show_gizmo_empty_image = not gizmos_active
                        area.spaces.active.show_gizmo_empty_force_field = not gizmos_active
                        area.spaces.active.show_gizmo_light_size = not gizmos_active
                        area.spaces.active.show_gizmo_light_look_at = not gizmos_active
                        area.spaces.active.show_gizmo_camera_lens = not gizmos_active
                        area.spaces.active.show_gizmo_camera_dof_distance = not gizmos_active

                        area.spaces.active.overlay.show_overlays = not gizmos_active
                        
                        area.spaces.active.show_region_header = not gizmos_active
                        
                        # Hide the N-Panel
                        area.spaces.active.show_region_ui = False
                        # Hide T-Panel
                        #area.spaces.active.show_region_tool_header = False
        
        return {'FINISHED'}



### GIZMO CALL OPERATORS
# **********************************************
class KT_VIEW3D_OT_toggle_camera_view(Operator):
    """Switch between camera view and perspective view"""
    bl_idname = "view3d.kt_toggle_camera_view"
    bl_label = "Toggle Camera View"
    
    def execute(self, context):
        area = context.area
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            if space.type == 'VIEW_3D':
                space.region_3d.view_perspective = 'CAMERA' if space.region_3d.view_perspective != 'CAMERA' else 'PERSP'

        return {'FINISHED'}



# **********************************************
class KT_VIEW3D_OT_toggle_solid_shading_view(Operator):
    """Toggle to Solid Shading."""
    bl_idname = "view3d.toggle_solid_shading_view"
    bl_label = "Toggle Solid Shading"

    def execute(self, context):
        area = context.area
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            if space.type == 'VIEW_3D':
                # Switches between Solid and Material
                shading = space.shading
                if shading.type == 'SOLID':
                    shading.type = 'SOLID'  # Switch to Solid if in another mode
                else:
                    shading.type = 'SOLID'  # Switch to Solid if in another mode
        return {'FINISHED'}



# **********************************************
class KT_VIEW3D_OT_toggle_material_shading_view(Operator):
    """Toggles between Material and Solid Shading."""
    bl_idname = "view3d.toggle_material_shading_view"
    bl_label = "Toggle Material Shading"

    def execute(self, context):
        area = context.area
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            if space.type == 'VIEW_3D':
                # Switches between Material and Solid
                shading = space.shading
                if shading.type == 'MATERIAL':
                    shading.type = 'SOLID'  # Switch to Solid if in Material
                else:
                    shading.type = 'MATERIAL'  # Switch to Material if in another mode
        return {'FINISHED'}



# **********************************************  
class KT_VIEW3D_OT_toggle_render_shading_view(Operator):
    """Toggles between Rendered and Solid Shading."""
    bl_idname = "view3d.toggle_render_shading_view"
    bl_label = "Toggle Render Shading"

    def execute(self, context):
        area = context.area
        if area.type == 'VIEW_3D':
            space = area.spaces.active
            if space.type == 'VIEW_3D':
                # Toggles between Rendered and previous mode
                shading = space.shading
                if shading.type == 'RENDERED':
                    shading.type = 'SOLID'  # Switch to Solid if in Rendered
                else:
                    shading.type = 'RENDERED'  # Switch to Rendered if in another mode
        return {'FINISHED'}



# **********************************************
class KT_VIEW3D_OT_call_shading_popover(bpy.types.Operator):
    ''' Shading Menu '''
    bl_idname = "view3d.call_shading_popover"
    bl_label = "Call Shading Popover"
    
    _timer = None
    _duration = 1.0  # Increased base duration
    _mouse_moved = False
    _initial_mouse = None

    def modal(self, context, event):
        # If mouse moves, keep the popover open
        if event.type == 'MOUSEMOVE':
            if not self._mouse_moved:
                self._initial_mouse = (event.mouse_x, event.mouse_y)
                self._mouse_moved = True
            # Keep popover open while mouse is moving
            return {'RUNNING_MODAL'}

        # Close on ESC or left click
        if event.type in {'ESC', 'LEFTMOUSE'}:
            return self.finish(context)
        
        return {'RUNNING_MODAL'}

    def invoke(self, context, event):
        # Call the popover panel
        bpy.ops.wm.call_panel(name="VIEW3D_PT_shading")
        # Add a modal handler
        context.window_manager.modal_handler_add(self)
        # Start a timer
        self._timer = context.window_manager.event_timer_add(self._duration, window=context.window)

        return {'RUNNING_MODAL'}

    def finish(self, context):
        if self._timer:
            context.window_manager.event_timer_remove(self._timer)
            self._timer = None

        context.area.tag_redraw()
        return {'CANCELLED'}


class KT_VIEW3D_OT_force_update(bpy.types.Operator):
    bl_idname = "view3d.force_lock_update"
    bl_label = "Force Update"
    bl_description = "Force update of the 3D Views list"

    def execute(self, context):
        wm = context.window_manager
        wm.view_sync_data.clear()
        
        global_view_index = 0

        for window_idx, window in enumerate(wm.windows):
            for area_idx, area in enumerate([a for a in window.screen.areas if a.type == 'VIEW_3D']):
                item = wm.view_sync_data.add()
                item.window_index = window_idx
                item.local_view_index = area_idx  # Local index for window
                item.global_view_index = global_view_index  # Global sequential numbering
                item.lock_rotation = area.spaces.active.region_3d.lock_rotation
                global_view_index += 1  # Increases the global index
        
        return {'FINISHED'}

# **********************************************
class KT_VIEW3D_OT_toggle_camera_pan(Operator):
    """Toggles the 'Enable Camera Pan' property"""
    bl_idname = "view3d.toggle_camera_pan"
    bl_label = "Toggle Camera Pan"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.sync_options

        props.enable_camera_pan = not props.enable_camera_pan
        
        # ADICIONADO: Força a atualização de todas as áreas para refletir a mudança
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()
                
        return {'FINISHED'}

# **********************************************
class KT_VIEW3D_OT_toggle_pan_on_lock(Operator):
    """Toggles the 'Enable Pan on Lock' property"""
    bl_idname = "view3d.toggle_pan_on_lock"
    bl_label = "Toggle Pan on Lock"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        props = scene.sync_options

        props.enable_pan_on_lock = not props.enable_pan_on_lock
        
        # ADICIONADO: Força a atualização de todas as áreas para refletir a mudança
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()
                
        return {'FINISHED'}

##
##
## Presets
class KT_VIEW3D_MT_lock_view_presets(bpy.types.Menu):
    """Pre-Defined presets for locking views in:
    Top, Bottom, Left, Right, Front, Back, Camera, and the Matching View from the Master View"""
    bl_label = "Lock View Presets"
    bl_description = "Pre-Defined presets for locking views in: Top, Bottom, Left, Right, Front, Back, Camera, and the Matching View from the Master View"

    def draw(self, context):
        layout = self.layout
        layout.operator_enum("view3d.lock_view_preset", "preset")

class KT_VIEW3D_OT_lock_view_preset(Operator):
    bl_idname = "view3d.lock_view_preset"
    bl_label = "Lock View Preset"
    
    preset: EnumProperty(
        items=[
            ('TOP', "Top", "Lock view from top", 'VIEW_TOP', 0),
            ('BOTTOM', "Bottom", "Lock view from bottom", 'VIEW_BOTTOM', 1),
            ('FRONT', "Front", "Lock view from front", 'VIEW_FRONT', 2),
            ('BACK', "Back", "Lock view from back", 'VIEW_BACK', 3),
            ('RIGHT', "Right", "Lock view from right", 'VIEW_RIGHT', 4),
            ('LEFT', "Left", "Lock view from left", 'VIEW_LEFT', 5),
            ('CAMERA', "Camera", "Lock to active camera", 'VIEW_CAMERA', 6),
            ('MATCH', "Match Master", "Match master view and lock", 'UV_SYNC_SELECT', 7)
        ],
        default='TOP'
    ) # type: ignore 
    view_index: IntProperty(default=0) # type: ignore
    window_index: IntProperty(default=0) # type: ignore

    def execute(self, context):
        scene = context.scene
        
        # Find target view using global index
        target_area = None
        global_index = 0
        
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                if area.type == 'VIEW_3D':
                    if global_index == self.view_index:
                        target_area = area
                        break
                    global_index += 1

        if not target_area:
            return {'CANCELLED'}

        region_3d = target_area.spaces.active.region_3d
        space_data = target_area.spaces.active

        if self.preset == 'MATCH':
            # Store current sync states
            sync_states = {}
            for i in range(20):  # Reasonable limit
                if hasattr(scene, f"sync_view_{i}"):
                    sync_states[i] = getattr(scene, f"sync_view_{i}")
                    setattr(scene, f"sync_view_{i}", False)  # Disable all views
            
            # Enable only the target view
            if hasattr(scene, f"sync_view_{self.view_index}"):
                setattr(scene, f"sync_view_{self.view_index}", True)
            
            # Call sync views operator
            bpy.ops.view3d.sync_views()
            
            # Restore original sync states
            for i, state in sync_states.items():
                if hasattr(scene, f"sync_view_{i}"):
                    setattr(scene, f"sync_view_{i}", state)
            
            # Lock the view after sync
            region_3d.lock_rotation = True
            
        elif self.preset == 'CAMERA':
            if context.scene.camera:
                region_3d.lock_rotation = True
                space_data.region_3d.view_perspective = 'CAMERA'
                
        else:
            # Standard view presets
            region_3d.lock_rotation = True
            region_3d.view_perspective = 'ORTHO'
            
            if self.preset == 'TOP':  # Num 7
                region_3d.view_rotation = (1, 0, 0, 0)  # View: Top to Bottom
            elif self.preset == 'BOTTOM':  # Ctrl + Num 7
                region_3d.view_rotation = (0, 1, 0, 0)  # View: Bottom to Top
            elif self.preset == 'FRONT':  # Num 1
                region_3d.view_rotation = (0.7071, 0.7071, 0, 0)  # View: Front to Back
            elif self.preset == 'BACK':  # Ctrl + Num 1
                region_3d.view_rotation = (0.0000, -0.0000, 0.7071, 0.7071)  # View: Back to Front
            elif self.preset == 'RIGHT':  # Num 3
                region_3d.view_rotation = (0.5000, 0.5000, 0.5000, 0.5000)  # View: Right to Left
            elif self.preset == 'LEFT':  # Ctrl + Num 3
                region_3d.view_rotation = (0.5000, 0.5000, -0.5000, -0.5000)  # View: Left to Right

        return {'FINISHED'}

# Pan when in Camera Mode Or Locked Views
class KT_VIEW3D_OT_camera_pan(Operator):
    """Pan when in camera view, rotate otherwise"""
    bl_idname = "view3d.camera_pan"
    bl_label = "Camera Pan"
    
    def invoke(self, context, event):
        # Check if we are in camera view
        if context.region_data.view_perspective == 'CAMERA':
            # If in camera view, do pan
            bpy.ops.view3d.move('INVOKE_DEFAULT')
        else:
            # If not in camera view, do normal rotation
            bpy.ops.view3d.rotate('INVOKE_DEFAULT')
        
        return {'FINISHED'}

class KT_VIEW3D_OT_lock_pan(Operator):
    """Pan when rotation is locked, rotate otherwise"""
    bl_idname = "view3d.lock_pan"
    bl_label = "Lock Pan"
    
    def invoke(self, context, event):
        # Check if rotation is locked
        if hasattr(context.region_data, 'lock_rotation') and context.region_data.lock_rotation:
            # If rotation is locked, do pan
            bpy.ops.view3d.move('INVOKE_DEFAULT')
        else:
            # If rotation not locked, do normal rotation
            bpy.ops.view3d.rotate('INVOKE_DEFAULT')
        
        return {'FINISHED'}

class KT_VIEW3D_OT_smart_pan(Operator):
    """Smart pan that combines camera pan and lock pan behaviors"""
    bl_idname = "view3d.smart_pan"
    bl_label = "Smart Pan"
    
    def invoke(self, context, event):
        scene = context.scene
        props = scene.sync_options
        
        # Priority 1: Check if rotation is locked and lock pan is enabled
        if (hasattr(context.region_data, 'lock_rotation') and 
            context.region_data.lock_rotation and 
            props.enable_pan_on_lock):
            bpy.ops.view3d.move('INVOKE_DEFAULT')
            return {'FINISHED'}
        
        # Priority 2: Check if in camera view and camera pan is enabled
        if (context.region_data.view_perspective == 'CAMERA' and 
            props.enable_camera_pan):
            bpy.ops.view3d.move('INVOKE_DEFAULT')
            return {'FINISHED'}
        
        # Default: Normal rotation (if not locked)
        if not (hasattr(context.region_data, 'lock_rotation') and context.region_data.lock_rotation):
            bpy.ops.view3d.rotate('INVOKE_DEFAULT')
        
        return {'FINISHED'}
##
##

classes = ( 
            KT_CameraViewToggleGizmo,
            KT_LockRotationProps,
            KT_VIEW3D_OT_toggle_camera_view,
            KT_VIEW3D_OT_toggle_solid_shading_view,
            KT_VIEW3D_OT_toggle_material_shading_view,
            KT_VIEW3D_OT_toggle_render_shading_view,
            KT_VIEW3D_OT_force_update,
            KT_VIEW3D_OT_call_shading_popover,
            KT_VIEW3D_OT_toggle_gizmos, 
            KT_VIEW3D_MT_lock_view_presets,
            KT_VIEW3D_OT_lock_view_preset,   
            KT_VIEW3D_OT_camera_pan,    
            KT_VIEW3D_OT_lock_pan,
            KT_VIEW3D_OT_smart_pan,
            KT_VIEW3D_OT_toggle_camera_pan,
            KT_VIEW3D_OT_toggle_pan_on_lock,
            
        )