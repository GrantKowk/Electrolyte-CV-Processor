# -*- mode: python ; coding: utf-8 -*-
# Portable onefile build. PyInstaller's normal matplotlib hook supplies mpl-data;
# only the QtAgg and explicit save backends used by the application are forced.
from pathlib import Path

packaging_dir = Path(SPECPATH).resolve()
project_dir = packaging_dir.parent
hidden = [
    'matplotlib.backends.backend_qtagg',
    'matplotlib.backends.backend_agg',
    'matplotlib.backends.backend_pdf',
    'matplotlib.backends.backend_svg',
]

a = Analysis(
    [str(project_dir / 'main.py')],
    pathex=[str(project_dir)],
    binaries=[],
    datas=[(str(project_dir / 'assets'), 'assets')],
    hiddenimports=hidden,
    hookspath=[], hooksconfig={}, runtime_hooks=[],
    excludes=['pytest'], noarchive=False, optimize=0,
)
pyz = PYZ(a.pure)
exe = EXE(
    pyz, a.scripts, a.binaries, a.datas, [],
    name='Electrolyte CV Processor',
    debug=False, bootloader_ignore_signals=False, strip=False, upx=False,
    console=False, disable_windowed_traceback=False,
    icon=str(project_dir / 'assets' / 'app_icon.ico'),
    version=str(packaging_dir / 'version_info.txt'),
)
