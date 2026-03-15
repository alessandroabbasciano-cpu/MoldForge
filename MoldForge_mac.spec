import os
import shutil
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

# Standard collection for CAD and 3D libraries
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

# 1. Internal executable creation (console=False to unlock Mac graphics)
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
    console=False, 
    icon='icon.ico'
)

# 2. Dependency collection
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

# 3. Official Apple .app bundle creation (Graphics wrapper)
app = BUNDLE( # type: ignore
    coll,
    name='MoldForge.app',
    icon='icon.ico',
    bundle_identifier='com.moldforge.app',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True'
    }
)

# --- 4. FINAL HYBRID FOLDER CONSTRUCTION ---
release_dir = os.path.abspath(os.path.join('dist', 'MOLDFORGE_RELEASE'))
built_dir = os.path.abspath(os.path.join('dist', 'MoldForge_Bin'))
if os.path.exists(release_dir):
    shutil.rmtree(release_dir)
os.makedirs(release_dir)

app_source = os.path.abspath(os.path.join('dist', 'MoldForge.app'))
app_dest = os.path.join(release_dir, 'MoldForge.app')
if os.path.exists(app_source):
    shutil.move(app_source, app_dest)

if os.path.exists(built_dir):
    shutil.rmtree(built_dir)

# Copy user-facing folders alongside the App
for folder in ['shapes_library', 'wiki']:
    source = os.path.abspath(folder)
    dest = os.path.join(release_dir, folder)
    if os.path.exists(source):
        shutil.copytree(source, dest)

# Copy text files and presets alongside the App
for file in ['icon.ico', 'icon.png', 'README_MAC.md', 'fb_presets.json']:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(release_dir, file))