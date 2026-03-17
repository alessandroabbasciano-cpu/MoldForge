# 🛹 MOLD F.O.R.G.E. - Linux Portable Edition

Welcome to **MOLD F.O.R.G.E.**, the standalone parametric CAD suite engineered for high-performance fingerboard manufacturing.

This native Linux release is provided as a **Portable App Folder**. It requires absolutely zero installation, no `apt-get` dependencies, and no Python environments. It does not alter your system files and can be run directly from any directory (or even a USB drive).

---

## 🚀 Quick Start (How to Run)

MOLD F.O.R.G.E. is designed to be completely "plug and play".

1. **Extract** the downloaded `.zip` file to a permanent location (e.g., your `~/Desktop` or `~/Documents` folder).
2. Open the extracted folder.
3. **Double-click** the `MoldForge` executable file to launch the application!

---

> **⚠️ Note on Execution Permissions**
>
> If double-clicking the executable doesn't work (or if your system opens it as a text document), your archive manager likely stripped the execution permissions during extraction. This is a standard Linux security feature. You can fix it easily in two ways:
>
> **Via GUI:**
> Right-click the `MoldForge` file -> **Properties** -> **Permissions** tab, and check the box that says **"Allow executing file as program"** (wording may vary depending on your Desktop Environment like GNOME or KDE).
>
> **Via Terminal (Faster):**
>
> 1. Open your terminal.
> 2. Navigate to the extracted folder: `cd /path/to/MoldForge-Linux-Portable`
> 3. Make the file executable: `chmod +x MoldForge`
> 4. Run the app: `./MoldForge`

---

## 📂 Customization & Assets

Because this is a portable application, you have direct access to the program's vital assets. **Do not delete these!:**

* **`shapes_library/`**: Drop your personal `.dxf` vector files here, and the engine will detect and load them automatically into the application's shape selection menu.
* **`fb_presets.json`**: This JSON file securely stores all your saved 3D printing parameters and mold design presets. *(Note: The app starts clean. This file will not be present initially; it is automatically generated the very first time you save a preset in the UI).* Back this file up if you ever move to a new PC!

---

## 💡 Troubleshooting & Known Terminal Output

If you prefer to launch the application via terminal to read the background logs, you might notice some of the following standard outputs:

### 1. `KeyError: '_PYI_SPLASH_IPC'`

If you see an error regarding the bootloader failing to initialize the splash screen, **do not panic!** This is completely harmless. It simply means your specific Linux distribution is missing a minor graphical library required to draw the initial startup image. The heavy CadQuery geometry engine and the PySide6 user interface will still load and function perfectly a few seconds later.

### 2. Fontconfig Warnings

Warnings such as `unknown element reset-dirs` are standard Linux background noise related to how your specific Desktop Environment manages system fonts. They do not affect the application's performance or CAD capabilities and can be safely ignored.

---

## 🐧 Pro-Tip: Adding MOLD F.O.R.G.E. to your Application Menu

If you want the software to appear natively in your system's application launcher (complete with the icon), you can manually create a `.desktop` shortcut file.
*(Note: Only do this if you plan to keep the extracted folder in a fixed location. Moving the folder later will break the shortcut).*

1. Create a new text file named `moldforge.desktop` inside `~/.local/share/applications/`
2. Paste the following text into it (make sure to replace `/path/to/...` with the actual absolute path to where you extracted the folder):

```ini
[Desktop Entry]
Version=1.0
Name=MOLD F.O.R.G.E.
Comment=Parametric Fingerboard CAD
Exec=/path/to/MoldForge-Linux-Portable/MoldForge
Icon=/path/to/MoldForge-Linux-Portable/icon.png
Terminal=false
Type=Application
Categories=Graphics;Engineering;3DGraphics;
