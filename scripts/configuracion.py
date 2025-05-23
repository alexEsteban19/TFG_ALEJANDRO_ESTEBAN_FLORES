import os
import platform
import subprocess
import sys

class Configuracion:
    @staticmethod
    def ruta_recurso(relativa):
        """Devuelve la ruta absoluta a un recurso, adaptada para PyInstaller."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relativa)
        return os.path.join(os.path.abspath("."), relativa)

    @staticmethod
    def abrir_admin_usuarios(frame_right, clear_frame_right, app):
        clear_frame_right()
        from scripts.admin_usuarios import AdminUsuarios
        AdminUsuarios.abrir_admin(frame_right, clear_frame_right, app)

    @staticmethod
    def abrir_manual():
        ruta_pdf = Configuracion.ruta_recurso("ManualDeUso\Manual_de_uso.pdf")
        
        # Detectar el sistema operativo y abrir el archivo
        if platform.system() == "Windows":
            os.startfile(ruta_pdf)
        elif platform.system() == "Darwin":  # macOS
            subprocess.call(["open", ruta_pdf])
        elif platform.system() == "Linux":
            subprocess.call(["xdg-open", ruta_pdf])
        else:
            raise OSError("Sistema operativo no soportado para abrir el archivo PDF.")

