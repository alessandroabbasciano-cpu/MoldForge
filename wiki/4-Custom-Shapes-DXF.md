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
4. **Clean Vectors:** Avoid overlapping lines, self-intersecting curves, or stray points. Use the absolute minimum number of nodes necessary to define your curve for the smoothest CNC-ready finish.

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

## 🧠 Behind the Scenes: Spline vs. Polygon

When you load a custom DXF, the engine attempts two distinct mathematical methods to reconstruct your shape:

1. **B-Spline (Primary Engine):** It tries to calculate a continuous, perfectly smooth mathematical B-Spline through your nodes. This produces the beautiful, flowing curves seen in high-end decks.
2. **Polygon (Fallback Engine):** If your shape has extremely sharp corners (like a rigid "Swallow Tail" or "Diamond Tip") that mathematically break the continuous spline logic, the engine detects the failure and automatically switches to a high-resolution polygon mesh to preserve those aggressive sharp details.

---

## 🛠️ Export Settings Checklist

When exporting your final file from your vector software, verify these exact settings:

* **Format:** AutoCAD DXF R14 (or newer).
* **Units:** Millimeters (mm).
* **Location:** Save directly into the `/shapes_library/` folder.

---
**[⬅️ Previous: The Parametric Engine](3-The-Parametric-Engine.md)** | **[🏠 Home](1-Introduction.md)** | **[Next: 3D Printing & Manufacturing ➡️](5-3D-Printing-Manufacturing.md)**
