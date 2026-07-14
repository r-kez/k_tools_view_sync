# 🎨 Shading Presets System

The Shading Presets system allows you to apply specialized visual analysis modes to individual viewports. This lets you inspect topology, check surface continuity, and analyze silhouettes side-by-side.

---

## 🔍 Shading Presets Table

| Category | Preset Name | Description & Best Use Case |
| :--- | :--- | :--- |
| **Artistic** | Silhouette | Flat black shading with a solid white background. Excellent for checking overall shape, balance, and visual read. |
| | Silhouette Inv | Inverted silhouette: flat white shading on a black background. |
| | Random Colors | Assigns a random color to each object. Useful for visually distinguishing complex assemblies of parts. |
| **Technical** | Topology | Solid viewport shading with a clean wireframe overlay. Best for checking polygon flow and edge loops. |
| | Normals Check | Applies a red/blue normal-direction Matcap. Helps identify flipped faces and surface direction issues. |
| | X-Ray | Translucent shading to reveal hidden structures and inner geometry. |
| **Surfacing** | Zebra (Horiz. / Vert.) | Reflective stripes mapped to surfaces. Perfect for checking reflection continuity and finding surface dents/seams. |
| | High Detail | High-contrast shading utilizing cavity and outline overlays to accentuate fine sculpted details. |
| | Red Clay | Classic red sculpting clay Matcap. Great for shape sculpting and organic model analysis. |

---

## 💾 Smart State Capture

When you apply a preset, the addon automatically captures and saves your current viewport status (including shading style, overlays, and gizmos). 

Selecting **"None"** (or toggling the preset off) restores your original viewport configuration exactly as it was.
