# -*- mode: python ; coding: utf-8 -*-
# Hair Skin Plus — PyInstaller build spec
# Run: pyinstaller HairSkinPlus.spec

import os
block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=['d:\\der'],
    binaries=[],
    datas=[
        # Bundle the Flask app source
        ('app.py',          '.'),
        ('schema.sql',      '.'),
        # Bundle templates and static assets
        ('templates',       'templates'),
        ('static',          'static'),
        # Bundle the database (initial snapshot — copied to user dir on install)
        ('medicines.db',    '.'),
    ],
    hiddenimports=[
        'flask',
        'flask.templating',
        'jinja2',
        'jinja2.ext',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.routing',
        'werkzeug.middleware.shared_data',
        'click',
        'sqlite3',
        'tkinter',
        'tkinter.messagebox',
        'importlib.util',
        'email.mime.multipart',
        'email.mime.text',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'PIL', 'cv2', 'scipy'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='HairSkinPlus',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,           # No black console window — GUI only
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='static\\app_icon.ico',   # Uses your clinic icon
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='HairSkinPlus',
)

