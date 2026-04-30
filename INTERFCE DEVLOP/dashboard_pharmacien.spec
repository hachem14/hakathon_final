# -*- mode: python ; coding: utf-8 -*-
# ============================================================
# MEDSAFE — Spec PyInstaller pour dashboard_pharmacien.py
# Usage : pyinstaller dashboard_pharmacien.spec
# ============================================================

import os

DOSSIER = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(DOSSIER, 'dashboard_pharmacien.py')],
    pathex=[DOSSIER],
    binaries=[],
    datas=[
        (os.path.join(DOSSIER, 'mokkt.jpg'),           '.'),
        (os.path.join(DOSSIER, 'medsafe_cabinet.db'),  '.'),
    ],
    hiddenimports=[
        'customtkinter',
        'PIL',
        'PIL.Image',
        'PIL._tkinter_finder',
        'sqlite3',
    ],
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
    name='MedSafe_Pharmacien',
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
    icon=os.path.join(DOSSIER, 'mokkt.jpg') if os.path.exists(os.path.join(DOSSIER, 'mokkt.jpg')) else None,
)
