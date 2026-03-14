# 🛹 MOLD F.O.R.G.E. - Linux Portable Edition

Welcome to **Mold Forge**, the parametric CAD suite specifically designed for high-performance fingerboard engineering.

This version is provided as a **Portable Folder**. It requires no formal installation, does not alter your system files, and can be run directly from any directory (or even a USB drive).

---

## 🚀 Quick Start (How to Run)

Mold Forge is designed to be "plug and play".

1. **Extract** the downloaded `.zip` file to a permanent location (e.g., your Desktop or Documents folder).
2. Open the extracted folder.
3. **Double-click** the `MoldForge` executable file to launch the application!

---

> **⚠️ Note on Execution Permissions**
> If double-clicking doesn't work (or if it opens the file as a text document), your archive manager might have stripped the execution permissions during extraction. You can fix this easily in two ways:
>
> **Via GUI:**
> Right-click the `MoldForge` file -> **Properties** -> **Permissions**, and check **"Allow executing file as program"** (wording may vary depending on your desktop environment).
>
> **Or via Terminal:**
>
> 1. Open your terminal.
> 2. Navigate to the extracted folder: `cd /path/to/MoldForge-Linux-Portable`
> 3. Make the file executable: `chmod +x MoldForge`
> 4. Run the app: `./MoldForge`

---

## 📂 Customization & Assets

Because this is a portable folder, you have direct access to the program's vital assets. Do not delete these folders!

* **`shapes_library/`**: The heart of your custom designs. Drop your personal `.dxf` vector files here, and Mold Forge will automatically load them into the application's shape selection menu.
* **`wiki/`**: Contains the full documentation and user guides. You can read these offline to master parametric modeling.
* **`fb_presets.json`**: This file stores your saved printing parameters and mold design presets. Back this file up if you move to a new PC!

---

## 🛠️ Detailed Troubleshooting

Mold Forge bundles its own Python environment and core libraries (like VTK and PySide6). However, it relies on your system for basic graphical output. If you encounter issues, check the solutions below:

### 1. The app doesn't start (Missing Qt platform plugin "xcb")

Most modern Linux distributions (like Ubuntu 24.04+ or Fedora) use Wayland by default. Mold Forge is configured to force X11 (`xcb`) compatibility for maximum 3D rendering stability. If your system is heavily stripped down, you might be missing basic X11 compatibility libraries.

* **Fix (Ubuntu/Debian/Mint):** Open the terminal and install the missing legacy libraries:
  `sudo apt install libxcb-cursor0 libxcb-icccm4 libxcb-keysyms1 libxcb-image0`
* **Fix (Arch Linux):**
  `sudo pacman -S xcb-util-cursor xcb-util-wm xcb-util-keysyms xcb-util-image`

### 2. Terminal shows a "KeyError: '_PYI_SPLASH_IPC'" warning

If you run the app via terminal and see an error about the bootloader failing to initialize the splash screen, **do not worry!** This is completely harmless. It simply means your system lacks a specific library to draw the initial loading image. The main CAD engine and the user interface will still load and function perfectly a few seconds later.

### 3. Fontconfig warnings in the terminal

Warnings like `"unknown element reset-dirs"` are standard Linux background noise related to how your system manages fonts. They do not affect Mold Forge's performance or functionality. You can safely ignore them.

---

## 💡 Pro-Tip: Adding Mold Forge to your Application Menu

If you want Mold Forge to appear in your system's application launcher (like a standard installed app), you can manually create a `.desktop` file.
*Note: Only do this if you plan to keep the Mold Forge folder in a fixed location, as moving the folder later will break the shortcut.*

1. Create a new text file named `moldforge.desktop` in `~/.local/share/applications/`
2. Paste the following text into it (make sure to replace `/path/to/...` with your actual absolute paths):

```ini
[Desktop Entry]
Version=1.0
Name=MOLD F.O.R.G.E.
Comment=Parametric Fingerboard CAD
Exec=/path/to/MoldForge-Linux-Portable/MoldForge
Icon=/path/to/MoldForge-Linux-Portable/icon.png
Terminal=false
Type=Application
Categories=Graphics;3DGraphics;Engineering;
