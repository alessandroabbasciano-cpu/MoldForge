# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import shutil
from PyInstaller.utils.hooks import collect_all

# --- INIZIALIZZAZIONE LISTE ---
datas = [('icon.ico', '.'), ('splash.png', '.')]
binaries = []
hidden_imports = [
    'cq_model', 'cq_utils', 'custom_widgets', 'file_manager', 
    'params', 'shape_loader', 'ui_builder', 'ui_menus', 
    'ui_panels', 'ui_sync', 'viewer_3d'
]

# --- LA SOLUZIONE DEFINITIVA: COLLECT_ALL ---
# Clona le cartelle intere senza rompere i collegamenti interni delle DLL
for pkg in ['cadquery', 'casadi', 'OCP', 'pyvista', 'vtkmodules']:
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hidden_imports += pkg_hiddenimports

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=binaries,
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
            always_on_top=False,
        )
        show_splash = True
    except Exception as e:
        print(f"DEBUG: Splash non configurato: {e}")

exe_name = 'MoldForgeApp' if sys.platform != 'win32' else 'MoldForge'

# --- COMPILAZIONE (MODALITÀ CARTELLA) ---
if show_splash and final_splash_obj:
    exe = EXE(pyz, a.scripts, final_splash_obj, [], exclude_binaries=True, name=exe_name, debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False, icon='icon.ico')
else:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=exe_name, debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False, icon='icon.ico')

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, upx_exclude=[], name='MoldForge_Bin')

# --- GESTIONE POST-BUILD ---
release_dir = os.path.abspath(os.path.join('dist', 'MOLDFORGE_RELEASE'))
built_dir = os.path.abspath(os.path.join('dist', 'MoldForge_Bin'))

if os.path.exists(release_dir):
    shutil.rmtree(release_dir)

os.rename(built_dir, release_dir)

if sys.platform != 'win32':
    old_exe = os.path.join(release_dir, 'MoldForgeApp')
    new_exe = os.path.join(release_dir, 'MoldForge')
    if os.path.exists(old_exe):
        os.rename(old_exe, new_exe)

for folder in ['shapes_library', 'wiki_drafts']:
    source = os.path.abspath(folder)
    dest = os.path.join(release_dir, folder)
    if os.path.exists(source):
        shutil.copytree(source, dest)

for file in ['icon.ico', 'icon.png']:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(release_dir, file))