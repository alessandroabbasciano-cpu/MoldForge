# 🛹 MOLD F.O.R.G.E. - macOS Portable Edition

Welcome to **Mold Forge**, the parametric CAD suite specifically designed for high-performance fingerboard engineering.

This version is provided as a Portable App Bundle (Native ARM64 for Apple Silicon). It requires no formal installation and can be run directly from any directory.

---

## 🚀 Quick Start (How to Run)

Because Mold Forge is a free, open-source tool and not signed with an expensive Apple Developer certificate, macOS's **Gatekeeper** security will block it by default. Here is how to bypass it safely:

### Method 1: The Terminal Fix (Highly Recommended)

macOS tags downloaded files with a "quarantine" flag. This can sometimes cause macOS to falsely claim the app is "damaged". To remove this restriction instantly:

1. Extract the downloaded `.zip` folder.
2. Open the built-in **Terminal** app on your Mac (Search for it in Spotlight).
3. Type `xattr -cr` *(make sure to leave a space after the 'r'!).*
4. Drag and drop the extracted Mold Forge folder directly into the Terminal window and press **Enter**.
5. You can now open the folder and simply **double-click** the `MoldForge` executable!

### Method 2: The Right-Click Method

If you don't want to use the terminal, you can try bypassing Gatekeeper manually:

1. Extract the folder to your Desktop or Documents.
2. Open the folder, **Right-click** (or hold `Control` and click) on the `MoldForge` executable file.
3. Select **Open** from the context menu.
4. A warning will appear saying the developer cannot be verified. Click the **Open** button anyway.
*(Note: If you just double-click it normally the first time, it won't give you the option to open it. You MUST right-click).*

---

## 📂 Customization & Assets

Because this is a portable folder, you have direct access to the program's vital assets. Do not delete these folders!

* **`shapes_library/`**: Drop your personal `.dxf` vector files here, and Mold Forge will load them automatically.
* **`wiki/`**: Contains the full documentation and user guides.
* **`fb_presets.json`**: This file stores your saved printing parameters and mold design presets.

---

## 💡 Troubleshooting

* **"MoldForge is damaged and can't be opened. You should move it to the Trash."**
  Don't panic! It is not a virus and it is not actually damaged. This is Apple's default error for quarantined open-source software. Follow **Method 1** above to run the `xattr -cr` command on the folder.
* **A Terminal window stays open in the background?**
  Because this is a portable UNIX executable, macOS might open a blank Terminal window behind the app. You can safely ignore it, but **do not close it** until you are done designing, or it will close Mold Forge too.
