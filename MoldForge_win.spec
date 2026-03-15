# -*- mode: python ; coding: utf-8 -*-
import os
import shutil
from PyInstaller.utils.hooks import collect_all

datas = [
    ('shapes_library', 'shapes_library'),
    ('fb_presets.json', '.'),
    ('icon.ico', '.'),
    ('icon.png', '.'),
    ('splash.png', '.'),
    ('README_WINDOWS.md', '.'),
    ('wiki', 'wiki')
]
binaries = []
hidden_imports = [
    'cq_model', 'cq_utils', 'custom_widgets', 'file_manager', 
    'params', 'shape_loader', 'ui_builder', 'ui_menus', 
    'ui_panels', 'ui_sync', 'viewer_3d'
]

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
except Exception as e:
    # Changed from Italian to English
    print(f"Splash screen error: {e}")
    final_splash_obj = None

exe = EXE( # type: ignore
    pyz, 
    a.scripts, 
    final_splash_obj, 
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

release_dir = os.path.abspath(os.path.join('dist', 'MOLDFORGE_RELEASE'))
built_dir = os.path.abspath(os.path.join('dist', 'MoldForge_Bin'))

if os.path.exists(release_dir):
    shutil.rmtree(release_dir)

os.rename(built_dir, release_dir)

for folder in ['shapes_library', 'wiki']:
    source = os.path.abspath(folder)
    dest = os.path.join(release_dir, folder)
    if os.path.exists(source) and not os.path.exists(dest):
        shutil.copytree(source, dest)

for file in ['icon.ico', 'icon.png', 'README_WINDOWS.md']:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(release_dir, file))