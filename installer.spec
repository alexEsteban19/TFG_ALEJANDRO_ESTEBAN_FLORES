# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['login.py'],
             pathex=['.'],
             binaries=[],
             datas=[
                 ('facturas', 'facturas'),
                 ('informes', 'informes'),
                 ('resources/font/sans-sulex/SANSSULEX.ttf', 'resources/font/sans-sulex/'),
                 ('resources/font/toxigenesis/toxigenesis bd.otf', 'resources/font/toxigenesis/'),
                 ('resources/logos/icon_logo.ico', 'resources/logos/'),

             ],
             hiddenimports=[],
             hookspath=[],
             runtime_hooks=[],
             excludes=['resources', 'icons', 'images', 'logos', 'scripts'],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='login',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False)

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='login')
