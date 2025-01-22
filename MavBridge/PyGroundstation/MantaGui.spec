# -*- mode: python ; coding: utf-8 -*-

from PyInstaller.utils.hooks import collect_submodules

# Collect submodules for PIL and cv2
hiddenimports = (
                collect_submodules('cv2') + 
                collect_submodules('haversine') + 
                collect_submodules('pymavlink') + 
                collect_submodules('pygame')
                )

a = Analysis(
    ['MantaGui.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hiddenimports,  # Use the collected hiddenimports here
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='MantaGui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
