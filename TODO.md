# K-Tools: Sync | Lock Viewport - Roadmap & TODO

## Features to Implement
- [x] **Shading Presets for Viewports**
    - [x] Create an Enum for shading presets.
    - [x] Implement artistic presets: `Silhouette`, `Silhouette Inverted`, `Random Colors`.
    - [x] Implement technical presets: `Topology` (Wireframe), `Normals Check` (Normal Matcap).
    - [x] Implement matcap-based presets: `Red Clay`, `Zebra (H/V)`, `Toon (Dark/Light)`.
    - [x] Implement `High Detail` (Max Cavity + Outline).
    - [x] Implement `Clean View` (Minimalist UI).
    - [x] Implement **Viewport State Capture**: Saves and restores original settings.
    - [x] **Bug Fix**: Fixed preset inheritance via state restoration.

## Improvements & Future
- [ ] **Analytic Window Mode** (WIP - Registration paused).
- [x] Refactor dynamic property creation for presets.
- [x] Add extensive Matcap-based presets.
- [ ] Implement custom user presets (Save current state as preset).
- [ ] UI: Add thumbnails/icons for each preset.
