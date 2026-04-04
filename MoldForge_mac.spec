import os
import shutil
from PyInstaller.utils.hooks import collect_all

datas = [
    ('shapes_library', 'shapes_library'),
    ('icon.ico', '.'),
    ('icon.png', '.'),
    ('splash.png', '.'),
    ('README_MAC.md', '.')
]
binaries = []
hidden_imports = [
    'cq_model', 'cq_utils', 'custom_widgets', 'file_manager', 
    'params', 'shape_loader', 'ui_builder', 'ui_menus', 
    'ui_panels', 'ui_sync', 'viewer_3d', 'community_browser'
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
    noarchive=False,
    target_arch='arm64',
)

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
    console=False, 
    icon='icon.ico'
)

def filter_datas(d_list):
    filtered = []
    for d in d_list:
        if 'sample_data' in d[0]:
            continue
        filtered.append(d)
    return filtered

a.datas = filter_datas(a.datas)

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

# OFFICIAL MACOS APP BUNDLE
app = BUNDLE( # type: ignore
    coll,
    name='MoldForge.app',
    icon='icon.ico',
    bundle_identifier='com.moldforge.app',
    info_plist={
        'NSPrincipalClass': 'NSApplication',
        'NSHighResolutionCapable': 'True',
        'NSDesktopFolderUsageDescription': 'MoldForge requires access to your Desktop to load custom DXF shapes.',
        'NSDocumentsFolderUsageDescription': 'MoldForge requires access to your Documents to load custom DXF shapes.',
        'NSDownloadsFolderUsageDescription': 'MoldForge requires access to your Downloads to load custom DXF shapes.'
    }
)

release_dir = os.path.abspath(os.path.join('dist', 'MOLDFORGE_RELEASE'))
if os.path.exists(release_dir):
    shutil.rmtree(release_dir)
os.makedirs(release_dir)

app_source = os.path.abspath(os.path.join('dist', 'MoldForge.app'))
app_dest = os.path.join(release_dir, 'MoldForge.app')
if os.path.exists(app_source):
    shutil.move(app_source, app_dest)

for folder in ['shapes_library']:
    source = os.path.abspath(folder)
    dest = os.path.join(release_dir, folder)
    if os.path.exists(source):
        shutil.copytree(source, dest)
        
for file in ['icon.ico', 'icon.png', 'README_MAC.md']:
    if os.path.exists(file):
        shutil.copy(file, os.path.join(release_dir, file))