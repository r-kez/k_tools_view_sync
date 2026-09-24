# K-Tools: Sync | Lock Viewport (v2.9.0)

**Addon Location:** `3D View -> N-Panel -> K-Tools -> Sync | Lock Viewport`

A powerful synchronization and analysis toolkit for Blender, designed for multi-monitor setups and complex scene reviewing. Sync navigation, lock specific rotations, or apply artistic shading presets across multiple viewports simultaneously.

---

## 🚀 What's New

### **v2.9.0 (Auto-Save Compatibility, 2D Timeline Sync, Lock HUD & Auto Lock Ortho)**
- **Blender Auto-Save Fully Restored**: Eliminated background modal operators (`real_time_sync_modal`, `auto_master_modal`) that blocked Blender's native Auto-Save mechanism. Background sync and Auto Master now operate completely non-blocking via native timers and direct viewport state detection.
- **Dedicated 3D vs 2D Tabs**: Clean tabbed interface separating 3D Viewport synchronization from 2D Animation Editors synchronization without clutter.
- **2D Animation Editors Sync**: Added support for synchronizing 2D animation editors (Timeline, Dopesheet, Graph Editor, NLA Editor) with horizontal time lock (disabled by default).
- **Auto Lock Ortho**: Automatically locks middle-mouse rotation when in standard orthographic axis-aligned views, strictly respecting the 'Enable Pan on Lock' toggle.
- **Lock HUD Improvements**: Added automatic padding above 2D navigation gizmos to prevent overlap, plus an option in preferences to draw the HUD card at the top of the viewport.
- **Global Preferences Defaults**: Configure default startup behaviors under Add-on Preferences.

---

## 📖 Wiki & Documentation

We have organized the features and guides into separate documentation files for the end-user. Click on any topic below to learn more:

1. **[View Synchronization](wiki/view_synchronization.md)**
   - Sync navigation (Location, Rotation, Zoom), camera attributes (Focal Length, Lens, Offset), and clip settings across different viewports and separate windows.
   - Use **Auto Master** to dynamically swap the driver viewport by simply hovering your mouse cursor over it.

2. **[Lock Rotation & Auto Lock Ortho](wiki/lock_rotation.md)**
   - Lock viewport rotation to top, bottom, front, back, right, left, or camera.
   - Use **Auto Lock Ortho** to automatically switch Middle Mouse drag behavior to **panning** in aligned flat views while keeping standard view keys (Numpad) functional.

3. **[Shading Presets System](wiki/shading_presets.md)**
   - Apply 10+ specialized visual presets (Silhouette, Zebra, Topology, Normals, Clay) to individual viewports to check mesh flow, surfaces, and forms.
   - Automatically restore original viewport styles when disabling presets.

4. **[Upgraded Local View](wiki/local_view.md)**
   - Isolate selected objects globally in all open viewports at once.
   - Keep scene lights visible during isolation to keep lighting contexts clear.

5. **[Global Settings & Customization](wiki/global_settings.md)**
   - Detailed settings for fine-tuning viewport synchronizations.
   - Session persistence and global preferences defaults.

---

**Developed by Robert Kezives**  
[Website/Support](https://kezives.gumroad.com/l/Sync-Lock_Viewport)
