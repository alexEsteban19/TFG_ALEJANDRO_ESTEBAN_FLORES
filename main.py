from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk
from tkinter import messagebox, filedialog
import tkinter.font as tkFont
import argparse  # Importar argparse para procesar argumentos de línea de comandos
import screeninfo
import os
import sys
import sqlite3
import subprocess
import platform
from scripts.FunCliente import Cliente
from scripts.FunProveedor import Proveedor
from scripts.FunAcreedor import Acreedor
from scripts.configuracion import Configuracion
from scripts.admin_usuarios import AdminUsuarios
from scripts.VO import VO
from scripts.login import Login
from scripts.Facturacion import Facturacion

# -------------------- Argumentos de línea de comandos --------------------
# Configuración del parser para recibir los datos del usuario
parser = argparse.ArgumentParser(description="Aplicación principal de HGC")
parser.add_argument("--UserName", type=str, help="Nombre de usuario")
parser.add_argument("--Password", type=str, help="Contraseña")
parser.add_argument("--Nombre", type=str, help="Nombre")
parser.add_argument("--Apellido1", type=str, help="Primer apellido")
parser.add_argument("--Apellido2", type=str, help="Segundo apellido")
parser.add_argument("--User_Type", type=str, help="Tipo de usuario")
parser.add_argument("--rutaImagen", type=str, help="Ruta de la imagen")


# Parsear los argumentos
args = parser.parse_args()

# Acceder a los datos del usuario
user_data = {
    "UserName": args.UserName,
    "Password": args.Password,
    "Nombre": args.Nombre,
    "Apellido1": args.Apellido1,
    "Apellido2": args.Apellido2,
    "User_Type": args.User_Type,
    "rutaImagen": args.rutaImagen
}

# Guardar el tipo de usuario
user_type = args.User_Type or "Usuario Desconocido"

print("Usuario conectado:", user_data)

perfil_frame = None  # Para controlar el frame desplegable del perfil

# Crear la ventana principal
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

app = ctk.CTk()

icon_path = "resources/logos/icon_logo.ico"

# Obtener el monitor principal
monitors = screeninfo.get_monitors()
main_monitor = next((m for m in monitors if m.is_primary), monitors[0])
main_monitor_ancho = main_monitor.width
main_monitor_alto = main_monitor.height

# Cargar la imagen de fondo
frame_bg = Image.open("resources/images/bg.png").resize((main_monitor.width, main_monitor.height))
frame_photo = ImageTk.PhotoImage(frame_bg)

# Tamaño de la ventana proporcional al monitor principal
window_width = int(main_monitor.width * 0.60)
window_height = int(main_monitor.height * 0.75)
x_position = (main_monitor.width - window_width) // 2
y_position = (main_monitor.height - window_height) // 2
app.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

# Crear la fuente personalizada después de haber definido window_height
fuente_custom = ctk.CTkFont(family="Audiowide")

# Para cambiar el icono de la barra de tareas en Windows
if sys.platform == "win32":
    import ctypes
    myappid = "mycompany.myapp.sellcars.1.0"
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
    app.iconbitmap(icon_path)

def maximize():
    app.state("zoomed")

app.after(100, maximize)
app.title("Menú Principal")

perfil_window = None
# -------------------- Frame superior (barra de herramientas) --------------------

frame_top = ctk.CTkFrame(app, height=int(window_height*0.3), corner_radius=0, fg_color="#990404")
frame_top.pack(fill="x", side="top")

frame_top.columnconfigure(0, weight=0)
frame_top.columnconfigure(1, weight=1)

