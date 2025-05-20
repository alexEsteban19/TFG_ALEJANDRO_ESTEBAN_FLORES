import sqlite3
from tkinter import ttk, StringVar, messagebox
import customtkinter as ctk
from PIL import Image, ImageTk
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
from functools import partial
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from babel.dates import format_datetime
import ctypes


class Acreedor:
    
    # Definimos variables base
    current_page = 1
    rows_per_page = 20
    visible_columns = None
    Filtro = False
    query = ""
    search_column = ""
    selected_Acreedor = None  # Mantener el Acreedor seleccionado como variable estática
    query_params = ""
    ventana_abierta = False  
    icon_path = "resources/logos/icon_logo.ico"
    ventanas_secundarias = []
    
    highlight_color = "#c91706"  # Color cuando se selecciona (borde)
    default_border_color = "#565b5e"  # Color del borde por defecto
    default_fg_color = "#181818"  # Color de fondo por defecto

    sort_column = None
    sort_order = "asc"  
    sort_states = {}  # Diccionario: {"columna": "asc" | "desc" | None}

    # todos los datos de la BD
    column_name_map = {
        "dni_cif": "DNI / CIF",
        "nombre": "Nombre",
        "apellido1": "1º Apellido",
        "apellido2": "2º Apellido",
        "direccion": "Dirección",
        "codigopostal": "Código Postal",
        "ciudad": "Ciudad",
        "idioma": "Idioma",
        "pais": "País",
        "telefono1": "Teléfono 1",
        "telefono2": "Teléfono 2",
        "telefono3": "Teléfono 3",
        "telefono4": "Teléfono 4",
        "fax1": "Fax 1",
        "fax2": "Fax 2",
        "email1": "Email 1",
    }

    # datos que muestra la tabla
    column_options = {
        "dni_cif": "DNI / CIF",
        "nombre": "Nombre",
        "apellido1": "1º Apellido",
        "apellido2": "2º Apellido",
        "direccion": "Dirección",
        "ciudad": "Ciudad",
        "telefono1": "Teléfono 1",
        "fax1": "Fax 1",
        "email1": "Email 1",
        "idioma": "Idioma",
    }

    # metodo para crear la tabla
    @staticmethod
    def create_table(query, columns, data, frame_right, app, clear_frame_right, total_pages, Filtro):
        for widget in frame_right.winfo_children():
            widget.destroy()

        Acreedor.selected_Acreedor = None
        total_width = app.winfo_width()
        rel_size = total_width / 100

        # Esta es la lista completa de columnas
        all_columns = [
            "dni_cif", "nombre", "apellido1", "apellido2", "direccion", "codigopostal", "ciudad", "idioma", "pais",
            "telefono1", "telefono2", "telefono3", "telefono4", "fax1", "fax2", "email1"
        ]

        # Usamos all_columns como respaldo si columns está vacío
        columns = columns or all_columns

        # Solo se establece visible_columns si aún no hay
        if Acreedor.visible_columns is None or not Acreedor.visible_columns:
            Acreedor.visible_columns = ["dni_cif", "nombre", "apellido1", "apellido2", "direccion", "ciudad",
                                        "telefono1", "fax1", "email1", "idioma"]


        # Contenedor invisible principal
        main_container = ctk.CTkFrame(frame_right, fg_color="#3d3d3d")
        main_container.place_forget()

        main_frame = ctk.CTkFrame(main_container, fg_color="#3d3d3d")
        main_frame.pack(fill="both", expand=True, padx=int(rel_size // 1.5), pady=int(rel_size // 1.5))

        btn_color = "black"
        btn_hover = "#16466e"
        icon_size = (int(rel_size * 3), int(rel_size * 2))

        #Barra dr Búsqueda
        search_frame = ctk.CTkFrame(main_frame, fg_color="transparent", corner_radius=int(rel_size // 2))
        search_frame.pack(fill="x", padx=rel_size // 6, pady=rel_size // 6)
        
        title = ctk.CTkLabel(search_frame, text="HGC - GESTIÓN DE ACREEDORES", 
                                    font=("Sans Sulex", int(rel_size * 1.4)),
                                    text_color="white")
        title.pack(side="left", padx=rel_size * 1.2, pady=int(rel_size // 1.8))

        # Espaciador para empujar botones a la derecha
        spacer = ctk.CTkLabel(search_frame, text="")  # Vacío, sirve solo para expandir
        spacer.pack(side="left", expand=True)

        factu_image = Image.open("resources/icons/white/facturas.png").resize(icon_size)
        factu_image = ctk.CTkImage(light_image=factu_image)
        factu_btn = ctk.CTkButton(search_frame, text="Crear Factura", image=factu_image, fg_color=btn_color,
                                font=("Sans Sulex", int(rel_size)),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2), anchor="w",
                                border_width=2, border_color="white", command=lambda: Acreedor.add_factura(Acreedor.selected_Acreedor, frame_right, clear_frame_right, app))
        factu_btn.pack(side="left", padx=rel_size // 2, pady=int(rel_size // 1.8))

        informe_image = Image.open("resources/icons/white/votacion.png").resize(icon_size)
        informe_image = ctk.CTkImage(light_image=informe_image)
        informe_btn = ctk.CTkButton(search_frame, text="Generar Informe", image=informe_image, fg_color=btn_color,
                                font=("Sans Sulex", int(rel_size)),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2), anchor="w",
                                border_width=2, border_color="white", command=lambda: Acreedor.generate_inform(app))
        informe_btn.pack(side="left", padx=rel_size // 2, pady=int(rel_size // 1.8))

        search_plus_image = Image.open("resources/icons/white/search.png").resize(icon_size)
        search_plus_image = ctk.CTkImage(light_image=search_plus_image)
        search_plus_button = ctk.CTkButton(search_frame, text="", image=search_plus_image, fg_color=btn_color,
                                    hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                    border_width=2, border_color="white",
                                    width=icon_size[0], height=icon_size[1],command=lambda: Acreedor.search_plus(frame_right, clear_frame_right, app)
                                    )
        search_plus_button.pack(side="left", padx=rel_size // 1.5)
        
        refresh_image = Image.open("resources/icons/white/refresh.png").resize(icon_size)
        refresh_image = ctk.CTkImage(light_image=refresh_image)
        clear_search_button = ctk.CTkButton(search_frame, text="", image=refresh_image, fg_color=btn_color,
                                            hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                            border_width=2, border_color="white",
                                            width=icon_size[0], height=icon_size[1],
                                            command=lambda: Acreedor.clear_search(frame_right, clear_frame_right, app))
        clear_search_button.pack(side="left", padx=rel_size // 1.5)
        
        # Frame desplegable principal
        column_filter_frame = ctk.CTkFrame(frame_right, fg_color="black", corner_radius=15, width=300)
        filter_open = [False]  # Para mutabilidad
        # Frame para el botón fijo en la parte de abajo
        button_frame = ctk.CTkFrame(column_filter_frame, fg_color="black")
        button_frame.pack(anchor="w",side="bottom",fill="both")

        apply_button = ctk.CTkButton(
            button_frame,
            font=("Sans Sulex", int(rel_size * 1.1)),
            text="Aplicar",
            command=lambda: apply_filter(),
            fg_color="#990404",
            hover_color="#540303",
            height=rel_size * 2.2,
            width=rel_size * 11
        )
        apply_button.pack(pady=rel_size // 5, padx=rel_size // 7)
        # Scrollable frame para los checkboxes
        checkbox_scroll_frame = ctk.CTkScrollableFrame(column_filter_frame, fg_color="black")
        checkbox_scroll_frame.pack(side="top", fill="both", expand=True)

        # Variables y checkboxes
        selected_columns = {
            col: ctk.BooleanVar(value=(col in Acreedor.visible_columns)) for col in columns
        }

        for col in columns:
            if col == "dni_cif":
                continue  # Saltar esta columna específica
            checkbox = ctk.CTkCheckBox(
                checkbox_scroll_frame,
                font=("Sans Sulex", int(rel_size * 1.1)),
                text=Acreedor.column_name_map.get(col, col),
                variable=selected_columns[col],
                fg_color="#990404",
                hover_color="#540303"
            )
            checkbox.pack(anchor="w", padx=int(rel_size // 3), pady=int(rel_size // 3))
      
        # Funciones toggle y apply
        def toggle_filter_dropdown():
            padding_x = 0.015  # Márgenes horizontales 
            padding_y = 0.02   # Márgenes verticales

            if filter_open[0]:
                column_filter_frame.place_forget()
                main_frame.place_configure(relwidth=1.0)
                filter_open[0] = False
            else:
                # Calculamos tamaño con márgenes simulados
                relwidth = 0.2 - (2 * padding_x)
                relheight = 46*padding_y
                relx = 0.8 + padding_x
                rely = 0.01 + padding_y

                column_filter_frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)
                main_frame.place_configure(relwidth=0.8)
                filter_open[0] = True

        def apply_filter():
            visible = [col for col, var in selected_columns.items() if var.get()]
            Acreedor.visible_columns = visible if visible else columns[:]
            toggle_filter_dropdown()
            Acreedor.abrir_Acreedor(frame_right, clear_frame_right, app, mantener_filtro=True)

            
        # Botón filtros
        filter_image = Image.open("resources/icons/white/ojoblanco.png").resize(icon_size)
        filter_image = ctk.CTkImage(light_image=filter_image)
        filter_button = ctk.CTkButton(
            search_frame, text="", image=filter_image, fg_color=btn_color,
            hover_color=btn_hover, corner_radius=int(rel_size // 2),
            border_width=2, border_color="white",
            width=icon_size[0], height=icon_size[1],
            command=lambda: toggle_filter_dropdown()
        )
        filter_button.pack(side="left", padx=rel_size // 1.5)
        
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
                                command=lambda: Acreedor.change_page(-1, frame_right, clear_frame_right, app))
        prev_btn.pack(side="left", padx=rel_size, pady=rel_size // 1.5)

        page_label = ctk.CTkLabel(nav_frame,
                                text=f"Página {Acreedor.current_page} de {total_pages}",
                                font=("Sans Sulex", heading_font_size),
                                text_color="white")
        page_label.pack(side="left")

        next_image = Image.open("resources/icons/white/angle-small-right.png").resize(icon_size)
        next_image = ctk.CTkImage(light_image=next_image)
        next_btn = ctk.CTkButton(nav_frame, text="", image=next_image, fg_color=btn_color,
                                height=rel_size, width=rel_size,
                                hover_color=btn_hover, corner_radius=250,
                                border_width=1, border_color="white",
                                command=lambda: Acreedor.change_page(1, frame_right, clear_frame_right, app))
        next_btn.pack(side="left", padx=rel_size, pady=rel_size // 1.5)
        
        #Botones Agregar/Modificar/Borrar
        action_frame = ctk.CTkFrame(nav_frame, fg_color="#3d3d3d")
        action_frame.pack(side="right", padx=rel_size, pady=rel_size // 1.5)

        add_image = Image.open("resources/icons/white/agregar.png").resize(icon_size)
        add_image = ctk.CTkImage(light_image=add_image)
        add_btn = ctk.CTkButton(action_frame, text="Agregar Acreedor", image=add_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2), anchor="w",
                                border_width=1, border_color="white", command=lambda: Acreedor.add_Acreedor(frame_right, clear_frame_right, app))
        add_btn.pack(side="left", padx=rel_size // 2)

        edit_image = Image.open("resources/icons/white/boli.png").resize(icon_size)
        edit_image = ctk.CTkImage(light_image=edit_image)
        edit_btn = ctk.CTkButton(action_frame, text="Editar Acreedor", image=edit_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                border_width=1, border_color="white", command=lambda: Acreedor.edit_Acreedor(Acreedor.selected_Acreedor, frame_right, clear_frame_right, app))
        edit_btn.pack(side="left", padx=rel_size // 2)

        delete_image = Image.open("resources/icons/white/trash.png").resize(icon_size)
        delete_image = ctk.CTkImage(light_image=delete_image)
        delete_btn = ctk.CTkButton(action_frame, text="Borrar Acreedor", image=delete_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                border_width=1, border_color="white", command=lambda: Acreedor.delete_Acreedor(Acreedor.selected_Acreedor, frame_right, clear_frame_right, app))
        delete_btn.pack(side="left", padx=rel_size // 2)

        if Acreedor.current_page == 1:
            prev_btn.configure(state="disabled")
        if Acreedor.current_page == total_pages:
            next_btn.configure(state="disabled")

        # Estimar altura de fila para llenar el espacio
        altura_total_disponible = int(app.winfo_height() * 0.65)
        altura_filas = int(altura_total_disponible / Acreedor.rows_per_page)

        style = ttk.Style()
        style.theme_use("clam")  # Asegura compatibilidad con fondo y colores personalizados
        
        style.configure("Treeview",
                        font=("Sans Sulex", int(rel_size * 0.85)),
                        rowheight=altura_filas,
                        background="black",         # fondo de las filas
                        foreground="#ededed",         # texto blanco
                        fieldbackground="black",    # fondo general
                        bordercolor="black"
                        )

        style.configure("Treeview.Heading",
                        font=("Sans Sulex", int(rel_size * 0.85)),
                        foreground="#ededed",         # texto encabezado
                        background="black",       # fondo encabezado
                        bordercolor="black",
                        padding=(rel_size // 2, rel_size // 2))

        # Estilo para selección (resalta fila seleccionada)
        style.map("Treeview",
                background=[("selected", "#16466e")],  # celeste oscuro al seleccionar
                foreground=[("selected", "white")])    # texto blanco en selección


        tree = ttk.Treeview(tree_frame, columns=Acreedor.visible_columns, show="headings", height=Acreedor.rows_per_page)
        Acreedor.tree = tree
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=x_scrollbar.set)
        x_scrollbar.pack(side="bottom", fill="x")
        
        tree.tag_configure('evenrow', background='#1a1a1a')  # Gris oscuro
        tree.tag_configure('oddrow', background='black')     # Negro



        for col in Acreedor.visible_columns:
            tree.heading(
                col,
                text=Acreedor.column_name_map.get(col, col), 
                anchor="center",
                command=partial( Acreedor.sort_column_click, col, tree, frame_right, clear_frame_right, app)
            )
            tree.column(col, width=int(rel_size * 9), anchor="center", stretch=False)


        for col in Acreedor.visible_columns:
            tree.heading(col, text=Acreedor.column_name_map.get(col, col), anchor="center")
            tree.column(col, width=int(rel_size * 9), anchor="center", stretch=False)

#Cambio Fecha-------------------------------------------------------------------------------------------------------------------
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
            filtered_row = [row[columns.index(col)] for col in Acreedor.visible_columns]
            
            # Formatea las fechas antes de mostrarlas
            for j, col in enumerate(Acreedor.visible_columns):
                if "fecha" in col.lower() and isinstance(filtered_row[j], str):
                    filtered_row[j] = format_date(filtered_row[j])
            
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=filtered_row, tags=(tag,))
#----------------------------------------------------------------------------------------------------------------------------------------

            
        tree.pack(pady=rel_size // 1.5, fill="both", expand=True)

        tree.bind("<<TreeviewSelect>>", lambda event: Acreedor.on_item_selected(tree))

        # MOSTRAR el frame principal una vez terminado
        main_container.place(relwidth=1.0, relheight=1.0)

        Acreedor.refresh_treeview_headings(tree, frame_right, clear_frame_right, app)


    @staticmethod
    def load_data(frame_right, clear_frame_right, app):
        db_path = "bd/Concesionario.db"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            offset = (Acreedor.current_page - 1) * Acreedor.rows_per_page

            # Construir cláusula ORDER BY si hay orden seleccionado
            order_clause = ""
            # Esto normaliza las letras con tilde (solo mayúsculas/minúsculas comunes en español)
            if Acreedor.sort_column:
                direction = Acreedor.sort_order if Acreedor.sort_order in ("asc", "desc") else "asc"
                col = Acreedor.sort_column
                col_normalized = (
          f"REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LOWER(\"{col}\"), 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u'), 'Á', 'a'), 'É', 'e'), 'Í','i'), 'Ó','o'), 'Ú','u')"
                )
                order_clause = f"ORDER BY {col_normalized} {direction}"
            else:
                order_clause = ""

            if Acreedor.Filtro:
                if isinstance(Acreedor.query_params, list):  # viene de search_plus
                    count_sql = f"SELECT COUNT(*) FROM Acreedor WHERE {Acreedor.query}"
                    cursor.execute(count_sql, Acreedor.query_params)
                    total_rows = cursor.fetchone()[0]

                    select_sql = f"SELECT * FROM Acreedor WHERE {Acreedor.query} {order_clause} LIMIT ? OFFSET ?"
                    cursor.execute(select_sql, Acreedor.query_params + [Acreedor.rows_per_page, offset])
                else:  # viene de search_data
                    cursor.execute(f"SELECT COUNT(*) FROM Acreedor WHERE {Acreedor.search_column} LIKE ?", (f"{Acreedor.query}%",))
                    total_rows = cursor.fetchone()[0]

                    cursor.execute(
                        f"SELECT * FROM Acreedor WHERE {Acreedor.search_column} LIKE ? {order_clause} LIMIT ? OFFSET ?",
                        (f"{Acreedor.query}%", Acreedor.rows_per_page, offset)
                    )
            else:
                cursor.execute("SELECT COUNT(*) FROM Acreedor")
                total_rows = cursor.fetchone()[0]

                cursor.execute(f"SELECT * FROM Acreedor {order_clause} LIMIT ? OFFSET ?", (Acreedor.rows_per_page, offset))

            data = cursor.fetchall()
            conn.close()

            total_pages = max((total_rows // Acreedor.rows_per_page) + (1 if total_rows % Acreedor.rows_per_page > 0 else 0), 1)

            Acreedor.create_table(
                Acreedor.query,
                [
                    "dni_cif", "nombre", "apellido1", "apellido2", "direccion",
                    "codigopostal", "ciudad", "idioma", "pais",
                    "telefono1", "telefono2", "telefono3", "telefono4",
                    "fax1", "fax2", "email1"
                ],
                data,
                frame_right,
                app,
                clear_frame_right,
                total_pages,
                Acreedor.Filtro
            )

        except sqlite3.Error as e:
            print("Error al cargar datos:", e)


    @staticmethod
    def clear_search(frame_right, clear_frame_right, app):
        Acreedor.Filtro = False
        Acreedor.query = ""
        Acreedor.current_page = 1
        Acreedor.abrir_Acreedor(frame_right, clear_frame_right, app)

    @staticmethod
    def change_page(direction, frame_right, clear_frame_right, app):
        Acreedor.current_page += direction
        Acreedor.load_data(frame_right, clear_frame_right, app)

    @staticmethod
    def abrir_Acreedor(frame_right, clear_frame_right, app, mantener_filtro=False):
        if not mantener_filtro:
            Acreedor.Filtro = False
            Acreedor.query = ""
            Acreedor.search_column = ""
            Acreedor.current_page = 1

        Acreedor.load_data(frame_right, clear_frame_right, app)


    @staticmethod
    def get_db_column_from_display_name(display_name):
        for db_col, disp_name in Acreedor.column_name_map.items():
            if disp_name == display_name:
                return db_col
        return display_name  

    @staticmethod
    def add_Acreedor(frame_right, clear_frame_right, app):
        if Acreedor.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        Acreedor.ventana_abierta = True  # Marcamos la ventana como abierta
        
        appAdd = ctk.CTk()
        Acreedor.ventanas_secundarias.append(appAdd)

        if sys.platform == "win32":
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            appAdd.iconbitmap(Acreedor.icon_path)

        appAdd.title("Agregar Acreedor")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        # Tamaño relativo a la pantalla
        monitors = screeninfo.get_monitors()
        main_monitor = next((m for m in monitors if m.is_primary), monitors[0])
        window_width = int(main_monitor.width * 0.55)
        window_height = int(main_monitor.height * 0.75)
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

        titulo = ctk.CTkLabel(main_frame, text="Agregar Acreedor", font=fuente_titulo, text_color="white")
        titulo.pack(pady=(int(window_height // 37),int(window_height // 37)))

        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=(int(window_height // 45)), pady=(int(window_height // 18.5)))

        campos = [
            "DNI / CIF", "Nombre", "1º apellido", "2º apellido", "Dirección",
                    "Código Postal", "Ciudad", "Idioma", "Pais",
                    "Telefono 1", "Telefono 2", "Telefono 3", "Telefono 4",
                    "Fax 1", "Fax2", "Email 1"
        ]

        entradas = []

        for idx, campo in enumerate(campos):
            fila = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            fila.pack(fill="x", padx=int(window_height // 18.5), pady=int(window_height * 0.015))

            label = ctk.CTkLabel(fila, text=campo + ":", font=fuente_labels, width=160, anchor="w", text_color="white")
            label.pack(side="left", padx=int(window_height // 18.5))

            entry = ctk.CTkEntry(fila, placeholder_text=campo, font=fuente_labels,
                                fg_color="#181818", text_color="white")
            
            entry.pack(side="left", fill="x", expand=True)
            entradas.append(entry)

            entry.bind("<FocusIn>", lambda event, e=entry: Acreedor.on_focus_in_entry(e))
            entry.bind("<FocusOut>", lambda event, e=entry: Acreedor.on_focus_out_entry(e))

        def guardar_nuevo_Acreedor():
            valores = []

            for idx, entrada in enumerate(entradas):
                label = campos[idx].replace(" ", "").replace("º", "").replace("-", "")
                contenido = entrada.get().strip()
                valores.append(contenido)

            dni = valores[0]
            if not dni:
                messagebox.showerror("Error de Validación", "El campo 'DNI / CIF' no puede estar vacío.", parent=appAdd)
                return  # Evita continuar y mantiene la ventana abierta
            
            try:
                with sqlite3.connect("bd/Concesionario.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO Acreedor (
                            dni_cif, nombre, apellido1, apellido2, direccion,
                            codigopostal, ciudad, idioma, pais,
                            telefono1, telefono2, telefono3, telefono4,
                            fax1, fax2, email1
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, tuple(valores))
                    conn.commit()
                    Acreedor.clear_search(frame_right, clear_frame_right, app)
                    Acreedor.ventana_abierta = False
                    appAdd.destroy()

            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error de Base de Datos", f"Error al insertar Acreedor:\n{e}")

        boton_guardar = ctk.CTkButton(
            main_frame,
            text="Guardar Acreedor",
            font=fuente_boton,
            fg_color="#990404",
            hover_color="#540303",
            border_width=2,
            border_color="black",
            corner_radius=10,
            height=int(window_height * 0.065),
            command=guardar_nuevo_Acreedor
        )
        boton_guardar.pack(pady=int(window_height * 0.03))
        
        def on_closing():
            Acreedor.ventana_abierta = False
            Acreedor.ventanas_secundarias.remove(appAdd)
            appAdd.destroy()

        appAdd.protocol("WM_DELETE_WINDOW", on_closing)
        appAdd.bind("<Return>", lambda event: guardar_nuevo_Acreedor())

        appAdd.mainloop()


    highlight_color = "#c91706"  # Color cuando se selecciona (borde)
    default_border_color = "#565b5e"  # Color del borde por defecto
    default_fg_color = "#181818"  # Color de fondo por defecto
    
    def on_focus_in_entry(entry):
        entry.configure(border_color=Acreedor.highlight_color)
        entry.configure(fg_color="#181818")

    def on_focus_out_entry(entry):
        entry.configure(border_color=Acreedor.default_border_color)
        entry.configure(fg_color=Acreedor.default_fg_color)

    @staticmethod
    def edit_Acreedor(dni_cif, frame_right, clear_frame_right, app):
        if Acreedor.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        Acreedor.ventana_abierta = True

        icon_path = "resources/logos/icon_logo.ico"
        conn = sqlite3.connect("bd/Concesionario.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT dni_cif, nombre, apellido1, apellido2, direccion, codigopostal, ciudad,
                idioma, pais, telefono1, telefono2, telefono3, telefono4,
                fax1, fax2, email1
            FROM Acreedor WHERE dni_cif = ?
        """, (dni_cif,))
        acreedor_data = cursor.fetchone()
        conn.close()

        if not acreedor_data:
            messagebox.showerror("Error", f"No se encontró Acreedor con DNI/CIF: {dni_cif}")
            Acreedor.ventana_abierta = False
            return

        appModify = ctk.CTk()
        Acreedor.ventanas_secundarias.append(appModify)

        if sys.platform == "win32":
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            appModify.iconbitmap(icon_path)

        appModify.title("Editar Acreedor")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        monitors = screeninfo.get_monitors()
        main_monitor = next((m for m in monitors if m.is_primary), monitors[0])
        window_width = int(main_monitor.width * 0.55)
        window_height = int(main_monitor.height * 0.70)
        x_position = (main_monitor.width - window_width) // 2
        y_position = (main_monitor.height - window_height) // 2
        appModify.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        appModify.resizable(False, False)

        fuente_labels = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.022))
        fuente_boton = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.03))
        fuente_titulo = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.045))

        padding_relativo = int(window_height * 0.02)
        main_frame = ctk.CTkFrame(appModify, fg_color="#373737", corner_radius=0)
        main_frame.pack(pady=padding_relativo, padx=padding_relativo, fill="both", expand=True)

        titulo = ctk.CTkLabel(main_frame, text="Editar Acreedor", font=fuente_titulo, text_color="white")
        titulo.pack(pady=(int(window_height // 37), 37))

        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=int(window_height // 37), pady=int(window_height // 37))

        campos = [
            ("DNI / CIF", acreedor_data[0]),
            ("Nombre", acreedor_data[1]),
            ("1º Apellido", acreedor_data[2]),
            ("2º Apellido", acreedor_data[3]),
            ("Dirección", acreedor_data[4]),
            ("Código Postal", acreedor_data[5]),
            ("Ciudad", acreedor_data[6]),
            ("Idioma", acreedor_data[7]),
            ("País", acreedor_data[8]),
            ("Teléfono 1", acreedor_data[9]),
            ("Teléfono 2", acreedor_data[10]),
            ("Teléfono 3", acreedor_data[11]),
            ("Teléfono 4", acreedor_data[12]),
            ("Fax 1", acreedor_data[13]),
            ("Fax 2", acreedor_data[14]),
            ("Email 1", acreedor_data[15])
        ]

        entradas = []

        for texto, valor in campos:
            fila = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            fila.pack(fill="x", padx=int(window_height // 18.5), pady=int(window_height * 0.015))

            label = ctk.CTkLabel(fila, text=texto + ":", font=fuente_labels, width=160, anchor="w", text_color="white")
            label.pack(side="left", padx=int(window_height // 18.5))

            entry = ctk.CTkEntry(fila, placeholder_text=texto, font=fuente_labels, fg_color="#181818", text_color="white")
            entry.insert(0, valor if valor is not None else "")
            entry.pack(side="left", fill="x", expand=True)
            entradas.append(entry)

            entry.bind("<FocusIn>", lambda event, e=entry: Acreedor.on_focus_in_entry(e))
            entry.bind("<FocusOut>", lambda event, e=entry: Acreedor.on_focus_out_entry(e))

        def guardar_cambios(dni_cif):
            valores = [entrada.get().strip() for entrada in entradas]
            nuevo_dni = valores[0]

            if not nuevo_dni:
                messagebox.showerror("Error de Validación", "El campo 'DNI / CIF' no puede estar vacío.", parent=appModify)
                return

            try:
                with sqlite3.connect("bd/Concesionario.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE Acreedor SET
                            dni_cif = ?, nombre = ?, apellido1 = ?, apellido2 = ?, direccion = ?,
                            codigopostal = ?, ciudad = ?, idioma = ?, pais = ?,
                            telefono1 = ?, telefono2 = ?, telefono3 = ?, telefono4 = ?,
                            fax1 = ?, fax2 = ?, email1 = ?
                        WHERE dni_cif = ?
                    """, (*valores, dni_cif))
                    conn.commit()

                Acreedor.clear_search(frame_right, clear_frame_right, app)
                Acreedor.ventana_abierta = False
                appModify.destroy()

            except sqlite3.IntegrityError:
                messagebox.showerror("Error", f"Ya existe un Acreedor con el DNI/CIF '{nuevo_dni}'.", parent=appModify)
            except sqlite3.OperationalError as e:
                messagebox.showerror("Error de Base de Datos", f"Ocurrió un error al guardar los cambios:\n{e}", parent=appModify)

        def on_closing():
            Acreedor.ventana_abierta = False
            Acreedor.ventanas_secundarias.remove(appModify)
            appModify.destroy()

        boton_guardar = ctk.CTkButton(
            main_frame,
            text="Guardar Cambios",
            font=fuente_boton,
            fg_color="#990404",
            hover_color="#540303",
            border_width=2,
            border_color="black",
            corner_radius=10,
            height=int(window_height * 0.065),
            command=lambda: guardar_cambios(dni_cif)
        )
        boton_guardar.pack(pady=int(window_height * 0.03))

        appModify.protocol("WM_DELETE_WINDOW", on_closing)
        appModify.bind("<Return>", lambda event: guardar_cambios(dni_cif))
        appModify.mainloop()


    @staticmethod
    def on_item_selected(tree):
        selected_item = tree.selection()
        if selected_item:
            Acreedor.selected_Acreedor = tree.item(selected_item, "values")[0]
    

    @staticmethod
    def delete_Acreedor(selected_dni, frame_right, clear_frame_right, app):
        if not selected_dni:
            messagebox.showwarning("Aviso", "Selecciona un Acreedor para borrar.")
            return

        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas borrar al Acreedor con DNI/CIF: {selected_dni}?"
        )

        if respuesta:
            try:
                with sqlite3.connect("bd/Concesionario.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM Acreedor WHERE dni_cif = ?", (selected_dni,))
                    conn.commit()

                messagebox.showinfo("Éxito", f"Acreedor con DNI/CIF {selected_dni} eliminado correctamente.")
                Acreedor.clear_search(frame_right, clear_frame_right, app)

            except sqlite3.OperationalError as e:
                messagebox.showerror("Error de Base de Datos", f"No se pudo eliminar el Acreedor:\n{e}")
        else:
            # El usuario eligió "No", no se hace nada
            return
    
    @staticmethod
    def obtener_datos_filtrados(columnas_sql):
        conn = sqlite3.connect("bd/Concesionario.db")
        cursor = conn.cursor()

        if Acreedor.Filtro:
            if isinstance(Acreedor.query_params, list):
                # Búsqueda avanzada
                cursor.execute(
                    f"SELECT {columnas_sql} FROM Acreedor WHERE {Acreedor.query}",
                    Acreedor.query_params
                )
            else:
                # Búsqueda simple
                cursor.execute(
                    f"SELECT {columnas_sql} FROM Acreedor WHERE {Acreedor.search_column} LIKE ?",
                    (f"{Acreedor.query}%",)
                )
        else:
            # Sin filtros
            cursor.execute(f"SELECT {columnas_sql} FROM Acreedor")

        datos = cursor.fetchall()
        conn.close()
        return datos

    @staticmethod
    def generate_inform(app):
        if Acreedor.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        Acreedor.ventana_abierta = True

        def confirmar_guardado(event=None):
            nombre_archivo = entrada_nombre.get().strip()

            if not nombre_archivo:
                messagebox.showerror("Error", "Debes introducir un nombre para el informe.", parent=ventana_nombre)
                return

            if not check_predefinido.get() and not check_personalizado.get():
                messagebox.showerror("Error", "Debes seleccionar un tipo de informe (predefinido o personalizado).", parent=ventana_nombre)
                return

            if check_predefinido.get() and check_personalizado.get():
                messagebox.showerror("Error", "Solo puedes seleccionar una opción.", parent=ventana_nombre)
                return

            if not nombre_archivo.endswith(".pdf"):
                nombre_archivo += ".pdf"

            ruta = os.path.join("informes", "Acreedores", nombre_archivo)
            os.makedirs(os.path.dirname(ruta), exist_ok=True)

            try:
                if check_predefinido.get():
                    columnas_fijas = [
                        "dni_cif", "nombre", "apellido1", "apellido2", "direccion",
                        "ciudad", "telefono1", "email1", "idioma"
                    ]
                    columnas_sql = ", ".join(columnas_fijas)
                    datos = Acreedor.obtener_datos_filtrados(columnas_sql)
                    paginas = [datos[i:i + Acreedor.rows_per_page] for i in range(0, len(datos), Acreedor.rows_per_page)]
                    Acreedor.generar_informe_pdf_fijo(paginas, ruta)

                elif check_personalizado.get():
                    columnas_visibles = Acreedor.visible_columns
                    columnas_sql = ", ".join(columnas_visibles)
                    columnas_texto = [Acreedor.column_name_map[col] for col in columnas_visibles]
                    datos = Acreedor.obtener_datos_filtrados(columnas_sql)
                    paginas = [datos[i:i + Acreedor.rows_per_page] for i in range(0, len(datos), Acreedor.rows_per_page)]
                    Acreedor.generar_informe_pdf(paginas, columnas_texto, ruta)

                cerrar_ventana()
                messagebox.showinfo("Éxito", f"Informe generado como:\n{ruta}", parent=app)

                import platform
                if platform.system() == "Windows":
                    os.startfile(ruta)
                elif platform.system() == "Darwin":
                    os.system(f"open '{ruta}'")
                else:
                    os.system(f"xdg-open '{ruta}'")

            except Exception as e:
                messagebox.showerror("Error", f"No se pudo generar el informe.\n\n{e}", parent=app)
                cerrar_ventana()

        def cerrar_ventana():
            Acreedor.ventana_abierta = False
            ventana_nombre.destroy()

        def toggle_check(tipo):
            if tipo == "predef":
                if check_predefinido.get():
                    check_personalizado.deselect()
            elif tipo == "personal":
                if check_personalizado.get():
                    check_predefinido.deselect()

        # Escalado
        screen_w = app.winfo_screenwidth()
        screen_h = app.winfo_screenheight()
        ref_w, ref_h = 1920, 1080
        escala_w, escala_h = screen_w / ref_w, screen_h / ref_h
        ancho_ventana = int(500 * escala_w)
        alto_ventana = int(330 * escala_h)

        fuente_titulo_size = max(14, int(28 * escala_h))
        fuente_label_size = max(10, int(18 * escala_h))
        fuente_boton_size = max(12, int(22 * escala_h))
        entry_width = int(300 * escala_w)

        x_pos = int((screen_w - ancho_ventana) / 2)
        y_pos = int((screen_h - alto_ventana) / 2)

        ventana_nombre = ctk.CTk()
        Acreedor.ventanas_secundarias.append(ventana_nombre)

        ventana_nombre.title("Guardar Informe de Acreedores")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        ventana_nombre.geometry(f"{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}")
        ventana_nombre.resizable(False, False)

        # Icono
        icon_path = "resources/logos/icon_logo.ico"
        if sys.platform == "win32":
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            try:
                ventana_nombre.iconbitmap(icon_path)
            except Exception as e:
                print(f"No se pudo cargar el icono: {e}")

        ventana_nombre.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        fuente_titulo = ctk.CTkFont(family="Sans Sulex", size=fuente_titulo_size)
        fuente_label = ctk.CTkFont(family="Sans Sulex", size=fuente_label_size)
        fuente_boton = ctk.CTkFont(family="Sans Sulex", size=fuente_boton_size)

        frame_principal = ctk.CTkFrame(ventana_nombre, fg_color="#373737", corner_radius=0)
        frame_principal.pack(fill="both", expand=True, padx=int(20 * escala_w), pady=int(20 * escala_h))

        label_titulo = ctk.CTkLabel(frame_principal, text="Informe de acreedores", font=fuente_titulo, text_color="white")
        label_titulo.pack(pady=(int(10 * escala_h), int(10 * escala_h)))

        entrada_nombre = ctk.CTkEntry(
            frame_principal,
            placeholder_text="Introduce nombre del informe",
            font=fuente_label,
            width=int(entry_width * 1.3),
            fg_color="#181818",
            text_color="white"
        )
        entrada_nombre.pack(pady=(int(10 * escala_h), int(10 * escala_h)))
        entrada_nombre.focus()

        frame_checks = ctk.CTkFrame(frame_principal, fg_color="transparent")
        frame_checks.pack(pady=(int(10 * escala_h), int(10 * escala_h)), anchor="w", padx=int(40 * escala_w))

        check_predefinido = ctk.CTkCheckBox(
            frame_checks,
            text="Informe Predefinido",
            font=fuente_label,
            text_color="white",
            fg_color="#990404",
            hover_color="#540303",
            command=lambda: toggle_check("predef")
        )
        check_predefinido.pack(anchor="w", pady=(0, int(5 * escala_h)))

        check_personalizado = ctk.CTkCheckBox(
            frame_checks,
            text="Informe Personalizado",
            font=fuente_label,
            text_color="white",
            fg_color="#990404",
            hover_color="#540303",
            command=lambda: toggle_check("personal")
        )
        check_personalizado.pack(anchor="w")

        boton_guardar = ctk.CTkButton(
            frame_principal,
            text="Guardar Informe",
            font=fuente_boton,
            fg_color="#990404",
            hover_color="#540303",
            border_width=2,
            border_color="black",
            corner_radius=10,
            command=confirmar_guardado
        )
        boton_guardar.pack(pady=(int(15 * escala_h), int(5 * escala_h)))

        ventana_nombre.bind("<Return>", confirmar_guardado)
        ventana_nombre.mainloop()


    @staticmethod
    def generar_informe_pdf_fijo(paginas, ruta_salida="informe_Acreedores.pdf"):

        columnas = [
            "DNI/CIF", "Nombre", "Apellido1", "Apellido2",
            "Dirección", "Ciudad", "Teléfono 1", "Email 1", "Idioma"
        ]

        pesos = {
            "DNI/CIF": 1,
            "Nombre": 1,
            "Apellido1": 1,
            "Apellido2": 1,
            "Dirección": 2,
            "Ciudad": 1,
            "Teléfono 1": 1.5,
            "Email 1": 2.5,
            "Idioma": 1
        }

        font_path = "resources/font/sans-sulex/SANSSULEX.ttf"
        pdfmetrics.registerFont(TTFont("Sans Sulex", font_path))

        c = canvas.Canvas(ruta_salida, pagesize=landscape(A4))
        width, height = landscape(A4)

        logo_path = "resources/logos/hgcnegro.png"
        total_padding = 2 * cm

        peso_total = sum(pesos.values())
        espacio_col = [(width - total_padding) * (pesos[col] / peso_total) for col in columnas]

        font_size = 9
        altura_fila = 0.75 * cm
        altura_encabezado = 1.0 * cm
        total_paginas = len(paginas)

        for num_pagina, datos_pagina in enumerate(paginas, start=1):
            y = height - 1 * cm

            # Cambiar la posición del logo al lado derecho
            try:
                logo = ImageReader(logo_path)
                orig_width, orig_height = logo.getSize()
                logo_width = 4 * cm
                logo_height = (orig_height / orig_width) * logo_width
                x_logo = width - logo_width - 1 * cm  # Alinear el logo a la derecha con un margen de 1 cm
                c.drawImage(logo, x_logo, y - logo_height + 0.5 * cm, width=logo_width, height=logo_height, mask='auto')
            except Exception as e:
                print(f"Error al cargar el logo: {e}")

            # Ajustar espacio entre el logo y el título
            y -= 2 * cm

            # Título
            c.setFont("Sans Sulex", 14)
            c.setFillColor(colors.black)
            c.drawString(1 * cm, y, f"LISTADO DE ACREEDORES")

            y -= 1.4 * cm

            # Encabezados
            c.setFillColorRGB(0.27, 0.27, 0.27)
            c.rect(1 * cm - 0.1 * cm, y - 0.1 * cm, width - total_padding + 0.2 * cm, altura_encabezado, fill=True, stroke=False)
            c.setFillColor(colors.white)
            c.setFont("Sans Sulex", font_size + 1)

            col_x = 1 * cm
            for idx, col in enumerate(columnas):
                c.drawString(col_x, y + altura_encabezado / 2 - font_size / 2.5, col)
                col_x += espacio_col[idx]

            y -= altura_encabezado

            # Filas de datos
            c.setFont("Sans Sulex", font_size)
            for fila in datos_pagina:
                c.setFillColor(colors.whitesmoke if datos_pagina.index(fila) % 2 == 0 else colors.lightgrey)
                c.rect(1 * cm - 0.1 * cm, y - 0.1 * cm, width - total_padding + 0.2 * cm, altura_fila, fill=True, stroke=False)
                c.setFillColor(colors.black)

                col_x = 1 * cm
                for idx, item in enumerate(fila):
                    texto = str(item) if item is not None else ""
                    max_chars = int((espacio_col[idx] / cm) * 5.5)
                    lineas = wrap(texto, width=max_chars)[:2]
                    for j, linea in enumerate(lineas):
                        c.drawString(col_x, y + altura_fila / 2 - j * (font_size + 1.5), linea)
                    col_x += espacio_col[idx]

                y -= altura_fila

            # Pie de página
            fecha_actual = format_datetime(datetime.now(), "EEEE, d 'de' MMMM 'de' y, HH:mm", locale="es")
            c.setFont("Sans Sulex", 9)
            c.setFillColor(colors.black)
            c.drawString(1 * cm, 0.4 * cm, f"Fecha de creación: {fecha_actual}")
            c.drawRightString(width - 1 * cm, 0.4 * cm, f"Página {num_pagina} de {total_paginas}")

            c.showPage()

        c.save()


    @staticmethod
    def generar_informe_pdf(paginas, columnas, ruta_salida="informe_Acreedores.pdf"):

        font_path = "resources/font/sans-sulex/SANSSULEX.ttf"
        pdfmetrics.registerFont(TTFont("Sans Sulex", font_path))

        c = canvas.Canvas(ruta_salida, pagesize=landscape(A4))
        width, height = landscape(A4)

        logo_path = "resources/logos/hgcnegro.png"
        total_padding = 2 * cm

        num_columnas = len(columnas)
        peso_columna = (width - total_padding) / num_columnas  # Equitativo

        font_size = 9
        altura_fila = 0.75 * cm
        altura_encabezado = 1.0 * cm
        max_chars_per_line = 30
        total_paginas = len(paginas)

        for num_pagina, datos_pagina in enumerate(paginas, start=1):
            y = height - 1 * cm

            # Cambiar la posición del logo al lado derecho
            try:
                logo = ImageReader(logo_path)
                orig_width, orig_height = logo.getSize()
                logo_width = 4 * cm
                logo_height = (orig_height / orig_width) * logo_width
                x_logo = width - logo_width - 1 * cm  # Alinear el logo a la derecha con un margen de 1 cm
                c.drawImage(logo, x_logo, y - logo_height + 0.5 * cm, width=logo_width, height=logo_height, mask='auto')
            except Exception as e:
                print(f"Error al cargar el logo: {e}")

            # Ajustar espacio entre el logo y el título
            y -= 2 * cm

            # Título
            c.setFont("Sans Sulex", 14)
            c.setFillColor(colors.black)
            c.drawString(1 * cm, y, "LISTADO DE ACREEDORES")

            y -= 1.4 * cm

            # Encabezados
            c.setFillColorRGB(0.27, 0.27, 0.27)
            c.rect(1 * cm - 0.1 * cm, y - 0.1 * cm, width - total_padding + 0.2 * cm, altura_encabezado, fill=True, stroke=False)
            c.setFillColor(colors.white)
            c.setFont("Sans Sulex", font_size + 1)

            col_x = 1 * cm
            for col in columnas:
                nombre_col = str(col)[:max_chars_per_line]
                c.drawString(col_x, y + altura_encabezado / 2 - font_size / 2.5, nombre_col)
                col_x += peso_columna

            y -= altura_encabezado
            c.setFont("Sans Sulex", font_size)

            # Filas de datos
            for fila in datos_pagina:
                c.setFillColor(colors.whitesmoke if datos_pagina.index(fila) % 2 == 0 else colors.lightgrey)
                c.rect(1 * cm - 0.1 * cm, y - 0.1 * cm, width - total_padding + 0.2 * cm, altura_fila, fill=True, stroke=False)
                c.setFillColor(colors.black)

                col_x = 1 * cm
                for idx, item in enumerate(fila):
                    texto = str(item) if item is not None else ""
                    max_chars = int((peso_columna / cm) * 5.5)
                    lineas = wrap(texto, width=max_chars)[:2]
                    for j, linea in enumerate(lineas):
                        c.drawString(col_x, y + altura_fila / 2 - j * (font_size + 1.5), linea)
                    col_x += peso_columna

                y -= altura_fila

            # Pie de página
            fecha_actual = format_datetime(datetime.now(), "EEEE, d 'de' MMMM 'de' y, HH:mm", locale="es")
            c.setFont("Sans Sulex", 9)
            c.setFillColor(colors.black)
            c.drawString(1 * cm, 0.4 * cm, f"Fecha de creación: {fecha_actual}")
            c.drawRightString(width - 1 * cm, 0.4 * cm, f"Página {num_pagina} de {total_paginas}")

            c.showPage()

        c.save()


    @staticmethod
    def get_all_Acreedor_data():
        conn = sqlite3.connect("bd/Concesionario.db")  # cambia según uses
        cursor = conn.cursor()

        columns = Acreedor.visible_columns
        query = f"SELECT {', '.join(columns)} FROM Acreedor"

        cursor.execute(query)
        data = cursor.fetchall()

        conn.close()
        return data
    
    @staticmethod
    def search_plus(frame_right, clear_frame_right, app):
        if Acreedor.ventana_abierta:
            messagebox.showerror("Ventana ya abierta", "Ya hay una ventana abierta. Ciérrala antes de abrir otra.", parent=app)
            return

        Acreedor.ventana_abierta = True
        total_width = app.winfo_width()
        rel_size = total_width / 100

        app_sp = ctk.CTk()
        Acreedor.ventanas_secundarias.append(app_sp)
        
        app_sp.title("Buscar Acreedor")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        if sys.platform == "win32":
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("mycompany.myapp.sellcars.1.0")

        icon_path = "resources/logos/icon_logo.ico"
        if os.path.exists(icon_path):
            app_sp.iconbitmap(icon_path)

        screen = screeninfo.get_monitors()[0]
        window_width, window_height = int(screen.width * 0.40), int(screen.height * 0.80)
        x, y = (screen.width - window_width) // 2, (screen.height - window_height) // 2
        app_sp.geometry(f"{window_width}x{window_height}+{x}+{y}")
        app_sp.resizable(False, False)

        fuente_labels = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.024))
        fuente_boton = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.032))
        fuente_titulo = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.048))

        main_frame = ctk.CTkFrame(app_sp, fg_color="#373737", corner_radius=0)
        main_frame.pack(pady=20, padx=20, fill="both", expand=True)

        ctk.CTkLabel(main_frame, text="Buscar Acreedor", font=fuente_titulo, text_color="white").pack(pady=(20, 10))

        content_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        content_frame.pack(expand=True)

        campos_nombres = [
            "DNI / CIF", "Nombre", "1º Apellido", "2º Apellido", "Dirección", "Código Postal", "Ciudad",
            "Idioma", "País", "Teléfono 1", "Teléfono 2", "Teléfono 3", "Teléfono 4",
            "Fax 1", "Fax 2", "Email 1"
        ]

        campos_db = {
            "DNI / CIF": "dni_cif", "Nombre": "nombre", "1º Apellido": "apellido1", "2º Apellido": "apellido2",
            "Dirección": "direccion", "Código Postal": "codigopostal", "Ciudad": "ciudad", "Idioma": "idioma",
            "País": "pais", "Teléfono 1": "telefono1", "Teléfono 2": "telefono2", "Teléfono 3": "telefono3",
            "Teléfono 4": "telefono4", "Fax 1": "fax1", "Fax 2": "fax2", "Email 1": "email1"
        }

        entradas = {}
        for idx, campo in enumerate(campos_nombres):
            fila, columna = divmod(idx, 2)
            entry = ctk.CTkEntry(content_frame, placeholder_text=campo, font=fuente_labels,
                                fg_color="#181818", text_color="white", width=int(window_width * 0.4))
            entry.grid(row=fila, column=columna, padx=20, pady=10, sticky="ew")
            entradas[campo] = entry
            entry.bind("<FocusIn>", lambda e, ent=entry: Acreedor.on_focus_in_entry(ent))
            entry.bind("<FocusOut>", lambda e, ent=entry: Acreedor.on_focus_out_entry(ent))

        def buscar():
            condiciones, valores = [], []
            for label, widget in entradas.items():
                texto = widget.get().strip()
                if texto:
                    condiciones.append(f"{campos_db[label]} LIKE ?")
                    valores.append(f"{texto}%")

            if not condiciones:
                messagebox.showwarning("Sin filtros", "Introduce al menos un criterio de búsqueda.", parent=app_sp)
                return

            where_clause = " AND ".join(condiciones)

            try:
                conn = sqlite3.connect("bd/Concesionario.db")
                cursor = conn.cursor()

                Acreedor.query = where_clause
                Acreedor.query_params = valores
                Acreedor.current_page = 1

                cursor.execute(f"SELECT COUNT(*) FROM Acreedor WHERE {where_clause}", valores)
                total_rows = cursor.fetchone()[0]

                if total_rows == 0:
                    messagebox.showinfo("Sin Resultados", "No se encontró ningún acreedor.", parent=app_sp)
                    conn.close()
                    return

                total_pages = max((total_rows // Acreedor.rows_per_page) + (1 if total_rows % Acreedor.rows_per_page else 0), 1)
                offset = (Acreedor.current_page - 1) * Acreedor.rows_per_page

                cursor.execute(f"SELECT * FROM Acreedor WHERE {where_clause} LIMIT ? OFFSET ?", valores + [Acreedor.rows_per_page, offset])
                data = cursor.fetchall()
                conn.close()

                # Todas las columnas
                all_columns = [
                    "dni_cif", "nombre", "apellido1", "apellido2", "direccion", "codigopostal", "ciudad", "idioma", "pais",
                    "telefono1", "telefono2", "telefono3", "telefono4", "fax1", "fax2", "email1"
                ]

                Acreedor.Filtro = True
                Acreedor.ventana_abierta = False

                Acreedor.create_table(
                    query=where_clause,
                    columns=all_columns,
                    data=data,
                    frame_right=frame_right,
                    app=app,
                    clear_frame_right=clear_frame_right,
                    total_pages=total_pages,
                    Filtro=True
                )

                app_sp.destroy()

            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Ocurrió un error al realizar la búsqueda:\n{e}", parent=app_sp)

        ctk.CTkButton(
            main_frame,
            text="Buscar",
            font=fuente_boton,
            fg_color="#990404",
            hover_color="#540303",
            border_width=2,
            border_color="black",
            corner_radius=10,
            height=40,
            command=buscar
        ).pack(pady=20)

        def on_closing():
            Acreedor.ventana_abierta = False
            Acreedor.ventanas_secundarias.remove(app_sp)
            app_sp.destroy()

        app_sp.protocol("WM_DELETE_WINDOW", on_closing)
        app_sp.bind("<Return>", lambda event: buscar())
        app_sp.mainloop()


    @staticmethod
    def add_factura(dni_cif, frame_right, clear_frame_right, app):
        
        if Acreedor.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        Acreedor.ventana_abierta = True  # Marcamos la ventana como abierta

        icon_path = "resources/logos/icon_logo.ico"
        conn = sqlite3.connect("bd/Concesionario.db")
        cursor = conn.cursor()
        cursor.execute("SELECT dni_cif FROM Acreedor WHERE dni_cif = ?", (dni_cif,))
        acreedor = cursor.fetchone()
        conn.close()

        if not acreedor:
            messagebox.showerror("Error", f"No se encontró Acreedor con DNI/CIF: {dni_cif}")
            Acreedor.ventana_abierta = False
            return


        appAddF = ctk.CTk()
        Acreedor.ventanas_secundarias.append(appAddF)

        if sys.platform == "win32":
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            appAddF.iconbitmap(Acreedor.icon_path)

        appAddF.title("Añadir factura")
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
        appAddF.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        appAddF.resizable(False, False)

        # Definir la fuente relativa para labels y botones
        fuente_labels = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.022))  # Fuente más pequeña
        fuente_boton = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.03))  # Fuente del botón más pequeña
        fuente_titulo = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.045))

        padding_relativo = int(window_height * 0.02)  # Ajustamos el padding a un valor relativo al tamaño de la ventana
        main_frame = ctk.CTkFrame(appAddF, fg_color="#373737", corner_radius=0)  # Color de fondo cambiado
        main_frame.pack(pady=padding_relativo, padx=padding_relativo, fill="both", expand=True)

        titulo = ctk.CTkLabel(main_frame, text="Crear Factura", font=fuente_titulo, text_color="white")
        titulo.pack(pady=(int(window_height // 37), 37))

        # Scrollable frame
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=int(window_height // 37), pady=int(window_height // 37))

        campos = [
            "ID Documento","Tipo de Factura","DNI / CIF", "Fecha de Factura","Cobro (€)","Tipo de Transacción",
            "Clase", "Centro", "Serie", "Referencia", "Cesado","R.E.C." 
        ]

        entradas = []

        for campo in campos:
            fila = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            fila.pack(fill="x", padx=int(window_height // 18.5), pady=int(window_height * 0.015))

            label = ctk.CTkLabel(fila, text=campo + ":", font=fuente_labels, width=160, anchor="w", text_color="white")
            label.pack(side="left", padx=int(window_height // 18.5))

            if campo == "Cesado":
                opciones = ["","Sí","No"]
                om = ctk.CTkOptionMenu(fila, values=opciones, button_color="#990404",
                                    button_hover_color="#540303", fg_color="#181818",
                                    dropdown_fg_color="#181818", font=fuente_labels,
                                    dropdown_font=fuente_labels)
                om.set(opciones[0])
                om.pack(side="left", fill="x", expand=True)
                entradas.append(om)

            elif campo == "DNI / CIF":
                entry_dni = ctk.CTkEntry(fila, font=fuente_labels, fg_color="#181818", text_color="white")

                if dni_cif is not None:
                    entry_dni.insert(0, str(dni_cif))  # Asegúrate de convertir a str

                entry_dni.configure(state="disabled")  # Bloquear después de insertar
                entry_dni.pack(side="left", fill="x", expand=True)
                entradas.append(entry_dni)

            elif "Fecha" in campo:
                entry_fecha = ctk.CTkEntry(fila, placeholder_text="dd/mm/yyyy", font=fuente_labels,
                                        fg_color="#181818", text_color="white")
                entry_fecha.pack(side="left", fill="x", expand=True)
                entradas.append(entry_fecha)
                entry_fecha.bind("<FocusIn>", lambda event, e=entry_fecha: Acreedor.on_focus_in_entry(e))
                entry_fecha.bind("<FocusOut>", lambda event, e=entry_fecha: Acreedor.on_focus_out_entry(e))

            else:
                entry = ctk.CTkEntry(fila, placeholder_text=campo, font=fuente_labels,
                                    fg_color="#181818", text_color="white")
                entry.pack(side="left", fill="x", expand=True)
                entradas.append(entry)
                entry.bind("<FocusIn>", lambda event, e=entry: Acreedor.on_focus_in_entry(e))
                entry.bind("<FocusOut>", lambda event, e=entry: Acreedor.on_focus_out_entry(e))

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
                label = campos[idx].replace(" ", "").replace("º", "").replace("-", "")
                contenido = entrada.get().strip()

                if isinstance(entrada, ctk.CTkOptionMenu):
                    if entrada.cget("values")[0] in ["Sí", "No"]:
                        valores.append("1" if entrada.get() == "Sí" else "0")
                    else:
                        valores.append(entrada.get())

                elif "Fecha" in campos[idx]:
                    if contenido == "":
                        valores.append("")
                    else:
                        try:
                            fecha = datetime.strptime(contenido, "%d/%m/%Y")
                            valores.append(fecha.strftime("%Y-%m-%d"))
                        except ValueError:
                            messagebox.showerror(
                                "Fecha inválida",
                                f"La fecha ingresada en el campo '{campos[idx]}' no es válida.",
                                parent=appAddF
                            )
                            return
                else:
                    valores.append(contenido)

            dni = valores[0]
            if not dni:
                messagebox.showerror("Error de Validación", "El campo 'ID Documento' no puede estar vacío.", parent=appAddF)
                return

            try:
                with sqlite3.connect("bd/Concesionario.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"""
                        INSERT INTO FacturasAcreedores (
                            IDDocumento, tipoFactura, dni_cif, FechaFactura, cobro,
                            TipoTransaccionRecibida, clase, centro, serie, referencia,
                            cesado, Rec
                        ) VALUES ({','.join(['?'] * 12)})
                    """, (valores[0:]))
                    conn.commit()

                    Acreedor.clear_search(frame_right, clear_frame_right, app)
                    Acreedor.ventana_abierta = False
                    appAddF.destroy()

            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error de Base de Datos", f"Error al insertar Factura:\n{e}", parent=appAddF)

        def on_closing():
            Acreedor.ventana_abierta = False
            Acreedor.ventanas_secundarias.remove(appAddF)
            appAddF.destroy()

        appAddF.protocol("WM_DELETE_WINDOW", on_closing)
        appAddF.bind("<Return>", lambda event: guardar_cambios())
        appAddF.mainloop()


    @staticmethod
    def sort_by_column(column, frame_right, clear_frame_right, app):
        if Acreedor.sort_column == column:
            Acreedor.sort_ascending = not Acreedor.sort_ascending
        else:
            Acreedor.sort_column = column
            Acreedor.sort_ascending = True

        Acreedor.current_page = 1
        Acreedor.load_data(frame_right, clear_frame_right, app)

    @staticmethod
    def update_sort_state(column):
        # Quitar estado de todas las columnas excepto la actual
        for col in Acreedor.visible_columns:
            if col != column:
                Acreedor.sort_states[col] = None

        current = Acreedor.sort_states.get(column)

        if current == "asc":
            Acreedor.sort_states[column] = "desc"
        elif current == "desc":
            Acreedor.sort_states[column] = None
        else:
            Acreedor.sort_states[column] = "asc"

        # Actualizar columna y orden actuales
        Acreedor.sort_column = column if Acreedor.sort_states[column] else None
        Acreedor.sort_order = Acreedor.sort_states[column] or ""



    @staticmethod
    def refresh_treeview_headings(tree, frame_right, clear_frame_right, app):

        for col in Acreedor.visible_columns:
            sort_state = Acreedor.sort_states.get(col)
            base_text = Acreedor.column_name_map.get(col, col)

            if sort_state == "asc":
                heading_text = f"{base_text} ▲"
            elif sort_state == "desc":
                heading_text = f"{base_text} ▼"
            else:
                heading_text = base_text

            # Vuelve a aplicar heading y command
            tree.heading(
                col,
                text=heading_text,
                anchor="center",
                command=partial(Acreedor.sort_column_click, col, tree, frame_right, clear_frame_right, app)
        )


    @staticmethod
    def sort_column_click(col, tree, frame_right, clear_frame_right, app):
        Acreedor.update_sort_state(col)
        Acreedor.refresh_treeview_headings(tree, frame_right, clear_frame_right, app) 
        Acreedor.load_data(frame_right, clear_frame_right, app)