HGC (Herramienta de gestión de concesionarios)
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

HGC es una aplicación de escritorio diseñada como proyecto de fin de grado en DAM (Desarrollo de Aplicaciones Multiplataforma), diseñada con python con el objetivo de gestionar la administración interna de un concesionario.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Descripción de la aplicación:

HGC está diseñada para ser utilizada por el departamento de administración de los concesionarios, especialmente desarrollada para concesionarios pequeños y medianos. El usuario accederá al programa con sus datos y entrará a la interfaz principal, desde donde podrá ver sus datos y gestionar diferentes módulos: clientes, proveedores, acreedores, vehículos de ocasión y facturas. Podrá generar informes, facturas, realizar operaciones CRUD, búsquedas personalizadas etc.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Características:

IDE (Entorno de desarrollo): Visual Studio Code.
Lenguaje de programación utilizado: Python 3.13 (aplicación), Inno Setup Script basado en Object Pascal (installer).
Gestor de BD: DB Browser for SQLite.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Estructura del repositorio de Github: 

- /bd: Contiene los archivos de base de datos del proyecto.
- /build y /dist: carpetas generadas por el archivo installer.spec, en /dist se encuentra el ejecutable y datos internos.
- /facturas: contiene las facturas generadas por el programa
- /imagenes_usuarios: contiene las imagenes de los usuarios con ruta reformateada para ser guardadas por la empresa a modo de dato interno.
- /imagenesCoches: contiene las imagenes de los vehículos con ruta reformateada para ser guardadas por la empresa a modo de dato interno.
- /informes: contiene los informes generados por el programa.
- /ManualDeUso: contiene el manual de uso en formato .pdf, este también podrá verse desde la aplicación.
- /resources: contiene todos los recursos visuales de la aplicación: logos, fuentes...
- /scripts: contiene los scripts necesarios para que el codigo funcione.

Archivos:

- installer.spec: archivo encargado de construir el ejecutable "HGC.exe".
- login.py: archivo principal del programa, primer archivo ejecutado al abrir la aplicación.
- README.md: archivo meramente informativo para la comodidad y el aprendizaje de quien utilice la aplicación.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Cómo ejecutar la aplicación:

1. En la carpeta del proyecto, se proporciona un archivo llamado "HGC Installer.exe", el primer paso es ejecutar este archivo. No hay que preocuparse por ninguna dependencia, ya que el installer le proporciona todo lo necesario.
2. Una vez ejecutado el archivo, nos lleva a la interfaz de instalación del programa.
3. La primera ventana nos da a elegir la ubicación de la aplicación entre las carpetas de nuestro ordenador.
4. En la siguiente ventana elegiremos el nombre de la carpeta de la aplicación.
5. Se nos da la opción de crear un acceso directo en el escritorio, lo que el usuario desee.
6. El programa procede a la instalación de todos los recursos necesarios. Al acabar la instalación, si ha elegido la opción de generar acceso directo en el escritorio, aparecerá la aplicación llamada "HGC", lista para ejecutarse.
7. Ejecute la aplicación.

IMPORTANTE: En la carpeta donde haya instalado el programa, no debe borrar las carpetas con nombre "_internal", ya que son necesarias para el funcionamiento de la aplicación. Lo mismo ocurre con los archivos cuya terminación es ".keep", estos archivos son necesarios para la lectura de carpetas a la hora de hacer el installer. Por tanto, los archivos mencionados NO BORRAR.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Cómo desinstalar la aplicación:

IMPORTANTE: Si desea conservar sus datos, por ejemplo informes o facturas, haga una copia de seguridad antes de borrar la aplicación.

1. Debe ir a la ruta que proporcionó en la instalación cuando ejecutó "HGC installer.exe", generalmente suele ser: C:/Program Files (x86)/HGC, o en español:
C:/Archivos de programa (x86)/HGC.
2. En dicha carpeta, encontrará un archivo llamado unins000.exe, ejecútelo y saldrá un aviso advirtiendo si quiere borrar la aplicación y todos sus componentes.
3. Pulse "Sí" en dicho aviso, el archivo desinstalará todo el programa y archivos relacionados de su sistema.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Autor:

Nombre: Alejandro Esteban Flores
Repositorio del proyecto: https://github.com/alexEsteban19/TFG_ALEJANDRO_ESTEBAN_FLORES.git
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
