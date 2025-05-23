HGC (Herramienta de gestión de concesionarios)
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

HGC es una aplicación de escritorio diseñada como proyecto de fin de grado en DAM (Desarrollo de Aplicaciones Multiplataforma), diseñada con python con el objetivo de gestionar la administración interna de un concesionario.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Descripción de la aplicación:

HGC está diseñada para ser utilizada por el departamento de administración de los concesionarios, especialmente desarrollada para concesionarios pequeños y medianos. El usuario accederá al programa con sus datos y entrará a la interfaz principal, desde donde podrá ver sus datos y gestionar diferentes módulos: clientes, proveedores, acreedores, vehículos de ocasión y facturas. Podrá generar informes, facturas, realizar operaciones CRUD, búsquedas personalizadas etc.
---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
Características:

IDE (Entorno de desarrollo): Visual Studio Code
Gestor de BD: DB Browser for SQLite
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



