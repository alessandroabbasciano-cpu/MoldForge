import os
import shutil
import sys
import re
from PyInstaller.utils.hooks import collect_all

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

# Collect complex 3D libraries
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
    noarchive=False,
)

# --- MACOS VTK DUPLICATE PURGE ---
# REQUIRED: Prevents the infinite freeze on macOS GUI initialization
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

exe = EXE( # type: ignore
    pyz, 
    a.scripts, 
    [], 
    exclude_binaries=True, 
    name='MoldForge',
    debug=False, 
    bootloader_ignore_signals=False, 
    strip=False, 
    upx=True, 
    console=True, 
    icon='icon.ico'
)

coll = COLLECT( # type: ignore
    exe, 
    a.binaries, 
    a.zipfiles, 
    a.datas, 
    strip=False, 
    upx=True, 
    upx_exclude=[], 
    name='MoldForge_Bin'
)

# Post-build file management
release_dir = os.path.abspath(os.path.join('dist', 'MOLDFORGE_RELEASE'))
built_dir = os.path.abspath(os.path.join('dist', 'MoldForge_Bin'))

if os.path.exists(release_dir):
    shutil.rmtree(release_dir)

os.rename(built_dir, release_dir)

# Copy necessary assets
for folder in ['shapes_library', 'wiki_drafts']:
    source = os.path.abspath(folder)
    dest = os.path.join(release_dir, folder)
    if os.path.exists(source):
        shutil.copytree(source, dest)

for file in ['icon.ico', 'icon.png']:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(release_dir, file))