# 3. The Parametric Engine

Welcome to the control room. This page provides a comprehensive, technical breakdown of every parameter and toggle available in the MOLD F.O.R.G.E. left and right control panels.

Understanding these variables is the key to unlocking the full potential of the procedural geometry engine.

---

## ⚙️ OUTPUT OPTIONS (Left Dock)

These settings determine what the engine actually builds and toggle specific structural features for the manufacturing process.

![MOLD FORGE 3D Viewport](assets/Options.jpg)

* **Object Type:** Selects which part of the project to generate and render in the 3D viewport.
  * `Board_Preview`: A realistic 3D representation of the final deck to check the shape and concaves.
  * `Male_Mold`: The bottom block of the press.
  * `Female_Mold`: The top block of the press.
  * `Shaper_Template`: The 2D-outline guide used to route/cut the board after pressing.
* **Clean Wireframe (Feature Edges):** Toggles the 3D viewport rendering style. When checked, it hides the dense triangular mesh and displays only the sharp feature edges for a cleaner, professional CAD look.
* **Add N/T Indicators:** Embosses 'N' (Nose) and 'T' (Tail) markers directly onto the molds and shaper to prevent accidental misalignment during the wood pressing phase.
* **Enable SideLocks (Vertical Print):** Generates robust interlocking side tabs on the mold halves. These are crucial for preventing the parts from sliding sideways when applying heavy pressure with a bench vise.
* **Add Top Shaper Shell:** Generates an additional mating top shell next to the Shaper Template. This allows you to "sandwich" the delicate wood veneers during the trimming phase, completely preventing edge splintering.
* **Add Base Fillet:** Adds a curved structural reinforcement fillet where the mold core meets the base plate to prevent stress fractures under clamping load.
  * *Dynamic UI:* **Fillet Radius (mm)** automatically appears when this feature is active, allowing you to set the radius of the reinforcement curve.
* **Add Guide Holes:** Generates vertical through-holes across the mold block for metal alignment pins (e.g., M6 threaded rods).
  * *Dynamic UI:* **Guide Diameter (mm)** automatically appears when this feature is active.
* **Enable Wheel Flares:** Toggles the generation of 3D wheel flares on the deck surface. Activating this magically reveals the dedicated "WHEEL FLARES" parameter group in the right panel.
* **Truck Pins (Molds) & (Shaper):** Replaces the standard through-holes with small embossed marking pins on the molds or shaper template. These act as "cleats" to grip the veneer stack and keep it perfectly centered before pressing.

---

## 🎨 SHAPE STYLE / PRESETS (Left Dock)

Manage the overarching DNA of your deck and handle your custom vector outlines.

* **Select Shape:** Defines the source of the board's outline.
  * `Custom`: Engages the internal Interactive Bezier engine (controlled via the bottom 2D Designer panel).
  * `[Filename]`: Instantly loads and adapts a specific DXF vector outline detected in your `/shapes_library/` folder.
* **Shape Shift Y (mm):** Slides the DXF shape along the longitudinal axis. This is vital for asymmetrical/directional boards (like Old School Fishtails) where the visual center of the waist does not align perfectly with the standard truck holes.
* **Load Preset:** A dropdown to instantly recall a pre-configured deck and mold setup from your local JSON database. Zero configuration required.
* **Save / Delete Preset:** Instantly commit your current exact UI configuration to the database, or cleanly remove it.

---

## 📦 MOLD DIMENSIONS (Left Dock)

These settings control the overall physical footprint and structural thickness of the 3D-printed blocks.

* **Mold Length & Core Width (mm):** The total physical footprint of the mold. The core *must* be wider and longer than your deck to ensure even pressing pressure across the entire surface.
* **Base Height (mm):** The thickness of the solid structural foundation plate. Thicker bases absorb vise clamping force better without flexing.
* **Base Width (mm):** The total width of the mold block, including the side shoulders.
  * *Pro Tip:* Set this equal to 'Core Width' to create perfectly flush, flat sides—ideal for printing the mold vertically!
* **Min. Core Thickness (mm):** The thickness of the mold's core at its lowest/thinnest point.
* **Mold Gap (mm):** The mathematical distance between the male and female molds. This usually equals your total `Veneer Thickness` plus a tiny margin (~0.2mm) for wood glue expansion.

---

## 🛹 DECK GEOMETRY & TRUCKS (Right Dock)

The core anatomical dimensions of your fingerboard.

* **Wheelbase (mm):** The distance between the inner truck holes. The most critical dimension for handling.
* **Board Width (mm):** The maximum target width of the deck. Imported DXF outlines scale automatically to match this dimension exactly.
* **Concave Drop (mm):** The vertical depth of the side-to-side concave curve in the center of the board.
* **Concave Length (mm):** The length of the central section where the concave stays at maximum depth before it begins flattening out towards the kicks.
* **Tub Width - Flat (mm):** The width of the totally flat central section. Set to 0 for a continuous U-shape, or increase it to create a flat pocket with steeper rails.
* **Veneer Thickness (mm):** The total physical thickness of the stacked wood veneers.
* **Truck Hole Distance (L / W) & Diameter (mm):** Precision parameters for the hardware mounting pattern. Industry standard for fingerboards is typically ~7.5mm (Length) by ~5.5mm (Width).

---

## 🛞 WHEEL FLARES (Right Dock)

Visible only if **Enable Wheel Flares** is checked. These parameters sculpt the 3D bumps over the wheels to prevent wheelbite and lock in the rider's fingers.

* **Flare Height (mm):** Maximum Z-height of the wheel flare bumps.
* **Flare Length (mm):** Total span of the flare along the board edge.
* **Flare Inward Width (mm):** Distance the flare extends inwards from the edge towards the center of the deck.
* **Offset Y (from truck mm):** Y-axis placement offset of the flare relative to the truck center. Positive values shift the flares towards the tips, negative values shift them towards the center of the wheelbase.

---

## 📐 KICKS (NOSE / TAIL) (Right Dock)

These sliders fine-tune the leverage and pop of the board's ends.
*Note: These parameters are automatically mirrored between Nose and Tail if the `Symmetrical` toggle is active in the 2D Interactive Designer.*

* **Angle (°):** The strict steepness angle of the kick.
* **Length (mm):** The physical length of the kick section.
* **Transition (mm):** The length of the smooth radial bend transitioning from the flat wheelbase into the angled kick.
* **Gap (Flat) (mm):** The flat distance between the outer truck holes and the exact start of the kick transition. Smaller gaps create a snappier, more aggressive pop.

---

## 📏 SHAPER / OUTLINE (Right Dock)

Settings for the 2D cutting guide and the internal Custom Bezier engine.

* **Template Height (mm):** The vertical thickness of the 3D-printed routing template.
* **Edge Rounding (mm):** The radius of the shape's corner fillets (only applies when using the Custom Bezier shape).

### Bezier Handles (Nose & Tail)

These percentage-based parameters dynamically map to the colored handles in the interactive 2D designer, allowing you to fine-tune the shape using math if you prefer not to use the mouse.

* **Yellow (Y %):** Controls the `StraightP` percentage. Determines how long the rails stay parallel before tapering.
* **Red (X % / Y %):** Position of the primary control point (controls the fullness of the "shoulder").
* **Blue (X %):** Position of the secondary control point (controls tip "pointiness" vs. "boxiness").

---
**[⬅️ Previous: UI & Workflow](2-User-Interface-&-Workflow-Guide.md)** | **[🏠 Home](1-Introduction.md)** | **[Next: Custom Shapes (DXF) ➡️](4-Custom-Shapes-DXF.md)**
