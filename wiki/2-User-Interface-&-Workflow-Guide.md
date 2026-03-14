# 2. User Interface & Workflow Guide

MOLD F.O.R.G.E. features a professional, industrial-grade interface designed for high-precision CAD work.
This guide explains how to master the 3D viewport, use the interactive designers, and leverage the full command set.

---

## 🖥️ The 3D Viewport

The central area of the application is your real-time 3D workspace.

* **Navigation Controls:**
* **Rotate:** Left-click and drag.
* **Zoom:** Use the mouse wheel or Right-click and drag.
* **Pan:** Middle-click (scroll wheel click) and drag.
* **Camera Overlays:** In the top-left corner, quick-snap buttons (**ISO, TOP, FRONT, SIDE**)
allow you to instantly align the view to standard engineering perspectives.

---

## 🎨 Interactive Shape Designer (2D Editor)

The bottom panel features the `KickShapeEditor`, a specialized tool for "sculpting" your board's outline using interactive Bezier handles.

### Understanding the Control Handles

When **Shape Style** is set to **Custom**, three color-coded handles appear on the canvas:

* **🟡 Yellow Handle (Straight Section):** Controls the `StraightP` percentage. It defines how long the rails stay parallel before the curve begins.
* **🔴 Red Handle (Primary Curve):** Adjusts the "shoulder" of the board (Ctrl1X/Y). It dictates the fullness and width of the transition.
* **🔵 Blue Handle (Tip Shape):** Controls the tip (Ctrl2X). Drag this to switch between a pointy "Popsicle" and a squared-off "Box" shape.

### Advanced Fillet & Analysis Visualization

The editor performs a live geometric analysis, visualizing how the **Edge Rounding** (`FilletYellow`) affects the physical edge:

* **The Green Line:** Represents the final, smooth physical edge of the board after rounding.
* **The Orange "Wedge":** Visualizes the exact material being removed by the rounding process.
* **The Crosshair (+):** Marks the **True Origin**—the mathematical center of the rounding arc.

### Technical Overlays

* **KICK START (Dashed Gray):** Indicates where the board begins to bend upwards.
* **Truck Holes (Gray Circles):** Shows the hardware mounting pattern to ensure your shape doesn't interfere with the trucks.
* **Wheel Flares (Purple Outlines):** Shows the 3D flare zones to help you align your outline with the wheel clearance bumps.

---

## 📂 Presets & Data Management

MOLD F.O.R.G.E. automates data management to ensure you can replicate your best designs perfectly.

* **JSON Presets:** Every parameter can be saved into the `fb_presets.json` database.
* **DXF Library:** Any `.dxf` file placed in the `/shapes_library/` folder is automatically detected and can be scaled to fit your wheelbase.
* **Config Reports:** Every export includes a `_Config.txt` file containing the "DNA" of your deck, which can be re-imported later.

---

## 📟 Log Console & Progress Bar

The bottom console provides real-time feedback on the geometry engine's state.

* **Diagnostic Info:** The console reports the **Max Dimensions** (Length, Width, Height) of the generated object. This is your final check to ensure the part will fit on your 3D printer's bed.
* **Unit Toggle:** Use the **View > Unit** menu to switch the console output between **Metric (mm)** and **Imperial (in)**. Note: Input sliders always remain in mm for engineering precision.
* **Validation Warnings:** If you enter a parameter that is physically impossible (e.g., a board wider than the mold), the software will auto-correct the value and flash the widget in **Orange**, logging a warning in the console.
* **Standard Output Redirection (Pro-Tip):** For advanced users and debugging, all standard output (`stdout`) and standard error (`stderr`) from the underlying Python environment and CAD engine are automatically intercepted and printed directly to this console.
* **Progress Bar:** 3D generation is a heavy mathematical process. The orange progress bar indicates that the CadQuery kernel is currently calculating the complex lofts and boolean subtractions.

---

## ⌨️ Shortcuts & Commands

MOLD F.O.R.G.E. utilizes a combination of hotkeys and menu commands to optimize the design-to-manufacturing pipeline.

* **F11:** Instantly toggles the visibility of the Left, Right, Bottom, and Interactive Designer panels.
This maximizes the 3D workspace for detailed inspection or high-resolution screenshots without interface clutter.
* **Export Current Object...:** Located in the **File Menu**. This action exports the specific 3D model currently visible in the viewport (Male Mold, Female Mold, etc.) as an STL or STEP file. It remains disabled until the engine successfully renders an object.
* **Batch Export:** Found in the **File Menu**, this is the primary production command.
It generates the Male Mold, Female Mold, and Shaper Template in a single sequence, saving them into a timestamped project folder alongside a technical `_Config.txt` report.
* **Load Config File:** Imports parameters from a previously exported text report.
This allows you to instantly restore every slider and toggle to a specific production state.
* **Unit Toggle:** Found in the **View Menu**, this command instantly converts all console measurements (Length, Width, Height) between **Metric (mm)** and **Imperial (in)**.
* **Enable Clipping Plane:** Found in the **View Menu**, this command triggers a dynamic cross-section cut.
Use this to visually verify the internal `MoldGap` and ensure the `VeneerThickness` is correctly accounted for.
* **Show Scale Grid:** Displays a persistent 3D bounding box with axis labels and measurements around the model. This is used for a final "sanity check" of the absolute physical footprint before starting a 3D print.
* **Interactive Symmetry Lock:** A toggle in the designer that mirrors Bezier changes symmetrically between the Nose and Tail. Uncheck this to unlock independent "Directional" design capabilities.

---

## 💾 File & Preset Actions

* **Save Preset:** Commits the current UI configuration to the local JSON database.
* **Delete Preset:** Permanently removes the selected custom configuration from your library.
* **Target Swap:** In the 2D Designer, use the **Target Dropdown** to quickly switch focus between editing the Nose and Tail planes.

---
**[⬅️ Previous: Introduction](1-Introduction.md)** | **[🏠 Home](1-Introduction.md)** | **[Next: The Parametric Engine ➡️](3-The-Parametric-Engine.md)**
