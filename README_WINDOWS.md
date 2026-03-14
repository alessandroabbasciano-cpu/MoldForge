# 🛹 MOLD F.O.R.G.E. - Windows Portable Edition

Welcome to **Mold Forge**, the parametric CAD suite specifically designed for high-performance fingerboard engineering.

This version is provided as a **Portable Folder**. It requires no formal installation, does not alter your system registry, and can be run directly from any directory.

---

## 🚀 Quick Start (How to Run)

Mold Forge is designed to be "plug and play".

1. **Extract** the downloaded `.zip` file.
2. **Move the folder** to a user-accessible location like your **Desktop** or **Documents** folder. *(Do not place it in `C:\Program Files`, as Windows restricts write permissions there).*
3. Open the folder and **double-click** the `MoldForge.exe` file to launch the application.

---

> **⚠️ IMPORTANT: Windows SmartScreen Warning**
> Because Mold Forge is a free, open-source tool built by the community, it is not signed with an expensive corporate certificate.
> When you run it for the first time, Windows may show a blue **"Windows protected your PC"** screen.
>
> **To bypass this:**
>
> 1. Click on **"More info"** (text right below the main warning).
> 2. A new button will appear at the bottom right. Click **"Run anyway"**.
>
> *Note: Some overzealous Antivirus software might falsely flag the `.exe` as suspicious because it's a new, unknown file created with Python. This is a common "False Positive" for portable indie software. If your antivirus deletes the file, you may need to add the Mold Forge folder to its exclusions list.*

---

## 📂 Customization & Assets

Because this is a portable folder, you have direct access to the program's vital assets. Do not delete these folders!

* **`shapes_library/`**: The heart of your custom designs. Drop your personal `.dxf` vector files here, and Mold Forge will automatically load them into the application's shape selection menu.
* **`wiki/`**: Contains the full documentation and user guides. You can read these offline to master parametric modeling.
* **`fb_presets.json`**: This file stores your saved printing parameters and mold design presets. Back this file up if you move to a new PC!

---

## 💡 Creating a Desktop Shortcut

Since this is a portable app, it won't automatically appear in your Start Menu.
If you want quick access, right-click on `MoldForge.exe`, select **"Show more options"** (on Windows 11) -> **"Send to"** -> **"Desktop (create shortcut)"**.
