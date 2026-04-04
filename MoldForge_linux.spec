# -*- mode: python ; coding: utf-8 -*-
import sys
import os
import shutil
from PyInstaller.utils.hooks import collect_all
from PyInstaller.building.splash import Splash

block_cipher = None

# Prepare lists to collect all assets
datas = [
    ('shapes_library', 'shapes_library'),
    ('icon.ico', '.'),
    ('icon.png', '.'),
    ('splash.png', '.'),
    ('README_LINUX.md', '.')
]
binaries = []
hidden_imports = [
    'cq_model', 'cq_utils', 'custom_widgets', 'file_manager', 
    'params', 'shape_loader', 'ui_builder', 'ui_menus', 
    'ui_panels', 'ui_sync', 'viewer_3d', 'community_browser'
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
        excludes=[
        'django',
        'flask',
        'werkzeug',
        'tornado',
        'boto',
        'boto3',
        'botocore',
        'pynamodb',
        'urllib3',
        'IPython',
        'jedi',
        'parso',
        'prompt_toolkit',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

def filter_datas(d_list):
    filtered = []
    for d in d_list:
        if 'sample_data' in d[0]:
            continue
        filtered.append(d)
    return filtered

a.datas = filter_datas(a.datas)

# === LINUX SPECIFIC: Exclude system graphics libraries to prevent OpenGL crashes ===
exclude_prefixes = (
    'libX11', 'libXext', 'libXdamage', 'libXfixes', 'libXrender',
    'libGL', 'libEGL', 'libGLES', 'libstdc++', 'libgcc_s', 
    'libdrm', 'libgbm', 'libglapi', 'libxshmfence'
)
a.binaries = [b for b in a.binaries if not b[0].startswith(exclude_prefixes)]

pyz = PYZ(a.pure) # type: ignore

# Splash Screen Configuration
# Disabled on Linux to prevent X11 BadDrawable/BadWindow crashes during Qt initialization
final_splash_obj = None

# Executable Generation
if final_splash_obj:
    exe = EXE(pyz, a.scripts, final_splash_obj, [], exclude_binaries=True, name='MoldForge', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False, icon='icon.png') # type: ignore
else:
    exe = EXE(pyz, a.scripts, [], exclude_binaries=True, name='MoldForge', debug=False, bootloader_ignore_signals=False, strip=False, upx=True, console=False, icon='icon.png') # type: ignore

coll = COLLECT(exe, a.binaries, a.zipfiles, a.datas, strip=False, upx=True, upx_exclude=[], name='MoldForge_Bin') # type: ignore

# Cleanup and rename output directories
release_dir = os.path.abspath(os.path.join('dist', 'MOLDFORGE_RELEASE'))
built_dir = os.path.abspath(os.path.join('dist', 'MoldForge_Bin'))

if os.path.exists(release_dir):
    shutil.rmtree(release_dir)

os.rename(built_dir, release_dir)

# Copy extra folders not handled by PyInstaller
for folder in ['shapes_library']:
    source = os.path.abspath(folder)
    dest = os.path.join(release_dir, folder)
    if os.path.exists(source):
        shutil.copytree(source, dest)

for file in ['icon.ico', 'icon.png', 'README_LINUX.md']:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(release_dir, file))