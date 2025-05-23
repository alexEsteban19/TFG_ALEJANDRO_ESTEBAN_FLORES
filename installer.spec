# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(['login.py','scripts/main.py','scripts/admin_usuarios.py','scripts/configuracion.py','scripts/Facturacion.py','scripts/FunAcreedor.py','scripts/FunCliente.py','scripts/FunProveedor.py','scripts/VO.py'],
             pathex=['.'],
             binaries=[],
             datas=[
                 ('facturas', 'facturas'),
                 ('informes', 'informes'),
                 ('resources/font/sans-sulex/SANSSULEX.ttf', 'resources/font/sans-sulex/'),
                 ('resources/font/toxigenesis/toxigenesis bd.otf', 'resources/font/toxigenesis/'),
                 ('resources/logos/', 'resources/logos/'),
                 ('resources/images/', 'resources/images/'),
                 ('resources/icons/', 'resources/icons/'),
                 ('imagenesCoches', 'imagenesCoches'),
                 ('bd', 'bd'),
                 ('imagenes_usuarios', 'imagenes_usuarios'),
                 ('ManualDeUso','ManualDeUso'),
             ],
             hiddenimports=[
                 "scripts.main",
                 "scripts.FunCliente",
                 "scripts.FunProveedor",
                 "scripts.FunAcreedor",
                 "scripts.configuracion",
                 "scripts.admin_usuarios",
                 "scripts.VO",
                 "scripts.Facturacion"
             ],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='HGC',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          upx_exclude=[],
          runtime_tmpdir=None,
          console=False,
          icon='resources/logos/icon_logo.ico')

coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='HGC')
