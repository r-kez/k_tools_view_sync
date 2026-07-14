# 📍 Upgraded Local View

The addon includes an upgraded version of Blender's native `/` (Numpad Slash) Local View feature, designed for complex, multi-viewport setups.

---

## 🛠 Features

- **Global Isolation**: Standard Blender Local View only isolates objects in the viewport where your mouse is. K-Tools View Sync isolates the selected objects in **all active viewports** simultaneously.
- **Keep Lights option**: 
  - Standard Local View hides all lights, which can make it hard to check shading and lighting on isolated models.
  - When **Don't Hide Lights** is enabled in the addon options, lights will remain visible in the scene when you enter Local View.
- **Default Hotkey Replacement**:
  - You can override Blender's default Local View keymap with K-Tools Local View under `Edit > Preferences > Add-ons > K-Tools View Sync > Keymap Options > Replace Default Local View`.
  - The addon dynamically detects whatever key you have assigned to native Local View (even if it's not the default Numpad `/`) and automatically overrides it.
  - A **Restore Default** button is available to revert back to native Blender behavior instantly.