image_path = "resources/logos/hgcblanco.png"
img = Image.open(image_path)
image_width = int((window_width * 0.5) // 2.5)
image_height = int((window_height * 0.25) // 2.5)
img = img.resize((image_width, image_height), Image.Resampling.LANCZOS)
img = ImageTk.PhotoImage(img)

logo_label = ctk.CTkLabel(frame_top, image=img, text="", cursor="hand2")
logo_label.grid(row=0, column=0, padx=int(window_width/20), pady=10)

def go_home(event=None):
    global active_button

    clear_frame_right()
    frame_label = ctk.CTkLabel(frame_right, image=frame_photo, text="")
    frame_label.image = frame_photo
    frame_label.place(relwidth=1, relheight=1)

    # 🔥 Cerrar cualquier ventana externa abierta
    cerrar_ventanas_externas(excluir=None)

    # 🔥 Deseleccionar cualquier botón activo
    if active_button:
        active_button.configure(fg_color=COLOR_NORMAL, border_width=0)
        active_button = None

logo_label.bind("<Button-1>", go_home)

def mostrar_perfil_usuario():
    """Muestra una ventana modal anclada a la app con la información del usuario y opción de cerrar sesión."""
    global perfil_window

    if perfil_window and perfil_window.winfo_exists():
        perfil_window.lift()
        return

    perfil_window = ctk.CTkToplevel(app)
    perfil_window.title("Información del Usuario")
    perfil_window.transient(app)
    perfil_window.grab_set()
    perfil_window.focus_force()
    perfil_window.resizable(False, False)

    win_w = int(window_width * 0.60)
    win_h = int(window_height * 0.9)
    app.update_idletasks()
    x = app.winfo_x() + (app.winfo_width() // 2) - (win_w // 2)
    y = app.winfo_y() + (app.winfo_height() // 2) - (win_h // 2)
    perfil_window.geometry(f"{win_w}x{win_h}+{x}+{y}")
    perfil_window.configure(bg="#1e1e1e")

    title_font = ctk.CTkFont(family="Sans Sulex", size=int(win_h * 0.05), weight="bold")
    label_font = ctk.CTkFont(family="Sans Sulex", size=int(win_h * 0.03))
    button_font = ctk.CTkFont(family="Sans Sulex", size=int(win_h * 0.035))

    container = ctk.CTkFrame(perfil_window, fg_color="#1a1a1a")
    container.pack(expand=True, fill="both", pady=int(win_h * 0.02))

    ctk.CTkLabel(container, text="Información del Usuario", text_color="#FFFFFF", font=title_font).pack(pady=(int(win_h * 0.02), int(win_h * 0.05)))

    profile_img_size = int(win_h * 0.35)
    borde_blanco = 2
    ruta_default = "imagenesCoches/noImage.jpg"
    ruta_img = user_data.get("rutaImagen", ruta_default)

    def crear_imagen_perfil(ruta):
        try:
            ruta_default = "imagenesCoches/noImage.jpg"  # Ruta predeterminada
            if not os.path.exists(ruta):
                ruta = ruta_default  # Usar imagen predeterminada si no existe

            scale = 4
            big_size = profile_img_size * scale
            big_border = borde_blanco * scale

            img = Image.open(ruta).convert("RGBA")
            img = img.resize((big_size, big_size), Image.Resampling.LANCZOS)

            mask = Image.new("L", (big_size, big_size), 0)
            draw = ImageDraw.Draw(mask)
            draw.ellipse((0, 0, big_size, big_size), fill=255)

            circular_img = Image.new("RGBA", (big_size, big_size), (0, 0, 0, 0))
            circular_img.paste(img, (0, 0), mask)

            bordered_size = big_size + 2 * big_border
            bordered_img = Image.new("RGBA", (bordered_size, bordered_size), (0, 0, 0, 0))
            draw = ImageDraw.Draw(bordered_img)
            draw.ellipse((0, 0, bordered_size, bordered_size), fill=(255, 255, 255, 255))
            bordered_img.paste(circular_img, (big_border, big_border), circular_img)

            final_img = bordered_img.resize((profile_img_size + 2 * borde_blanco, profile_img_size + 2 * borde_blanco), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(final_img)
        except Exception as e:
            print(f"Error al crear imagen de perfil: {e}")
            return None


    if os.path.exists(ruta_img):
        perfil_window.profile_photo = crear_imagen_perfil(ruta_img)
    else:
        perfil_window.profile_photo = crear_imagen_perfil(ruta_default)

    def seleccionar_imagen():
        ruta = filedialog.askopenfilename(
            title="Seleccionar Imagen",
            filetypes=[("Archivos de imagen", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Todos los archivos", "*.*")]
        )
        if ruta:
            user_data["rutaImagen"] = ruta
            try:
                conn = sqlite3.connect('bd/Users.sqlite')
                cursor = conn.cursor()
                cursor.execute("UPDATE Usuarios SET rutaImagen = ? WHERE UserName = ?", (ruta, user_data["UserName"]))
                conn.commit()

                nueva_foto = crear_imagen_perfil(ruta)
                if nueva_foto:
                    perfil_window.profile_photo = nueva_foto
                    profile_photo_label.configure(image=perfil_window.profile_photo)
                    profile_photo_label.image = perfil_window.profile_photo

            except sqlite3.Error as e:
                print(f"Error al actualizar la base de datos: {e}")
            finally:
                conn.close()

    profile_photo_label = ctk.CTkLabel(container, image=perfil_window.profile_photo, text="")
    profile_photo_label.pack(pady=(int(win_h * 0.02), int(win_h * 0.05)))
    profile_photo_label.bind("<Button-1>", lambda e: seleccionar_imagen())

    nombre = user_data.get("Nombre", "")
    apellidos = f"{user_data.get('Apellido1', '')} {user_data.get('Apellido2', '')}".strip()
    username = user_data.get("UserName", "")
    rol = user_data.get("User_Type", "")

    datos = [
        f"Nombre: {nombre} {apellidos}",
        f"Nombre de usuario: {username}",
        f"Tipo de usuario: {rol}"
    ]

    for texto in datos:
        ctk.CTkLabel(container, text=texto, text_color="#FFFFFF", font=label_font).pack(pady=(int(win_h * 0.01), int(win_h * 0.02)))

    ctk.CTkButton(
        container,
        text="Cerrar Sesión",
        fg_color="#990404",
        hover_color="#540303",
        border_color="#FFFFFF",
        border_width=2,
        text_color="#FFFFFF",
        font=button_font,
        corner_radius=10,
        command=cerrar_sesion
    ).pack(pady=(int(win_h * 0.05), int(win_h * 0.05)))



def cerrar_sesion():
    """Cierra la ventana actual y vuelve al login."""
    global perfil_window
    
    # Cerrar la ventana de perfil si existe
    if perfil_window and perfil_window.winfo_exists():
        perfil_window.destroy()
    
    cerrar_todo()    
    # Reiniciar el login
    iniciar_login()


def iniciar_login():
    os.system("python scripts/login.py")


# Proporciones relativas para el tamaño del botón
button_width = int(window_width * 0.06)
button_height = int(window_height * 0.08)

# Colores para hover y normal
COLOR_NORMAL = "#990404"
COLOR_HOVER = "#540303"

# Cargar imagen del botón de la carpeta
folder_img = Image.open("resources/icons/white/folder.png")
folder_img = folder_img.resize((int(button_width * 0.65), int(button_height * 0.65)), Image.Resampling.LANCZOS)
folder_img = ImageTk.PhotoImage(folder_img)

# Variable global para manejar el estado de la ventana abierta
carpeta_proceso = None

def abrir_carpeta_informes():
    global carpeta_proceso
    ruta_carpeta = "informes"

    if platform.system() == "Windows":
        if carpeta_proceso:
            try:
                carpeta_proceso.terminate()
            except:
                pass
            carpeta_proceso = None
        carpeta_proceso = subprocess.Popen(f'explorer "{os.path.abspath(ruta_carpeta)}"')
    elif platform.system() == "Darwin":  # macOS
        subprocess.call(["open", ruta_carpeta])
    elif platform.system() == "Linux":
        subprocess.call(["xdg-open", ruta_carpeta])
    else:
        messagebox.showerror("Error", "Sistema operativo no soportado.")

# Crear el botón para abrir la carpeta de informes
folder_button = ctk.CTkButton(
    frame_top,
    fg_color=COLOR_NORMAL,
    hover_color=COLOR_HOVER,  # Color al pasar el cursor
    image=folder_img,
    text="",
    width=button_width,
    height=button_height,
    command=abrir_carpeta_informes
)
folder_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

# Cargar imagen del botón de perfil
profile_img = Image.open("resources/icons/white/User.png")
profile_img = profile_img.resize((int(button_width * 0.8), int(button_height * 0.8)), Image.Resampling.LANCZOS)
profile_img = ImageTk.PhotoImage(profile_img)

# Crear el botón de perfil
profile_button = ctk.CTkButton(
    frame_top,
    fg_color=COLOR_NORMAL,
    hover_color=COLOR_HOVER,  # Color al pasar el cursor
    image=profile_img,
    text="",
    width=button_width,
    height=button_height,
    command=mostrar_perfil_usuario
)
profile_button.grid(row=0, column=2, padx=10, pady=10, sticky="e")

# -------------------- Frame inferior --------------------
frame_bottom = ctk.CTkFrame(app)
frame_bottom.pack(fill="both", side="top", expand=True)

frame_left = ctk.CTkFrame(frame_bottom, width=int(window_width * 0.2), fg_color="#acb4c4", corner_radius=0)
frame_left.pack(side="left", fill="y")

frame_right = ctk.CTkFrame(frame_bottom, fg_color="#3d3d3d")
frame_right.pack(side="left", fill="both", expand=True)

frame_label = ctk.CTkLabel(frame_right, image=frame_photo, text="")
frame_label.image = frame_photo
frame_label.place(relwidth=1, relheight=1)

# -------------------- Crear botones de menú --------------------
def create_menu_button(frame, text, img_path, row, command=None):

    fuente_custom = ctk.CTkFont(family="Toxigenesis Rg", size=int(window_height * 0.032))
    button_width = int(window_width * 0.25)
    button_height = int(window_height * 0.12)
    vertical_padding = int(window_height * 0.02)

    img_width = int(button_width * 0.20)
    img_height = int(button_height * 0.6)
    img = Image.open(img_path).resize((img_width, img_height), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(img)

    button = ctk.CTkButton(
        frame,
        text=text,
        text_color="#ffffff",
        image=img,
        compound="left",
        fg_color="#990404",
        corner_radius=10,
        font=fuente_custom,
        width=button_width,
        height=button_height,
        anchor="w",
        command=command
    )
    button.image = img
    button.grid(row=row, column=0, padx=10, pady=vertical_padding, sticky="ew")
    return button

VO_Button = create_menu_button(frame_left, "Vehículo Ocasión", "resources/icons/white/VO.png", 0)
Cliente_Button = create_menu_button(frame_left, "Clientes", "resources/icons/white/Cliente.png", 1)
Proveedor_Button = create_menu_button(frame_left, "Proveedores", "resources/icons/white/proveedores.png", 2)
Accreedores_Button = create_menu_button(frame_left, "Acreedores", "resources/icons/white/acreedores.png", 3)
Facturacion_Button = create_menu_button(frame_left, "Facturación", "resources/icons/white/facturas.png", 4)
AdminUsers_Button = create_menu_button(frame_left, "Admin Usuarios", "resources/icons/white/administrador1.png", 5)
Manual_Button = create_menu_button(frame_left, "Manual de uso", "resources/icons/white/manual_icon.png", 6)

# -------------------- Configuración de permisos --------------------
# Asociamos roles permitidos para cada botón
boton_roles_map = {
    VO_Button: ["admin", "usuario"],
    Cliente_Button: ["admin", "usuario"],
    Proveedor_Button: ["admin", "usuario"],
    Accreedores_Button: ["admin", "usuario"],
    Facturacion_Button: ["admin", "usuario"],
    AdminUsers_Button: ["admin"],  # Solo admin tiene acceso
    Manual_Button: ["admin", "usuario"],
}

# -------------------- Validación de permisos --------------------
def validar_permisos(button, action):
    roles_permitidos = boton_roles_map.get(button, [])

    if user_type in roles_permitidos:
        action()  # Ejecutar la acción si el usuario tiene permiso
    else:
        # Mostrar mensaje de error si no tiene permisos
        go_home()
        messagebox.showerror(
            "Acceso Denegado",
            "No tienes los permisos necesarios para acceder a esta función."
        )

# -------------------- Gestión de ventanas abiertas --------------------
def cerrar_todo():
    for clase in (Proveedor, Cliente, Acreedor, VO, Facturacion, AdminUsuarios):
        for ventana in getattr(clase, "ventanas_secundarias", []):
            try:
                ventana.destroy()
            except:
                pass
        clase.ventanas_secundarias.clear()
    app.destroy()

def cerrar_ventanas_externas(excluir=None):
    for clase in (Proveedor, Cliente, Acreedor, VO, Facturacion, AdminUsuarios):
        if clase == excluir:
            continue
        for ventana in getattr(clase, "ventanas_secundarias", []):
            try:
                clase.ventana_abierta = False
                ventana.destroy()
            except:
                pass
        clase.ventanas_secundarias.clear()

app.protocol("WM_DELETE_WINDOW", cerrar_todo)

# -------------------- Eventos --------------------
def on_hover(button):
    def on_enter(event):
        if button == active_button:
            button.configure(fg_color=COLOR_HOVER_ACTIVO)
        else:
            button.configure(fg_color=COLOR_HOVER)

    def on_leave(event):
        if button == active_button:
            button.configure(fg_color=COLOR_ACTIVO)
        else:
            button.configure(fg_color=COLOR_NORMAL)

    button.bind("<Enter>", on_enter)
    button.bind("<Leave>", on_leave)

def clear_frame_right():
    for widget in frame_right.winfo_children():
        widget.destroy()

buttons = [
    (VO_Button, lambda: VO.abrir_VO(frame_right, clear_frame_right, app)),
    (Cliente_Button, lambda: Cliente.abrir_cliente(frame_right, clear_frame_right, app)),
    (Proveedor_Button, lambda: Proveedor.abrir_proveedor(frame_right, clear_frame_right, app)),
    (Accreedores_Button, lambda: Acreedor.abrir_Acreedor(frame_right, clear_frame_right, app)),
    (Facturacion_Button, lambda: Facturacion.abrir_Factu(frame_right, clear_frame_right, app)),
    (AdminUsers_Button, lambda: Configuracion.abrir_admin_usuarios(frame_right, clear_frame_right, app)),
    (Manual_Button, lambda: Configuracion.abrir_manual()),
]

active_button = None

COLOR_NORMAL = "#990404"
COLOR_HOVER = "#540303"
COLOR_ACTIVO = "#540303"
COLOR_HOVER_ACTIVO = "#3b0202"

# 🔁 Relación botón <-> clase para saber cuál es el módulo activo
boton_clase_map = {
    VO_Button: VO,
    Cliente_Button: Cliente,
    Proveedor_Button: Proveedor,
    Accreedores_Button: Acreedor,
    Facturacion_Button: VO,
    AdminUsers_Button: Configuracion,
    Manual_Button: Configuracion
}

def on_click(action, button):
    def wrapper(event):
        global active_button

        if active_button and active_button != button:
            active_button.configure(fg_color=COLOR_NORMAL, border_width=0)

        active_button = button
        button.configure(fg_color=COLOR_ACTIVO)
        button.configure(border_color="black", border_width=3)
        button.configure(state="active")
        button.configure(fg_color=COLOR_HOVER_ACTIVO)

        # Cierra ventanas externas no relacionadas al módulo actual
        modulo_actual = boton_clase_map.get(button)
        cerrar_ventanas_externas(excluir=modulo_actual)

        action()
    return wrapper

for button, action in buttons:
    def wrapped_action(button=button, action=action):
        return lambda: validar_permisos(button, action)

    on_hover(button)
    button.bind("<Button-1>", on_click(wrapped_action(), button))


# -------------------- Inicia la app --------------------
app.mainloop()
