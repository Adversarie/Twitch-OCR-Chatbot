# -*- mode: python ; coding: utf-8 -*-
import sys
import os

block_cipher = None

added_files = [
    ('static', 'static'),
    ('templates', 'templates'),
    ('zones.json', '.'),
    ('.env.example', '.'),
    ('LICENSE.txt', '.'),
]

hidden_imports = [
    'uvicorn',
    'uvicorn.logging',
    'uvicorn.loops',
    'uvicorn.loops.auto',
    'uvicorn.protocols',
    'uvicorn.protocols.http',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan',
    'uvicorn.lifespan.on',
    'fastapi',
    'fastapi.staticfiles',
    'fastapi.responses',
    'starlette',
    'starlette.responses',
    'starlette.staticfiles',
    'starlette.middleware',
    'twitchio',
    'twitchio.ext.commands',
    'mss',
    'cv2',
    'numpy',
    'requests',
    'dotenv',
    'ctypes',
    'multiprocessing',
    'config',
    'twitch_client',
    'license_manager',
    'game_detector',
    'log_watcher',
    'ocr_scanner',
    'template_scanner',
    'reaction_engine',
]

a = Analysis(
    ['web.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['tkinter', 'matplotlib', 'scipy', 'IPython', 'notebook'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Standalone directory build (Recommended for fast sub-second startup & Inno Setup installer)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='TwitchOCRBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Windowless: runs as background service and auto-opens browser
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static/app_icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TwitchOCRBot',
)
