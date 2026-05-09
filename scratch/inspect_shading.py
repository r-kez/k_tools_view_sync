import bpy

def inspect_details():
    area = next((a for a in bpy.context.screen.areas if a.type == 'VIEW_3D'), None)
    if not area:
        print("No 3D View found!")
        return

    space = area.spaces.active
    
    print("-" * 50)
    print("INSPECTING SpaceView3D (Gizmos & Display)")
    print("-" * 50)
    
    rna_space = space.bl_rna.properties
    gizmo_props = [p for p in rna_space.keys() if 'gizmo' in p.lower()]
    for p in gizmo_props:
        prop = rna_space[p]
        print(f"Prop: {p:<40} | Type: {prop.type}")

    print("\n" + "-" * 50)
    print("INSPECTING View3DOverlay (Deep)")
    print("-" * 50)
    
    overlay = space.overlay
    rna_overlay = overlay.bl_rna.properties
    for p in rna_overlay.keys():
        prop = rna_overlay[p]
        line = f"Prop: {p:<40} | Type: {prop.type}"
        if prop.type == 'ENUM':
            items = [item.identifier for item in prop.enum_items]
            line += f" | Enums: {items}"
        print(line)

if __name__ == "__main__":
    inspect_details()
