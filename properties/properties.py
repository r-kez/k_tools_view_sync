import bpy
from bpy.props import (
    EnumProperty, 
    IntProperty,
    FloatProperty
)
from bpy.types import PropertyGroup
from bpy.props import BoolProperty, IntProperty, FloatProperty
from ..operators.op_auto_master import auto_master_update

shading_preset_items = [
    ('NONE', "None", "No shading preset applied", 'NONE', 0),
    ('SILHOUETTE', "Silhouette", "Flat shading with black background for silhouette analysis", 'GHOST_ENABLED', 1),
    ('SILHOUETTE_INV', "Silhouette Inv", "Inverted silhouette: Black models on white background", 'GHOST_DISABLED', 12),
    ('TOPOLOGY', "Topology", "Solid shading with wireframe overlay for checking mesh flow", 'SHADING_WIRE', 2),
    ('NORMALS', "Normals Check", "Show face orientation using Matcap normal check", 'FACESEL', 3),
    ('XRAY', "X-Ray View", "Solid shading with X-Ray transparency", 'XRAY', 4),
    ('RANDOM', "Random Colors", "Assign random colors to each object to distinguish shapes", 'COLOR', 5),
    ('CLEAN', "Clean View", "Hide all overlays and gizmos but keep current shading", 'RESTRICT_SELECT_OFF', 6),
    ('HARD_SURFACE', "Red Clay", "Hard surface analysis using Red Clay Matcap", 'SCULPTMODE_HLT', 7),
    ('REFL_H', "Refl. Horizontal", "Check surfaces with horizontal zebra matcap", 'STRANDS', 8),
    ('REFL_V', "Refl. Vertical", "Check surfaces with vertical zebra matcap", 'STRANDS', 9),
    ('TOON_DARK', "Toon Dark", "Apply Toon Dark shading matcap", 'LIGHT', 10),
    ('TOON_LIGHT', "Toon Light", "Apply Toon Light shading matcap", 'LIGHT', 11),
    ('HIGH_DETAIL', "High Detail", "Maximize contrast with Cavity and Outlines for detail analysis", 'SOLO_ON', 13),
]

def update_view_list(self, context):
    scene = context.scene

    bpy.ops.view3d.update_view_count()

class KT_SyncOptions(PropertyGroup):
    addon_mode: EnumProperty( # type: ignore
        name="Panel Mode",
        description="Choose addon mode",
        items=[
            ('SYNC_VIEW', "Sync", "Sync all selected Viewports based on a Master viewport", 'LINKED', 0),
            ('LOCK_VIEW', "Lock", "Lock Rotation from selected 3D Views", 'LOCKED', 1),
        ],
        default='SYNC_VIEW',
        update = update_view_list,
    ) # type: ignore

    view_3d_index: IntProperty( # type: ignore
        name="View 3D ID", 
        default=-1
        ) # type: ignore
    master_view_index: IntProperty( # type: ignore
        name="Master View Index",
        description="Index of the master View3D",
        default=0,
        min=0
    ) # type: ignore
    sync_refresh_rate: FloatProperty( # type: ignore
        name="Refresh Rate",
        description="Refresh rate for real-time synchronization (in seconds)",
        default=0.01,
        min=0.01,
        max=1.0
    ) # type: ignore
    
    auto_master: bpy.props.BoolProperty( # type: ignore
        name="Auto Master",
        description="Automatically set master view to the active 3D view",
        default=False,
        update=auto_master_update
    ) # type: ignore

    sync_view_distance: BoolProperty( # type: ignore
        name="Sync View Distance", 
        default=True, 
        description="Sync viewing distance between View Distance"
    )    # type: ignore
    
    sync_view_location: BoolProperty( # type: ignore
        name="Sync View Location",
        default=True,
        description="Sync viewing location between 3D Views"
    )    # type: ignore
    
    sync_view_rotation: BoolProperty( # type: ignore
        name="Sync View Rotation",
        default=True,
        description="Sync viewing rotation between 3D Views"
    )    # type: ignore
    
    sync_camera_zoom: BoolProperty( # type: ignore
        name="Sync Camera Zoom",
        default=True,
        description="Sync camera zoom between 3D Views"
    )    # type: ignore

    sync_camera_offset: BoolProperty( # type: ignore
        name="Sync Camera Offset",
        default=True,
        description="Sync camera offset between 3D Views"
    )    # type: ignore
    
    sync_view_perspective: BoolProperty( # type: ignore
        name="Sync View Perspective",
        default=True,
        description="Sync viewing perspective between 3D Views"
    )    # type: ignore 
    
    sync_clip_start: BoolProperty( # type: ignore
        name="Sync Clip Start",
        default=True,
        description="Sync the start point of the viewing clip between 3D Views"
    )    # type: ignore

    sync_clip_end: BoolProperty( # type: ignore
        name="Sync Clip End",
        default=True,
        description="Sync the end point of the viewing clip between 3D Views"
    )    # type: ignore

    sync_focal_length: BoolProperty( # type: ignore
        name="Sync Focal Length",
        default=True,
        description="Sync focal length between 3D Views"
    )    # type: ignore   

    sync_view_distance_adjust: FloatProperty( # type: ignore
        name="Adjust View Distance:",
        default=1.0,
        min=0.01,
        max=5.0,
        description="Fine adjustment (Multiplier) for Sync View Distance"
    )   # type: ignore

    dont_exclude_lights: bpy.props.BoolProperty( # type: ignore
        name="Don't Hide Lights", 
        default=True,
        description="Keep lights visible when using Local View"
    )   # type: ignore

## LOCK
    enable_camera_pan: BoolProperty( # type: ignore
        name="Enable Camera Pan",
        description="Enable panning with middle mouse in camera view",
        default=False
    )   # type: ignore
    enable_pan_on_lock: BoolProperty( # type: ignore
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