# -*- mode: python ; coding: utf-8 -*-
import os

# Get the directory where this spec file is located
spec_root = os.path.abspath(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    # Use absolute path to image folder
    datas=[(os.path.join(spec_root, 'image'), 'image')],
    hiddenimports=[],
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
    name='AbyssMacro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Set to True to see debug output
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
