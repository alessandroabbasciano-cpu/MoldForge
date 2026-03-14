import os
import shutil
import sys
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

# Standard collection for CAD and 3D libraries without custom filtering
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

pyz = PYZ(a.pure) # type: ignore

# Folder mode build (not an .app bundle)
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

# Post-build management
release_dir = os.path.abspath(os.path.join('dist', 'MOLDFORGE_RELEASE'))
built_dir = os.path.abspath(os.path.join('dist', 'MoldForge_Bin'))

if os.path.exists(release_dir):
    shutil.rmtree(release_dir)

os.rename(built_dir, release_dir)

# Copy necessary external assets directly into the release folder
for folder in ['shapes_library', 'wiki_drafts']:
    source = os.path.abspath(folder)
    dest = os.path.join(release_dir, folder)
    if os.path.exists(source):
        shutil.copytree(source, dest)

for file in ['icon.ico', 'icon.png']:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(release_dir, file))