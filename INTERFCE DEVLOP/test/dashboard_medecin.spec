# -*- mode: python ; coding: utf-8 -*-
# ============================================================
# MEDSAFE — Spec PyInstaller pour dashboard_medecin.py
# Usage : pyinstaller dashboard_medecin.spec
# ============================================================

import os

# Dossier contenant ce fichier .spec
DOSSIER = os.path.dirname(os.path.abspath(SPEC))

a = Analysis(
    [os.path.join(DOSSIER, 'dashboard_medecin.py')],
    pathex=[DOSSIER],
    binaries=[],
    datas=[
        # (source, destination_dans_le_bundle)
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
    name='MedSafe_Medecin',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,           # Pas de fenêtre console noire
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(DOSSIER, 'mokkt.jpg') if os.path.exists(os.path.join(DOSSIER, 'mokkt.jpg')) else None,
)
