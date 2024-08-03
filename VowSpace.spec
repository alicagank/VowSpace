# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['VowSpace.py'],
    pathex=[],
    binaries=[],
    datas=[],
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
    [],
    exclude_binaries=True,
    name='VowSpace',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['/Users/alicagank/Desktop/VowSpace/VowSpace/logo-and-icons/icon-256x256.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='VowSpace',
)
app = BUNDLE(
    coll,
    name='VowSpace.app',
    icon='/Users/alicagank/Desktop/VowSpace/VowSpace/logo-and-icons/icon-256x256.ico',
    bundle_identifier=None,
)
