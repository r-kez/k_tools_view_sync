# 🔧 Global Settings & Options

Customize how data is shared between viewports, set defaults, and configure global preferences.

---

## ⚙️ Sync Options (The "What" to Sync)

Click the **Settings (gear icon)** popover in the panel to choose which attributes are shared across synchronized viewports:

- **Navigation**:
  - **Location**: Sync the center position of the viewport.
  - **Rotation**: Sync the rotation angle.
  - **Distance**: Sync the zoom level.
  - **Adjust Distance**: A multiplier (from `0.01` to `5.0`) to offset the zoom level of synced target viewports relative to the Master View (e.g., keeping a target view twice as zoomed-out).
  
- **Camera Data**:
  - **Focal Length**: Sync lens focal length (mm).
  - **Camera Zoom**: Sync viewport zoom levels when in Camera view.
  - **Camera Offset**: Sync offset settings of the active camera.
  
- **Viewport**:
  - **Clip Start / End**: Sync near and far clip distances to avoid geometry clipping.
  - **Perspective**: Sync whether the viewports are in Perspective, Orthographic, or Camera mode.

---

## 💾 Smart Session Persistence

Addon configurations are saved directly inside `.blend` files. When you save and reopen your file:
- Real-time Sync and Auto Master states are automatically restored.
- The active timers and viewport listeners resume exactly where you left off.

---

## 🔩 Addon Preferences & Defaults

Go to `Edit > Preferences > Add-ons > K-Tools View Sync` to configure global settings. The preferences are organized into three tabs:

### ⚙️ Global Defaults
- **Auto Master On by Default**: Starts new Blender sessions with Auto Master enabled automatically.
- **Auto Lock Ortho by Default**: Starts new Blender sessions with Auto Lock Ortho enabled automatically.

### 🎴 UI Options
- **Show Lock HUD Overlay**: Toggle the visibility of the bottom-center HUD card in locked/auto-locked viewports.

### ⌨️ Keymap Options
- **Replace Default Local View**: If enabled, the user's active Local View hotkey (which defaults to Numpad `/`) will trigger the K-Tools Global Local View.
- **Restore Default (Button)**: Reverts the hotkey back to Blender's native Local View action.
- **Enable Floating Panel Hotkey**: Enables a global shortcut (`Alt + .` by default) to bring up the K-Tools View Sync panel as a floating popover directly under the mouse. When enabled, users can interactively configure the shortcut keys directly inside the Blender preferences window.
