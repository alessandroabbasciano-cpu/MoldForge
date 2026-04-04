# 4. Custom Shapes (DXF Integration)

MOLD F.O.R.G.E. refuses to lock you into standard popsicle shapes. The parametric engine allows you to import entirely custom vector outlines and automatically adapts the 3D geometry (concave, wheel flares, and transitions) to fit your exact design.

This guide explains how to prepare and integrate your `.dxf` files to achieve perfect, professional results.

---

## 📂 The Auto-Scanning Library

We eliminated the tedious "File > Import" workflow. MOLD F.O.R.G.E. features a dynamic, auto-scanning shape library.

1. Save your completed `.dxf` file.
2. Drop it directly into the `shapes_library/` folder located next to your application executable.
3. Launch MOLD F.O.R.G.E.
4. The software will instantly detect the new file and add it to the **Select Shape** dropdown menu in the Left Panel.

---

## 📐 General Drawing Rules

To ensure the geometry engine can loft a solid 3D mesh from your 2D drawing, strictly follow these rules in your vector software (Illustrator, Inkscape, AutoCAD, etc.):

1. **Full Profile:** Draw the **entire** closed outline of the deck. Do not draw only one half; the mathematical engine expects a complete, continuous loop.
2. **Y-Axis Orientation:** The length of the board *must* run along the **Y-axis** (Vertical). The width must run along the **X-axis** (Horizontal).
3. **Perfectly Closed Loops:** Ensure the vector path is completely closed. Even a microscopic gap between two nodes will cause the 3D generation to fail and throw an error in the console.
4. **Clean Vectors & Zero Noise:** Avoid overlapping lines, self-intersecting curves, or stray points. Use the absolute minimum number of nodes necessary to define your curve for the smoothest CNC-ready finish.
5. **No Ghost Layers (CRITICAL):** OpenCASCADE is a strict mathematical kernel, not a forgiving visual editor. It calculates the Bounding Box of the *entire* DXF file. If your vector software exports hidden default layers (like `Layer 0`), template bounds, or invisible absolute origin anchors, the bounding box calculation will explode and the 3D boolean operation will throw an **"Out of bounds"** error. Delete ALL empty/hidden layers before exporting.

---

## ⚖️ Smart Scaling & Centering (The "Don't Worry" Rules)

The MOLD F.O.R.G.E. loading sequence is designed to be highly intelligent. You do not need to do the math in your vector software:

* **Automatic Centering:** You do not need to center your drawing perfectly at the (0,0) origin coordinate. The engine calculates the geometric True Center of your shape and aligns it to the mold automatically.
* **Automatic Scaling:** The software completely ignores the original scale of your DXF. It will intelligently stretch and squeeze the shape to precisely match the `Board Width` slider and the total length calculated by your `Wheelbase`, `Kicks`, and `Gaps` parameters.

---

## 💡 Pro Tip: Asymmetrical & Directional Shapes

If you are designing a directional shape (like a Fishtail, Old School Cruiser, or a shape with a massive blunt nose), the visual "waist" of the board might not align perfectly with the standard truck holes.

Use the **`Shape Shift Y (mm)`** slider in the Left Panel. This parameter allows you to slide the DXF outline up or down along the longitudinal axis, letting you perfectly align your custom wheel wells and truck holes exactly where you want them.

---

## 🌍 The Community Shapes Library

Beyond your personal designs, MOLD F.O.R.G.E. supports an ever-expanding, user-driven open-source database.

**How to download Community DXFs:**
We integrated the download process directly into the application engine, eliminating manual file management.

1. Inside the application, open the **File** menu and select **Community Shapes Store...**.
2. The dedicated built-in browser will open and connect directly to the GitHub repository. It automatically parses the community's `catalog.json` file to display the shape's name alongside its **description** and the original **author**.
3. Files you already have will be smartly greyed out and marked as `[Installed]`.
4. Select an available shape and click **Download and Install**.
5. The system will automatically save the `.dxf` file into your local `shapes_library/` folder.

**How to contribute (The Voting Pool):**
Did you design a killer shape and want to share it with the rest of the makers? The process is strictly regulated:

1. **Submit:** Open a new Issue on GitHub using the dedicated **DXF Submission Template** and attach your file.
2. **Validation:** The Issue will be tagged as *pending-validation*. A topological check will be run on your vector to ensure it complies with the strict rules of OpenCASCADE (perfectly closed loops, zero ghost layers).
3. **Voting Pool:** If the file passes the geometry check, the Issue will be opened for public community voting.
4. **Merge:** If your shape reaches the minimum threshold of **10 up-votes**, it will be officially merged into the `community_shapes/` repository folder and documented in the global JSON catalog.

---

## 🧠 Behind the Scenes: Spline vs. Polygon

When you load a custom DXF, the engine attempts two distinct mathematical methods to reconstruct your shape:

1. **B-Spline (Primary Engine):** It tries to calculate a continuous, perfectly smooth mathematical B-Spline through your nodes. This produces the beautiful, flowing curves seen in high-end decks.
2. **Polygon (Fallback Engine):** If your shape has extremely sharp corners (like a rigid "Swallow Tail" or "Diamond Tip") that mathematically break the continuous spline logic, the engine detects the failure and automatically switches to a high-resolution polygon mesh to preserve those aggressive sharp details.

---

## 🛠️ Export Settings Checklist

When exporting your final file from your vector software (Inkscape, Illustrator, Fusion360), strictly follow this protocol to prevent 3D engine crashes:

* **Global Units:** Must be strictly set to **Millimeters (mm)** in your Document Properties. If your background document is set to Inches but you export in mm, the scale multiplier will corrupt the bounding box tolerance.
* **Export Selection Only:** DO NOT "Save As" the whole document. Select ONLY your single, closed path. Choose "Export..." and ensure a checkbox like "Export Selected Only" is active. This strips out all ghost layers and background noise.
* **Format:** AutoCAD DXF R14 (or newer). R14 is heavily recommended as it automatically flattens complex splines into safe, continuous polylines.
* **Location:** Save directly into the `/shapes_library/` folder.

---
**[⬅️ Previous: The Parametric Engine](3-The-Parametric-Engine.md)** | **[🏠 Home](1-Introduction.md)** | **[Next: 3D Printing & Manufacturing ➡️](5-3D-Printing-Manufacturing.md)**
