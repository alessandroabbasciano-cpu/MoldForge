# 1. Welcome to MOLD F.O.R.G.E.

**MOLD F.O.R.G.E.** (Mold FORGE Outputs Realistic Gnarly Equipment) is a professional, standalone parametric CAD suite engineered specifically for high-fidelity fingerboard design and mold generation.

Moving beyond static 3D models and legacy CAD dependencies, this engine gives you complete mathematical control over every single aspect of your fingerboard deck. Whether you are pressing your first wooden deck or running a high-end boutique fingerboard brand, MOLD F.O.R.G.E. bridges the gap between digital design and physical manufacturing.

![MOLD FORGE UI Overview](assets/ui_overview.png)

## 🚀 Core Features

* **⚡ Standalone & Multi-Threaded Engine:** Powered by CadQuery (OpenCASCADE) and PySide6, MOLD F.O.R.G.E. is now a 100% native application. Heavy 3D calculations run in a dedicated background thread, ensuring your interface and 2D/3D viewports never freeze during complex lofting operations.
* **📐 Dynamic Asymmetry:** Break free from standard shapes. Achieve independent nose and tail sculpting using our interactive Bezier curve editor, or import your own custom `.dxf` outlines for immediate 3D generation.
* **🏭 Press-Ready Manufacturing:** Built for the bench vise. The engine automatically calculates crucial physical tolerances, including mold gaps, base reinforcements, vertical print side-locks, and alignment pins to ensure a perfect press every time.
* **🔄 Real-Time Synchronization:** Experience live 2D/3D visualization with built-in geometric collision prevention. Adjust a slider and watch the asynchronous progress bar calculate your new geometry seamlessly.
* **⚙️ Automated Production:** Generate everything you need with a single click. The dedicated Batch Export system simultaneously outputs the Male Mold, Female Mold, and 2D Shaper Template.

![MOLD FORGE UI Overview](assets/ui_overview.jpg)

## 📖 How to Use This Wiki

This documentation is designed to take you from a beginner to a master mold maker. We highly recommend reading through the sections in the following order to fully grasp the power of the parametric engine:

1. **[User Interface & Workflow](2-User-Interface-&-Workflow-Guide.md):** A masterclass on navigating the 3D viewport, using the interactive 2D shape designer, and reading the live console. *Learn to drive before tuning the engine.*
2. **[The Parametric Engine](3-The-Parametric-Engine.md):** A comprehensive breakdown of every slider, toggle, and setting available in the design panels.
3. **[Custom Shapes (DXF Guide)](4-Custom-Shapes-DXF.md):** Step-by-step rules for preparing, exporting, and importing your own vector outlines (like Fishtails or Old School cruisers).
4. **[3D Printing & Manufacturing Guide](5-3D-Printing-Manufacturing.md):** Essential engineering advice on material selection, structural slicer settings, print orientation, and the wood pressing process.
5. **[Glossary of Terms](6-Glossary.md):** A quick reference guide covering skateboard anatomy, mold manufacturing concepts, and CAD terminology.

## 🤝 Open Source & License

Developed with passion and engineering rigor for the fingerboard community.

* **Code Engine License:** [LGPLv2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html) - Free to study, modify, and distribute.
* **3D Output & Designs:** CC BY-NC-SA 4.0 - Molds and decks generated using the default factory presets are for personal/non-commercial use.

Curious about what powers the engine? Check out the **About MOLD F.O.R.G.E.** window in the Help menu for a breakdown of the open-source technologies used.

If this tool helps you craft the perfect deck, consider checking out the **"Support the Project"** link in the app's menu!

---
**[Next: User Interface & Workflow ➡️](2-User-Interface-&-Workflow-Guide.md)**
