# 5. 3D Printing & Manufacturing Guide

Creating a high-quality fingerboard mold requires more than just a good 3D model. Since the mold will be subjected to significant clamping force, your print settings and material choice are critical for success and safety.

## 🧵 Material Selection

* **PLA / PLA+:**
The most common choice. It is very rigid, which is excellent for maintaining the deck's shape.
However, it can be brittle. Use a high-quality PLA+ for better impact resistance.

* **PETG:**
Offers a good balance between rigidity and toughness.
It's less likely to "snap" than PLA but might flex slightly more under extreme pressure.

* **Tough Resin:**
If using an SLA printer, ensure you use an engineering-grade "Tough" or "ABS-like" resin. Standard resins are too brittle and will shatter under a vise.

## 🛠️ Slicer Settings (Strength is Key)

Do not use standard "decorative" settings. Your mold needs internal structural integrity.

* **Perimeters (Walls):**
4 to 6 walls. Most of the strength comes from the shells.

* **Infill:**
40% to 60% using Gyroid or Cubic patterns. These are isotropic, meaning they provide equal strength in all directions.
Avoid "Grid" or "Lines" as they can collapse under one-dimensional pressure.

* **Top/Bottom Layers:**
At least 5 layers to prevent the vise from crushing the surface.

## 📐 Print Orientation

You have two main strategies for printing MOLD F.O.R.G.E. parts:

1. **Flat Printing (Fast & Easy):**
   * Print the mold halves with the base plate flat on the bed.
   * **Pros:** Very stable, no supports needed.
   * **Cons:** You may see "stair-stepping" (layer lines) on the curves of the deck.

2. **Side Printing (Professional Finish):**
   * Print the mold standing on its side (ensure `MoldCoreWidth` is equal to `MoldBaseWidth` for a flat side surface).
   * **Pros:** The layer lines follow the profile of the board, resulting in much smoother curves and a "glass-like" finish on the wood.
   * **Cons:** Requires a well-leveled bed and potentially a "brim" for stability.

## 🔩 Hardware & Assembly

MOLD F.O.R.G.E. supports two distinct manufacturing workflows depending on your printing strategy and available tools.

### Option A: The "Self-Clamping" Method (Horizontal Printing)

If you print your molds flat and enable the guide holes (`AddGuideHoles`), you do not need an external press or vise.
The mold itself acts as the clamping mechanism.

* **Hardware:** 6x **M6 threaded rods** (or long bolts) with matching nuts and washers.

* **The Process:**
    1. Apply glue between your 5 wood plies.
    2. Place the stack between the Male and Female molds.
    3. Insert the M6 rods through the 6 alignment holes.
    4. Gradually tighten the nuts in a "cross" pattern (like car wheel lugs) to ensure even pressure distribution.
    5. Tighten until the mold halves meet the limit defined by the `MoldGap`.

### Option B: The "External Press" Method (Side Printing)

If you print your molds on their side for a smoother finish, a bench vise or hydraulic press is required.

* **Essential Feature:** Enable **`SideLocks`**. These interlocking tabs are vital to prevent the mold halves from sliding laterally when the vise begins to apply pressure on the stack.

* **The Process:**
    1. Align the veneers between the molds.
    2. Place the entire assembly into the vise.
    3. The `SideLocks` will keep the parts perfectly registered while you tighten the vise.

### 🛹 General Assembly Tips

* **Veneer Alignment:** If `AddMoldTruckPins` is enabled, use the embossed pins to "pierce" the veneers or as a visual reference. This ensures your truck holes stay centered even if the wood shifts slightly under pressure.

* **Curing:** Regardless of the method, keep the deck under pressure for at least 24 hours to allow the glue to set fully and minimize "springback."

* **Release Agent:** A thin layer of wax or a specific release agent on the mold surface will prevent escaped glue from bonding your new deck to the 3D-printed plastic.

## 🪚 Post-Processing

* **Sanding:**
Even with side-printing, a light sanding with 400-800 grit sandpaper on the mold surface will improve the final deck quality.

* **Waxing:**
Applying a bit of wax or a release agent to the mold can prevent the wood glue from sticking to the plastic.

---
**[⬅️ Previous: Custom Shapes (DXF)](4-Custom-Shapes-DXF.md)** | **[🏠 Home](1-Introduction.md)** | **[Next: Glossary ➡️](6-Glossary.md)**
