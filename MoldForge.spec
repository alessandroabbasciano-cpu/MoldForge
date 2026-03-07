# -*- mode: python ; coding: utf-8 -*-
import os
import shutil
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# --- CONFIGURAZIONE ---
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
datas.append(('splash.png', '.'))

# --- ANALISI ---
a = Analysis(
    ['app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['PySide6.QtWebEngine', 'PySide6.QtWebEngineCore', 'PySide6.QtWebEngineWidgets'],
    noarchive=False,
)
pyz = PYZ(a.pure)

# --- GESTIONE SPLASH SCREEN (FIX PER MAC E NOMI VARIABILI) ---
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

# --- COMPILAZIONE ESEGUIBILE ---
exe = EXE(
    pyz,
    final_splash_obj if show_splash else None, # Corretto: ora il nome corrisponde!
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MoldForge',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
)

# --- COPIA POST-BUILD DELLE RISORSE ---
dest_base = os.path.abspath(os.path.join('dist', 'MoldForge'))
for folder in ['shapes_library', 'wiki_drafts']:
    source = os.path.abspath(folder)
    dest = os.path.join(dest_base, folder)
    if os.path.exists(source):
        if os.path.exists(dest): shutil.rmtree(dest)
        shutil.copytree(source, dest)