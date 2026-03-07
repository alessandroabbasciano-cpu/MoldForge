# -*- mode: python ; coding: utf-8 -*-
import os
import shutil
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# --- CONFIGURAZIONE E IMPORT ---
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

# --- GESTIONE SPLASH SCREEN ---
show_splash = False
final_splash_obj = None

if sys.platform != 'darwin':
    try:
        from PyInstaller.building.api import Splash
        final_splash_obj = Splash(
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

# --- FIX: NOME ESEGUIBILE TEMPORANEO (Definito PRIMA dell'uso!) ---
exe_name = 'MoldForgeApp' if sys.platform != 'win32' else 'MoldForge'

# --- COMPILAZIONE ESEGUIBILE (FIX MAC NONE-TYPE) ---
if show_splash and final_splash_obj:
    exe = EXE(
        pyz,
        final_splash_obj,
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

# --- GESTIONE POST-BUILD ---
release_dir = os.path.abspath(os.path.join('dist', 'MOLDFORGE_RELEASE'))
if os.path.exists(release_dir):
    shutil.rmtree(release_dir)
os.makedirs(release_dir)

ext = '.exe' if sys.platform == 'win32' else ''
current_exe = os.path.join('dist', exe_name + ext)
if os.path.exists(current_exe):
    shutil.move(current_exe, os.path.join(release_dir, 'MoldForge' + ext))

for folder in ['shapes_library', 'wiki_drafts']:
    source = os.path.abspath(folder)
    dest = os.path.join(release_dir, folder)
    if os.path.exists(source):
        shutil.copytree(source, dest)

for file in ['icon.ico', 'icon.png']:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(release_dir, file))