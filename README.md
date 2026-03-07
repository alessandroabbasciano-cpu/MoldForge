# MOLD F.O.R.G.E. 🛹

**F**ORGE **O**utputs **R**ealistic **G**narly **E**quipment.

![Version](https://img.shields.io/badge/version-V1_Standalone-2ecc71.svg)
![License](https://img.shields.io/badge/license-LGPLv2.1-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)

**MOLD F.O.R.G.E.** is an advanced, standalone parametric CAD suite engineered exclusively for the fingerboard industry. Design custom decks with mathematical precision, tweak transitions in real-time, and export production-ready, press-safe molds directly to your 3D printer.

---

## 🔥 Core Features

- **Dynamic Asymmetry:** Independent nose/tail shaping via interactive 2D Bezier curves.
- **Custom DXF Support:** Drop your custom `.dxf` outlines into the `shapes_library/` folder and the software will dynamically adapt the 3D mesh.
- **Press-Ready Molds:** Automated clearances, precise mold gaps, base fillets, alignment pins, and vertical interlocking sidelocks.
- **Real-Time Sync:** Live 2D/3D visualization with geometric collision prevention.
- **Automated Production:** A dedicated Batch Export system that generates the Male Mold, Female Mold, and Shaper Template in a single sequence.
- **Pro Geometry:** Parametric wheel flares, tub concaves, and D.H.O. (Deck's Helper Opposite) routing templates.

---

## 🛠️ Installation & Setup

MOLD F.O.R.G.E. provides two ways to run the software, depending on your needs:

### 🟢 Method A: Standalone App (For Users & Makers)

*No programming knowledge or Python installation required.*

1. Go to the **Releases** page of this repository.
2. Download the latest `.zip` file for your Operating System (Windows / Linux).
3. Extract the folder, double-click `MoldForge.exe` (or the Linux binary), and start designing.
*(Mac Users: Please read the specific workaround in the Release notes to bypass Apple's Gatekeeper).*

### 🔴 Method B: Source Code (For Developers)

Due to the heavy C++ geometry engine under the hood (CadQuery / OpenCASCADE), standard `pip` installations might fail. Use `miniconda` for a clean, isolated environment:

1. Clone the repository: `git clone https://.../YourUsername/MoldForge.git`
2. Create environment: `conda create -n moldforge python=3.10`
3. Activate: `conda activate moldforge`
4. Install CadQuery: `conda install -c cadquery -c conda-forge cadquery`
5. Install dependencies: `pip install -r requirements.txt`
6. Run: `python app.py`

---

## 📚 Official Documentation (The Mastery Path)

Looking for a deep dive into every parameter, custom DXF import rules, or 3D printing tips?
👉 **[Check out the Official MOLD F.O.R.G.E. Wiki](wiki_drafts/1-Introduction.md)**

The Wiki is structured as a step-by-step course to take you from beginner to master mold maker:

1. **User Interface & Workflow:** Master the 3D viewport and shortcuts.
2. **The Parametric Engine:** A breakdown of every slider and toggle.
3. **Custom Shapes (DXF Guide):** How to import your own vector designs.
4. **3D Printing & Manufacturing:** Print settings, materials, and pressing techniques.
5. **Glossary of Terms:** Skateboard and CAD terminology explained.

### Adding Custom Deck Shapes (Quick Guide)

To use your own deck outlines instead of the parametric Bezier generator:

1. Draw the **entire, closed** outline of your deck in a vector software (like Inkscape or Illustrator), aligned to the Y-axis. *(Do not draw only half!)*
2. Export it as a clean `.dxf` file (use splines/polylines, avoid complex blocks).
3. Place the file inside the `shapes_library/` directory.
4. Relaunch the app. Your shape will automatically appear in the **Shape Style** dropdown menu.

---

## ⚠️ Troubleshooting

- **The 3D viewer is black or crashes on startup:** This is usually caused by outdated graphics drivers or unsupported OpenGL features (like MSAA or SSAO). Ensure your GPU drivers are up to date. The software includes a fallback mechanism, but specific integrated GPUs may still struggle with VTK rendering.
- **Conda fails to find CadQuery:** Ensure you have the `conda-forge` channel prioritized. You can force it by running: `conda config --add channels conda-forge`.

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!  
If you are a developer or a fingerboard maker with ideas for new parametric features, feel free to fork the repository and submit a Pull Request.

---

## 📄 License

- **Source Code:** [LGPLv2.1](https://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html) - Free to use, modify, and distribute.
- **3D Output / Designs:** CC BY-NC-SA 4.0 - Designs generated using the default presets are for personal/non-commercial use unless otherwise stated.

*Developed with passion for the fingerboard community.*
