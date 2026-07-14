# 🔗 View Synchronization

The View Synchronization system allows you to mirror navigation, camera settings, and view attributes from a **Master View** to other target viewports, including views inside separate Blender windows.

---

## 🛠 Core Sync Controls

- **Single Match**: Instantly synchronizes all selected target viewports once. Useful if you want to align your viewports but keep navigating them independently afterward.
- **Real-time Sync**: Constantly mirrors navigation (location, rotation, zoom) from the Master View to all selected targets. Moving in the Master View moves all synced views instantly.
- **Customizable Refresh Rate**: Adjusts how often the synchronization runs (in seconds). Lower values (e.g., `0.01s`) are smoother but consume more CPU/GPU resources; higher values (e.g., `0.1s` or more) are more performant for heavy scenes.
- **Master View Control**: Choose which viewport acts as the "Driver" (Master). Use the **Identify Views** button to draw unique ID numbers over each viewport to easily see which viewport is which.

---

## 🚀 Advanced Master Logic

- **Auto Master**: When enabled, the addon automatically promotes whichever viewport your mouse cursor is hovering over to be the Master View. This makes multi-window workflows extremely fluid: just hover and navigate, and the other views will sync immediately.
- **Set Current as Master**: Instantly sets the currently active viewport as the Master View.

---

## 📋 Smart View List

The sidebar panel organizes all detected 3D viewports under a list structured by window:
- **Window Sections**: If you use multiple Blender windows (e.g., on a multi-monitor setup), the views are grouped by Window ID.
- **Individual Toggles**: Enable or disable synchronization for each viewport independently using the toggles.
- **Shading Presets**: Directly apply specialized visual modes to specific viewports from the list.

---

> [!NOTE]
> Make sure to configure which attributes (Location, Rotation, Camera Focal Length, Zoom, etc.) you want to synchronize in the **Settings** popover. See [Sync Options](global_settings.md) for details.
