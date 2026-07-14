# 🔒 Lock Rotation System

The Lock Rotation system allows you to freeze individual viewports into specific angles, allowing you to model or inspect from a constant viewpoint while navigating elsewhere.

---

## 📐 Locking View Angles & Presets

In the **Lock View** panel, you can lock viewports to preset angles:
- **Standard Presets**: Fast-lock to Front, Back, Right, Left, Top, or Bottom.
- **Camera View**: Freeze the viewport to the active camera.
- **Match Master**: Instantly match the viewport to the current orientation of the Master View and lock it.
- **Independent Navigation**: Keeps the locked viewport fixed while allowing you to orbit, zoom, or navigate freely in other views.

---

## ⚡ Smart Panning & Auto Lock Ortho

Accidentally orbiting out of an orthographic view (like Front or Top) when trying to pan is a common issue. The addon solves this with two options:

- **Pan on Rotation Lock**: When rotation is locked manually on a viewport, dragging with the **Middle Mouse Button** performs a **Pan** (`view3d.move`) instead of Orbiting (`view3d.rotate`).
- **Auto Lock Ortho**: 
  When active, the addon automatically intercepts the Middle Mouse button on any viewport aligned to a standard orthographic axis (Front, Back, Right, Left, Top, Bottom).
  - Dragging the **Middle Mouse Button** in an aligned view automatically **Pans** the viewport.
  - Orbiting is locked, meaning you will never accidentally exit your flat modeling view by clicking Middle Mouse.
  - Standard view hotkeys (Numpad `1`, `3`, `7`, etc.) remain fully functional, allowing you to switch between different orthographic views without needing to unlock the rotation first.

---

## 🎴 Lock HUD Indicator

When a viewport is rotation-locked (either manually or automatically via Auto Lock Ortho), a premium HUD card is displayed in the bottom-center of the viewport:
- **LOCKED** (Orange Accent): Rendered when the viewport rotation has been locked manually.
- **AUTO-LOCK** (Cyan Accent): Rendered when the viewport is automatically locked in an axis-aligned orthographic view.
- **Toggle Visibility**: This overlay can be toggled on/off under `Edit > Preferences > Add-ons > K-Tools View Sync > UI Options`.

---

> [!TIP]
> **To Orbit out of an Auto-Locked View**: If you need to orbit out of a flat view while **Auto Lock Ortho** is active, you can use the viewport navigation gizmo in the top right, or toggle **Auto Lock Ortho** off in the Lock View sidebar panel.
