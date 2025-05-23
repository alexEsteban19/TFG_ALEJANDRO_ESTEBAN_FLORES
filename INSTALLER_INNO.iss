[Setup]
AppName=HGC
AppVersion=1.0
DefaultDirName={pf}\HGC
DefaultGroupName=HGC
OutputBaseFilename=HGC Installer
Compression=lzma
SolidCompression=yes
SetupIconFile=resources\logos\icon_logo.ico
UninstallDisplayIcon=resources\logos\UNINSTALL.ico
PrivilegesRequired=admin

[Files]
; Archivos principales
Source: "dist\HGC\*"; DestDir: "{app}"; Flags: recursesubdirs

; Fuente
Source: "resources\font\sans-sulex\SANSSULEX.ttf"; DestDir: "{fonts}"; FontInstall: "SANS SULEX"; Flags: onlyifdoesntexist uninsneveruninstall
Source: "resources\font\toxigenesis\toxigenesis bd.otf"; DestDir: "{fonts}"; FontInstall: "Toxigenesis Rg"; Flags: onlyifdoesntexist uninsneveruninstall

; Carpetas de datos internas
Source: "dist\HGC\facturas"; DestDir: "{app}\_internal\facturas"; Flags: recursesubdirs createallsubdirs
Source: "dist\HGC\informes"; DestDir: "{app}\_internal\informes"; Flags: recursesubdirs createallsubdirs
Source: "dist\HGC\bd"; DestDir: "{app}\_internal\bd"; Flags: recursesubdirs createallsubdirs
Source: "dist\HGC\imagenes_usuarios"; DestDir: "{app}\_internal\imagenes_usuarios"; Flags: recursesubdirs createallsubdirs
Source: "dist\HGC\imagenesCoches"; DestDir: "{app}\_internal\imagenesCoches"; Flags: recursesubdirs createallsubdirs

[Icons]
Name: "{group}\HGC"; Filename: "{app}\HGC.exe"
Name: "{commondesktop}\HGC"; Filename: "{app}\HGC.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear un acceso directo en el escritorio"; GroupDescription: "Opciones adicionales:"

[Run]
; Quitar solo lectura de todo lo interno
Filename: "cmd.exe"; Parameters: "/C attrib -R ""{app}\_internal"" /S /D"; Flags: runhidden

; Dar permisos completos a toda la carpeta _internal
Filename: "cmd.exe"; Parameters: "/C icacls ""{app}\_internal"" /grant *S-1-1-0:(OI)(CI)F /T /C /Q"; Flags: runhidden

; Quitar solo lectura específicamente a archivos .sqlite
Filename: "cmd.exe"; Parameters: "/C attrib -R ""{app}\_internal\bd\*.sqlite"""; Flags: runhidden

; Dar permisos completos a los .sqlite
Filename: "cmd.exe"; Parameters: "/C icacls ""{app}\_internal\bd\*.sqlite"" /grant *S-1-1-0:F /C /Q"; Flags: runhidden
