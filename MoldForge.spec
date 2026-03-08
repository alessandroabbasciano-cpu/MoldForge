# -*- mode: python ; coding: utf-8 -*-
import os
import shutil
import sys
import glob
from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_dynamic_libs

# --- CONFIGURAZIONE E IMPORT ---
hidden_imports = []
hidden_imports += collect_submodules('cadquery')
hidden_imports += collect_submodules('pyvista')
hidden_imports += collect_submodules('vtkmodules')
hidden_imports += collect_submodules('OCP')
hidden_imports += collect_submodules('casadi')

hidden_imports += [
    'cq_model', 'cq_utils', 'custom_widgets', 'file_manager', 
    'params', 'shape_loader', 'ui_builder', 'ui_menus', 
    'ui_panels', 'ui_sync', 'viewer_3d'
]

datas = [('icon.ico', '.'), ('splash.png', '.')]
datas += collect_data_files('cadquery')
datas += collect_data_files('pyvista')
datas += collect_data_files('casadi')

binaries = []
binaries += collect_dynamic_libs('casadi')

# --- FIX DEFINITIVO DLL CONDA PER WINDOWS ---
pathex_dirs = []
if sys.platform == 'win32':
    # sys.prefix punta alla root dell'ambiente Conda
    conda_bin_dir = os.path.join(sys.prefix, 'Library', 'bin')
    pathex_dirs.append(conda_bin_dir)
    
    if os.path.exists(conda_bin_dir):
        print(f"DEBUG: Trovata cartella bin di Conda: {conda_bin_dir}")
        # FORZA BRUTA: Prendi TUTTE le DLL della cartella, nessuna esclusa
        for dll in glob.glob(os.path.join(conda_bin_dir, '*.dll')):
            binaries.append((dll, '.'))
    else:
        print("ATTENZIONE: Cartella Library/bin di Conda non trovata!")

a = Analysis(
    ['app.py'],
    pathex=pathex_dirs,  # Aiuta PyInstaller a risolvere i percorsi interni
    binaries=binaries,   # Qui ci sono TUTTE le DLL di Conda
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

exe_name = 'MoldForgeApp' if sys.platform != 'win32' else 'MoldForge'

# --- COMPILAZIONE (MODALITÀ CARTELLA / ONEDIR) ---
if show_splash and final_splash_obj:
    exe = EXE(
        pyz,
        a.scripts,
        final_splash_obj,
        [],
        exclude_binaries=True, # <--- Questo dice a PyInstaller di NON compattare tutto
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
        [],
        exclude_binaries=True,
        name=exe_name,
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        icon='icon.ico',
    )

# Questo blocco genera la cartella con l'eseguibile e _internal
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='MoldForge_Bin'
)

# --- GESTIONE POST-BUILD ---
release_dir = os.path.abspath(os.path.join('dist', 'MOLDFORGE_RELEASE'))
built_dir = os.path.abspath(os.path.join('dist', 'MoldForge_Bin'))

if os.path.exists(release_dir):
    shutil.rmtree(release_dir)

# Trasforma la cartella base in quella di rilascio
os.rename(built_dir, release_dir)

# Rinomina l'eseguibile per Mac/Linux per pulizia
if sys.platform != 'win32':
    old_exe = os.path.join(release_dir, 'MoldForgeApp')
    new_exe = os.path.join(release_dir, 'MoldForge')
    if os.path.exists(old_exe):
        os.rename(old_exe, new_exe)

# Copia cartelle utente e icone
for folder in ['shapes_library', 'wiki_drafts']:
    source = os.path.abspath(folder)
    dest = os.path.join(release_dir, folder)
    if os.path.exists(source):
        shutil.copytree(source, dest)

for file in ['icon.ico', 'icon.png']:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(release_dir, file))