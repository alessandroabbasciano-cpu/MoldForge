# 🛹 MOLD F.O.R.G.E. - macOS Portable Edition

Welcome to **MOLD F.O.R.G.E.**, the standalone parametric CAD suite engineered exclusively for high-performance fingerboard manufacturing.

This native macOS release marks the completion of *Project Exodus*. It is provided as a **Portable App Bundle (Available for both Apple Silicon M-Series and older Intel Macs)**. It requires absolutely zero installation, no Python environments, and can be run directly from any folder.

*(Make sure you downloaded the correct `.zip` file for your specific Mac processor!)*

---

## 🚀 Quick Start & Gatekeeper Bypass

Because MOLD F.O.R.G.E. is a free, open-source indie tool and is not signed with an expensive corporate Apple Developer certificate, macOS's **Gatekeeper** security will block it by default, often falsely claiming the app is "damaged."

**Do not panic. This is standard Apple behavior for unsigned open-source software.** Here is the 10-second permanent fix:

### Method 1: The Terminal Fix (Highly Recommended & Fastest)

macOS tags downloaded files from the internet with a strict "quarantine" flag. We just need to remove it.

1. Extract the downloaded `.zip` folder.
2. Open the built-in **Terminal** app on your Mac (Search for it in Spotlight).
3. Type `xattr -cr ` *(make sure to leave a single space after the 'r'!)*
4. Drag and drop the extracted Mold Forge folder directly into the Terminal window and press **Enter**.
5. You can now open the folder and simply **double-click** the `MoldForge` executable to start designing!

### Method 2: The Right-Click Method (Alternative)

If you prefer not to use the terminal:

1. Extract the folder to your Desktop or Documents.
2. Open the folder, **Right-click** (or hold `Control` and click) on the `MoldForge` executable file.
3. Select **Open** from the context menu.
4. A warning will appear. Click the **Open** button anyway.
*(Note: If you just double-click it normally the first time, macOS won't give you the option to open it. You MUST right-click).*

---

## 📂 Customization & Assets

Because this is a portable application, you have direct access to the program's vital assets. **Do not delete these!:**

* **`shapes_library/`**: Drop your personal `.dxf` vector files here, and the engine will detect and load them automatically into the application's shape selection menu.
* **`fb_presets.json`**: This JSON file securely stores all your saved 3D printing parameters and mold design presets. *(Note: The app starts clean. This file will not be present initially; it is automatically generated the very first time you save a preset in the UI).* Back this file up if you ever move to a new PC!

---

## 💡 Troubleshooting

* **A Terminal window stays open in the background?**
  Because this is a native UNIX executable, macOS might open a blank Terminal window behind the main application. You can safely ignore it, but **do not close it**, or it will instantly terminate the MOLD F.O.R.G.E. 3D engine as well. Just let it run in the background.
