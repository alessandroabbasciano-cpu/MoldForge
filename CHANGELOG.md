# Changelog

All notable changes to this project will be documented in this file.

## [1.1.0] - 2026-04-04

**Added:**

- **BEAST MODE**: Added a new option to unlock mechanical limits for extreme geometries.
- **Spoon Kicks (Experimental)**: Added parametric support for concave curvature on the nose and tail.
- **Community Shapes**: Created a dedicated `community_shapes` folder and JSON catalog for community-submitted DXF shapes (requires min 10 upvotes). Added an issue template for submissions.
- **Version Checker**: Implemented an automatic version check function and added a download menu entry.
- **Parametric Bolt Holes**: Truck mounting holes are now fully parametric and hidden under a custom flag for advanced users.

**Changed:**

- **UI Refactoring**: Refactored menus, moved the wheel flares flag to a more logical position, and reviewed the Design Option box.

**Removed:**

- **STL Export**: Removed legacy STL export function (use STEP for high-precision CNC/3D printing).

## [1.0.3] - 2026-03-28

**Fixed:**

- **3D Engine (Topological Crash)**: Resolved a critical `ValueError: Inner wires not allowed` in the OpenCASCADE kernel when generating tapered truck pins with a diameter exceeding 1.9mm. Re-engineered the boolean operation to instantiate and translate a single master pin via `.eachpoint()`.
- **UI / Data Parsing (Race Condition)**: Fixed a signal loop bug where loading asymmetric configuration files (`.json` or `.txt`) would inadvertently trigger the "Symmetrical" checkbox state change, overwriting Tail parameters with Nose values.

**Changed:**

- **GUI (Parameter Limits)**: Increased the maximum allowable Mold Base Width from 70mm to 90mm.

**Documentation:**

- **Custom Shapes (DXF)**: Heavily revised the vector import guidelines. Added critical warnings regarding ghost/hidden layers and imperial/metric unit conflicts.

## [1.0.2] - 2026-03-21

**Fixed:**

- **Female Mold Corners**: Resolved a bug where setting the Mold Base Width equal to the Core Width would incorrectly result in rounded corners on the internal core of the Female Mold.

**Changed:**

- **Optimized 3D Generation**: Removed obsolete geometry-cutting code (`shoulder_tool`) from the Female Mold generation pipeline.

## [1.0.1] - 2026-03-21

**Fixed:**

- **Critical Math Error**: Fixed a logic error in the parametric engine that caused the truck holes to be exactly twice as wide as they should have been (Thanks @KAME3D!).
- **Female Mold Base**: Minor fix to female mold base corners.

## [1.0.0] - 2026-03-21

**Added:**

- Initial Stable Release of MOLD F.O.R.G.E. (Project Exodus completion).
- Native standalone builds for Windows, macOS (Intel & Apple Silicon), and Linux.
