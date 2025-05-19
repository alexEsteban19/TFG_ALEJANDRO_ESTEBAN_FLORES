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
from functools import partial
import platform
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from babel.dates import format_datetime
import ctypes
import platform




class Facturacion:
    
    # Definimos variables base
    highlight_color = "#c91706"  # Color cuando se selecciona (borde)
    default_border_color = "#565b5e"  # Color del borde por defecto
    default_fg_color = "#181818"  # Color de fondo por defecto
    
    current_page = 1
    rows_per_page = 20
    visible_columns = None
    Filtro = False
    query = ""
    search_column = ""
    selected_Factura = None  # Mantener el cliente seleccionado como variable estática
    query_params = ""
    ventana_abierta = False  
    icon_path = "resources/logos/icon_logo.ico"
    ventanas_secundarias = [] 
    
    sort_column = None
    sort_order = "asc" 
    sort_states = {}  # Diccionario: {"columna": "asc" | "desc" | None}

    tablas = ["FacturasClientes", "FacturasProveedores", "FacturasAcreedores"]
    tabla_seleccionada = "FacturasClientes"

    # todos los datos de la BD
    column_name_map = {
        "IDDocumento": "ID Documento",
        "tipoFactura": "TipoFactura",
        "dni_cif": "DNI / CIF",
        "FechaFactura": "FechaFactura",
        "cobro": "Cobro (€)",
        "TipoTransaccionRecibida": "TipoTransacción",
        "clase": "Clase",
        "centro": "Centro",
        "serie": "Serie",
        "referencia": "Referencia",
        "cesado": "Cesado",
        "Rec": "R.E.C."
    }

    # datos que muestra la tabla
    column_options = {
        "IDDocumento": "ID Documento",
        "tipoFactura": "TipoFactura",
        "dni_cif": "DNI / CIF",
        "FechaFactura": "FechaFactura",
        "cobro": "Cobro (€)",
        "TipoTransaccionRecibida": "TipoTransacción",
        "clase": "Clase",
        "centro": "Centro",
        "serie": "Serie",
        "referencia": "Referencia",
        "cesado": "Cesado",
        "Rec": "R.E.C."
    }

    # metodo para crear la tabla
    @staticmethod
    def create_table(query, columns, data, frame_right, app, clear_frame_right, total_pages, Filtro):
        for widget in frame_right.winfo_children():
            widget.destroy()

        Facturacion.selected_Factura = None
        total_width = app.winfo_width()
        rel_size = total_width / 100
        
        # si no hubiera columnas, definimos unas "default"
        if Facturacion.visible_columns is None or not Facturacion.visible_columns:
            Facturacion.visible_columns = ["IDDocumento","tipoFactura","dni_cif","FechaFactura","cobro", "TipoTransaccionRecibida","clase","centro","serie","referencia","cesado","Rec"]

        #Crear contenedor invisible
        main_container = ctk.CTkFrame(frame_right, fg_color="#3d3d3d")
        main_container.place_forget()

        #Contenido principal
        main_frame = ctk.CTkFrame(main_container, fg_color="#3d3d3d")
        main_frame.pack(fill="both", expand=True, padx=int(rel_size // 1.5), pady=int(rel_size // 1.5))

        #Estilo Botones
        btn_color = "black"
        btn_hover = "#16466e"
        icon_size = (int(rel_size * 3), int(rel_size * 2))
        
        #Barra dr Búsqueda
        search_frame = ctk.CTkFrame(main_frame, fg_color="transparent", corner_radius=int(rel_size // 2))
        search_frame.pack(fill="x", padx=rel_size // 6, pady=rel_size // 6)
        
        title = ctk.CTkLabel(search_frame, text="HGC - GESTIÓN DE FACTURAS", 
                                    font=("Sans Sulex", int(rel_size * 1.4)),
                                    text_color="white")
        title.pack(side="left", padx=rel_size * 1.2, pady=int(rel_size // 1.8))

        # Espaciador para empujar botones a la derecha
        spacer = ctk.CTkLabel(search_frame, text="")  # Vacío, sirve solo para expandir
        spacer.pack(side="left", expand=True)

        # Creación del botón de informes
        informe_image = Image.open("resources/icons/white/votacion.png").resize(icon_size)
        informe_image = ctk.CTkImage(light_image=informe_image)
        informe_btn = ctk.CTkButton(search_frame, text="Generar Informe", image=informe_image, fg_color=btn_color,
                                font=("Sans Sulex", int(rel_size)),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2), anchor="w",
                                border_width=2, border_color="white", command=lambda: Facturacion.generate_inform(app))
        informe_btn.pack(side="left", padx=rel_size // 2, pady=int(rel_size // 1.8))

        #Creación del botón de busqueda
        search_plus_image = Image.open("resources/icons/white/search.png").resize(icon_size)
        search_plus_image = ctk.CTkImage(light_image=search_plus_image)
        search_plus_button = ctk.CTkButton(search_frame, text="", image=search_plus_image, fg_color=btn_color,
                                    hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                    border_width=2, border_color="white",
                                    width=icon_size[0], height=icon_size[1],command=lambda: Facturacion.search_plus(frame_right, clear_frame_right, app)
                                    )
        search_plus_button.pack(side="left", padx=rel_size // 1.5)

        #Función dedicada al cambio de tablas, dependiendo del tipo de factura requerida
        def on_tabla_change(value):
            Facturacion.tabla_seleccionada = value
            Facturacion.clear_search(frame_right, clear_frame_right, app)

        #Marco que actúa como borde para el OptionMenu de tablas (más compacto)
        option_menu_border = ctk.CTkFrame(
            search_frame,
            fg_color="white",
            border_color="white",
            border_width=0,
            corner_radius=int(rel_size // 2.5)
        )
        option_menu_border.pack(side="right", padx=int(rel_size // 2), pady=int(rel_size // 2.5))

        #OptionMenu más reducido y proporcionado
        Facturacion.option_menu_tablas = ctk.CTkOptionMenu(
            option_menu_border,
            values=Facturacion.tablas,
            command=on_tabla_change,
            fg_color="black",
            text_color="white",
            button_color="#990404",
            button_hover_color="#540303",
            dropdown_fg_color="black",
            dropdown_text_color="white",
            dropdown_font=("Sans Sulex", int(rel_size * 0.85)),
            font=("Sans Sulex", int(rel_size * 0.85)),
            width=int(rel_size * 12)
        )
        Facturacion.option_menu_tablas.set(Facturacion.tabla_seleccionada)
        Facturacion.option_menu_tablas.pack(padx=int(rel_size // 7), pady=int(rel_size // 7))

        #Creación del botón de refrescar
        refresh_image = Image.open("resources/icons/white/refresh.png").resize(icon_size)
        refresh_image = ctk.CTkImage(light_image=refresh_image)
        clear_search_button = ctk.CTkButton(search_frame, text="", image=refresh_image, fg_color=btn_color,
                                            hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                            border_width=2, border_color="white",
                                            width=icon_size[0], height=icon_size[1],
                                            command=lambda: Facturacion.clear_search(frame_right, clear_frame_right, app))
        clear_search_button.pack(side="left", padx=rel_size // 1.5)

        # Frame desplegable para la selección de columnas (filtro)
        column_filter_frame = ctk.CTkFrame(frame_right, fg_color="black", corner_radius=15, width=300)
        filter_open = [False]

        button_frame = ctk.CTkFrame(column_filter_frame, fg_color="black")
        button_frame.pack(anchor="w", side="bottom", fill="both")

        # Botón para aplicar las opciones del filtro
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

        # Frame para las opcciones del filtro 
        checkbox_scroll_frame = ctk.CTkScrollableFrame(column_filter_frame, fg_color="black")
        checkbox_scroll_frame.pack(side="top", fill="both", expand=True)

        selected_columns = {
            col: ctk.BooleanVar(value=(col in Facturacion.visible_columns)) for col in columns
        }

        # Bucle para la creacion de cada una de las opcciones del filtro (que son las columnas de la tabla) 
        for col in columns:
            # Para que no se pueda desactivar y dar error en la función de selección 
            if col == "IDDocumento":
                continue
            # Direcctrices para le creación de la checkbox
            checkbox = ctk.CTkCheckBox(
                checkbox_scroll_frame,
                font=("Sans Sulex", int(rel_size * 1.1)),
                text=Facturacion.column_name_map.get(col, col),
                variable=selected_columns[col],
                fg_color="#990404",
                hover_color="#540303"
            )
            checkbox.pack(anchor="w", padx=int(rel_size // 3), pady=int(rel_size // 3))

        #Función para mostrar o dejar de mostrar el filtro a la derecha
        def toggle_filter_dropdown():
            padding_x = 0.015
            padding_y = 0.02

            if filter_open[0]:
                column_filter_frame.place_forget()
                main_frame.place_configure(relwidth=1.0)
                filter_open[0] = False
            else:
                relwidth = 0.2 - (2 * padding_x)
                relheight = 46 * padding_y
                relx = 0.8 + padding_x
                rely = 0.01 + padding_y

                column_filter_frame.place(relx=relx, rely=rely, relwidth=relwidth, relheight=relheight)
                main_frame.place_configure(relwidth=0.8)
                filter_open[0] = True

        #Función para la aplicación del filtro
        def apply_filter():
            visible = [col for col, var in selected_columns.items() if var.get()]
            Facturacion.visible_columns = visible if visible else columns[:]
            toggle_filter_dropdown()
            Facturacion.abrir_Factu(frame_right, clear_frame_right, app, mantener_filtro=True)

        # Botón de filtro
        filter_image = Image.open("resources/icons/white/ojoblanco.png").resize(icon_size)
        filter_image = ctk.CTkImage(light_image=filter_image)
        filter_button = ctk.CTkButton(search_frame, text="", image=filter_image, fg_color=btn_color,
                                    hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                    border_width=2, border_color="white",
                                    width=icon_size[0], height=icon_size[1],
                                    command=toggle_filter_dropdown)
        filter_button.pack(side="left", padx=rel_size // 1.5)
        
        # Tabla
        tree_frame = ctk.CTkFrame(main_frame, fg_color="#3d3d3d")
        tree_frame.pack(fill="both", expand=True, padx=rel_size, pady=rel_size // 14)

        heading_font_size = int(rel_size)

        # Botones Navegación
        nav_frame = ctk.CTkFrame(main_frame, fg_color="#3d3d3d")
        nav_frame.pack(side="top", fill="x", padx=int(rel_size // 3), pady=int(rel_size // 3))

        # Botón para ir a la página anterior
        prev_image = Image.open("resources/icons/white/angle-small-left.png").resize(icon_size)
        prev_image = ctk.CTkImage(light_image=prev_image)
        prev_btn = ctk.CTkButton(nav_frame, text="", image=prev_image, fg_color=btn_color,
                                height=rel_size, width=rel_size,
                                hover_color=btn_hover, corner_radius=250,
                                border_width=1, border_color="white",
                                command=lambda: Facturacion.change_page(-1, frame_right, clear_frame_right, app))
        prev_btn.pack(side="left", padx=rel_size, pady=rel_size // 1.5)

        #Texto de "Página"
        page_label = ctk.CTkLabel(nav_frame,
                                text=f"Página {Facturacion.current_page} de {total_pages}",
                                font=("Sans Sulex", heading_font_size),
                                text_color="white")
        page_label.pack(side="left")

        # Botón para ir a la página siguiente
        next_image = Image.open("resources/icons/white/angle-small-right.png").resize(icon_size)
        next_image = ctk.CTkImage(light_image=next_image)
        next_btn = ctk.CTkButton(nav_frame, text="", image=next_image, fg_color=btn_color,
                                height=rel_size, width=rel_size,
                                hover_color=btn_hover, corner_radius=250,
                                border_width=1, border_color="white",
                                command=lambda: Facturacion.change_page(1, frame_right, clear_frame_right, app))
        next_btn.pack(side="left", padx=rel_size, pady=rel_size // 1.5)
        
        # Botones Agregar/Modificar/Borrar
        action_frame = ctk.CTkFrame(nav_frame, fg_color="#3d3d3d")
        action_frame.pack(side="right", padx=rel_size, pady=rel_size // 1.5)

        # Botón para la vista de una factura en particular
        vistaFactura_image = Image.open("resources/icons/white/facturas.png").resize(icon_size)
        vistaFactura_image = ctk.CTkImage(light_image=vistaFactura_image)
        vistaFactura_btn = ctk.CTkButton(action_frame, text="Ver Factura", image=vistaFactura_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                border_width=1, border_color="white", command=lambda: Facturacion.ver_factura())
        vistaFactura_btn.pack(side="left", padx=rel_size // 2)

        # Botón para la edición de un registro
        edit_image = Image.open("resources/icons/white/boli.png").resize(icon_size)
        edit_image = ctk.CTkImage(light_image=edit_image)
        edit_btn = ctk.CTkButton(action_frame, text="Editar Factura", image=edit_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                border_width=1, border_color="white", command=lambda: Facturacion.edit_factura(Facturacion.selected_Factura, frame_right, clear_frame_right, app))
        edit_btn.pack(side="left", padx=rel_size // 2)

        # Botón para la eliminación de un registro
        delete_image = Image.open("resources/icons/white/trash.png").resize(icon_size)
        delete_image = ctk.CTkImage(light_image=delete_image)
        delete_btn = ctk.CTkButton(action_frame, text="Borrar Factura", image=delete_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                border_width=1, border_color="white", command=lambda: Facturacion.delete_factura(Facturacion.selected_Factura, frame_right, clear_frame_right, app))
        delete_btn.pack(side="left", padx=rel_size // 2)

#Pregunta
        if Facturacion.current_page == 1:
            prev_btn.configure(state="disabled")
        if Facturacion.current_page == total_pages:
            next_btn.configure(state="disabled")

        # Estimar altura de fila para llenar el espacio
        altura_total_disponible = int(app.winfo_height() * 0.65)
        altura_filas = int(altura_total_disponible / Facturacion.rows_per_page)

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
                        foreground="#ededed",         #texto encabezado
                        background="black",       # fondo encabezado
                        bordercolor="black",
                        padding=(rel_size // 2, rel_size // 2))

        # Estilo para selección (resalta fila seleccionada)
        style.map("Treeview",
                background=[("selected", "#16466e")],  # celeste oscuro al seleccionar
                foreground=[("selected", "white")])    # texto blanco en selección


        # Creación del scrollbar lateral para la tabla
        tree = ttk.Treeview(tree_frame, columns=Facturacion.visible_columns, show="headings", height=Facturacion.rows_per_page)
        Facturacion.tree = tree
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=x_scrollbar.set)
        x_scrollbar.pack(side="bottom", fill="x")
        
        tree.tag_configure('evenrow', background='#1a1a1a')  # Gris oscuro
        tree.tag_configure('oddrow', background='black')     # Negro

#Pregunta
        # Bucle para la creacion de los headings de la tabla
        for col in Facturacion.visible_columns:
            tree.heading(
                col,
                text=Facturacion.column_name_map.get(col, col),
                anchor="center",
                command=partial(Facturacion.sort_column_click, col, tree, frame_right, clear_frame_right, app)
            )
            tree.column(col, width=int(rel_size * 9), anchor="center", stretch=False)

#Pregunta
        for col in Facturacion.visible_columns:
            tree.heading(col, text=Facturacion.column_name_map.get(col, col), anchor="center")
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
            filtered_row = [row[columns.index(col)] for col in Facturacion.visible_columns]
            
            # Formatea las fechas antes de mostrarlas
            for j, col in enumerate(Facturacion.visible_columns):
                if "fecha" in col.lower() and isinstance(filtered_row[j], str):
                    filtered_row[j] = format_date(filtered_row[j])
            
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=filtered_row, tags=(tag,))
#----------------------------------------------------------------------------------------------------------------------------------------

        tree.pack(pady=rel_size // 1.5, fill="both", expand=True)
        tree.bind("<<TreeviewSelect>>", lambda event: Facturacion.on_item_selected(tree))

        # Mostrar el frame principal una vez terminado
        main_container.place(relwidth=1.0, relheight=1.0)

        # Llamada al metodo de refrescar los headings (Necesario para que se vea la flecha de ordenación de la columna)
        Facturacion.refresh_treeview_headings(tree, frame_right, clear_frame_right, app)


    # Metodo  que nos ayuda a cargar todos los datos que vamos a escribir en la base de datos
    @staticmethod
    def load_data(frame_right, clear_frame_right, app):
        db_path = "bd/BDSellCars1.db"
        try:
            #Creamos la conexión con la base de datos
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

#Preguntar
            #Especificamos el offset
            offset = (Facturacion.current_page - 1) * Facturacion.rows_per_page

            tabla = Facturacion.tabla_seleccionada

            # Construir cláusula ORDER BY si hay orden seleccionado
            order_clause = ""
            # Esto normaliza las letras con tilde (solo mayúsculas/minúsculas comunes en español)
            if Facturacion.sort_column:
                direction = Facturacion.sort_order if Facturacion.sort_order in ("asc", "desc") else "asc"
                col = Facturacion.sort_column
                # Para que a la hora de ordenar, tome en cuenta las letras con tilde, como letras normales
                col_normalized = (
          f"REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LOWER(\"{col}\"), 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u'), 'Á', 'a'), 'É', 'e'), 'Í','i'), 'Ó','o'), 'Ú','u')"
                )
                #Sentencia de ordenación
                order_clause = f"ORDER BY {col_normalized} {direction}"
            else:
                order_clause = ""

            # Sentencias, que dependiendo de si hay filtro o no, para el conteo, para la creación de páginas
            # y los datos que se van a mostrar
            if Facturacion.Filtro:
                # Sentencia para el conteo de datos
                if isinstance(Facturacion.query_params, list): 
                    count_sql = f"SELECT COUNT(*) FROM {tabla} WHERE {Facturacion.query}"
                    cursor.execute(count_sql, Facturacion.query_params)
                    total_rows = cursor.fetchone()[0]

                    # Sentencia para la recoleccion de datos
                    select_sql = f"SELECT * FROM {tabla} WHERE {Facturacion.query} {order_clause} LIMIT ? OFFSET ?"
                    cursor.execute(select_sql, Facturacion.query_params + [Facturacion.rows_per_page, offset])

                #(((((((Se puede borrar)))))))
                else: 
                    cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE {Facturacion.search_column} LIKE ?", (f"{Facturacion.query}%",))
                    total_rows = cursor.fetchone()[0]

                    cursor.execute(
                        f"SELECT * FROM {tabla} WHERE {Facturacion.search_column} LIKE ? {order_clause} LIMIT ? OFFSET ?",
                        (f"{Facturacion.query}%", Facturacion.rows_per_page, offset)
                    )
            # Coger todos los datos cuando no hay filtros
            else:
                # Conteo
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                total_rows = cursor.fetchone()[0]

                #Recolección de datos
                cursor.execute(f"SELECT * FROM {tabla} {order_clause} LIMIT ? OFFSET ?", (Facturacion.rows_per_page, offset))

            data = cursor.fetchall()
            conn.close()

            # Calculo del máximo de paginas que va a tener la recolecta de datos (cada página consta de 20 registros)
            total_pages = max((total_rows // Facturacion.rows_per_page) + (1 if total_rows % Facturacion.rows_per_page > 0 else 0), 1)
            
            #Llamamos al metodo necesario para crear la tabla
            Facturacion.create_table(
                Facturacion.query,
                list(Facturacion.column_name_map.keys()),
                data,
                frame_right,
                app,
                clear_frame_right,
                total_pages,
                Facturacion.Filtro
            )

        except sqlite3.Error as e:
            print("Error al cargar datos:", e)


    #Metodo para refrescar la interfaz ,deshacer la búsqueda y volver a la página 1`
    @staticmethod
    def clear_search(frame_right, clear_frame_right, app):
        Facturacion.Filtro = False
        Facturacion.query = ""
        Facturacion.current_page = 1
        Facturacion.abrir_Factu(frame_right, clear_frame_right, app)

    #Metodo para el cambio de página
    @staticmethod
    def change_page(direction, frame_right, clear_frame_right, app):
        Facturacion.current_page += direction
        Facturacion.load_data(frame_right, clear_frame_right, app)

    #Funcion para inicializar todo
    @staticmethod
    def abrir_Factu(frame_right, clear_frame_right, app, mantener_filtro=False):
        if not mantener_filtro:
            Facturacion.Filtro = False
            Facturacion.query = ""
            Facturacion.search_column = ""
            Facturacion.current_page = 1

        Facturacion.load_data(frame_right, clear_frame_right, app)

    #
    @staticmethod
    def get_db_column_from_display_name(display_name):
        # Recorre el diccionario de mapeo entre nombres de base de datos y nombres mostrados en la interfaz
        for db_col, disp_name in Facturacion.column_name_map.items():
            if disp_name == display_name:
                return db_col # Si encuentra coincidencia, devuelve el nombre real de columna en la base de datos
        
        return display_name # Si no encuentra el display_name, lo devuelve tal cual (por si ya es un nombre de columna válido)
    
    # Focus para entrys
    def on_focus_in_entry(entry):
        entry.configure(border_color=Facturacion.highlight_color)
        entry.configure(fg_color="#181818")

    def on_focus_out_entry(entry):
        entry.configure(border_color=Facturacion.default_border_color)
        entry.configure(fg_color=Facturacion.default_fg_color)

    # Metodo para la edición de facturas
    @staticmethod
    def edit_factura(selected_Factura, frame_right, clear_frame_right, app):
        # Metodo para la detección de otra ventana abierta (no abrir 2 ventanas a la vez)
        if Facturacion.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        # Marcar la ventana como abierta
        Facturacion.ventana_abierta = True  

        # Recolección de todos los datos de la factura seleccionada
        icon_path = "resources/logos/icon_logo.ico"
        tabla = Facturacion.tabla_seleccionada
        conn = sqlite3.connect("bd/BDSellCars1.db")
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {tabla} WHERE IDDocumento = ?", (selected_Factura,))
        factura = cursor.fetchone()
        conn.close()

        # Comprobación y exposición de un error si no hay ninguna factura seleccionada
        if not selected_Factura:
            messagebox.showerror("Error", f"No se encontró la factura con ID: {selected_Factura}")
            Facturacion.ventana_abierta = False
            return

        appModify = ctk.CTk()
        # Añadir la ventana a la array de ventanas secundarias
        Facturacion.ventanas_secundarias.append(appModify)

        # Asociamos el icono personalizado al proceso para que lo detecte bien
        if sys.platform == "win32":
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            appModify.iconbitmap(Facturacion.icon_path)

        # Titulo de la ventana
        appModify.title("Editar Factura")
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

        # Para que no se pueda cambiar el tamaño de la ventana
        appModify.resizable(False, False)

        # Definir la fuente relativa para labels y botones
        fuente_labels = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.022)) 
        fuente_boton = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.03)) 
        fuente_titulo = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.045))

        padding_relativo = int(window_height * 0.02)
        main_frame = ctk.CTkFrame(appModify, fg_color="#373737", corner_radius=0) 
        main_frame.pack(pady=padding_relativo, padx=padding_relativo, fill="both", expand=True)

        # Título dentro de la ventana
        titulo = ctk.CTkLabel(main_frame, text="Editar Factura", font=fuente_titulo, text_color="white")
        titulo.pack(pady=(int(window_height // 37), 37))

        # Scrollable frame para los entry
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=int(window_height // 37), pady=int(window_height // 37))

        # Campos para utilizarlos en conjunto con los entrys
        campos = [
            ("ID Documento", factura[0]),
            ("TipoFactura", factura[1]),
            ("DNI / CIF", factura[2]),
            ("FechaFactura", factura[3]),
            ("Cobro (€)", factura[4]),
            ("TipoTransacción", factura[5]),
            ("Clase", factura[6]),
            ("Centro", factura[7]),
            ("Serie", factura[8]),
            ("Referencia", factura[9]),
            ("Cesado", factura[10]),
            ("R.E.C.", factura[11]),
        ]

        # Array para el guardado de los datos de los entry
        entradas = []

        # Bucle para la creacion del contenido del scrollable frame
        for idx, (texto, valor) in enumerate(campos):
            # Frame para el titulo y el entry
            fila = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            fila.pack(fill="x", padx=int(window_height // 18.5), pady=int(window_height * 0.015))  # Padding relativo

            # Titulo de la linea (cual va a ser el contenido del entry)
            label = ctk.CTkLabel(fila, text=texto + ":", font=fuente_labels, width=160, anchor="w", text_color="white")
            label.pack(side="left", padx=int(window_height // 18.5))

            # Si el campo equivale a una fecha, se hace esto 
            if "Fecha" in texto:
                # Creamos un entry con un placeholder que equivale a lo que queremos que el usuario introduzca
                entry_fecha = ctk.CTkEntry(fila, placeholder_text="dd/mm/yyyy", font=fuente_labels,
                                        fg_color="#181818", text_color="white")
                if valor:
                    try:
                        # Una vez introducida la fecha, se convierte a un formato adecuado para SQL 
                        fecha_convertida = datetime.strptime(valor.strip(), "%Y-%m-%d").strftime("%d/%m/%Y")
                        entry_fecha.insert(0, fecha_convertida)
                    except ValueError:
                        entry_fecha.insert(0, valor.strip())  # Por si ya está en otro formato

                entry_fecha.pack(side="left", fill="x", expand=True)
                entradas.append(entry_fecha)

                # Para el focus del entry (cambio de color al centrarse en el campo)
                entry_fecha.bind("<FocusIn>", lambda event, e=entry_fecha: Facturacion.on_focus_in_entry(e))
                entry_fecha.bind("<FocusOut>", lambda event, e=entry_fecha: Facturacion.on_focus_out_entry(e))

            # Si el campo es este, creamos un optionmenu con sus diferentes opciones
            elif texto == "Cesado":
                opciones = ["", "Sí", "No"]
                option_menu = ctk.CTkOptionMenu(
                    fila, values=opciones,
                    button_color="#990404",  # Color del botón del OptionMenu
                    button_hover_color="#540303",  # Hover del OptionMenu
                    fg_color="#181818",  # Fondo gris oscuro del OptionMenu
                    dropdown_fg_color="#181818",  # Fondo negro en la lista del OptionMenu
                    font=fuente_labels,  # Fuente de texto del OptionMenu
                )
                option_menu.set(valor) 
                option_menu.pack(side="left", fill="x", expand=True)
                entradas.append(option_menu)


            else:
                # Fondos oscuros para los Entry
                entry = ctk.CTkEntry(fila, placeholder_text=texto, font=fuente_labels, fg_color="#181818", text_color="white")
                entry.insert(0, valor if valor is not None else "")
                entry.pack(side="left", fill="x", expand=True)
                entradas.append(entry)

                # Aplicamos el manejo de focus a los Entry
                entry.bind("<FocusIn>", lambda event, e=entry: Facturacion.on_focus_in_entry(e))
                entry.bind("<FocusOut>", lambda event, e=entry: Facturacion.on_focus_out_entry(e))

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
            command=lambda: guardar_cambios(selected_Factura)
        )
        boton_guardar.pack(pady=int(window_height * 0.03))

        # Función para el guardado de los datos escritos dentro de la ventana que hemos creado arriba
        def guardar_cambios(selected_Factura):
            valores = [] # Lista para almacenar los valores extraídos del formulario

            # Recorre todas las entradas del formulario (input fields)
            for idx, entrada in enumerate(entradas):
                contenido = entrada.get().strip() # Obtiene y limpia el texto del campo

                # Si el campo tiene una fecha
                if "Fecha" in campos[idx][0]:
                    if contenido == "":
                        valores.append("")  # Si está vacío, se deja vacío
                    else:
                        try:
                            # Intenta convertir la fecha a formato YYYY-MM-DD
                            fecha = datetime.strptime(contenido, "%d/%m/%Y")
                            valores.append(fecha.strftime("%Y-%m-%d"))  # Formato correcto de fecha Para SQLite

                        #Excepción para fechas invalidas o con formato erroneo
                        except ValueError:
                            messagebox.showerror(
                                "Fecha inválida",
                                f"La fecha ingresada en el campo '{campos[idx]}' no es válida.",
                                parent=appModify
                            )
                            return  # Abortamos el guardado
                else:
                    valores.append(contenido)
                    
            # Validación: el campo IDDocumento (factura) no puede estar vacío
            factura = valores[0].strip()
            if not factura:
                messagebox.showerror("Error de Validación", "El campo 'ID Documento' no puede estar vacío.", parent=appModify)
                return

            # Si todo es válido, hacemos el update
            try:
                with sqlite3.connect("bd/BDSellCars1.db") as conn:
                    cursor = conn.cursor()
                    # En el cursos, ponemos {tabla}, para insertar los datos en la tabla necesaria, y asi podemos
                    # ahorrar algo de código
                    cursor.execute(f"""UPDATE {tabla} SET
                            IDDocumento = ?, tipoFactura = ?,dni_cif = ?,FechaFactura = ?,cobro = ?,TipoTransaccionRecibida = ?,
                            clase = ?,centro = ?,serie = ?,referencia = ?,cesado = ?,Rec = ?
                        WHERE IDDocumento = ?""", 
                    (*valores, selected_Factura)) # Se pasan los valores y el ID anterior como condición
                    conn.commit() # Guarda los cambios

                # Refresca la interfaz después de actualizar y cierra la ventana de modificación
                Facturacion.clear_search(frame_right, clear_frame_right, app)
                Facturacion.ventana_abierta = False
                appModify.destroy()

            # Manejo de errores comunes
            except sqlite3.IntegrityError:
                # Si el nuevo IDDocumento ya existe, muestra un error
                messagebox.showerror("Error", f"Ya existe una factura con el ID: '{factura}'.", parent=appModify)
            except sqlite3.OperationalError as e:
                # Si ocurre otro error con SQLite, muestra un mensaje de error general
                messagebox.showerror("Error de Base de Datos", f"Ocurrió un error al guardar los cambios:\n{e}")
                
        # Metodo para cerrar la ventana
        def on_closing():
            Facturacion.ventana_abierta = False
            Facturacion.ventanas_secundarias.remove(appModify)
            appModify.destroy()

        appModify.protocol("WM_DELETE_WINDOW", on_closing)
        appModify.bind("<Return>", lambda event: guardar_cambios(selected_Factura))
        appModify.mainloop()

    # Metodo para selección de un usuario de la tabla
    @staticmethod
    def on_item_selected(tree):
        selected_item = tree.selection()
        if selected_item:
            Facturacion.selected_Factura = tree.item(selected_item, "values")[0]
    

    # Metodo para borrar usuario
    @staticmethod
    def delete_factura(selected_Factura, frame_right, clear_frame_right, app):
        if not selected_Factura:
            messagebox.showwarning("Aviso", "Selecciona una Factura para borrar.")
            return

        tabla = Facturacion.tabla_seleccionada
        
        # Ventana de aviso de elimincaión con pregunta de continuar o cancelar (si, no)
        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas borrar la factura con ID: {selected_Factura}?"
        )

        if respuesta:
            try:
                #Sentencia del borrado del registro por medio de la localización de este por su ID
                with sqlite3.connect("bd/BDSellCars1.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"DELETE FROM {tabla} WHERE IDDocumento = ?;", (selected_Factura,))
                    conn.commit()

                messagebox.showinfo("Éxito", f"Factura con ID {selected_Factura} eliminado correctamente.")
                Facturacion.clear_search(frame_right, clear_frame_right, app)

            except sqlite3.OperationalError as e:
                messagebox.showerror("Error de Base de Datos", f"No se pudo eliminar la factura:\n{e}")
        else:
            # El usuario eligió "No", no se hace nada
            return
    
    # 
    @staticmethod
    def obtener_datos_filtrados(columnas_sql):
        conn = sqlite3.connect("bd/BDSellCars1.db")
        cursor = conn.cursor()

        tabla = Facturacion.tabla_seleccionada  #tomamos la tabla seleccionada

        if Facturacion.Filtro:
            if isinstance(Facturacion.query_params, list):
                # Búsqueda avanzada
                cursor.execute(
                    f"SELECT {columnas_sql} FROM {tabla} WHERE {Facturacion.query}",
                    Facturacion.query_params
                )
            else:
                cursor.execute(
                    f"SELECT {columnas_sql} FROM {tabla} WHERE {Facturacion.search_column} LIKE ?",
                    (f"{Facturacion.query}%",)
                )
        else:
            # Sin filtros
            cursor.execute(f"SELECT {columnas_sql} FROM {tabla}")

        datos = cursor.fetchall()
        conn.close()
        return datos

     
    @staticmethod
    def generate_inform(app):

        # Evita abrir múltiples ventanas al mismo tiempo
        if Facturacion.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        Facturacion.ventana_abierta = True  # Marca la ventana como abierta

        # Función para la creacion y guardado del pdf en su carpeta correspondiente
        def confirmar_guardado(event=None):
            nombre_archivo = entrada_nombre.get().strip()  # Obtiene el nombre del informe ingresado

            # Validaciones
            if not nombre_archivo:
                messagebox.showerror("Error", "Debes introducir un nombre para el informe.", parent=ventana_nombre)
                return

            if not check_predefinido.get() and not check_personalizado.get():
                messagebox.showerror("Error", "Debes seleccionar un tipo de informe (predefinido o personalizado).", parent=ventana_nombre)
                return

            if check_predefinido.get() and check_personalizado.get():
                messagebox.showerror("Error", "Solo puedes seleccionar una opción.", parent=ventana_nombre)
                return

            # Añade extensión .pdf si no se incluyó
            if not nombre_archivo.endswith(".pdf"):
                nombre_archivo += ".pdf"

            # Carpeta correspondiente a la tabla seleccionada
            carpeta = Facturacion.tabla_seleccionada  # Nueva carpeta según tabla
            ruta = os.path.join("informes", carpeta, nombre_archivo) # Ruta final del informe
            os.makedirs(os.path.dirname(ruta), exist_ok=True) # Crea la carpeta si no existe

            try:
                if check_predefinido.get():
                    # Columnas fijas para el informe predefinido
                    columnas_fijas = [
                        "IDDocumento", "tipoFactura", "dni_cif", "FechaFactura", "cobro",
                        "TipoTransaccionRecibida", "clase", "centro", "serie", "referencia", "cesado", "Rec"
                    ]
                    columnas_sql = ", ".join(columnas_fijas)

                    # Obtiene los datos filtrados en función de esas columnas
                    datos = Facturacion.obtener_datos_filtrados(columnas_sql)

                    # Divide los datos en páginas
                    paginas = [datos[i:i + Facturacion.rows_per_page] for i in range(0, len(datos), Facturacion.rows_per_page)]

                    # Genera el informe PDF predefinido
                    Facturacion.generar_informe_pdf_fijo(paginas, ruta)

                elif check_personalizado.get():
                    # Columnas seleccionadas por el usuario
                    columnas_visibles = Facturacion.visible_columns
                    columnas_sql = ", ".join(columnas_visibles)

                    # Traducción de los nombres de columnas a nombres legibles
                    columnas_texto = [Facturacion.column_name_map.get(col, col) for col in columnas_visibles]

                    # Obtiene los datos y los divide en páginas
                    datos = Facturacion.obtener_datos_filtrados(columnas_sql)
                    paginas = [datos[i:i + Facturacion.rows_per_page] for i in range(0, len(datos), Facturacion.rows_per_page)]

                    # Genera el informe PDF personalizado
                    Facturacion.generar_informe_pdf(paginas, columnas_texto, ruta)

                cerrar_ventana()
                messagebox.showinfo("Éxito", f"Informe generado como:\n{ruta}", parent=app)

                # Abre el archivo generado con la aplicación predeterminada
                if platform.system() == "Windows":
                    os.startfile(ruta)
                elif platform.system() == "Darwin":
                    os.system(f"open '{ruta}'")
                else:
                    os.system(f"xdg-open '{ruta}'")

            except Exception as e:
                # Muestra mensaje de error en caso de excepción
                messagebox.showerror("Error", f"No se pudo generar el informe.\n\n{e}", parent=app)
                cerrar_ventana()

        # Cierra la ventana y libera el bloqueo
        def cerrar_ventana():
            Facturacion.ventana_abierta = False
            ventana_nombre.destroy()

        # Lógica para seleccionar solo una opción de tipo de informe
        def toggle_check(tipo):

            if tipo == "predef":
                if check_predefinido.get():
                    check_personalizado.deselect()
            elif tipo == "personal":
                if check_personalizado.get():
                    check_predefinido.deselect()

         # Escalado de la ventana según resolución de pantalla
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

        # Crea la ventana secundaria
        ventana_nombre = ctk.CTk()
        Facturacion.ventanas_secundarias.append(ventana_nombre)

        ventana_nombre.title("Guardar Informe de Facturas")
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

        # Asocia el cierre de la ventana al método `cerrar_ventana`
        ventana_nombre.protocol("WM_DELETE_WINDOW", cerrar_ventana)

        # Fuentes personalizadas
        fuente_titulo = ctk.CTkFont(family="Sans Sulex", size=fuente_titulo_size)
        fuente_label = ctk.CTkFont(family="Sans Sulex", size=fuente_label_size)
        fuente_boton = ctk.CTkFont(family="Sans Sulex", size=fuente_boton_size)

        # Frame principal con fondo oscuro
        frame_principal = ctk.CTkFrame(ventana_nombre, fg_color="#373737", corner_radius=0)
        frame_principal.pack(fill="both", expand=True, padx=int(20 * escala_w), pady=int(20 * escala_h))

        # Título de la ventana
        label_titulo = ctk.CTkLabel(frame_principal, text="Informe de Facturas", font=fuente_titulo, text_color="white")
        label_titulo.pack(pady=(int(10 * escala_h), int(10 * escala_h)))

        # Entrada de texto para el nombre del archivo
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
        # Permite usar la tecla Enter para guardar
        ventana_nombre.bind("<Return>", confirmar_guardado)

        # Inicia el bucle principal de la ventana
        ventana_nombre.mainloop()

        
    @staticmethod
    def generar_informe_pdf_fijo(paginas, ruta_salida="informe_facturas.pdf"):
        # Columnas base y nombres legibles para el encabezado
        columnas = [
            "IDDocumento", "tipoFactura", "dni_cif", "FechaFactura", "cobro",
            "TipoTransaccionRecibida", "clase", "centro", "serie", "referencia", "cesado", "Rec"
        ]

        nombres_columnas = [
            "ID", "Tipo", "DNI/CIF", "Fecha", "€",
            "Transaccion", "Clase", "Centro", "Serie", "Referencia", "Cesado", "REC"
        ]
        # Peso proporcional de cada columna (determina el ancho relativo)
        pesos = {
            "ID": 1.2,
            "Tipo": 1.2,
            "DNI/CIF": 1.3,
            "Fecha": 1.2,
            "€": 1.0,
            "Transaccion": 2.2,
            "Clase": 1.0,
            "Centro": 1.0,
            "Serie": 1.0,
            "Referencia": 2.0,
            "Cesado": 0.9,
            "REC": 0.9
        }

        # Registrar fuente personalizada
        font_path = "resources/font/sans-sulex/SANSSULEX.ttf"
        pdfmetrics.registerFont(TTFont("Sans Sulex", font_path))
        
        # Crear objeto PDF en orientación horizontal
        c = canvas.Canvas(ruta_salida, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Configuraciones de márgenes y proporción
        x = 1 * cm
        total_padding = 2 * cm
        peso_total = sum(pesos.values())
        espacio_col = [(width - total_padding) * (pesos[col] / peso_total) for col in nombres_columnas]

        font_size = 9
        altura_fila = 0.75 * cm
        altura_encabezado = 1.0 * cm
        total_paginas = len(paginas)

        # Iterar sobre cada página de datos
        for num_pagina, datos_pagina in enumerate(paginas, start=1):
            y = height - 1 * cm

            # Mover el logo a la derecha
            try:
                logo = ImageReader("resources/logos/hgcnegro.png")
                orig_width, orig_height = logo.getSize()
                logo_width = 4 * cm
                logo_height = (orig_height / orig_width) * logo_width
                c.drawImage(logo, width - logo_width - x, y - logo_height + 0.5 * cm, width=logo_width, height=logo_height, mask='auto')
            except:
                pass   # Si falla el logo, continuar "sin error"

            y -= 1.4 * cm

            # Título centrado a la izquierda del logo
            c.setFont("Sans Sulex", 14)
            c.setFillColor(colors.black)
            c.drawString(x, y, "LISTADO DE FACTURAS")

            y -= 1.4 * cm

            # Cabeceras
            c.setFillColorRGB(0.27, 0.27, 0.27)
            c.rect(x - 0.1 * cm, y - 0.1 * cm, width - total_padding + 0.2 * cm, altura_encabezado, fill=True, stroke=False)
            c.setFillColor(colors.white)
            c.setFont("Sans Sulex", font_size + 1)

            col_x = x
            for idx, col in enumerate(nombres_columnas):
                c.drawString(col_x, y + altura_encabezado / 2 - font_size / 2.5, col)
                col_x += espacio_col[idx]

            y -= altura_encabezado
            c.setFont("Sans Sulex", font_size)

            # Dibujar cada fila de datos
            for fila in datos_pagina:
                # Alternar color de fondo (gris claro/blanco)
                c.setFillColor(colors.whitesmoke if datos_pagina.index(fila) % 2 == 0 else colors.lightgrey)
                c.rect(x - 0.1 * cm, y - 0.1 * cm, width - total_padding + 0.2 * cm, altura_fila, fill=True, stroke=False)
                c.setFillColor(colors.black)

                # Dibujar columnas de la fila
                col_x = x
                for idx, item in enumerate(fila):
                    texto = str(item) if item is not None else ""
                    max_chars = int((espacio_col[idx] / cm) * 5.5)
                    lineas = wrap(texto, width=max_chars)[:2]
                    for j, linea in enumerate(lineas):
                        c.drawString(col_x, y + altura_fila / 2 - j * (font_size + 1.5), linea)
                    col_x += espacio_col[idx]

                y -= altura_fila

            # Pie de página con fecha y número de página
            fecha_actual = format_datetime(datetime.now(), "EEEE, d 'de' MMMM 'de' y, HH:mm", locale="es")
            c.setFont("Sans Sulex", 9)
            c.setFillColor(colors.black)
            c.drawString(x, 0.4 * cm, f"Fecha de creación: {fecha_actual}")
            c.drawRightString(width - x, 0.4 * cm, f"Página {num_pagina} de {total_paginas}")

            c.showPage()

        c.save()

    
    # Genera un informe PDF en formato horizontal con los datos proporcionados en múltiples páginas.
    # Cada página incluye un logo, título, encabezado de columnas y filas con datos, además de pie 
    # de página con la fecha y número de página.

    @staticmethod
    def generar_informe_pdf(paginas, columnas, ruta_salida="informe_facturas_personalizado.pdf"):

        # Registrar la fuente personalizada desde el archivo .ttf
        font_path = "resources/font/sans-sulex/SANSSULEX.ttf"
        pdfmetrics.registerFont(TTFont("Sans Sulex", font_path))

        # Crear el canvas del PDF en orientación horizontal
        c = canvas.Canvas(ruta_salida, pagesize=landscape(A4))
        width, height = landscape(A4)

        # Ruta del logo y margen izquierdo
        logo_path = "resources/logos/hgcnegro.png"
        x = 1 * cm  # margen izquierdo
        total_padding = 2 * cm  # márgenes izquierdo y derecho combinados

        # Cálculo del ancho de cada columna
        num_columnas = len(columnas)
        peso_columna = (width - total_padding) / num_columnas

        # Configuración de estilo
        font_size = 9
        altura_fila = 0.75 * cm
        altura_encabezado = 1.0 * cm
        max_chars_per_line = 30 
        total_paginas = len(paginas)

        # Iterar por cada página de datos
        for num_pagina, datos_pagina in enumerate(paginas, start=1):
            y = height - 1 * cm

            # Mover logo a la derecha
            try:
                logo = ImageReader(logo_path)
                orig_width, orig_height = logo.getSize()
                logo_width = 4 * cm
                logo_height = (orig_height / orig_width) * logo_width
                c.drawImage(logo, width - logo_width - x, y - logo_height + 0.5 * cm, width=logo_width, height=logo_height, mask='auto')
            except:
                pass  # Si el logo no se encuentra o da error, se omite

            y -= 1.4 * cm

            # Título a la izquierda
            c.setFont("Sans Sulex", 14)
            c.setFillColor(colors.black)
            c.drawString(x, y, "LISTADO DE FACTURAS")

            y -= 1.4 * cm

            # Encabezados
            c.setFillColorRGB(0.27, 0.27, 0.27)
            c.rect(x - 0.1 * cm, y - 0.1 * cm, width - total_padding + 0.2 * cm, altura_encabezado, fill=True, stroke=False)
            c.setFillColor(colors.white)
            c.setFont("Sans Sulex", font_size + 1)

            col_x = x
            for col in columnas:
                nombre_col = str(col)[:max_chars_per_line]
                c.drawString(col_x, y + altura_encabezado / 2 - font_size / 2.5, nombre_col)
                col_x += peso_columna

            y -= altura_encabezado  # bajar para dibujar las filas
            c.setFont("Sans Sulex", font_size)

            # Dibujar filas de datos
            for fila in datos_pagina:
                c.setFillColor(colors.whitesmoke if datos_pagina.index(fila) % 2 == 0 else colors.lightgrey)
                c.rect(x - 0.1 * cm, y - 0.1 * cm, width - total_padding + 0.2 * cm, altura_fila, fill=True, stroke=False)
                c.setFillColor(colors.black)

                col_x = x
                for idx, item in enumerate(fila):
                    texto = str(item) if item is not None else ""
                    max_chars = int((peso_columna / cm) * 5.5)
                    lineas = wrap(texto, width=max_chars)[:2]
                    for j, linea in enumerate(lineas):
                        c.drawString(col_x, y + altura_fila / 2 - j * (font_size + 1.5), linea)
                    col_x += peso_columna

                y -= altura_fila

            # Pie de página con fecha actual y número de página
            fecha_actual = format_datetime(datetime.now(), "EEEE, d 'de' MMMM 'de' y, HH:mm", locale="es")
            c.setFont("Sans Sulex", 9)
            c.setFillColor(colors.black)
            c.drawString(x, 0.4 * cm, f"Fecha de creación: {fecha_actual}")
            c.drawRightString(width - x, 0.4 * cm, f"Página {num_pagina} de {total_paginas}")

            c.showPage()

        c.save() # Guardar todo el progreso

    @staticmethod
    def ver_factura():
        if not Facturacion.selected_Factura:
            messagebox.showerror("Error", "Selecciona una factura para ver.")
            return

        try:

            # === REGISTRAR FUENTES ===
            try:
                pdfmetrics.registerFont(TTFont("Sans Sulex", "resources/font/sans-sulex/SANSSULEX.ttf"))
            except Exception as e:
                messagebox.showerror("Error de fuente", f"No se pudo cargar la fuente Sans Sulex.\n{e}")
                return

            # === OBTENER DATOS DE FACTURA ===
            conn = sqlite3.connect("bd/BDSellCars1.db")
            cursor = conn.cursor()
            tabla = Facturacion.tabla_seleccionada  # Determinar la tabla activa
            cursor.execute(f"SELECT * FROM {tabla} WHERE IDDocumento = ?", (Facturacion.selected_Factura,))
            factura = cursor.fetchone()
            conn.close()

            if not factura:
                messagebox.showerror("Error", "No se encontró la factura.")
                return

            # === CREAR RUTA DINÁMICA SEGÚN LA TABLA ===
            if tabla == "FacturasClientes":
                subcarpeta = "clientes"
            elif tabla == "FacturasProveedores":
                subcarpeta = "proveedores"
            elif tabla == "FacturasAcreedores":
                subcarpeta = "acreedores"
            else:
                messagebox.showerror("Error", f"Tabla desconocida: {tabla}")
                return

            carpeta_destino = os.path.join("facturas", subcarpeta)
            os.makedirs(carpeta_destino, exist_ok=True)

            ruta = os.path.join(carpeta_destino, f"factura_{factura[0]}.pdf")

            # === CREACIÓN DEL PDF ===
            c = canvas.Canvas(ruta, pagesize=A4)
            width, height = A4

            # === LOGO ===
            try:
                logo_path = "resources/logos/hgcnegro.png"
                logo = ImageReader(logo_path)
                c.drawImage(logo, 2 * cm, height - 3 * cm, width=4 * cm, height=2 * cm, mask='auto')
            except Exception as e:
                print(f"Error cargando el logo: {e}")

            # === EMPRESA (DERECHA) ===
            c.setFont("Sans Sulex", 16)
            c.drawRightString(width - 2 * cm, height - 1.5 * cm, "HGC COMPANY S.L.")
            c.setFont("Sans Sulex", 10)
            c.drawRightString(width - 2 * cm, height - 2.2 * cm, "www.hgccompany.com")
            c.drawRightString(width - 2 * cm, height - 2.8 * cm, "info@hgccompany.com")

            # === SEPARADOR ===
            c.setStrokeColor(colors.grey)
            c.setLineWidth(0.8)
            c.line(2 * cm, height - 3.5 * cm, width - 2 * cm, height - 3.5 * cm)

            # === TÍTULO ===
            c.setFont("Sans Sulex", 14)
            c.drawCentredString(width / 2, height - 4.5 * cm, "FACTURA DETALLADA")

            # === FECHA DE EMISIÓN ===
            c.setFont("Sans Sulex", 10)
            c.drawString(2 * cm, height - 5.3 * cm, f"Fecha de emisión: {datetime.now().strftime('%d/%m/%Y %H:%M')}")

            # === DATOS ===
            campos = [
                ("ID Documento", factura[0]), ("Tipo de Factura", factura[1]), ("DNI / CIF", factura[2]),
                ("Fecha de Factura", factura[3]), ("Cobro (€)", f"{factura[4]:.2f}" if factura[4] else ""),
                ("Tipo de Transacción", factura[5]), ("Clase", factura[6]), ("Centro", factura[7]),
                ("Serie", factura[8]), ("Referencia", factura[9]), ("Cesado", "Sí" if factura[10] == "1" else "No"),
                ("R.E.C.", factura[11])
            ]

            y = height - 6.2 * cm
            c.setFont("Sans Sulex", 11)
            c.setFillColor(colors.HexColor("#990404"))

            for i, (etiqueta, valor) in enumerate(campos):
                if i == 6:
                    y -= 1.0 * cm
                c.drawString(2 * cm, y, f"{etiqueta}:")
                c.setFont("Sans Sulex", 10)
                c.setFillColor(colors.black)
                c.drawString(6.2 * cm, y, str(valor) if valor is not None else "")
                y -= 0.7 * cm
                c.setFont("Sans Sulex", 11)
                c.setFillColor(colors.HexColor("#990404"))

            # === PIE ===
            c.setFont("Sans Sulex", 9)
            c.setFillColor(colors.darkgrey)
            c.drawString(2 * cm, 2 * cm, "Documento generado automáticamente. No requiere firma.")
            c.drawRightString(width - 2 * cm, 2 * cm, "Página 1 de 1")

            c.save()

            # Abrir
            if platform.system() == "Windows":
                os.startfile(ruta)
            elif platform.system() == "Darwin":
                os.system(f"open '{ruta}'")
            else:
                os.system(f"xdg-open '{ruta}'")

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar la factura.\n{e}")




    @staticmethod
    def search_plus(frame_right, clear_frame_right, app):
        
        # Verifica si ya hay una ventana de búsqueda abierta
        if Facturacion.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return
        
        tabla = Facturacion.tabla_seleccionada  # Obtiene la tabla seleccionada
        Facturacion.ventana_abierta = True  # Marcar la ventana como abierta
        
        
        total_width = app.winfo_width()

        # Crea una nueva ventana
        app_sp = ctk.CTk()
        Facturacion.ventanas_secundarias.append(app_sp)  # Añade esta ventana a la lista de ventanas secundarias

        # Establece el icono de la ventana en Windows
        if sys.platform == "win32":
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            app_sp.iconbitmap(Facturacion.icon_path)

        app_sp.title("Buscar Factura")  # Título de la ventana
        ctk.set_appearance_mode("dark")  # Modo oscuro
        ctk.set_default_color_theme("dark-blue")  # Tema de colores

        # Establece el icono de la ventana si existe
        icon_path = "resources/logos/icon_logo.ico"
        if icon_path and os.path.exists(icon_path):
            app_sp.iconbitmap(icon_path)

        # Obtiene el monitor principal y configura la geometría de la ventana
        monitors = screeninfo.get_monitors()
        main_monitor = next((m for m in monitors if m.is_primary), monitors[0])
        window_width = int(main_monitor.width * 0.55)
        window_height = int(main_monitor.height * 0.55)
        x_position = (main_monitor.width - window_width) // 2
        y_position = (main_monitor.height - window_height) // 2
        app_sp.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        app_sp.resizable(False, False)

        # Fuentes y espaciado
        fuente_labels = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.03))
        fuente_boton = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.038))
        fuente_titulo = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.053))
        padding_relativo = int(window_height * 0.007)

        main_frame = ctk.CTkFrame(app_sp, fg_color="#373737", corner_radius=0)
        main_frame.pack(pady=padding_relativo, padx=padding_relativo, fill="both", expand=True)

        titulo = ctk.CTkLabel(main_frame, text="Buscar Factura", font=fuente_titulo, text_color="white")
        titulo.pack(pady=(int(window_height * 0.03), int(window_height * 0.015)))

        contenido_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        contenido_frame.pack(expand=True)

        # Lista de campos de texto simples
        campos_nombres = [
        "ID Documento","TipoFactura","DNI / CIF","FechaFactura","TipoTransacción","Clase",
        "Centro","Serie","Referencia","R.E.C."]

        entradas = {}  # Diccionario para guardar los campos
        columnas_por_fila = 3  # Cantidad de campos por fila
        fila_actual = ctk.CTkFrame(contenido_frame, fg_color="transparent")
        fila_actual.pack(pady=int(window_height * 0.01))

        # Crear los Entry por cada campo de texto
        count = 0
        for texto in campos_nombres:
            if count % columnas_por_fila == 0 and count != 0:
                fila_actual = ctk.CTkFrame(contenido_frame, fg_color="transparent")
                fila_actual.pack(pady=int(window_height * 0.01))

            campo = ctk.CTkEntry(fila_actual, placeholder_text=texto, font=fuente_labels,
                                fg_color="#181818", text_color="white", width=int(window_width * 0.25),height=int(window_height * 0.07))
            campo.pack(side="left", padx=int(window_width * 0.01))
            entradas[texto] = campo
            count += 1
            
            # Efectos de focus en el campo
            campo.bind("<FocusIn>", lambda event, e=campo: Facturacion.on_focus_in_entry(e))
            campo.bind("<FocusOut>", lambda event, e=campo: Facturacion.on_focus_out_entry(e))

        # Campos especiales que requieren operadores o selección
        bloques_especiales = [

            [("Cobro (€)", "num"),
            ("Cesado", ctk.CTkOptionMenu, ["", "Sí", "No"]),
            ("FechaFactura", "fecha")]
        ]
        
        # Lo que el usuario ve como clave, lo que se usará en SQL como valor
        operadores_fecha = {
            "=": "=",
            "<": "<=",
            ">": ">="
        }

        condiciones_fecha = {}  # Guarda el operador seleccionado para fechas
        condiciones_num = {}    # Guarda el operador seleccionado para números

        especiales_frame = ctk.CTkFrame(contenido_frame, fg_color="transparent")
        especiales_frame.pack(pady=int(window_height * 0.01))

        # Crear widgets especiales (Números con botón de comparación, optionmenus, o fechas con botón de mayor o menor)
        for fila in bloques_especiales:
            fila_frame = ctk.CTkFrame(especiales_frame, fg_color="transparent")
            fila_frame.pack(pady=int(window_height * 0.01))

            for texto, tipo_widget, *extra in fila:
                sub_frame = ctk.CTkFrame(fila_frame, fg_color="transparent")
                sub_frame.pack(side="left", padx=int(window_width * 0.015))

                ctk.CTkLabel(
                    sub_frame,
                    text=texto,
                    font=fuente_labels,
                    text_color="white"
                ).pack(anchor="w", pady=(0, int(window_height * 0.005)))

                if tipo_widget == "fecha":
                    # Campo de fecha con operador
                    campo_container = ctk.CTkFrame(sub_frame, fg_color="transparent")
                    campo_container.pack()

                    operador_menu = ctk.CTkOptionMenu(
                        campo_container,
                        values=list(operadores_fecha.keys()),
                        width=int(window_width * 0.08),
                        font=fuente_labels,
                        fg_color="#2b2b2b",
                        button_color="#444",
                        dropdown_fg_color="#181818"
                    )
                    operador_menu.set("=")
                    operador_menu.pack(side="left", padx=(0, int(window_width * 0.005)))

                    campo = ctk.CTkEntry(
                        campo_container,
                        placeholder_text="dd/mm/yyyy",
                        font=fuente_labels,
                        fg_color="#181818",
                        text_color="white",
                        width=int(window_width * 0.2)
                    )
                    campo.pack(side="left")

                    condiciones_fecha[texto] = operador_menu

                # Campo numérico con operador
                elif tipo_widget == "num":
                    campo_container = ctk.CTkFrame(sub_frame, fg_color="transparent")
                    campo_container.pack()

                    operador_menu = ctk.CTkOptionMenu(
                        campo_container,
                        values=list(operadores_fecha.keys()),
                        width=int(window_width * 0.08),
                        font=fuente_labels,
                        fg_color="#2b2b2b",
                        button_color="#444",
                        dropdown_fg_color="#181818"
                    )
                    operador_menu.set("=")
                    operador_menu.pack(side="left", padx=(0, int(window_width * 0.005)))

                    campo = ctk.CTkEntry(
                        campo_container,
                        placeholder_text="Escriba un número",
                        font=fuente_labels,
                        fg_color="#181818",
                        text_color="white",
                        width=int(window_width * 0.2)
                    )
                    campo.pack(side="left")

                    condiciones_num[texto] = operador_menu

                # OptionMenu simple (por ejemplo, Cesado)
                else:
                    opciones = extra[0]
                    campo = tipo_widget(
                        sub_frame,
                        values=opciones,
                        font=fuente_labels,
                        fg_color="#181818",
                        button_color="#990404",
                        button_hover_color="#540303",
                        dropdown_fg_color="#181818",
                        dropdown_font=("Sans Sulex", int(window_height * 0.025)),
                        width=int(window_width * 0.27),
                        height=int(window_width * 0.045)
                    )
                    campo.set("")
                    campo.pack()

                entradas[texto] = campo

        # Función que realiza la búsqueda al pulsar el botón
        def buscar():

            datos = {k: v.get().strip() for k, v in entradas.items()}
            print("Datos recogidos:", datos)

            db_path = "bd/BDSellCars1.db"

            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                condiciones = []
                valores = []

                # Mapea los nombres del UI a los nombres reales en la BD
                campos_db = {
                    "ID Documento": "IDDocumento",
                    "TipoFactura": "tipoFactura",
                    "DNI / CIF": "dni_cif",
                    "FechaFactura": "FechaFactura",
                    "Cobro (€)": "cobro",
                    "TipoTransacción": "TipoTransaccionRecibida",
                    "Clase": "clase",
                    "Centro": "centro",
                    "Serie": "serie",
                    "Referencia": "referencia",
                    "Cesado": "cesado",
                    "R.E.C.": "Rec"
                }

                for campo_ui, valor in datos.items():
                    if valor:
                        if campo_ui in condiciones_fecha:
                            operador_ui = condiciones_fecha[campo_ui].get()  # =, < o >
                            operador_sql = operadores_fecha.get(operador_ui, "=")  # =, <=, >=

                            # Transformación del formato de fechas
                            try:
                                fecha_obj = datetime.strptime(valor, "%d/%m/%Y")
                                valor_sql = fecha_obj.strftime("%Y-%m-%d")
                            except ValueError:
                                valor_sql = valor

                            condiciones.append(f"{campos_db[campo_ui]} {operador_sql} ?")
                            valores.append(valor_sql)
                        else:
                            condiciones.append(f"{campos_db[campo_ui]} LIKE ?")
                            valores.append(f"{valor}%")

                where_clause = " AND ".join(condiciones) if condiciones else "1"

                #Ejecución de la query con todos los campos que hemos querido saber 
                Facturacion.current_page = 1
                cursor.execute(f"SELECT COUNT(*) FROM {tabla} WHERE {where_clause}", valores)
                total_rows = cursor.fetchone()[0]

                if total_rows == 0:
                    messagebox.showinfo(
                        "Sin Resultados",
                        "No se encontró ningún cliente que cumpla con todos los criterios indicados.",
                        parent=app_sp
                    )
                    conn.close()
                    return

                total_pages = max((total_rows // Facturacion.rows_per_page) + (1 if total_rows % Facturacion.rows_per_page > 0 else 0), 1)
                offset = (Facturacion.current_page - 1) * Facturacion.rows_per_page

                cursor.execute(
                    f"SELECT * FROM {tabla} WHERE {where_clause} LIMIT ? OFFSET ?",
                    valores + [Facturacion.rows_per_page, offset]
                )
                data = cursor.fetchall()

                conn.close()

                # Actualiza la tabla principal con los nuevos resultados
                Facturacion.Filtro = bool(condiciones)
                Facturacion.query = where_clause
                Facturacion.query_params = valores
                Facturacion.ventana_abierta = False
                Facturacion.create_table(
                    Facturacion.query,
                    [
                        "IDDocumento","tipoFactura","dni_cif","FechaFactura","cobro",
                        "TipoTransaccionRecibida","clase","centro","serie","referencia","cesado","Rec"
                    ],
                    data,
                    frame_right,
                    app,
                    clear_frame_right,
                    total_pages,
                    Facturacion.Filtro
                )

                app_sp.destroy()

            except sqlite3.Error as e:
                print("Error al buscar Facturas:", e)

        # Botón para realizar la búsqueda
        boton_buscar = ctk.CTkButton(
            main_frame,
            text="Buscar",
            font=fuente_boton,
            fg_color="#990404",
            hover_color="#540303",
            border_width=2,
            border_color="black",
            corner_radius=10,
            height=int(window_height * 0.065),
            command=buscar
        )
        
        # Acción al cerrar la ventana
        def on_closing():
            Facturacion.ventana_abierta = False
            Facturacion.ventanas_secundarias.remove(app_sp)
            app_sp.destroy()

        boton_buscar.pack(pady=int(window_height * 0.03))
        app_sp.protocol("WM_DELETE_WINDOW", on_closing)
        app_sp.bind("<Return>", lambda event: buscar()) # Permite pulsar Enter para buscar

        app_sp.mainloop() # Ejecuta la ventana


# Funciones para ordenar las columnas de la tabla--------------------------------------------------------------------
    @staticmethod
    def sort_by_column(column, frame_right, clear_frame_right, app):
        # Si ya se está ordenando por esta columna, se cambia el orden (ascendente <-> descendente)
        if Facturacion.sort_column == column:
            Facturacion.sort_ascending = not Facturacion.sort_ascending
        # Si es una columna nueva, se establece como columna actual de ordenación y en orden ascendente
        else:
            Facturacion.sort_column = column
            Facturacion.sort_ascending = True

        # Se resetea la página actual a la primera (importante para paginación)
        Facturacion.current_page = 1

        # Se recargan los datos con la nueva ordenación
        Facturacion.load_data(frame_right, clear_frame_right, app)

    @staticmethod
    def update_sort_state(column):
        # Quitar estado de todas las columnas excepto la actual
        for col in Facturacion.visible_columns:
            if col != column:
                Facturacion.sort_states[col] = None

        # Obtiene el estado actual de la columna seleccionada (puede ser 'asc', 'desc' o None)
        current = Facturacion.sort_states.get(column)

        # Ciclo de estados: asc -> desc -> None -> asc ...
        if current == "asc":
            Facturacion.sort_states[column] = "desc"
        elif current == "desc":
            Facturacion.sort_states[column] = None
        else:
            Facturacion.sort_states[column] = "asc"

        # Actualiza la columna y el orden actuales según el nuevo estado
        Facturacion.sort_column = column if Facturacion.sort_states[column] else None
        Facturacion.sort_order = Facturacion.sort_states[column] or ""



    @staticmethod
    def refresh_treeview_headings(tree, frame_right, clear_frame_right, app):
        # Actualiza los encabezados del Treeview para reflejar el estado de ordenación actual

        for col in Facturacion.visible_columns:
            sort_state = Facturacion.sort_states.get(col)  # estado actual de orden de esa columna
            base_text = Facturacion.column_name_map.get(col, col)  # nombre legible de la columna

            # Añade un símbolo al encabezado según el estado de orden (▲ para asc, ▼ para desc)
            if sort_state == "asc":
                heading_text = f"{base_text} ▲"
            elif sort_state == "desc":
                heading_text = f"{base_text} ▼"
            else:
                heading_text = base_text

            # Asigna nuevamente el encabezado al Treeview y enlaza el evento de clic
            tree.heading(
                col,
                text=heading_text,
                anchor="center",
                command=partial(Facturacion.sort_column_click, col, tree, frame_right, clear_frame_right, app)
        )


    @staticmethod
    def sort_column_click(col, tree, frame_right, clear_frame_right, app):

        # Al hacer clic en un encabezado de columna:
        # Se actualiza el estado de orden (asc, desc, o ninguno)
        Facturacion.update_sort_state(col)

        # Se refrescan los encabezados para mostrar los símbolos de orden correctamente
        Facturacion.refresh_treeview_headings(tree, frame_right, clear_frame_right, app)
    
        # Se recargan los datos con la nueva ordenación aplicada
        Facturacion.load_data(frame_right, clear_frame_right, app)