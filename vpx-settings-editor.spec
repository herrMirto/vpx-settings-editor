# -*- mode: python ; coding: utf-8 -*-

import sys
import os

# Determine the platform
if sys.platform == "win32":
    icon_file = "icon.ico"
else:
    icon_file = "icon.icns"

a = Analysis(
    ['main.py'],
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
    a.binaries,
    a.datas,
    [],
    name='vpx-settings-editor',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=icon_file,  # Use the correct icon file for the platform
)

# macOS app bundle
if sys.platform == "darwin":
    app = BUNDLE(
        exe,
        name='VPX-Settings-Editor.app',
        icon='icon.icns',
        bundle_identifier=None,
    )

