# 4. Custom Shapes (DXF Guide)

MOLD F.O.R.G.E. allows you to move beyond standard popsicle shapes by importing custom vector outlines.
This guide explains how to prepare your DXF files to achieve the most precise and professional results.

## 📐 General Drawing Rules

To ensure the geometry engine interprets your design correctly, follow these rules in your CAD or vector software (Inkscape, Illustrator, AutoCAD):

1. **Full Profile:** Draw the **entire** closed outline of the deck.
Do not draw only half; the engine expects a complete loop.

2. **Y-Axis Orientation:**
The length of the board must run along the **Y-axis** (Vertical).
The width must run along the **X-axis** (Horizontal).

3. **Closed Loops:**
Ensure the path is perfectly closed. Gaps between nodes will cause the 3D generation to fail.

4. **Clean Vectors:**
Avoid overlapping lines or stray points. Use the minimum number of nodes necessary to define the curve for a smoother finish.

## ⚖️ Scaling and Centering (The "Don't Worry" Rules)

The MOLD F.O.R.G.E. loader is designed to be user-friendly:

* **Automatic Centering:**
You don't need to center your drawing at the (0,0) origin.
The engine calculates the geometric center of your shape and aligns it automatically.

* **Automatic Scaling:**
The software ignores the original dimensions of your DXF.
It will force the shape to match the `BoardWidth` and the total length calculated from your `Wheelbase`, `Kicks`, and `Gaps` parameters.

## 🧠 Behind the Scenes: Spline vs. Polygon

When you load a DXF, the engine attempts two methods to reconstruct your shape:

1. **B-Spline (Primary):**
It tries to build a continuous, mathematically smooth B-Spline through your points.
This produces the "beautiful" professional curves seen in high-end decks.

2. **Polygon (Fallback):**
If your shape has sharp corners (like a "Swallow Tail" or "Diamond Tail") that break the spline logic, the engine automatically switches to a high-resolution polygon to preserve those sharp details.

## 🛠️ Export Settings

When exporting your file from Inkscape or Illustrator, use these settings:

* **Format:** AutoCAD DXF R14 or newer.
* **Units:** Millimeters (mm).
* **Location:** Save the file into the `/shapes_library/` folder of the project.

## 💡 Pro Tip: Asymmetrical Shapes (FishTails & Old School)

If you are designing a directional shape where the visual center of the "waist" doesn't align with the truck holes, use the **`ShapeOffsetY`** parameter in the software.
This allows you to slide the outline up or down until the wheel wells and truck holes sit exactly where you want them.

---
**[⬅️ Previous: Custom Shapes (DXF)](4-Custom-Shapes-DXF.md)** | **[🏠 Home](1-Introduction.md)** | **[Next: Glossary ➡️](6-Glossary.md)**
