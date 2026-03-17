# 🛹 MOLD F.O.R.G.E. - Windows Portable Edition

Welcome to **MOLD F.O.R.G.E.**, the standalone parametric CAD suite engineered exclusively for high-performance fingerboard manufacturing.

This native Windows release marks the completion of *Project Exodus*. It is provided as a **Portable App Folder**. It requires absolutely zero installation, no Python dependencies, does not alter your system registry, and can be run directly from any directory.

---

## 🚀 Quick Start (How to Run)

MOLD F.O.R.G.E. is designed to be completely "plug and play".

1. **Extract** the downloaded `.zip` file.
2. **Move the folder** to a user-accessible location like your **Desktop** or **Documents** folder. *(Do not place it in `C:\Program Files`, as Windows restricts write permissions there).*
3. Open the folder and **double-click** the `MoldForge.exe` file to launch the application.

---

> **⚠️ IMPORTANT: Windows SmartScreen & Antivirus Warnings**
>
> Because MOLD F.O.R.G.E. is a free, open-source indie tool and is not signed with an expensive corporate Microsoft certificate, Windows will likely block it on the first launch.
>
> **To bypass the blue "Windows protected your PC" screen:**
>
> 1. Click on **"More info"** (the small text right below the main warning).
> 2. A new button will appear at the bottom right. Click **"Run anyway"**.
>
> *Note: Some overzealous Antivirus software might falsely flag the `.exe` as suspicious simply because it is a newly compiled open-source executable. This is a common "False Positive" for portable indie software. If your antivirus deletes the file, simply restore it from the quarantine and add the MOLD F.O.R.G.E. folder to your exclusions list.*

---

## 📂 Customization & Assets

Because this is a portable application, you have direct access to the program's vital assets. **Do not delete these!:**

* **`shapes_library/`**: Drop your personal `.dxf` vector files here, and the engine will detect and load them automatically into the application's shape selection menu.
* **`fb_presets.json`**: This JSON file securely stores all your saved 3D printing parameters and mold design presets. *(Note: The app starts clean. This file will not be present initially; it is automatically generated the very first time you save a preset in the UI).* Back this file up if you ever move to a new PC!

---

## 💡 Pro-Tip: Creating a Desktop Shortcut

Since this is a portable app, it won't automatically appear in your Start Menu.
If you want quick access from your desktop:

1. Right-click on `MoldForge.exe`.
2. Select **"Show more options"** (if on Windows 11) -> **"Send to"** -> **"Desktop (create shortcut)"**.
