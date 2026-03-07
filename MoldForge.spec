# -*- mode: python ; coding: utf-8 -*-
import os
import sys
import shutil
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs, collect_submodules

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

datas = []
datas += collect_data_files('cadquery')
datas += collect_data_files('pyvista')
datas.append(('icon.ico', '.'))

# --- AGGRESSIVE SIZE REDUCTION ---
exclude_list = [
    'PySide6.QtWebEngine', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets',
    'PySide6.QtQml', 'PySide6.QtQuick', 'PySide6.QtQuickWidgets', 'PySide6.QtQuick3D',
    'PySide6.QtBluetooth', 'PySide6.QtMultimedia', 'PySide6.QtSql', 'PySide6.QtNetwork',
    'PySide6.QtPdf', 'PySide6.QtSensors', 'PySide6.QtLocation', 'PySide6.QtPositioning',
    'pandas', 'scipy', 'IPython', 'jupyter', 'notebook', 'tkinter', 'PyQt5', 'PyQt6'
]

a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=exclude_list,
    noarchive=False,
)

pyz = PYZ(a.pure)

# --- NATIVE SPLASH SCREEN CONFIGURATION ---
show_splash = False
splash_obj = None

# Se NON è un Mac, proviamo a configurare lo splash screen
if sys.platform != 'darwin':
    try:
        from PyInstaller.utils.win32 import icon as pyi_icon
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
    except:
        show_splash = False

exe = EXE(
    pyz,
    a.scripts,
    splash,            
    splash.binaries,   
    [],
    exclude_binaries=True,
    name='MoldForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',   
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MoldForge',
)

# =========================================================================
# AZIONE POST-BUILD: COPIA FISICA DELLA LIBRERIA SHAPES
# =========================================================================
# Una volta terminata la compilazione, questo script copia l'intera cartella
# originale dei DXF direttamente nella cartella di destinazione.
print("\n--- ESECUZIONE POST-BUILD: COPIA SHAPES LIBRARY ---")
# 1. Copia shapes_library
source_shapes = os.path.abspath('shapes_library')
dest_shapes = os.path.abspath(os.path.join('dist', 'MoldForge', 'shapes_library'))

if os.path.exists(source_shapes):
    if os.path.exists(dest_shapes):
        shutil.rmtree(dest_shapes)
    shutil.copytree(source_shapes, dest_shapes)
    print(f"SUCCESS: shapes_library copiata con successo in {dest_shapes}")

# 2. Copia l'icona
source_icon = os.path.abspath('icon.ico')
dest_icon = os.path.abspath(os.path.join('dist', 'MoldForge', 'icon.ico'))

if os.path.exists(source_icon):
    shutil.copyfile(source_icon, dest_icon)
    print(f"SUCCESS: icon.ico copiata con successo in {dest_icon}")