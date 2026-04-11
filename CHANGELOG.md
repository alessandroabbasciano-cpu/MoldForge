# Changelog

All notable changes to this project will be documented in this file.

## [1.2.2] - 2026-04-12

**Fixed:**

* **Geometry Smoothing:** Fixed a regression in the high-res geometry engine where smooth transitions on the kicks were incorrectly rendered as sharp angles. Restored ultra-high resolution curvature for better veneer compression.

**Changed:**

* **SideLocks (Solid Reversion):** Nuked the experimental "grooved/ribbed" structure introduced in v1.2.1. Reverted to 100% solid interlocking blocks to eliminate unnecessary printer head micro-movements and ensure uniform infill.
* **Mechanical Tolerance:** Standardized the X-axis sidelock clearance at a calibrated `0.25mm`. This provides a reliable "sliding fit" that prevents friction without sacrificing structural stability.

## [1.2.1] - 2026-04-11

**Added:**

* **Spoon Kicks Geometry:** Introduced a new 3-Zone geometric logic to support "Spoon Kicks" (3D concave curvature extending into the Nose and Tail). Includes a dynamically visible `Spoon Depth` parameter.
* **Extreme Mode (Unleash The Beast):** Added a global safety override toggle. Removes all topological clamps (-9999 to 9999) for experimental mold design. Automatically disables Live Preview to prevent calculation loops.
* **Cut Base (Flush Sides):** New toggle that forces the Mold Base Width to equal the Core Width, creating perfectly flush sides. Automatically disables guide holes and fillets. Optimized for vertical 3D printing.
* **Marking Truck Pins:** Added toggles for `Truck Pins (Molds)` and `Truck Pins (Shaper)`. Replaces standard through-holes with 0.5mm tapered embossed pins for pilot-hole marking.
* **Dynamic Guide Holes:** Expanded alignment pin configuration. You can now define the `Hole Count` (must be an even number, min. 4) and set explicit X/Y offset distances from the core edges.
* **Community Shapes Store:** Integrated a native `CommunityBrowserDialog` to fetch and download community-designed DXF shapes directly from the GitHub repository. Updates the shape combo-box dynamically.
* **Custom Dimensions Toggle:** Added a UI lock/unlock toggle for standard Truck Hole dimensions to prevent accidental modifications to standard wheelbases.
* **Background Version Checker:** Added a non-blocking background thread (`UpdateCheckerWorker`) that queries the public GitHub API on startup to notify users of new releases, bypassing PyInstaller SSL bundle issues.

**Changed:**

* **STEP Export:** Replaced the legacy `save_stl` function with `export_step` for higher fidelity CAD exports.
* **Boolean Kernel Optimization:** Migrated from surface cuts to solid intersections (`intersect()`) for Shapers and Wood Sheets. This ensures topological stability when generating complex Spoon Kick geometries.
* **SideLocks Refactoring:** Reduced clearance to `0.25mm` and shortened extension to `6.0mm`. Completely rewrote the generation logic to use a 2-part system (Main Column + Attachment Tab) that dynamically adapts to the mold edge and kick height.
* **UI/UX Polish:** Applied the "Dark Industrial" theme to the Top Menu Bar and Dropdowns. Compressed the vertical margins of all `QGroupBox` elements to eliminate excessive dead space under panel titles.
* **Support Link:** Migrated the donation link from PayPal to Ko-fi.

**Fixed:**

* **Mac OS Deadlocks:** Added critical environment variable patches (`MPLCONFIGDIR`) to prevent `matplotlib` caching from hanging the PyInstaller build on macOS.
* **Zero-Thickness Geometry:** Added safety clamps (`max(0.01)`) to straight kick sections and a sink extension (`1.5mm`) to Truck Pins to prevent OpenCASCADE boolean failures.

## [1.1.0] - 2026-04-04

**Added:**

* **BEAST MODE**: Added a new option to unlock mechanical limits for extreme geometries.
* **Spoon Kicks (Experimental)**: Added parametric support for concave curvature on the nose and tail.
* **Community Shapes**: Created a dedicated `community_shapes` folder and JSON catalog for community-submitted DXF shapes (requires min 10 upvotes). Added an issue template for submissions.
* **Version Checker**: Implemented an automatic version check function and added a download menu entry.
* **Parametric Bolt Holes**: Truck mounting holes are now fully parametric and hidden under a custom flag for advanced users.

**Changed:**

* **UI Refactoring**: Refactored menus, moved the wheel flares flag to a more logical position, and reviewed the Design Option box.

**Removed:**

* **STL Export**: Removed legacy STL export function (use STEP for high-precision CNC/3D printing).

## [1.0.3] - 2026-03-28

**Fixed:**

* **3D Engine (Topological Crash)**: Resolved a critical `ValueError: Inner wires not allowed` in the OpenCASCADE kernel when generating tapered truck pins with a diameter exceeding 1.9mm. Re-engineered the boolean operation to instantiate and translate a single master pin via `.eachpoint()`.
* **UI / Data Parsing (Race Condition)**: Fixed a signal loop bug where loading asymmetric configuration files (`.json` or `.txt`) would inadvertently trigger the "Symmetrical" checkbox state change, overwriting Tail parameters with Nose values.

**Changed:**

* **GUI (Parameter Limits)**: Increased the maximum allowable Mold Base Width from 70mm to 90mm.

**Documentation:**

* **Custom Shapes (DXF)**: Heavily revised the vector import guidelines. Added critical warnings regarding ghost/hidden layers and imperial/metric unit conflicts.

## [1.0.2] - 2026-03-21

**Fixed:**

* **Female Mold Corners**: Resolved a bug where setting the Mold Base Width equal to the Core Width would incorrectly result in rounded corners on the internal core of the Female Mold.

**Changed:**

* **Optimized 3D Generation**: Removed obsolete geometry-cutting code (`shoulder_tool`) from the Female Mold generation pipeline.

## [1.0.1] - 2026-03-21

**Fixed:**

* **Critical Math Error**: Fixed a logic error in the parametric engine that caused the truck holes to be exactly twice as wide as they should have been (Thanks @KAME3D!).
* **Female Mold Base**: Minor fix to female mold base corners.

## [1.0.0] - 2026-03-21

**Added:**

* Initial Stable Release of MOLD F.O.R.G.E. (Project Exodus completion).
* Native standalone builds for Windows, macOS (Intel & Apple Silicon), and Linux.
