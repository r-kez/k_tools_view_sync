import bpy

def test_split():
    # 1. Create a temporary workspace to not mess up the user's current one
    ws_name = "KT_Test_Layout"
    if ws_name in bpy.data.workspaces:
        bpy.data.workspaces.remove(bpy.data.workspaces[ws_name])
    
    bpy.ops.workspace.duplicate()
    new_ws = bpy.context.workspace
    new_ws.name = ws_name
    
    # 2. Open a new window on this workspace
    # Note: window_new opens a copy of the current window/workspace
    bpy.ops.wm.window_new()
    
    # The new window is now active in context (usually)
    # We want to split the 3D view area in this new window
    target_window = bpy.context.window_manager.windows[-1]
    
    # Use context override for the new window
    with bpy.context.temp_override(window=target_window, screen=target_window.screen):
        area = next((a for a in target_window.screen.areas if a.type == 'VIEW_3D'), None)
        if area:
            # Vertical split
            bpy.ops.screen.area_split(direction='VERTICAL', factor=0.5)
            
            # Now we have two 3D areas. Let's find them.
            areas_3d = [a for a in target_window.screen.areas if a.type == 'VIEW_3D']
            print(f"Areas after vertical split: {len(areas_3d)}")
            
            # Split each one horizontally
            # We need to be careful with overrides here
            for a in areas_3d:
                with bpy.context.temp_override(area=a):
                    bpy.ops.screen.area_split(direction='HORIZONTAL', factor=0.5)
            
            areas_3d_final = [a for a in target_window.screen.areas if a.type == 'VIEW_3D']
            print(f"Final areas: {len(areas_3d_final)}")

if __name__ == "__main__":
    test_split()
