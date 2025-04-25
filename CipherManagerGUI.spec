# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['gui_main.py'],
             pathex=['.'],
             binaries=[],
             datas=[('LICENSE','.'), ('README.md','.'), ('.venv/Lib/site-packages/PyQt6/Qt6/translations',
                    './PyQt6/Qt6/translations')],
             hiddenimports=['pymdownx','pymdownx.emoji'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='CipherManagerGUI',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=False, version='gui/file_version_info', icon='gui/designer/cm-gui.png')
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='CipherManagerGUI')
