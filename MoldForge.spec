# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import shutil
import re
from PyInstaller.utils.hooks import collect_all

block_cipher = None

# Prepare lists to collect all assets
datas = [
    ('shapes_library', 'shapes_library'),
    ('fb_presets.json', '.'),
    ('icon.ico', '.'),
    ('splash.png', '.')
]
binaries = []
hidden_imports = [
    'cq_model', 'cq_utils', 'custom_widgets', 'file_manager', 
    'params', 'shape_loader', 'ui_builder', 'ui_menus', 
    'ui_panels', 'ui_sync', 'viewer_3d'
]

# Use collect_all for complex libraries (VTK, CadQuery, etc.)
for pkg in ['cadquery', 'casadi', 'OCP', 'pyvista', 'vtkmodules']:
    pkg_datas, pkg_binaries, pkg_hiddenimports = collect_all(pkg)
    datas += pkg_datas
    binaries += pkg_binaries
    hidden_imports += pkg_hiddenimports

a = Analysis( # type: ignore
    ['app.py'],
    pathex=[],
    binaries=binaries,     
    datas=datas,           
    hiddenimports=hidden_imports, 
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

import vtkmodules
vtk_path = os.path.dirname(vtkmodules.__file__)
a.datas += Tree(vtk_path, prefix='vtkmodules') # type: ignore

# --- LINUX HOST SYSTEM LIBRARY EXCLUSION ---
if sys.platform == 'linux':
    exclude_prefixes = (
        'libX11', 'libXext', 'libXdamage', 'libXfixes', 'libXrender',
        'libGL', 'libEGL', 'libGLES', 'libstdc++', 'libgcc_s', 
        'libdrm', 'libgbm', 'libglapi', 'libxshmfence'
    )
    a.binaries = [b for b in a.binaries if not b[0].startswith(exclude_prefixes)]

# --- MACOS VTK DUPLICATE PURGE ---
if sys.platform == 'darwin':
    filtered_binaries = []
    for binary in a.binaries:
        dest, src, typecode = binary
        # Ignore unversioned VTK libraries to prevent Objective-C class conflicts
        if "libvtk" in dest and dest.endswith(".dylib") and not re.search(r'-\d+\.\d+', dest):
            continue
        filtered_binaries.append(binary)
    a.binaries = filtered_binaries

pyz = PYZ(a.pure) # type: ignore

show_splash = False
final_splash_obj = None

if sys.platform != 'darwin':
    try:
        final_splash_obj = Splash( # type: ignore
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
        print(f"Splash screen error: {e}")

exe_name = 'MoldForgeApp' if sys.platform != 'win32' else 'MoldForge'

if show_splash and final_splash_obj:
    exe = EXE(pyz, a.scripts, final_splash_obj, [], exclude_binaries=True, name=exe_name, debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False, icon='icon.ico') # type: ignore
else:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name=exe_name, debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False, icon='icon.ico') # type: ignore

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, upx_exclude=[], name='MoldForge_Bin') # type: ignore

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