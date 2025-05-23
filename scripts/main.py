from PIL import Image, ImageTk, ImageDraw
import customtkinter as ctk
from tkinter import messagebox, filedialog
import argparse  
import screeninfo
import os
import sys
import shutil
import sqlite3
import subprocess
import platform
from scripts.VO import VO
from scripts.FunCliente import Cliente
from scripts.FunProveedor import Proveedor
from scripts.FunAcreedor import Acreedor
from scripts.configuracion import Configuracion
from scripts.admin_usuarios import AdminUsuarios
from scripts.Facturacion import Facturacion
active_button = None
perfil_window = None
carpeta_proceso = None

def menu(user_data): 

    # Acceder a los datos del usuario que provienen del login
    UserName = user_data.get("UserName", "")
    Password = user_data.get("Password", "")
    Nombre = user_data.get("Nombre", "")
    Apellido1 = user_data.get("Apellido1", "")
    Apellido2 = user_data.get("Apellido2", "")
    User_Type = user_data.get("User_Type", "Usuario Desconocido")
    rutaImagen = user_data.get("rutaImagen", "")

    # Guardar el tipo de usuario para después conceder permisos
    user_type = User_Type

    perfil_frame = None 

    #------------------------ Creamos la ventana principal ----------------------
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("dark-blue")

    app = ctk.CTk()

    @staticmethod
    def ruta_recurso(relativa):
        """Devuelve la ruta absoluta a un recurso, adaptada para PyInstaller."""
        if hasattr(sys, '_MEIPASS'):
            return os.path.join(sys._MEIPASS, relativa)
        return os.path.join(os.path.abspath("."), relativa)

    icon_path = ruta_recurso("resources/logos/icon_logo.ico")

    # Obtener el monitor principal para obtener sus dimensiones
    monitors = screeninfo.get_monitors()
    main_monitor = next((m for m in monitors if m.is_primary), monitors[0])
    main_monitor_ancho = main_monitor.width
    main_monitor_alto = main_monitor.height

    # Cargar la imagen de fondo
    frame_bg = Image.open(ruta_recurso("resources/images/bg.png")).resize((main_monitor.width, main_monitor.height))
    frame_photo = ImageTk.PhotoImage(frame_bg)

    # Tamaño de la ventana proporcional al monitor principal
    window_width = int(main_monitor.width * 0.60)
    window_height = int(main_monitor.height * 0.75)
    x_position = (main_monitor.width - window_width) // 2
    y_position = (main_monitor.height - window_height) // 2
    app.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

    # Crear la fuente personalizada 
    fuente_custom = ctk.CTkFont(family="Audiowide")

    # Asociamos el icono personalizado al proceso para que lo detecte bien
    if sys.platform == "win32":
        import ctypes
        myappid = "mycompany.myapp.hgc.1.0"
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
        app.iconbitmap(icon_path)

    def maximize():
        app.state("zoomed")

    app.resizable(True, True)
    app.after(100, maximize)
    app.title("Menú Principal")

    perfil_window = None
    # -------------------- Frame superior (barra de herramientas) --------------------

    # Definimos el frame top
    frame_top = ctk.CTkFrame(app, height=int(window_height*0.3), corner_radius=0, fg_color="#990404")
    frame_top.pack(fill="x", side="top")

    frame_top.columnconfigure(0, weight=0)
    frame_top.columnconfigure(1, weight=1)

    # Boton con el logo (home)
    image_path = ruta_recurso("resources/logos/hgcblanco.png")
    img = Image.open(image_path)
    image_width = int((window_width * 0.5) // 2.5)
    image_height = int((window_height * 0.25) // 2.5)
    img = img.resize((image_width, image_height), Image.Resampling.LANCZOS)
    img = ImageTk.PhotoImage(img)

    logo_label = ctk.CTkLabel(frame_top, image=img, text="", cursor="hand2")
    logo_label.grid(row=0, column=0, padx=int(window_width/20), pady=10)

    # Metodo para volver a home
    def go_home(event=None):
        global active_button

        clear_frame_right()
        frame_label = ctk.CTkLabel(frame_right, image=frame_photo, text="")
        frame_label.image = frame_photo
        frame_label.place(relwidth=1, relheight=1)

        # Cerrar cualquier ventana externa abierta
        cerrar_ventanas_externas(excluir=None)

        # Deseleccionar cualquier botón activo
        if active_button:
            active_button.configure(fg_color=COLOR_NORMAL, border_width=0)
            active_button = None

    logo_label.bind("<Button-1>", go_home)

    # Metodo para abrir el apartado de informacion de usuario
    def mostrar_perfil_usuario():
        global perfil_window

        # "Elevar la ventana"
        if perfil_window and perfil_window.winfo_exists():
            perfil_window.lift()
            return

        # Definir la ventana
        perfil_window = ctk.CTkToplevel(app)
        perfil_window.title("Información del Usuario")
        perfil_window.transient(app)
        perfil_window.grab_set()
        perfil_window.focus_force()
        perfil_window.resizable(False, False)

        # Colocar la ventana centrada en la pantalla basandome en el tamaño de la pantalla
        win_w = int(window_width * 0.60)
        win_h = int(window_height * 0.9)
        app.update_idletasks()
        x = app.winfo_x() + (app.winfo_width() // 2) - (win_w // 2)
        y = app.winfo_y() + (app.winfo_height() // 2) - (win_h // 2)
        perfil_window.geometry(f"{win_w}x{win_h}+{x}+{y}")
        perfil_window.configure(bg="#1e1e1e")

        # Fuentes para los diferentes apartados
        title_font = ctk.CTkFont(family="Sans Sulex", size=int(win_h * 0.05), weight="bold")
        label_font = ctk.CTkFont(family="Sans Sulex", size=int(win_h * 0.03))
        button_font = ctk.CTkFont(family="Sans Sulex", size=int(win_h * 0.035))

        container = ctk.CTkFrame(perfil_window, fg_color="#1a1a1a")
        container.pack(expand=True, fill="both", pady=int(win_h * 0.02))

        ctk.CTkLabel(container, text="Información del Usuario", text_color="#FFFFFF", font=title_font).pack(pady=(int(win_h * 0.02), int(win_h * 0.05)))

        profile_img_size = int(win_h * 0.35)
        borde_blanco = 2

        ruta_img_rel = user_data.get("rutaImagen", "")
        ruta_default = ruta_recurso("imagenesCoches/noImage.jpg")

        # Detectar si hay ruta, si es relativa o absoluta
        if not ruta_img_rel:
            ruta_img = ruta_default
        else:
            ruta_img = ruta_img_rel


        # Metodo para acceder a la imagen del usuario
        def crear_imagen_perfil(ruta):
            try:
                ruta_default = ruta_recurso("imagenesCoches/noImage.jpg")  # Ruta predeterminada
                if not os.path.exists(ruta):
                    ruta = ruta_default  # Usar imagen predeterminada si no existe

                scale = 4
                big_size = profile_img_size * scale
                big_border = borde_blanco * scale

                img = Image.open(ruta).convert("RGBA")
                img = img.resize((big_size, big_size), Image.Resampling.LANCZOS)

                # Dibujo un borde circular  
                mask = Image.new("L", (big_size, big_size), 0)
                draw = ImageDraw.Draw(mask)
                draw.ellipse((0, 0, big_size, big_size), fill=255)

                circular_img = Image.new("RGBA", (big_size, big_size), (0, 0, 0, 0))
                circular_img.paste(img, (0, 0), mask)

                # Transformo la imagen en circular y la añado dentro
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

        # Metemos la imagen correspondiente
        if os.path.exists(ruta_img):
            perfil_window.profile_photo = crear_imagen_perfil(ruta_img)
        else:
            perfil_window.profile_photo = crear_imagen_perfil(ruta_default)

        # Metodo para transformar la ruta de la imagen seleccionada
        def seleccionar_imagen():
            ruta_origen = filedialog.askopenfilename(
                title="Selecciona una imagen",
                filetypes=(("Archivos de imagen", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Todos los archivos", "*.*"))
            )

            if ruta_origen:
                nombre_usuario = user_data.get("UserName", "").strip()
                if not nombre_usuario:
                    messagebox.showerror("Error", "No se encontró el nombre de usuario. No se puede guardar la imagen.", parent=perfil_window)
                    return

                # Guardar en una carpeta accesible, junto al .exe
                carpeta_destino = ruta_recurso("imagenes_usuarios")
                if not os.path.exists(carpeta_destino):
                    os.makedirs(carpeta_destino)


                # Creamos la nueva ruta para la imagen
                extension = os.path.splitext(ruta_origen)[1]
                nuevo_nombre = f"{nombre_usuario}{extension}"
                ruta_destino = os.path.join(carpeta_destino, nuevo_nombre)

                try:
                    # Cambio la variable que va asociada al dato en la BD (la imagen)
                    # Copiar imagen
                    shutil.copyfile(ruta_origen, ruta_destino)

                    # Guardar ruta relativa en la BD
                    ruta_relativa = os.path.relpath(ruta_destino)
                    user_data["rutaImagen"] = ruta_relativa

                    # Actualizar ruta en la base de datos
                    conn = sqlite3.connect(ruta_recurso('bd/Users.sqlite'))
                    cursor = conn.cursor()
                    cursor.execute("UPDATE Usuarios SET rutaImagen = ? WHERE UserName = ?", (ruta_relativa, nombre_usuario))
                    conn.commit()

                    # Actualizar imagen en la interfaz de la ventana
                    nueva_foto = crear_imagen_perfil(ruta_destino)
                    if nueva_foto:
                        perfil_window.profile_photo = nueva_foto
                        profile_photo_label.configure(image=perfil_window.profile_photo)
                        profile_photo_label.image = perfil_window.profile_photo

                except Exception as e:
                    messagebox.showerror("Error al copiar imagen", str(e), parent=perfil_window)
                finally:
                    if conn:
                        conn.close()

        profile_photo_label = ctk.CTkLabel(container, image=perfil_window.profile_photo, text="")
        profile_photo_label.pack(pady=(int(win_h * 0.02), int(win_h * 0.05)))
        profile_photo_label.bind("<Button-1>", lambda e: seleccionar_imagen())

        # Datos del usuario
        nombre = user_data.get("Nombre", "")
        apellidos = f"{user_data.get('Apellido1', '')} {user_data.get('Apellido2', '')}".strip()
        username = user_data.get("UserName", "")
        rol = user_data.get("User_Type", "")

        datos = [
            f"Nombre: {nombre} {apellidos}",
            f"Nombre de usuario: {username}",
            f"Tipo de usuario: {rol}"
        ]

        # Imprimo los datos en la ventana
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

    # Metodo para cerrar la app y volver al login
    def cerrar_sesion():
        global perfil_window
        
        # Cerrar la ventana de perfil si existe
        if perfil_window and perfil_window.winfo_exists():
            perfil_window.destroy()
        
        cerrar_todo()    

        # Reiniciar el login
        iniciar_login()

    # Metodo para ejecutar el login
    def iniciar_login():
        
        if hasattr(sys, '_MEIPASS'):
            subprocess.Popen(["HGC.exe"])
        else:
            os.system("python login.py")

    # Proporciones relativas para el tamaño del botón
    button_width = int(window_width * 0.06)
    button_height = int(window_height * 0.08)

    # Colores para hover y normal
    COLOR_NORMAL = "#990404"
    COLOR_HOVER = "#540303"

    folder_img = Image.open(ruta_recurso("resources/icons/white/folder.png"))
    folder_img = folder_img.resize((int(button_width * 0.65), int(button_height * 0.65)), Image.Resampling.LANCZOS)
    folder_img = ImageTk.PhotoImage(folder_img)


    # Metodo para acceder a la carpeta de informes
    def abrir_carpeta_informes():
        global carpeta_proceso
        ruta_carpeta = ruta_recurso("informes")

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
        hover_color=COLOR_HOVER,
        image=folder_img,
        text="",
        width=button_width,
        height=button_height,
        command=abrir_carpeta_informes
    )
    folder_button.grid(row=0, column=1, padx=10, pady=10, sticky="e")

    profile_img = Image.open(ruta_recurso("resources/icons/white/User.png"))
    profile_img = profile_img.resize((int(button_width * 0.8), int(button_height * 0.8)), Image.Resampling.LANCZOS)
    profile_img = ImageTk.PhotoImage(profile_img)

    # Crear el botón de perfil
    profile_button = ctk.CTkButton(
        frame_top,
        fg_color=COLOR_NORMAL,
        hover_color=COLOR_HOVER,
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

        # Tamaño, fuente e imagen para el botón
        fuente_custom = ctk.CTkFont(family="Toxigenesis Rg", size=int(window_height * 0.032))
        button_width = int(window_width * 0.25)
        button_height = int(window_height * 0.12)
        vertical_padding = int(window_height * 0.02)

        img_width = int(button_width * 0.20)
        img_height = int(button_height * 0.6)
        img = Image.open(img_path).resize((img_width, img_height), Image.Resampling.LANCZOS)
        img = ImageTk.PhotoImage(img)

        # Definimos el botón 
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

    # Creo los botones con el metodo 
    VO_Button = create_menu_button(frame_left, "Vehículo Ocasión", ruta_recurso("resources/icons/white/VO.png"), 0)
    Cliente_Button = create_menu_button(frame_left, "Clientes", ruta_recurso("resources/icons/white/Cliente.png"), 1)
    Proveedor_Button = create_menu_button(frame_left, "Proveedores", ruta_recurso("resources/icons/white/proveedores.png"), 2)
    Accreedores_Button = create_menu_button(frame_left, "Acreedores", ruta_recurso("resources/icons/white/acreedores.png"), 3)
    Facturacion_Button = create_menu_button(frame_left, "Facturación", ruta_recurso("resources/icons/white/facturas.png"), 4)
    AdminUsers_Button = create_menu_button(frame_left, "Admin Usuarios", ruta_recurso("resources/icons/white/administrador1.png"), 5)
    Manual_Button = create_menu_button(frame_left, "Manual de uso", ruta_recurso("resources/icons/white/manual_icon.png"), 6)

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
    # Cerrar todas las ventanas si cierro la app
    def cerrar_todo():
        for clase in (Proveedor, Cliente, Acreedor, VO, Facturacion, AdminUsuarios):
            for ventana in getattr(clase, "ventanas_secundarias", []):
                try:
                    ventana.destroy()
                except:
                    pass
            clase.ventanas_secundarias.clear()
        app.destroy()

    # Cerrar ventanas secudarias si cambio de botón (función)
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
    # Hovers
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

    # Limpiar el frame right para redibujar después
    def clear_frame_right():
        for widget in frame_right.winfo_children():
            widget.destroy()

    # Asginar funciones a cada botón
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

    # Relación botón <-> clase para saber cuál es el módulo activo
    boton_clase_map = {
        VO_Button: VO,
        Cliente_Button: Cliente,
        Proveedor_Button: Proveedor,
        Accreedores_Button: Acreedor,
        Facturacion_Button: VO,
        AdminUsers_Button: Configuracion,
        Manual_Button: Configuracion
    }

    # Hacer que el click ejecute la acción
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
