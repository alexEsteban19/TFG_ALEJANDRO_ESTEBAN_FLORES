import customtkinter as ctk
import tkinter.messagebox as messagebox
import sqlite3
import os
import sys
from PIL import Image
import screeninfo

class Login:
    def __init__(self):
        self.app = ctk.CTk()
        self.app.title("IDENTIFICACIÓN - HGC")
        self.icon_path = "resources/logos/icon_logo.ico"

        if sys.platform == "win32":
            import ctypes
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            self.app.iconbitmap(self.icon_path)

        monitors = screeninfo.get_monitors()
        main_monitor = next((m for m in monitors if m.is_primary), monitors[0])
        screen_width = main_monitor.width
        screen_height = main_monitor.height

        # Cambios aquí: ventana más pequeña
        window_width = int(screen_width * 0.3)
        window_height = int(screen_height * 0.6)
        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2
        self.app.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self.app.resizable(False, False)

        # Cambios aquí: escala en base al monitor, no a la ventana
        scale_factor = 0.58 
        scale_w = (screen_width / 1920) * scale_factor
        scale_h = (screen_height / 1080) * scale_factor

        font_size = int(32 * scale_h)
        entry_width = int(700 * scale_w)
        entry_height = int(50 * scale_h)
        button_height = int(72 * scale_h)
        eye_icon_size = int(30 * scale_h)
        logo_width = int(screen_width * 0.2)

        self.fuente_custom = ctk.CTkFont(family="Sans Sulex", size=font_size, weight="bold")

        # Fondo principal
        self.main_frame = ctk.CTkFrame(self.app, fg_color="#1a1a1a", corner_radius=0)
        self.main_frame.pack(pady=int(50 * scale_h), padx=int(30 * scale_w), fill="both", expand=True)

        # Imagen principal centrada
        try:
            img = Image.open("resources/logos/hgcmetal.png")
            image_width = img.width * 2.2
            aspect_ratio = ((img.height / image_width) * 2)
            image_height = int(logo_width * aspect_ratio)
            image = ctk.CTkImage(light_image=img, size=(logo_width, image_height))
            image_label = ctk.CTkLabel(self.main_frame, image=image, text="")
            image_label.pack(pady=(0, int(30 * scale_h)))
        except Exception as e:
            print(f"Error al cargar la imagen principal:", e)

        # Usuario
        self.identity_label = ctk.CTkLabel(self.main_frame, text="Nombre de Usuario:", font=self.fuente_custom)
        self.identity_label.pack(pady=(int(30 * scale_h), int(10 * scale_h)))

        self.identity_entry = ctk.CTkEntry(self.main_frame, width=entry_width, height=entry_height, font= self.fuente_custom)
        self.identity_entry.pack(pady=int(10 * scale_h))

        # Contraseña
        self.password_label = ctk.CTkLabel(self.main_frame, text="Contraseña:", font=self.fuente_custom)
        self.password_label.pack(pady=(int(30 * scale_h), int(10 * scale_h)))

        self.password_frame = ctk.CTkFrame(self.main_frame, fg_color="#242424")
        self.password_frame.pack(pady=int(10 * scale_h))

        self.password_entry = ctk.CTkEntry(self.password_frame, width=entry_width - 60, height=entry_height, show="*", font= self.fuente_custom)
        self.password_entry.pack(side="left", padx=5)

        self.eye_icon = ctk.CTkImage(light_image=Image.open("resources/images/ojotachado.png"), size=(eye_icon_size, eye_icon_size))
        self.eye_crossed_icon = ctk.CTkImage(light_image=Image.open("resources/images/ojoblanco.png"), size=(eye_icon_size, eye_icon_size))

        self.is_password_visible = False

        def toggle_password_visibility():
            self.is_password_visible = not self.is_password_visible
            if self.is_password_visible:
                self.password_entry.configure(show="")
                self.eye_button.configure(image=self.eye_crossed_icon)
            else:
                self.password_entry.configure(show="*")
                self.eye_button.configure(image=self.eye_icon)

        self.eye_button = ctk.CTkButton(
            self.password_frame, image=self.eye_icon, text="", command=toggle_password_visibility,
            fg_color="#343638", width=eye_icon_size + 24, height=entry_height - 10,
            border_width=2, border_color="#565b5e"
        )
        self.eye_button.pack(side="right", padx=0, pady=0)

        def on_enter_eye(event):
            self.eye_button.configure(fg_color="black")

        def on_leave_eye(event):
            self.eye_button.configure(fg_color="#343638")

        self.eye_button.bind("<Enter>", on_enter_eye)
        self.eye_button.bind("<Leave>", on_leave_eye)

        # Focus styling
        highlight_color = "#c91706"

        def on_focus_in_identity(event):
            self.identity_entry.configure(border_color=highlight_color, fg_color="black")

        def on_focus_out_identity(event):
            self.identity_entry.configure(border_color="#565b5e", fg_color="#343638")

        def on_focus_in_password(event):
            self.password_entry.configure(border_color=highlight_color, fg_color="black")

        def on_focus_out_password(event):
            self.password_entry.configure(border_color="#565b5e", fg_color="#343638")

        self.identity_entry.bind("<FocusIn>", on_focus_in_identity)
        self.identity_entry.bind("<FocusOut>", on_focus_out_identity)
        self.password_entry.bind("<FocusIn>", on_focus_in_password)
        self.password_entry.bind("<FocusOut>", on_focus_out_password)

        # Botón de login
        self.login_button = ctk.CTkButton(
            self.main_frame,
            text="Iniciar Sesión",
            command=self.login,
            fg_color="#c91706",
            font=self.fuente_custom,
            height=button_height,
            corner_radius=8,
            border_width=2,
            border_color="black"
        )
        self.login_button.pack(pady=int(40 * scale_h), padx=int(30 * scale_w))

        def on_enter(event):
            self.login_button.configure(fg_color="#7d0404")

        def on_leave(event):
            self.login_button.configure(fg_color="#c91706")

        self.login_button.bind("<Enter>", on_enter)
        self.login_button.bind("<Leave>", on_leave)

        self.app.bind("<Return>", lambda event: self.login())

    def login(self):
        username = self.identity_entry.get().strip()
        password = self.password_entry.get().strip()

        if not username or not password:
            messagebox.showerror("Campos Vacíos", "Por favor, complete todos los campos.")
            return

        user_data = self.verificar_usuario(username, password)
        if user_data:
            messagebox.showinfo("Inicio de Sesión Exitoso", f"Bienvenido a HGC ({user_data['User_Type']})")
            self.app.destroy()

            # Asegurar que ningún valor sea None y envolver entre comillas
            args = [
                "--UserName", f"\"{user_data.get('UserName', '')}\"",
                "--Password", f"\"{user_data.get('Password', '')}\"",
                "--Nombre", f"\"{user_data.get('Nombre', '')}\"",
                "--Apellido1", f"\"{user_data.get('Apellido1', '')}\"",
                "--Apellido2", f"\"{user_data.get('Apellido2', '')}\"",
                "--User_Type", f"\"{user_data.get('User_Type', '')}\"",
                "--rutaImagen", f"\"{user_data.get('rutaImagen', '')}\""
            ]

            os.system(f"python main.py {' '.join(args)}")
        else:
            messagebox.showerror("Error de Inicio de Sesión", "Los datos no coinciden con ningún usuario registrado.")

    def verificar_usuario(self, username, password):
        db_path = "bd/Users.sqlite"
        default_image_path = "imagenesCoches/noImage.jpg"  # Ruta predeterminada
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute(
                "SELECT UserName, Password, Nombre, Apellido1, Apellido2, User_Type, rutaImagen "
                "FROM Usuarios WHERE UserName = ? AND Password = ?",
                (username, password)
            )
            result = cursor.fetchone()
            conn.close()

            if result:
                ruta_imagen = result[6] if result[6] else default_image_path
                # Verifica si la ruta existe físicamente; si no, usa la predeterminada
                if not os.path.exists(ruta_imagen):
                    ruta_imagen = default_image_path

                return {
                    "UserName": result[0],
                    "Password": result[1],
                    "Nombre": result[2],
                    "Apellido1": result[3],
                    "Apellido2": result[4],
                    "User_Type": result[5],
                    "rutaImagen": ruta_imagen
                }
            return None
        except sqlite3.Error as e:
            messagebox.showerror("Error de Base de Datos", f"Error al conectar con la base de datos: {e}")
            return None

    def ejecutar(self):
        self.app.mainloop()

if __name__ == "__main__":
    login_app = Login()
    login_app.ejecutar()
