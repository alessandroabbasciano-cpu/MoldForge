# 3. The Parametric Engine

This page provides a comprehensive breakdown of every parameter available in the MOLD F.O.R.G.E.

## ⚙️ OUTPUT OPTIONS

These settings determine what the engine builds and toggle specific geometric features for the manufacturing process.

* **Object Type:** Selects which part of the project to generate for export in the 3D viewport.
* `Board_Preview`: A realistic 3D representation of the final deck to check the shape.
* `Male_Mold`: The bottom part of the press (convex).
* `Female_Mold`: The top part of the press (concave).
* `Shaper_Template`: The 2D-outline guide used to cut the board after pressing.
* **Clean Wireframe (Feature Edges):** Toggles the 3D viewport rendering style. When checked, it hides the dense triangular mesh and displays only the sharp feature edges for a cleaner CAD look.
* **Add N/T Indicators:** Embosses 'N' (Nose) and 'T' (Tail) markers on the molds and shaper to prevent accidental misalignment during pressing.
* **Enable SideLocks (Vertical Print):** Generates interlocking side tabs on the mold halves. These prevent the parts from sliding sideways when applying heavy pressure with a vise.
* **Add Top Shaper Shell:** Generates an additional mating top shell next to the Shaper Template. This allows you to "sandwich" the wood veneers during the trimming phase, preventing splintering.
* **Base Reinforcement (AddFillet):** Adds a curved fillet where the mold core meets the base plate to prevent stress fractures.
* **Fillet Radius (mm):** The radius of the base reinforcement curve. Appears only when the reinforcement toggle is active.
* **Add Guide Holes:** Generates vertical holes through the mold for metal alignment pins (e.g., M6 threaded rods).
* **Guide Diameter (mm):** The diameter of the alignment pin holes. Appears only when guide holes are enabled.
* **Enable Wheel Flares:** Toggles the generation of 3D wheel flares on the deck surface. Activating this makes the "WHEEL FLARES" group visible in the right panel.
* **Truck Pins (Molds):** Replaces the through-holes with small embossing marking pins on the Male and Female molds to help align the veneer stack before pressing.
* **Truck Pins (Shaper):** Replaces the through-holes with marking pins on the Shaper Template to ensure your cutting guide is perfectly centered.

---

## 🎨 SHAPE STYLE / PRESETS

* **Select Shape:** Defines the source of the board's outline.
* `Custom`: Uses the internal interactive Bezier mathematical generator.
* `[Filename]`: Loads a specific DXF vector outline from the `shapes_library` folder.
* **Shape Shift Y (mm):** Shifts the DXF shape along the length axis. This is vital for asymmetrical boards (like Fishtails) where the visual center does not align with the truck holes.
* **Load Preset:** A dropdown to instantly load a pre-configured deck and mold setup from your local JSON database.
* **Save / Delete Preset:** Buttons to permanently save your current configuration to the database or remove it.

---

## 📦 MOLD DIMENSIONS

These settings control the overall physical size and structural thickness of the 3D printed mold blocks.

* **Mold Length (mm):** The total physical length of the mold block. It must be longer than your deck to ensure the Nose and Tail are fully supported.
* **Core Width (mm):** The width of the elevated central pressing core. It must be wider than your deck to ensure even pressure.
* **Base Height (mm):** The thickness of the solid structural foundation plate that absorbs the clamping force.
* **Base Width (mm):** The total width of the mold block, including the side shoulders. *Pro Tip: Set this equal to 'Core Width' to create flush, flat sides for vertical printing.*
* **Min. Core Thickness (mm):** The thickness of the core at its lowest/thinnest point.
* **Mold Gap (mm):** The modeled distance between the male and female molds. Usually equals your veneer thickness plus a tiny margin for glue.

---

## 🔩 TRUCKS HOLES

Precision parameters for the hardware mounting pattern.

* **Hole Distance (Length) (mm):** The longitudinal distance between the two holes in a single truck mount (industry standard is ~7.5mm).
* **Hole Distance (Width) (mm):** The lateral distance between the two holes (industry standard is ~5.5mm).
* **Hole Diameter (mm):** The diameter of the truck mounting holes. Default is 1.7mm for a tight fit with standard fingerboard screws.

---

## 🛹 DECK GEOMETRY

These parameters define the fundamental curvature of your fingerboard deck.

* **Wheelbase (mm):** Distance between the inner truck holes.
* **Board Width (mm):** The maximum target width of the deck. Imported DXF outlines scale automatically to match this dimension.
* **Concave Drop (mm):** The vertical depth of the concave curve in the center of the board.
* **Concave Length (mm):** The length of the central section where the concave stays at maximum depth before smoothly flattening out towards the kicks.
* **Tub Width - Flat (mm):** The width of the totally flat central section. Set to 0 for a continuous "U-shape", or increase for a flat pocket with steeper rails.
* **Veneer Thickness (mm):** The total physical thickness of the stacked wood veneers.

---

## 🛞 WHEEL FLARES

Visible only if **Enable Wheel Flares** is checked in the Output Options.

* **Flare Height (mm):** Maximum Z-height of the wheel flare bumps.
* **Flare Length (mm):** Total span of the flare along the board edge.
* **Flare Inward Width (mm):** Distance the flare extends inwards from the edge towards the center.
* **Offset Y (from truck mm):** Y-axis placement offset of the flare relative to the truck center. Positive moves it towards the tips, negative towards the center of the wheelbase.

---

## 📐 KICKS (NOSE / TAIL)

These sliders fine-tune the leverage and steepness of the board's ends. **Note:** Parameters are automatically mirrored between Nose and Tail if the `Symmetrical` toggle is active in the Interactive Designer.

* **Nose/Tail Angle (°):** Steepness angle of the kick.
* **Nose/Tail Length (mm):** Physical length of the kick section.
* **Nose/Tail Transition (mm):** Length of the smooth radial bend transitioning from the flat wheelbase into the kick.
* **Nose/Tail Gap (Flat) (mm):** The flat distance between the outer truck holes and the start of the kick transition. Smaller gaps create a snappier, more aggressive pop.

---

## 📏 SHAPER / OUTLINE

Settings for the 2D cutting guide and the internal Custom Bezier engine.

* **Template Height (mm):** The vertical thickness of the 3D-printed routing template.
* **Edge Rounding (mm):** Radius of the shape's corner fillets (only applies when using the Custom Bezier shape).

### Bezier Handles (Nose & Tail)

These parameters dynamically map to the colored handles in the interactive 2D designer.

* **Yellow (Y %):** Controls the `StraightP` percentage. Determines how long the rails stay parallel before tapering.
* **Red (X %):** X-axis position of the primary control point (controls "shoulder" fullness).
* **Red (Y %):** Y-axis position of the primary control point.
* **Blue (X %):** X-axis position of the secondary control point (controls tip "pointiness" or "boxiness").

---
**[⬅️ Previous: UI & Workflow](2-User-Interface-&-Workflow-Guide.md)** | **[🏠 Home](1-Introduction.md)** | **[Next: Custom Shapes (DXF) ➡️](4-Custom-Shapes-DXF.md)**
