# -*- mode: python ; coding: utf-8 -*-
import os
import shutil
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# --- CONFIGURATION ---
hidden_imports = []
hidden_imports += collect_submodules('cadquery')
hidden_imports += collect_submodules('pyvista')
hidden_imports += collect_submodules('vtkmodules')
hidden_imports += collect_submodules('OCP')

hidden_imports += [
    'cq_model', 'cq_utils', 'custom_widgets', 'file_manager', 
    'params', 'shape_loader', 'ui_builder', 'ui_menus', 
    'ui_panels', 'ui_sync', 'viewer_3d'
]

datas = [('icon.ico', '.'), ('splash.png', '.')]
datas += collect_data_files('cadquery')
datas += collect_data_files('pyvista')

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    noarchive=False,
)
pyz = PYZ(a.pure)

show_splash = False
splash_obj = None

if sys.platform != 'darwin':
    try:
        from PyInstaller.building.api import Splash
        splash_obj = Splash(
            'splash.png',
            binaries=a.binaries,
            datas=a.datas,
            text_pos=None,
            text_size=12,
            minify_script=True,
            always_on_top=True,
        )
        show_splash = True
    except Exception as e:
        print(f"DEBUG: Splash non configurato: {e}")

if show_splash and splash_obj:
    exe = EXE(
        pyz,
        splash_obj,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=exe_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        icon='icon.ico',
    )
else:
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name=exe_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        icon='icon.ico',
    )

# Use a temp name to avoid directory collision
exe_name = 'MoldForgeApp' if sys.platform != 'win32' else 'MoldForge'

exe = EXE(
    pyz,
    final_splash_obj if show_splash else None,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name=exe_name,
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    icon='icon.ico', # This sets the metadata icon
)

# --- POST-BUILD ASSET MANAGEMENT ---
release_dir = os.path.abspath(os.path.join('dist', 'MOLDFORGE_RELEASE'))
if os.path.exists(release_dir):
    shutil.rmtree(release_dir)
os.makedirs(release_dir)

# Move EXE to release folder with final name
ext = '.exe' if sys.platform == 'win32' else ''
current_exe = os.path.join('dist', exe_name + ext)
shutil.move(current_exe, os.path.join(release_dir, 'MoldForge' + ext))

# Copy Folders (Presets/Shapes and Wiki)
for folder in ['shapes_library', 'wiki_drafts']:
    source = os.path.abspath(folder)
    dest = os.path.join(release_dir, folder)
    if os.path.exists(source):
        shutil.copytree(source, dest)

# Copy Files (Icon file for the UI to find it at runtime)
# Many apps need the physical icon file in the folder to show it in the Taskbar/System
for file in ['icon.ico', 'icon.png']:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(release_dir, file))
        print(f"SUCCESS: {file} copied to release folder")