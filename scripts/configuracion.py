import os
import platform
import subprocess

class Configuracion:

    @staticmethod
    def abrir_admin_usuarios(frame_right, clear_frame_right, app):
        clear_frame_right()
        from scripts.admin_usuarios import AdminUsuarios
        AdminUsuarios.abrir_admin(frame_right, clear_frame_right, app)

    @staticmethod
    def abrir_manual():
        ruta_pdf = "ManualDeUso\Manual_de_uso.pdf"
        
        # Detectar el sistema operativo y abrir el archivo
        if platform.system() == "Windows":
            os.startfile(ruta_pdf)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", ruta_pdf])
        elif platform.system() == "Linux":
            subprocess.call(["xdg-open", ruta_pdf])
        else:
            raise OSError("Sistema operativo no soportado para abrir el archivo PDF.")
