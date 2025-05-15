import sqlite3
from tkinter import ttk, StringVar, messagebox
import customtkinter as ctk
from PIL import Image
import screeninfo
import scripts.admin_usuarios as adminUsers
from tkcalendar import DateEntry
import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from textwrap import wrap
from datetime import datetime
import sqlite3
from tkinter import ttk, messagebox, filedialog
import customtkinter as ctk
from PIL import Image
import screeninfo
import os
import sys
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader
from textwrap import wrap
from datetime import datetime

class AdminUsuarios:
    current_page = 1
    rows_per_page = 20
    visible_columns = None
    Filtro = False
    query = ""
    search_column = ""
    selected_user = None  # Mantener el cliente seleccionado como variable estática
    query_params = ""
    ventana_abierta = False  
    icon_path = "resources/logos/icon_logo.ico"
    ventanas_secundarias = []

    column_name_map = {
        "UserName": "Nombre de Usuario",
        "Password": "Contraseña",
        "Nombre": "Nombre",
        "Apellido1": "1º Apellido",
        "Apellido2": "2º Apellido",
        "User_Type": "Tipo de Usuario",
        "rutaImagen": "Ruta Imagen",
    }
    column_options = {
        "UserName": "Nombre de Usuario",
        "Nombre": "Nombre",
        "Apellido1": "1º Apellido",
        "Apellido2": "2º Apellido",
        "User_Type": "Tipo de Usuario",
    }


    @staticmethod
    def create_table(query, columns, data, frame_right, app, clear_frame_right, total_pages, Filtro):
        for widget in frame_right.winfo_children():
            widget.destroy()

        AdminUsuarios.selected_user = None
        total_width = app.winfo_width()
        rel_size = total_width / 100

        if AdminUsuarios.visible_columns is None or not AdminUsuarios.visible_columns:
            AdminUsuarios.visible_columns = ["UserName","Nombre","Apellido1","Apellido2","User_Type"]

        # 🔒 Crear contenedor invisible
        main_container = ctk.CTkFrame(frame_right, fg_color="#3d3d3d")
        main_container.place_forget()

        # Contenido principal
        main_frame = ctk.CTkFrame(main_container, fg_color="#3d3d3d")
        main_frame.pack(fill="both", expand=True, padx=int(rel_size // 1.5), pady=int(rel_size // 1.5))

        #Estilo Botones
        btn_color = "black"
        btn_hover = "#16466e"
        icon_size = (int(rel_size * 3), int(rel_size * 2))
        
        #Barra dr Búsqueda
        search_frame = ctk.CTkFrame(main_frame, fg_color="transparent", corner_radius=int(rel_size // 2))
        search_frame.pack(fill="x", padx=rel_size // 6, pady=rel_size // 6)
        
        title = ctk.CTkLabel(search_frame, text="HGC - GESTIÓN DE USUARIOS", 
                                    font=("Sans Sulex", int(rel_size * 1.4)),
                                    text_color="white")
        title.pack(side="left", padx=rel_size * 1.2, pady=int(rel_size // 1.8))

        # Espaciador para empujar botones a la derecha
        spacer = ctk.CTkLabel(search_frame, text="")  # Vacío, sirve solo para expandir
        spacer.pack(side="left", expand=True)

        #Tabla
        tree_frame = ctk.CTkFrame(main_frame, fg_color="#3d3d3d")
        tree_frame.pack(fill="both", expand=True, padx=rel_size, pady=rel_size // 14)

        heading_font_size = int(rel_size)

        #Botones Navegación
        nav_frame = ctk.CTkFrame(main_frame, fg_color="#3d3d3d")
        nav_frame.pack(side="top", fill="x", padx=int(rel_size // 3), pady=int(rel_size // 3))

        prev_image = Image.open("resources/icons/white/angle-small-left.png").resize(icon_size)
        prev_image = ctk.CTkImage(light_image=prev_image)
        prev_btn = ctk.CTkButton(nav_frame, text="", image=prev_image, fg_color=btn_color,
                                height=rel_size, width=rel_size,
                                hover_color=btn_hover, corner_radius=250,
                                border_width=1, border_color="white",
                                command=lambda: AdminUsuarios.change_page(-1, frame_right, clear_frame_right, app))
        prev_btn.pack(side="left", padx=rel_size, pady=rel_size // 1.5)

        page_label = ctk.CTkLabel(nav_frame,
                                text=f"Página {AdminUsuarios.current_page} de {total_pages}",
                                font=("Sans Sulex", heading_font_size),
                                text_color="white")
        page_label.pack(side="left")

        next_image = Image.open("resources/icons/white/angle-small-right.png").resize(icon_size)
        next_image = ctk.CTkImage(light_image=next_image)
        next_btn = ctk.CTkButton(nav_frame, text="", image=next_image, fg_color=btn_color,
                                height=rel_size, width=rel_size,
                                hover_color=btn_hover, corner_radius=250,
                                border_width=1, border_color="white",
                                command=lambda: AdminUsuarios.change_page(1, frame_right, clear_frame_right, app))
        next_btn.pack(side="left", padx=rel_size, pady=rel_size // 1.5)
        
        #Botones Agregar/Modificar/Borrar
        action_frame = ctk.CTkFrame(nav_frame, fg_color="#3d3d3d")
        action_frame.pack(side="right", padx=rel_size, pady=rel_size // 1.5)

        add_image = Image.open("resources/icons/white/agregar.png").resize(icon_size)
        add_image = ctk.CTkImage(light_image=add_image)
        add_btn = ctk.CTkButton(action_frame, text="Agregar Usuario", image=add_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2), anchor="w",
                                border_width=1, border_color="white", command=lambda: AdminUsuarios.add_user(frame_right, clear_frame_right, app))
        add_btn.pack(side="left", padx=rel_size // 2)

        edit_image = Image.open("resources/icons/white/boli.png").resize(icon_size)
        edit_image = ctk.CTkImage(light_image=edit_image)
        edit_btn = ctk.CTkButton(action_frame, text="Editar Usuario", image=edit_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                border_width=1, border_color="white", command=lambda: AdminUsuarios.edit_user(AdminUsuarios.selected_user, frame_right, clear_frame_right, app))
        edit_btn.pack(side="left", padx=rel_size // 2)

        delete_image = Image.open("resources/icons/white/trash.png").resize(icon_size)
        delete_image = ctk.CTkImage(light_image=delete_image)
        delete_btn = ctk.CTkButton(action_frame, text="Borrar Usuario", image=delete_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                border_width=1, border_color="white", command=lambda: AdminUsuarios.delete_User(AdminUsuarios.selected_user, frame_right, clear_frame_right, app))
        delete_btn.pack(side="left", padx=rel_size // 2)

        if AdminUsuarios.current_page == 1:
            prev_btn.configure(state="disabled")
        if AdminUsuarios.current_page == total_pages:
            next_btn.configure(state="disabled")

        # Estimar altura de fila para llenar el espacio
        altura_total_disponible = int(app.winfo_height() * 0.65)
        altura_filas = int(altura_total_disponible / AdminUsuarios.rows_per_page)

        style = ttk.Style()
        style.theme_use("clam")  # Asegura compatibilidad con fondo y colores personalizados
        
        style.configure("Treeview",
                        font=("Sans Sulex", int(rel_size * 0.85)),
                        rowheight=altura_filas,
                        background="black",         # ← fondo de las filas
                        foreground="#ededed",         # ← texto blanco
                        fieldbackground="black",    # ← fondo general
                        bordercolor="black"
                        )

        style.configure("Treeview.Heading",
                        font=("Sans Sulex", int(rel_size * 0.85)),
                        foreground="#ededed",         # ← texto encabezado
                        background="black",       # ← fondo encabezado
                        bordercolor="black",
                        padding=(rel_size // 2, rel_size // 2))

        # Estilo para selección (resalta fila seleccionada)
        style.map("Treeview",
                background=[("selected", "#16466e")],  # celeste oscuro al seleccionar
                foreground=[("selected", "white")])    # texto blanco en selección


        tree = ttk.Treeview(tree_frame, columns=AdminUsuarios.visible_columns, show="headings", height=AdminUsuarios.rows_per_page)
        AdminUsuarios.tree = tree
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=x_scrollbar.set)
        x_scrollbar.pack(side="bottom", fill="x")
        
        tree.tag_configure('evenrow', background='#1a1a1a')  # Gris oscuro
        tree.tag_configure('oddrow', background='black')     # Negro

        for col in AdminUsuarios.visible_columns:
            tree.heading(col, text=AdminUsuarios.column_name_map.get(col, col), anchor="center")
            tree.column(col, anchor="center", stretch=True)

        # Inserta filas con colores alternos

##Picha Cambio Fecha-------------------------------------------------------------------------------------------------------------------
        def format_date(value):
            try:
                # Detecta si el valor es una fecha en formato yyyy-mm-dd o yyyy/mm/dd
                if isinstance(value, str) and "-" in value:
                    return datetime.strptime(value, "%Y-%m-%d").strftime("%d/%m/%Y")
                elif isinstance(value, str) and "/" in value:
                    return datetime.strptime(value, "%Y/%m/%d").strftime("%d/%m/%Y")
            except:
                pass
            return value  # Si no es una fecha válida, deja el valor original

        
        for i, row in enumerate(data):
            filtered_row = [row[columns.index(col)] for col in AdminUsuarios.visible_columns]
            
            # ➕ Formatea las fechas antes de mostrarlas
            for j, col in enumerate(AdminUsuarios.visible_columns):
                if "fecha" in col.lower() and isinstance(filtered_row[j], str):
                    filtered_row[j] = format_date(filtered_row[j])
            
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=filtered_row, tags=(tag,))
#----------------------------------------------------------------------------------------------------------------------------------------

        tree.pack(pady=rel_size // 1.5, fill="both", expand=True)
        tree.bind("<<TreeviewSelect>>", lambda event: AdminUsuarios.on_item_selected(tree))

        # ✅ MOSTRAR el frame principal una vez terminado
        main_container.place(relwidth=1.0, relheight=1.0)

    @staticmethod
    def search_data(query, search_column, frame_right, clear_frame_right, app):
        AdminUsuarios.query = query
        AdminUsuarios.search_column = search_column
        AdminUsuarios.Filtro = True
        AdminUsuarios.current_page = 1
        AdminUsuarios.load_data(frame_right, clear_frame_right, app)

    @staticmethod
    def load_data(frame_right, clear_frame_right, app):
        db_path = "bd/Users.sqlite"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            offset = (AdminUsuarios.current_page - 1) * AdminUsuarios.rows_per_page
            
            cursor.execute(f"SELECT COUNT(*) FROM Usuarios")
            total_rows = cursor.fetchone()[0]

            cursor.execute("SELECT UserName, Nombre, Apellido1, Apellido2, User_Type FROM Usuarios LIMIT ? OFFSET ?", (AdminUsuarios.rows_per_page, offset))

            data = cursor.fetchall()
            conn.close()

            total_pages = max((total_rows // AdminUsuarios.rows_per_page) + (1 if total_rows % AdminUsuarios.rows_per_page > 0 else 0), 1)

            AdminUsuarios.create_table(
                AdminUsuarios.query,
                ["UserName","Nombre","Apellido1","Apellido2","User_Type"],
                data,
                frame_right,
                app,
                clear_frame_right,
                total_pages,
                AdminUsuarios.Filtro
            )

        except sqlite3.Error as e:
            print("Error al cargar datos:", e)


    @staticmethod
    def clear_search(frame_right, clear_frame_right, app):
        AdminUsuarios.Filtro = False
        AdminUsuarios.query = ""
        AdminUsuarios.current_page = 1
        AdminUsuarios.abrir_admin(frame_right, clear_frame_right, app)

    @staticmethod
    def change_page(direction, frame_right, clear_frame_right, app):
        AdminUsuarios.current_page += direction
        AdminUsuarios.load_data(frame_right, clear_frame_right, app)

    @staticmethod
    def abrir_admin(frame_right, clear_frame_right, app):
        AdminUsuarios.load_data(frame_right, clear_frame_right, app)

    @staticmethod
    def get_db_column_from_display_name(display_name):
        for db_col, disp_name in AdminUsuarios.column_name_map.items():
            if disp_name == display_name:
                return db_col
        return display_name  # fallback en caso de no encontrarlo

    @staticmethod
    def add_user(frame_right, clear_frame_right, app):
        if AdminUsuarios.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        AdminUsuarios.ventana_abierta = True  # Marcamos la ventana como abierta
        
        appAdd = ctk.CTk()
        AdminUsuarios.ventanas_secundarias.append(appAdd)

        if sys.platform == "win32":
            import ctypes
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            appAdd.iconbitmap(AdminUsuarios.icon_path)

        appAdd.title("Agregar Usuario")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Tamaño relativo a la pantalla
        monitors = screeninfo.get_monitors()
        main_monitor = next((m for m in monitors if m.is_primary), monitors[0])
        window_width = int(main_monitor.width * 0.55)
        window_height = int(main_monitor.height * 0.70)
        x_position = (main_monitor.width - window_width) // 2
        y_position = (main_monitor.height - window_height) // 2
        appAdd.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        appAdd.resizable(False, False)

        fuente_labels = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.022))
        fuente_boton = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.03))
        fuente_titulo = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.045))

        padding_relativo = int(window_height * 0.02)
        main_frame = ctk.CTkFrame(appAdd, fg_color="#373737", corner_radius=0)
        main_frame.pack(pady=padding_relativo, padx=padding_relativo, fill="both", expand=True)

        titulo = ctk.CTkLabel(main_frame, text="Agregar Usuario", font=fuente_titulo, text_color="white")
        titulo.pack(pady=(int(window_height // 37),int(window_height // 37)))

        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=(int(window_height // 45)), pady=(int(window_height // 18.5)))

        campos = ["Nombre de Usuario","Contraseña","Nombre","1º Apellido","2º Apellido","Tipo de Usuario","Ruta Imagen"]

        entradas = []

        for campo in campos:
            fila = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            fila.pack(fill="x", padx=int(window_height // 18.5), pady=int(window_height * 0.015))

            label = ctk.CTkLabel(fila, text=campo + ":", font=fuente_labels, width=160, anchor="w", text_color="white")
            label.pack(side="left", padx=int(window_height // 18.5))

            if campo == "Tipo de Usuario":
                opciones = ["admin", "usuario"]
                om = ctk.CTkOptionMenu(fila, values=opciones, button_color="#990404",
                                    button_hover_color="#540303", fg_color="#181818",
                                    dropdown_fg_color="#181818", font=fuente_labels,
                                    dropdown_font=fuente_labels)
                om.set(opciones[0])
                om.pack(side="left", fill="x", expand=True)
                entradas.append(om)

            elif campo == "Ruta Imagen":
                entry_ruta = ctk.CTkEntry(fila, placeholder_text="Ruta de la imagen", font=fuente_labels,
                                        fg_color="#181818", text_color="white")
                entry_ruta.pack(side="left", fill="x", expand=True)
                entradas.append(entry_ruta)

                def seleccionar_archivo():
                    ruta_origen = filedialog.askopenfilename(
                        title="Selecciona una imagen",
                        filetypes=(("Archivos de imagen", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Todos los archivos", "*.*"))
                    )
                    if ruta_origen:
                        nombre_usuario = entradas[0].get().strip()
                        if not nombre_usuario:
                            messagebox.showerror("Error", "Introduce primero el Nombre de Usuario antes de seleccionar la imagen.", parent=appAdd)
                            return

                        import os
                        import shutil

                        carpeta_destino = "imagenes_usuarios"
                        if not os.path.exists(carpeta_destino):
                            os.makedirs(carpeta_destino)

                        extension = os.path.splitext(ruta_origen)[1]
                        nuevo_nombre = f"{nombre_usuario}{extension}"
                        ruta_destino = os.path.join(carpeta_destino, nuevo_nombre)

                        try:
                            shutil.copyfile(ruta_origen, ruta_destino)
                            entry_ruta.delete(0, "end")
                            entry_ruta.insert(0, ruta_destino)
                        except Exception as e:
                            messagebox.showerror("Error al copiar imagen", str(e), parent=appAdd)

                boton_ruta = ctk.CTkButton(fila, text="Seleccionar Imagen", font=fuente_labels,
                                        command=seleccionar_archivo,
                                        fg_color="#990404", hover_color="#540303", border_color="black",
                                        border_width=2)
                boton_ruta.pack(side="left", padx=int(window_height // 37))


            else:
                entry = ctk.CTkEntry(fila, placeholder_text=campo, font=fuente_labels,
                                    fg_color="#181818", text_color="white")
                entry.pack(side="left", fill="x", expand=True)
                entradas.append(entry)
                
                entry.bind("<FocusIn>", lambda event, e=entry: AdminUsuarios.on_focus_in_entry(e))
                entry.bind("<FocusOut>", lambda event, e=entry: AdminUsuarios.on_focus_out_entry(e))

        def guardar_nuevo_user():
            valores = []

            for idx, entrada in enumerate(entradas):
                label = campos[idx].replace(" ", "").replace("º", "").replace("-", "")
                contenido = entrada.get().strip()

                if isinstance(entrada, ctk.CTkOptionMenu):
                    if entrada.cget("values")[0] in ["Sí", "No"]:
                        valores.append("1" if entrada.get() == "Sí" else "0")
                    else:
                        valores.append(entrada.get())
                else:
                    valores.append(contenido)

            username = valores[0]
            password = valores[1]

            if not username:
                messagebox.showerror("Error de Validación", "El campo 'Nombre de Usuario' no puede estar vacío.", parent=appAdd)
                return

            if not password:
                messagebox.showerror("Error de Validación", "El campo 'Contraseña' no puede estar vacía.", parent=appAdd)
                return

            try:
                with sqlite3.connect("bd/Users.sqlite") as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO Usuarios (
                            UserName, Password, Nombre, Apellido1, Apellido2, User_Type, rutaImagen
                        ) VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, tuple(valores))
                    conn.commit()
                    AdminUsuarios.clear_search(frame_right, clear_frame_right, app)
                    AdminUsuarios.ventana_abierta = False
                    appAdd.destroy()

            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error de Base de Datos", f"Error al insertar usuario:\n{e}")

        boton_guardar = ctk.CTkButton(
            main_frame,
            text="Guardar Usuario",
            font=fuente_boton,
            fg_color="#990404",
            hover_color="#540303",
            border_width=2,
            border_color="black",
            corner_radius=10,
            height=int(window_height * 0.065),
            command=guardar_nuevo_user
        )
        boton_guardar.pack(pady=int(window_height * 0.03))
        
        def on_closing():
            AdminUsuarios.ventana_abierta = False
            AdminUsuarios.ventanas_secundarias.remove(appAdd)
            appAdd.destroy()

        appAdd.protocol("WM_DELETE_WINDOW", on_closing)
        appAdd.bind("<Return>", lambda event: guardar_nuevo_user())

        appAdd.mainloop()

    highlight_color = "#c91706"  # Color cuando se selecciona (borde)
    default_border_color = "#565b5e"  # Color del borde por defecto
    default_fg_color = "#181818"  # Color de fondo por defecto
    
    def on_focus_in_entry(entry):
        entry.configure(border_color=AdminUsuarios.highlight_color)
        entry.configure(fg_color="#181818")

    def on_focus_out_entry(entry):
        entry.configure(border_color=AdminUsuarios.default_border_color)
        entry.configure(fg_color=AdminUsuarios.default_fg_color)

    @staticmethod
    def edit_user(dni_cif, frame_right, clear_frame_right, app):
        if AdminUsuarios.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        AdminUsuarios.ventana_abierta = True  # Marcamos la ventana como abierta

        icon_path = "resources/logos/icon_logo.ico"
        conn = sqlite3.connect("bd/Users.sqlite")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Usuarios WHERE UserName = ?", (dni_cif,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            messagebox.showerror("Error", f"No se encontró Usuario con Nombre de Usuario: {dni_cif}")
            AdminUsuarios.ventana_abierta = False
            return

        appModify = ctk.CTk()
        AdminUsuarios.ventanas_secundarias.append(appModify)

        if sys.platform == "win32":
            import ctypes
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            appModify.iconbitmap(AdminUsuarios.icon_path)

        appModify.title("Editar Usuario")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Cambiar el icono de la ventana, si se proporciona una ruta
        if icon_path and os.path.exists(icon_path):
            app.iconbitmap(icon_path)

        # Ajuste del tamaño de la ventana según el monitor
        monitors = screeninfo.get_monitors()
        main_monitor = next((m for m in monitors if m.is_primary), monitors[0])
        window_width = int(main_monitor.width * 0.55)
        window_height = int(main_monitor.height * 0.70)
        x_position = (main_monitor.width - window_width) // 2
        y_position = (main_monitor.height - window_height) // 2
        appModify.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        appModify.resizable(False, False)

        # Definir la fuente relativa para labels y botones
        fuente_labels = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.022))  # Fuente más pequeña
        fuente_boton = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.03))  # Fuente del botón más pequeña
        fuente_titulo = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.045))

        padding_relativo = int(window_height * 0.02)  # Ajustamos el padding a un valor relativo al tamaño de la ventana
        main_frame = ctk.CTkFrame(appModify, fg_color="#373737", corner_radius=0)  # Color de fondo cambiado
        main_frame.pack(pady=padding_relativo, padx=padding_relativo, fill="both", expand=True)

        titulo = ctk.CTkLabel(main_frame, text="Editar Usuario", font=fuente_titulo, text_color="white")
        titulo.pack(pady=(int(window_height // 37), 37))

        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=int(window_height // 37), pady=int(window_height // 37))

        campos = [
            ("Nombre de Usuario", user[0]),
            ("Contraseña", user[1]),
            ("Nombre", user[2]),
            ("1º Apellido", user[3]),
            ("2º Apellido", user[4]),
            ("Tipo de Usuario", user[5]),
            ("Ruta Imagen", user[6])
        ]

        entradas = []

        for idx, (texto, valor) in enumerate(campos):
            fila = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            fila.pack(fill="x", padx=int(window_height // 18.5), pady=int(window_height * 0.015))  # Padding relativo

            label = ctk.CTkLabel(fila, text=texto + ":", font=fuente_labels, width=160, anchor="w", text_color="white")
            label.pack(side="left", padx=int(window_height // 18.5))

            if texto == "Tipo de Usuario":
                opciones = ["admin", "usuario"]
                option_menu = ctk.CTkOptionMenu(
                    fila, values=opciones,
                    button_color="#990404",  # Color del botón del OptionMenu
                    button_hover_color="#540303",  # Hover del OptionMenu
                    fg_color="#181818",  # Fondo gris oscuro del OptionMenu
                    dropdown_fg_color="#181818",  # Fondo negro en la lista del OptionMenu
                    font=fuente_labels,  # Fuente de texto del OptionMenu
                )
                option_menu.set(valor)  # Usamos el método `set()` para seleccionar el valor
                option_menu.pack(side="left", fill="x", expand=True)
                entradas.append(option_menu)

                # Aplicamos el manejo de focus a los OptionMenu
                option_menu.bind("<FocusIn>", lambda event, om=option_menu: AdminUsuarios.on_focus_in_option_menu(om))
                option_menu.bind("<FocusOut>", lambda event, om=option_menu: AdminUsuarios.on_focus_out_option_menu(om))
            
            elif texto == "Ruta Imagen":
                entry_ruta = ctk.CTkEntry(fila, placeholder_text="Ruta de la imagen", font=fuente_labels,
                                        fg_color="#181818", text_color="white")
                entry_ruta.insert(0, valor if valor else "")
                entry_ruta.pack(side="left", fill="x", expand=True)
                entradas.append(entry_ruta)

                def seleccionar_archivo():
                    ruta_origen = filedialog.askopenfilename(
                        title="Selecciona una imagen",
                        filetypes=(("Archivos de imagen", "*.png *.jpg *.jpeg *.bmp *.gif"), ("Todos los archivos", "*.*"))
                    )
                    if ruta_origen:
                        nombre_usuario = entradas[0].get().strip()
                        if not nombre_usuario:
                            messagebox.showerror("Error", "Introduce primero el Nombre de Usuario antes de seleccionar la imagen.", parent=appModify)
                            return

                        import os
                        import shutil

                        carpeta_destino = "imagenes_usuarios"
                        if not os.path.exists(carpeta_destino):
                            os.makedirs(carpeta_destino)

                        # Eliminar imagen anterior si existe
                        ruta_anterior = entry_ruta.get().strip()
                        if ruta_anterior and os.path.exists(ruta_anterior):
                            try:
                                os.remove(ruta_anterior)
                            except Exception as e:
                                messagebox.showwarning("Advertencia", f"No se pudo eliminar la imagen anterior:\n{e}", parent=appModify)

                        extension = os.path.splitext(ruta_origen)[1]
                        nuevo_nombre = f"{nombre_usuario}{extension}"
                        ruta_destino = os.path.join(carpeta_destino, nuevo_nombre)

                        try:
                            shutil.copyfile(ruta_origen, ruta_destino)
                            entry_ruta.delete(0, "end")
                            entry_ruta.insert(0, ruta_destino)
                        except Exception as e:
                            messagebox.showerror("Error al copiar imagen", str(e), parent=appModify)


                boton_ruta = ctk.CTkButton(fila, text="Seleccionar Imagen", font=fuente_labels,
                                        command=seleccionar_archivo,
                                        fg_color="#990404", hover_color="#540303", border_color="black",
                                        border_width=2)
                boton_ruta.pack(side="left", padx=int(window_height // 37))



            else:
                # Fondos oscuros para los Entry
                entry = ctk.CTkEntry(fila, placeholder_text=texto, font=fuente_labels, fg_color="#181818", text_color="white")
                entry.insert(0, valor if valor is not None else "")
                entry.pack(side="left", fill="x", expand=True)
                entradas.append(entry)

                # Aplicamos el manejo de focus a los Entry
                entry.bind("<FocusIn>", lambda event, e=entry: AdminUsuarios.on_focus_in_entry(e))
                entry.bind("<FocusOut>", lambda event, e=entry: AdminUsuarios.on_focus_out_entry(e))

        boton_guardar = ctk.CTkButton(
            main_frame,
            text="Guardar Cambios",
            font=fuente_boton,
            fg_color="#990404",  # Color de fondo
            hover_color="#540303",  # Hover del botón
            border_width= 2,
            border_color= "black",
            corner_radius=10,
            height=int(window_height * 0.065),  # Tamaño relativo al alto de la ventana
            command=lambda: guardar_cambios(dni_cif)
        )
        boton_guardar.pack(pady=int(window_height * 0.03))

        def guardar_cambios(dni_cif):
            valores = []

            for idx, entrada in enumerate(entradas):
                label = campos[idx][0].replace(" ", "").replace("º", "").replace("-", "")
                contenido = entrada.get().strip()

                if isinstance(entrada, ctk.CTkOptionMenu):
                    if entrada.cget("values")[0] in ["Sí", "No"]:
                        valores.append("1" if entrada.get() == "Sí" else "0")
                    else:
                        valores.append(entrada.get())
                else:
                    valores.append(contenido)
                    
            UserName = valores[0].strip()
            Password = valores[1].strip()

            if not UserName or not Password:
                mensaje = ""
                if not UserName:
                    mensaje += "El campo 'Nombre de Usuario' no puede estar vacío.\n"
                if not Password:
                    mensaje += "El campo 'Contraseña' no puede estar vacío."
                messagebox.showerror("Error de Validación", mensaje.strip(), parent=appModify)
                return  # No continuamos si faltan campos obligatorios

            # Si todo es válido, hacemos el update
            try:
                with sqlite3.connect("bd/Users.sqlite") as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE Usuarios SET
                            UserName = ?, Password = ?, Nombre = ?, Apellido1 = ?, Apellido2 = ?, User_Type = ?, rutaImagen = ?
                        WHERE UserName = ?
                    """, (*valores, dni_cif))  # Usa el DNI original para buscar el registro
                    conn.commit()

                AdminUsuarios.clear_search(frame_right, clear_frame_right, app)
                AdminUsuarios.ventana_abierta = False
                appModify.destroy()

            except sqlite3.IntegrityError:
                messagebox.showerror("Error", f"Ya existe un usuario con el Nombre de Usuario '{UserName}'.", parent=appModify)
            except sqlite3.OperationalError as e:
                messagebox.showerror("Error de Base de Datos", f"Ocurrió un error al guardar los cambios:\n{e}")

                
        def on_closing():
            AdminUsuarios.ventana_abierta = False
            AdminUsuarios.ventanas_secundarias.remove(appModify)
            appModify.destroy()

        appModify.protocol("WM_DELETE_WINDOW", on_closing)
        appModify.bind("<Return>", lambda event: guardar_cambios(dni_cif))
        appModify.mainloop()

    @staticmethod
    def on_item_selected(tree):
        selected_item = tree.selection()
        if selected_item:
            AdminUsuarios.selected_user = tree.item(selected_item, "values")[0]
    

    @staticmethod
    def delete_User(selected_dni, frame_right, clear_frame_right, app):
        if not selected_dni:
            messagebox.showwarning("Aviso", "Selecciona un usuario para borrar.")
            return

        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas borrar al usuario con Nombre de Usuario: {selected_dni}?"
        )

        if respuesta:
            try:
                # Primero obtenemos la ruta de la imagen asociada al usuario
                with sqlite3.connect("bd/Users.sqlite") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT rutaImagen FROM Usuarios WHERE UserName = ?", (selected_dni,))
                    ruta_imagen = cursor.fetchone()

                # Si existe una ruta de imagen, la borramos
                if ruta_imagen and ruta_imagen[0] and os.path.exists(ruta_imagen[0]):
                    try:
                        os.remove(ruta_imagen[0])  # Borramos la imagen
                    except Exception as e:
                        messagebox.showwarning("Advertencia", f"No se pudo eliminar la imagen del usuario:\n{e}")

                # Ahora borramos el usuario de la base de datos
                with sqlite3.connect("bd/Users.sqlite") as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Usuarios WHERE UserName = ?", (selected_dni,))
                    conn.commit()

                messagebox.showinfo("Éxito", f"Usuario con Nombre de Usuario {selected_dni} y su imagen eliminados correctamente.")
                AdminUsuarios.clear_search(frame_right, clear_frame_right, app)

            except sqlite3.OperationalError as e:
                messagebox.showerror("Error de Base de Datos", f"No se pudo eliminar el usuario:\n{e}")
        else:
            # El usuario eligió "No", no se hace nada
            return
