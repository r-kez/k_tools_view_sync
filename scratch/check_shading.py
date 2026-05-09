import bpy
area = [a for a in bpy.context.screen.areas if a.type == 'VIEW_3D'][0]
shading = area.spaces.active.shading
print(f"Background Type: {shading.background_type}")
print(f"Available Types: {shading.bl_rna.properties['background_type'].enum_items.keys()}")
if hasattr(shading, 'background_color'):
    print(f"Has background_color: {shading.background_color}")
else:
    print("No background_color attribute")
