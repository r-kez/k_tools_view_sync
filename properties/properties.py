import bpy
from bpy.props import (
    EnumProperty, 
    IntProperty,
    FloatProperty
)
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, FloatProperty
from ..operators.op_auto_master import auto_master_update

def update_view_list(self, context):
    scene = context.scene

    bpy.ops.view3d.update_view_count()

class KT_SyncOptions(PropertyGroup):
    addon_mode: EnumProperty(
        name="Panel Mode",
        description="Choose addon mode",
        items=[
            ('SYNC_VIEW', "Sync", "Sync all selected Viewports based on a Master viewport", 'LINKED', 0),
            ('LOCK_VIEW', "Lock", "Lock Rotation from selected 3D Views", 'LOCKED', 1),
        ],
        default='SYNC_VIEW',
        update = update_view_list,
    ) # type: ignore

    view_3d_index: IntProperty(
        name="View 3D ID", 
        default=-1
        ) # type: ignore
    master_view_index: IntProperty(
        name="Master View Index",
        description="Index of the master View3D",
        default=0,
        min=0
    ) # type: ignore
    sync_refresh_rate: FloatProperty(
        name="Refresh Rate",
        description="Refresh rate for real-time synchronization (in seconds)",
        default=0.01,
        min=0.01,
        max=1.0
    ) # type: ignore
    
    auto_master: bpy.props.BoolProperty(
        name="Auto Master",
        description="Automatically set master view to the active 3D view",
        default=False,
        update=auto_master_update
    ) # type: ignore

    sync_view_distance: BoolProperty(
        name="Sync View Distance", 
        default=True, 
        description="Sync viewing distance between View Distance"
    )    # type: ignore
    
    sync_view_location: BoolProperty(
        name="Sync View Location",
        default=True,
        description="Sync viewing location between 3D Views"
    )    # type: ignore
    
    sync_view_rotation: BoolProperty(
        name="Sync View Rotation",
        default=True,
        description="Sync viewing rotation between 3D Views"
    )    # type: ignore
    
    sync_camera_zoom: BoolProperty(
        name="Sync Camera Zoom",
        default=True,
        description="Sync camera zoom between 3D Views"
    )    # type: ignore

    sync_camera_offset: BoolProperty(
        name="Sync Camera Offset",
        default=True,
        description="Sync camera offset between 3D Views"
    )    # type: ignore
    
    sync_view_perspective: BoolProperty(
        name="Sync View Perspective",
        default=True,
        description="Sync viewing perspective between 3D Views"
    )    # type: ignore 
    
    sync_clip_start: BoolProperty(
        name="Sync Clip Start",
        default=True,
        description="Sync the start point of the viewing clip between 3D Views"
    )    # type: ignore

    sync_clip_end: BoolProperty(
        name="Sync Clip End",
        default=True,
        description="Sync the end point of the viewing clip between 3D Views"
    )    # type: ignore

    sync_focal_length: BoolProperty(
        name="Sync Focal Length",
        default=True,
        description="Sync focal length between 3D Views"
    )    # type: ignore   

    sync_view_distance_adjust: FloatProperty(
        name="Adjust View Distance:",
        default=1.0,
        min=0.01,
        max=5.0,
        description="Fine adjustment (Multiplier) for Sync View Distance"
    )   # type: ignore

    dont_exclude_lights: bpy.props.BoolProperty(
        name="Don't Hide Lights", 
        default=True,
        description="Keep lights visible when using Local View"
    )   # type: ignore

## LOCK
    enable_camera_pan: BoolProperty(
        name="Enable Camera Pan",
        description="Enable panning with middle mouse in camera view",
        default=False
    )   # type: ignore
    enable_pan_on_lock: BoolProperty(
        name="Pan on Rotation Lock",
        description="Enable panning with middle mouse when View Rotation is locked",
        default=False
    )   # type: ignore

classes = (  
    KT_SyncOptions,      
    )

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.sync_options = bpy.props.PointerProperty(type=KT_SyncOptions)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.sync_options

if __name__ == "__main__":
    register()