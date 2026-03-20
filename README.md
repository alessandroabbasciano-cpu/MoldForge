# 🛹 **MOLD F.O.R.G.E.**

**F**ORGE **O**utputs **R**ealistic **G**narly **E**quipment.

![Version](https://img.shields.io/badge/version-V1.0.0_Standalone-2ecc71.svg)
![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-blue.svg)
![License](https://img.shields.io/badge/license-AGPLv3-red.svg)

**MOLD F.O.R.G.E.** is a professional, standalone parametric CAD suite engineered exclusively for the fingerboard industry.

Moving beyond basic scripts and legacy CAD dependencies, Version 1.0.0 marks the completion of *Project Exodus*. MOLD F.O.R.G.E. is now a 100% native, multi-threaded desktop application powered by **CadQuery (OpenCASCADE)**, **PyVista (VTK)**, and **PySide6**.

Design custom decks with mathematical precision, tweak transitions in real-time without UI freezes, and export production-ready, press-safe molds directly to your 3D printer.

![MOLD FORGE 3D](wiki/assets/ui_overview.png)

---

## 🔥 Core Features

- **⚡ Standalone & Multi-Threaded:** No Python environments or Conda setups required. The heavy CAD geometry engine runs asynchronously in the background, keeping the UI perfectly fluid.
- **📐 Dynamic Asymmetry:** Break free from standard shapes. Sculpt independent nose and tail angles via the interactive 2D Bezier editor.
- **📁 Auto-Scanning DXF Library:** Drop your custom `.dxf` vector outlines (Fishtails, Cruisers, etc.) into the `shapes_library/` folder. The software automatically detects them and dynamically adapts the 3D mesh.
- **🏭 Press-Ready Manufacturing:** Built to withstand the bench vise. The engine calculates precise mold gaps, base structural fillets, hardware alignment pins, and vertical interlocking SideLocks.
- **🔄 Real-Time Sync:** Live 2D/3D visualization with built-in geometric collision prevention.
- **⚙️ Automated Production:** A dedicated Batch Export system generates the Male Mold, Female Mold, and 2D Shaper Template in a single, perfectly aligned sequence.

---

### 🖥️ System Requirements / Requisiti di Sistema

To ensure a smooth 3D rendering and parametric generation experience, please check if your hardware meets these criteria:

| Feature | Minimum Specification | Recommended Specification |
| :--- | :--- | :--- |
| **OS (Windows)** | Windows 10 / 11 (64-bit) | Windows 11 (64-bit) |
| **OS (macOS)** | macOS 11.0 Big Sur (Intel or Apple Silicon) | macOS 13.0+ (M1/M2/M3 chips) |
| **OS (Linux)** | Ubuntu 22.04+ / Modern Distros (X11/XWayland) | Latest Stable Distro |
| **Processor** | Dual-core 64-bit CPU | Quad-core CPU (High single-thread speed) |
| **Memory (RAM)** | 4 GB | **8 GB or more** |
| **Graphics** | OpenGL 2.1 compatible GPU | Dedicated GPU or Apple M-series |
| **Storage** | 500 MB of free space | SSD (for faster asset loading) |

---

## 🚀 Quick Start (Portable Editions)

MOLD F.O.R.G.E. requires **ZERO installation**. It does not alter your system files or registry.

1. Go to the [Releases](../../releases) page and download the `.zip` file for your Operating System (Windows, macOS, or Linux).
2. Extract the folder to a user-accessible location (e.g., your Desktop or Documents).
3. Run the `MoldForge` executable.

> **🍎 macOS Users:** Due to strict Gatekeeper security on unsigned open-source software, you must run a quick terminal command (`xattr -cr`) to un-quarantine the app on first launch. Please refer to the `README_MAC.md` inside the release bundle for the 10-second fix. **Make sure to download the correct `.zip` file (Intel or Apple Silicon) for your specific Mac processor!**

---

## 📚 Documentation & Wiki

Want to master the parametric engine? Read our comprehensive [Official Wiki](link-to-your-wiki) (also included as offline `.md` files in the release bundle):

1. **[User Interface & Workflow](wiki/2-User-Interface-&-Workflow-Guide.md)**
2. **[The Parametric Engine](wiki/3-The-Parametric-Engine.md)**
3. **[Custom Shapes (DXF Integration)](wiki/4-Custom-Shapes-DXF.md)**
4. **[3D Printing & Manufacturing Guide](wiki/5-3D-Printing-Manufacturing.md)**
5. **[Glossary of Terms](wiki/6-Glossary.md)**

---

## ⚠️ Troubleshooting

- **The 3D viewer is black or crashes on startup:** This is usually caused by outdated graphics drivers or unsupported OpenGL features on older machines. Ensure your GPU drivers are up to date, as the PyVista (VTK) rendering engine requires hardware acceleration.
- **False Positive Antivirus Warning (Windows):** Because this is a newly compiled open-source executable, Windows SmartScreen or some Antivirus software might flag it as "unrecognized". Simply click "More Info" -> "Run anyway", or whitelist the folder.

---

## 👨‍💻 For Developers (Building from Source)

If you wish to modify the source code or build the executable yourself:

1. Clone the repository.
2. Install the requirements (we highly recommend using `conda-forge` to easily resolve CadQuery and VTK dependencies).
3. Run `python app.py` to start the software in development mode.
4. Use the provided `.spec` files with PyInstaller to compile the standalone builds.

---

## 🤝 Contributing

Contributions, issues, and feature requests are incredibly welcome!  
If you are a developer, a 3D printing enthusiast, or a fingerboard maker with ideas for new parametric features, feel free to fork the repository and submit a Pull Request.

---

## 📄 License

- **Source Code Engine:** [AGPLv3](https://www.gnu.org/licenses/agpl-3.0.en.html) - Free to study, modify, and distribute. Network usage requires source disclosure.
- **3D Output / Designs:** CC BY-NC-SA 4.0 - Molds and decks generated using the default factory presets are for personal/non-commercial use.

## ☕ Support the Project

MOLD F.O.R.G.E. is developed out of pure passion for the fingerboard community and is 100% free and open-source. However, maintaining a native, multi-platform CAD suite requires significant personal investment... I even unwillingly funded a certain trillion-dollar fruit company...

If this tool streamlines your manufacturing process, saves your brand time and money, or simply helps you press the perfect deck, consider [buying me a beer](https://www.paypal.me/AlessandroAbbasciano).

Your tips directly help cover these mandatory hardware costs, keep the project alive, and fuel future updates. Every little bit is hugely appreciated! 🛹🛠️
