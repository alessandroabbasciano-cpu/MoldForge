# MOLD F.O.R.G.E. 🛹

**F**ORGE **O**utputs **R**ealistic **G**narly **E**quipment.

![Version](https://img.shields.io/badge/version-V1_Standalone-2ecc71.svg)
![License](https://img.shields.io/badge/license-LGPLv2.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

**MOLD F.O.R.G.E.** is an advanced, standalone parametric CAD suite engineered exclusively for the fingerboard industry. Design custom decks with mathematical precision, tweak transitions in real-time, and export production-ready, press-safe molds directly to STL.

---

## 🔥 Core Features

- **Dynamic Asymmetry:** Independent nose/tail shaping via interactive 2D Bezier curves.
- **Custom DXF Support:** Drop your custom `.dxf` outlines into the `shapes_library/` folder and the software will dynamically adapt the 3D mesh.
- **Press-Ready Molds:** Automated clearances, precise mold gaps, base fillets, and vertical interlocking sidelocks.
- **Real-Time Sync:** Live 2D/3D visualization with geometric collision prevention (prevents OpenCASCADE core dumps).
- **Pro Geometry:** Parametric wheel flares, tub concaves, and routing shaper templates.

---

## 🛠️ Installation

Due to the heavy C++ geometry engine under the hood (CadQuery / OpenCASCADE), standard `pip` installations might fail on certain operating systems. It is **highly recommended** to use `conda` or `miniconda` for a clean, isolated environment.

### Prerequisites

- [Git](https://git-scm.com/)
- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or Anaconda

### 1. Clone the repository

```bash
git clone [https://github.com/yourusername/Mold-Forge.git](https://github.com/yourusername/Mold-Forge.git)
cd Mold-Forge
```

### 2. Create a fresh Conda environment

```bash
conda create -n moldforge python=3.10
conda activate moldforge
```

### 3. Install CadQuery (Crucial step)

```bash
conda install -c cadquery -c conda-forge cadquery
```

### 4. Install the GUI and Rendering dependencies

```bash
pip install -r requirements.txt
```

---

## 🚀 Usage

Once the environment is activated and dependencies are installed, run the main application file from your terminal:

```bash
python app.py
```

### Adding Custom Deck Shapes

To use your own deck outlines instead of the parametric Bezier generator:

1. Draw **half** of your deck outline in a vector software (like Inkscape or Adobe Illustrator), aligned to the Y-axis.
2. Export it as a clean `.dxf` file (use splines/polylines, avoid complex blocks).
3. Place the file inside the `shapes_library/` directory.
4. Relaunch the app. Your shape will automatically appear in the **Shape Style** dropdown menu.

---

## 🏗️ Architecture Overview

The codebase is structured modularly for easy maintenance and community contributions:

- `app.py`: Main application loop and thread management.
- `cq_model.py`: The CadQuery 3D engine and boolean logic.
- `ui_panels.py` / `ui_menus.py`: PySide6 GUI construction.
- `ui_sync.py`: Logic controller and mechanical constraint validation.
- `viewer_3d.py`: PyVista VTK rendering pipeline.

---

## ⚠️ Troubleshooting

**The 3D viewer is black or crashes on startup:**
This is usually caused by outdated graphics drivers or unsupported OpenGL features (like MSAA or SSAO). Ensure your GPU drivers are up to date. The software includes a fallback mechanism, but specific integrated GPUs may still struggle with VTK rendering.

**Conda fails to find CadQuery:**
Ensure you have the `conda-forge` channel prioritized. You can force it by running: `conda config --add channels conda-forge`.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
If you are a developer or a fingerboard maker with ideas for new parametric features (like different mold locking mechanisms or concave styles), feel free to fork the repository and submit a Pull Request.

---

## 📄 License

- **Source Code:** [LGPLv2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html) - Free to use, modify, and distribute.
- **3D Output / Designs:** CC BY-NC-SA 4.0 - Designs generated using the default presets are for personal/non-commercial use unless otherwise stated.

*Developed with passion for the fingerboard community.*
