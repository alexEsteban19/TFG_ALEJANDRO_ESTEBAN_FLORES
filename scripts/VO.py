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
import matplotlib.pyplot as plt
from matplotlib import font_manager

class VO:
    current_page = 1
    rows_per_page = 20
    visible_columns = None
    Filtro = False
    query = ""
    search_column = ""
    selected_VO = None  # Mantener el cliente seleccionado como variable estática
    query_params = ""
    ventana_abierta = False  
    icon_path = "resources/logos/icon_logo.ico"
    ventanas_secundarias = []

    sort_column = None
    sort_order = "asc"  # o "DESC"
    sort_states = {}  # Diccionario: {"columna": "asc" | "desc" | None}


    column_name_map = {
        "matriculaVO": "Matricula",
        "numeroExpediente": "Nº Expediente",
        "marca": "Marca",
        "modelo": "Modelo",
        "version": "Versión",
        "chasis": "Chasis",
        "anomatriculacion": "Año Matriculación",
        "FechaCompletaMatriculacion": "Fecha Matriculación",
        "AntiguedadVO": "Antigüedad",
        "kilometros": "Kilometros",
        "CC": "CC",
        "CV": "CV",
        "colorExterno": "Color",
        "colorTapiceria": "Tapiceria",
        "N_puertas": "Nº Puertas",
        "categoria": "Categoria",
        "emisionCO2": "Emisiones CO2",
        "tipoVO": "Tipo VO",
        "capacidadDeposito": "Capacidad Deposito",
        "TipoCombustible": "Tipo Combustible",
        "situacion": "Situacion",
        "DiasStock": "Dias en Stock",
        "ubicacionStock": "Ubicacion Stock",
        "FechaDisponibleVenta": "Fecha Disponible Venta",
        "PrecioVentaVO": "Precio Venta",
        "PrecioCompraVentaVO": "Precio Compra-Venta",
        "FechaRecogidaVO": "Fecha Recogida",
        "DistintivoAmbiental": "Distintivo Ambiental",
        "FechaSalidaVO": "Fecha Salida", 
        "FechaTransferenciaCompleta": "Fecha Transf Completa",     
        "FechaITVhasta": "Fecha ITV Hasta", 
        "cifExpropietario": "DNI/CIF Expropietario",  
        "FechaReservaVO": "Fecha Reserva"
    }
    
    column_options = {
        "matriculaVO": "Matricula",
        "numeroExpediente": "Nº Expediente",
        "marca": "Marca",
        "modelo": "Modelo",
        "version": "Versión",
        "chasis": "Chasis",
        "anomatriculacion": "Año Matriculación",
        "kilometros": "Kilometros",
        "CV": "CV",
        "colorExterno": "Color",
        "N_puertas": "Nº Puertas",
        "TipoCombustible": "Tipo Combustible",
        "situacion": "Situacion",
        "DiasStock": "Dias en Stock",
        "ubicacionStock": "Ubicacion Stock",
        "PrecioVentaVO": "Precio Venta",
        "FechaTransferenciaCompleta": "Fecha Transf Completa",     
        "FechaITVhasta": "Fecha ITV Hasta", 
        "cifExpropietario": "DNI/CIF Expropietario",  
    }


    @staticmethod
    def create_table(query, columns, data, frame_right, app, clear_frame_right, total_pages, Filtro):
        for widget in frame_right.winfo_children():
            widget.destroy()

        VO.selected_VO = None
        total_width = app.winfo_width()
        rel_size = total_width / 100

        if VO.visible_columns is None or not VO.visible_columns:
            VO.visible_columns = ["matriculaVO","numeroExpediente","marca","modelo","version",
                                  "chasis","anomatriculacion","kilometros",
                                  "CV","colorExterno","N_puertas","TipoCombustible"
                                  ,"situacion","DiasStock","ubicacionStock","PrecioVentaVO"
                                  ,"FechaTransferenciaCompleta","FechaITVhasta", "cifExpropietario"]
            
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
        
        search_frame = ctk.CTkFrame(main_frame, fg_color="transparent", corner_radius=int(rel_size // 2))
        search_frame.pack(fill="x", padx=rel_size // 6, pady=rel_size // 6)
        
        title = ctk.CTkLabel(search_frame, text="HGC - GESTIÓN DE VEHÍCULOS DE OCASIÓN", 
                                    font=("Sans Sulex", int(rel_size * 1.4)),
                                    text_color="white")
        title.pack(side="left", padx=rel_size * 1.2, pady=int(rel_size // 1.8))

        # Espaciador para empujar botones a la derecha
        spacer = ctk.CTkLabel(search_frame, text="")  # Vacío, sirve solo para expandir
        spacer.pack(side="left", expand=True)

        informe_image = Image.open("resources/icons/white/votacion.png").resize(icon_size)
        informe_image = ctk.CTkImage(light_image=informe_image)
        informe_btn = ctk.CTkButton(search_frame, text="Generar Informe", image=informe_image, fg_color=btn_color,
                                font=("Sans Sulex", int(rel_size)),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2), anchor="w",
                                border_width=2, border_color="white", command=lambda: VO.generate_inform(app))
        informe_btn.pack(side="left", padx=rel_size // 2, pady=int(rel_size // 1.8))

        search_plus_image = Image.open("resources/icons/white/search.png").resize(icon_size)
        search_plus_image = ctk.CTkImage(light_image=search_plus_image)
        search_plus_button = ctk.CTkButton(search_frame, text="", image=search_plus_image, fg_color=btn_color,
                                    hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                    border_width=2, border_color="white",
                                    width=icon_size[0], height=icon_size[1],command=lambda: VO.search_plus(frame_right, clear_frame_right, app)
                                    )
        search_plus_button.pack(side="left", padx=rel_size // 1.5)

        refresh_image = Image.open("resources/icons/white/refresh.png").resize(icon_size)
        refresh_image = ctk.CTkImage(light_image=refresh_image)
        clear_search_button = ctk.CTkButton(search_frame, text="", image=refresh_image, fg_color=btn_color,
                                            hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                            border_width=2, border_color="white",
                                            width=icon_size[0], height=icon_size[1],
                                            command=lambda: VO.clear_search(frame_right, clear_frame_right, app))
        clear_search_button.pack(side="left", padx=rel_size // 1.5)


        # 🔹 Frame desplegable principal
        column_filter_frame = ctk.CTkFrame(frame_right, fg_color="black", corner_radius=15, width=300)
        filter_open = [False]  # Para mutabilidad

        # 🔹 Frame para el botón fijo en la parte de abajo
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

        # 🔹 Scrollable frame para los checkboxes
        checkbox_scroll_frame = ctk.CTkScrollableFrame(column_filter_frame, fg_color="black")
        checkbox_scroll_frame.pack(side="top", fill="both", expand=True)

        # 🔹 Variables y checkboxes
        selected_columns = {
            col: ctk.BooleanVar(value=(col in VO.visible_columns)) for col in columns
        }

        max_line_length = 14  # ajusta este valor según tu diseño

        for col in columns:
            if col == "matriculaVO":
                continue  # Saltar esta columna específica

            raw_text = VO.column_name_map.get(col, col)
            wrapped_text = "\n".join(wrap(raw_text, width=max_line_length))

            checkbox = ctk.CTkCheckBox(
                checkbox_scroll_frame,
                font=("Sans Sulex", int(rel_size * 1.1)),
                text=wrapped_text,
                variable=selected_columns[col],
                fg_color="#990404",
                hover_color="#540303",
                width=rel_size * 11
            )
            checkbox.pack(anchor="w", padx=int(rel_size // 3), pady=int(rel_size // 1.2))


      
        # 🔹 Funciones toggle y apply
        def toggle_filter_dropdown():
            padding_x = 0.015  # Márgenes horizontales (relativos)
            padding_y = 0.02   # Márgenes verticales (relativos)

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
            VO.visible_columns = visible if visible else columns[:]
            toggle_filter_dropdown()
            VO.abrir_VO(frame_right, clear_frame_right, app, mantener_filtro=True)
            

        filter_image = Image.open("resources/icons/white/ojoblanco.png").resize(icon_size)
        filter_image = ctk.CTkImage(light_image=filter_image)
        filter_button = ctk.CTkButton(search_frame, text="", image=filter_image, fg_color=btn_color,
                                    hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                    border_width=2, border_color="white",
                                    width=icon_size[0], height=icon_size[1],
                                    command=toggle_filter_dropdown)
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
                                command=lambda: VO.change_page(-1, frame_right, clear_frame_right, app))
        prev_btn.pack(side="left", padx=rel_size, pady=rel_size // 1.5)

        page_label = ctk.CTkLabel(nav_frame,
                                text=f"Página {VO.current_page} de {total_pages}",
                                font=("Sans Sulex", heading_font_size),
                                text_color="white")
        page_label.pack(side="left")

        next_image = Image.open("resources/icons/white/angle-small-right.png").resize(icon_size)
        next_image = ctk.CTkImage(light_image=next_image)
        next_btn = ctk.CTkButton(nav_frame, text="", image=next_image, fg_color=btn_color,
                                height=rel_size, width=rel_size,
                                hover_color=btn_hover, corner_radius=250,
                                border_width=1, border_color="white",
                                command=lambda: VO.change_page(1, frame_right, clear_frame_right, app))
        next_btn.pack(side="left", padx=rel_size, pady=rel_size/ 1.5)
        
        #Botones Agregar/Modificar/Borrar
        action_frame = ctk.CTkFrame(nav_frame, fg_color="#3d3d3d")
        action_frame.pack(side="right", padx=rel_size, pady=rel_size // 1.5)

        VistaVenta_image = Image.open("resources/icons/white/votacion.png").resize(icon_size)
        VistaVenta_image = ctk.CTkImage(light_image=VistaVenta_image)
        VistaVenta_btn = ctk.CTkButton(action_frame, text="Vista de venta", image=VistaVenta_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2), anchor="w",
                                border_width=1, border_color="white", command=lambda: VO.sell_inform(app))
        VistaVenta_btn.pack(side="left", padx=rel_size // 2)

        add_image = Image.open("resources/icons/white/agregar.png").resize(icon_size)
        add_image = ctk.CTkImage(light_image=add_image)
        add_btn = ctk.CTkButton(action_frame, text="Agregar VO", image=add_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2), anchor="w",
                                border_width=1, border_color="white", command=lambda: VO.add_VO(frame_right, clear_frame_right, app))
        add_btn.pack(side="left", padx=rel_size // 2)

        edit_image = Image.open("resources/icons/white/boli.png").resize(icon_size)
        edit_image = ctk.CTkImage(light_image=edit_image)
        edit_btn = ctk.CTkButton(action_frame, text="Modificar VO", image=edit_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                border_width=1, border_color="white", command=lambda: VO.edit_VO(VO.selected_VO, frame_right, clear_frame_right, app))
        edit_btn.pack(side="left", padx=rel_size // 2)

        delete_image = Image.open("resources/icons/white/trash.png").resize(icon_size)
        delete_image = ctk.CTkImage(light_image=delete_image)
        delete_btn = ctk.CTkButton(action_frame, text="Borrar VO", image=delete_image, fg_color=btn_color,
                                font=("Sans Sulex", heading_font_size),
                                hover_color=btn_hover, corner_radius=int(rel_size // 2),
                                border_width=1, border_color="white", command=lambda: VO.delete_VO(VO.selected_VO, frame_right, clear_frame_right, app))
        delete_btn.pack(side="left", padx=rel_size // 2)

        if VO.current_page == 1:
            prev_btn.configure(state="disabled")
        if VO.current_page == total_pages:
            next_btn.configure(state="disabled")

        # Estimar altura de fila para llenar el espacio
        altura_total_disponible = int(app.winfo_height() * 0.65)
        altura_filas = int(altura_total_disponible / VO.rows_per_page)

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


        tree = ttk.Treeview(tree_frame, columns=VO.visible_columns, show="headings", height=VO.rows_per_page)
        VO.tree = tree
        x_scrollbar = ttk.Scrollbar(tree_frame, orient="horizontal", command=tree.xview)
        tree.configure(xscrollcommand=x_scrollbar.set)
        x_scrollbar.pack(side="bottom", fill="x")
        
        tree.tag_configure('evenrow', background='#1a1a1a')  # Gris oscuro
        tree.tag_configure('oddrow', background='black')     # Negro

        from functools import partial

        for col in VO.visible_columns:
            tree.heading(
                col,
                text=VO.column_name_map.get(col, col),  # inicial, sin flecha
                anchor="center",
                command=partial(VO.sort_column_click, col, tree, frame_right, clear_frame_right, app)
            )
            tree.column(col, width=int(rel_size * 9), anchor="center", stretch=False)




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
            filtered_row = [row[columns.index(col)] for col in VO.visible_columns]
            
            # ➕ Formatea las fechas antes de mostrarlas
            for j, col in enumerate(VO.visible_columns):
                if "fecha" in col.lower() and isinstance(filtered_row[j], str):
                    filtered_row[j] = format_date(filtered_row[j])
            
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            tree.insert("", "end", values=filtered_row, tags=(tag,))
#----------------------------------------------------------------------------------------------------------------------------------------

            
        tree.pack(pady=rel_size // 1.5, fill="both", expand=True)

        tree.bind("<<TreeviewSelect>>", lambda event: VO.on_item_selected(tree))

        # ✅ MOSTRAR el frame principal una vez terminado
        main_container.place(relwidth=1.0, relheight=1.0)
        VO.refresh_treeview_headings(tree, frame_right, clear_frame_right, app)

    @staticmethod
    def search_data(query, search_column, frame_right, clear_frame_right, app):
        VO.query = query
        VO.search_column = search_column
        VO.Filtro = True
        VO.current_page = 1
        VO.load_data(frame_right, clear_frame_right, app)

    @staticmethod
    def load_data(frame_right, clear_frame_right, app):
        db_path = "bd/BDSellCars1.db"
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()

            offset = (VO.current_page - 1) * VO.rows_per_page

            # Construir cláusula ORDER BY si hay orden seleccionado
            order_clause = ""
            # Esto normaliza las letras con tilde (solo mayúsculas/minúsculas comunes en español)
            if VO.sort_column:
                direction = VO.sort_order if VO.sort_order in ("asc", "desc") else "asc"
                col = VO.sort_column
                col_normalized = (
                    f"REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(LOWER({col}), 'á', 'a'), 'é', 'e'), 'í', 'i'), 'ó', 'o'), 'ú', 'u'), 'Á', 'a'), 'É', 'e')"  # puedes expandir si quieres más letras
                )
                order_clause = f"ORDER BY {col_normalized} {direction}"
            else:
                order_clause = ""

            if VO.Filtro:
                if isinstance(VO.query_params, list):  # viene de search_plus
                    count_sql = f"SELECT COUNT(*) FROM VO WHERE {VO.query}"
                    cursor.execute(count_sql, VO.query_params)
                    total_rows = cursor.fetchone()[0]

                    select_sql = f"SELECT * FROM VO WHERE {VO.query} {order_clause} LIMIT ? OFFSET ?"
                    cursor.execute(select_sql, VO.query_params + [VO.rows_per_page, offset])
                else:  # viene de search_data
                    cursor.execute(f"SELECT COUNT(*) FROM VO WHERE {VO.search_column} LIKE ?", (f"{VO.query}%",))
                    total_rows = cursor.fetchone()[0]

                    cursor.execute(
                        f"SELECT * FROM VO WHERE {VO.search_column} LIKE ? {order_clause} LIMIT ? OFFSET ?",
                        (f"{VO.query}%", VO.rows_per_page, offset)
                    )
            else:
                cursor.execute("SELECT COUNT(*) FROM VO")
                total_rows = cursor.fetchone()[0]

                cursor.execute(f"SELECT * FROM VO {order_clause} LIMIT ? OFFSET ?", (VO.rows_per_page, offset))

            data = cursor.fetchall()
            conn.close()

            total_pages = max((total_rows // VO.rows_per_page) + (1 if total_rows % VO.rows_per_page > 0 else 0), 1)

            VO.create_table(
                VO.query,
                [
                    "matriculaVO", "numeroExpediente", "marca", "modelo", "version", "chasis",
                    "anomatriculacion", "FechaCompletaMatriculacion", "AntiguedadVO", "kilometros", "CC", "CV",
                    "colorExterno", "colorTapiceria", "N_puertas", "categoria", "emisionCO2", "tipoVO",
                    "capacidadDeposito", "TipoCombustible", "situacion", "DiasStock", "ubicacionStock",
                    "FechaDisponibleVenta", "PrecioVentaVO", "PrecioCompraVentaVO", "FechaRecogidaVO",
                    "DistintivoAmbiental", "FechaSalidaVO", "FechaTransferenciaCompleta", "FechaITVhasta",
                    "cifExpropietario", "FechaReservaVO"
                ],
                data,
                frame_right,
                app,
                clear_frame_right,
                total_pages,
                VO.Filtro
            )

        except sqlite3.Error as e:
            print("Error al cargar datos:", e)



    @staticmethod
    def clear_search(frame_right, clear_frame_right, app):
        VO.Filtro = False
        VO.query = ""
        VO.search_column = ""
        VO.current_page = 1
            
        VO.abrir_VO(frame_right, clear_frame_right, app)

    @staticmethod
    def change_page(direction, frame_right, clear_frame_right, app):
        VO.current_page += direction
        VO.load_data(frame_right, clear_frame_right, app)

    @staticmethod
    def abrir_VO(frame_right, clear_frame_right, app, mantener_filtro=False):
        if not mantener_filtro:
            VO.Filtro = False
            VO.query = ""
            VO.search_column = ""
            VO.current_page = 1

        VO.load_data(frame_right, clear_frame_right, app)

    @staticmethod
    def get_db_column_from_display_name(display_name):
        for db_col, disp_name in VO.column_name_map.items():
            if disp_name == display_name:
                return db_col
        return display_name  # fallback en caso de no encontrarlo

    @staticmethod
    def add_VO(frame_right, clear_frame_right, app):
        if VO.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        VO.ventana_abierta = True
        appAdd = ctk.CTk()
        VO.ventanas_secundarias.append(appAdd)

        if sys.platform == "win32":
            import ctypes
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            appAdd.iconbitmap(VO.icon_path)

        appAdd.title("Agregar VO")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

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

        titulo = ctk.CTkLabel(main_frame, text="Agregar VO", font=fuente_titulo, text_color="white")
        titulo.pack(pady=(int(window_height // 37),int(window_height // 37)))

        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=(int(window_height // 45)), pady=(int(window_height // 18.5)))

        opciones_tipo_vo = ["", "VO Garantía", "VO Ocasión", "KM 0", "Gerencia"]
        opciones_tipo_combustible = ["", "Gasolina", "Diésel", "Eléctrico", "Híbrido", "GLP", "GNC"]
        opciones_situacion = ["", "Disponible", "Reservado", "Vendido", "En trámite"]
        opciones_distintivo_ambiental = ["", "A", "B", "C", "ECO", "0"]

        campos = [
            "Matricula", "Nº Expediente", "Marca", "Modelo", "Versión", "Chasis",
            "Año Matriculación", "Fecha Matriculación", "Antigüedad", "Kilometros", "CC", "CV",
            "Color", "Tapiceria", "Nº Puertas", "Categoria", "Emisiones CO2", "Tipo VO",
            "Capacidad Deposito", "Tipo Combustible", "Situacion", "Dias en Stock", "Ubicacion Stock",
            "Fecha Disponible Venta", "Precio Venta", "Precio Compra-Venta", "Fecha Recogida",
            "Distintivo Ambiental", "Fecha Salida", "Fecha Transf Completa", "Fecha ITV Hasta",
            "DNI/CIF Expropietario", "Fecha Reserva"
        ]

        entradas = []

        for campo in campos:
            fila = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            fila.pack(fill="x", padx=int(window_height // 18.5), pady=int(window_height * 0.015))

            label = ctk.CTkLabel(fila, text=campo + ":", font=fuente_labels, width=160, anchor="w", text_color="white")
            label.pack(side="left", padx=int(window_height // 18.5))

            if campo == "Tipo VO":
                opciones = opciones_tipo_vo
                om = ctk.CTkOptionMenu(fila, values=opciones, button_color="#990404",
                                    button_hover_color="#540303", fg_color="#181818",
                                    dropdown_fg_color="#181818", font=fuente_labels,
                                    dropdown_font=fuente_labels)
                om.set(opciones[0])
                om.pack(side="left", fill="x", expand=True)
                entradas.append(om)

            elif campo == "Tipo Combustible":
                opciones = opciones_tipo_combustible
                om = ctk.CTkOptionMenu(fila, values=opciones, button_color="#990404",
                                    button_hover_color="#540303", fg_color="#181818",
                                    dropdown_fg_color="#181818", font=fuente_labels,
                                    dropdown_font=fuente_labels)
                om.set(opciones[0])
                om.pack(side="left", fill="x", expand=True)
                entradas.append(om)

            elif campo == "Situacion":
                opciones = opciones_situacion
                om = ctk.CTkOptionMenu(fila, values=opciones, button_color="#990404",
                                    button_hover_color="#540303", fg_color="#181818",
                                    dropdown_fg_color="#181818", font=fuente_labels,
                                    dropdown_font=fuente_labels)
                om.set(opciones[0])
                om.pack(side="left", fill="x", expand=True)
                entradas.append(om)

            elif campo == "Distintivo Ambiental":
                opciones = opciones_distintivo_ambiental
                om = ctk.CTkOptionMenu(fila, values=opciones, button_color="#990404",
                                    button_hover_color="#540303", fg_color="#181818",
                                    dropdown_fg_color="#181818", font=fuente_labels,
                                    dropdown_font=fuente_labels)
                om.set(opciones[0])
                om.pack(side="left", fill="x", expand=True)
                entradas.append(om)

            elif "Fecha" in campo:
                entry_fecha = ctk.CTkEntry(fila, placeholder_text="dd/mm/yyyy", font=fuente_labels,
                                        fg_color="#181818", text_color="white")
                entry_fecha.pack(side="left", fill="x", expand=True)
                entradas.append(entry_fecha)
                entry_fecha.bind("<FocusIn>", lambda event, e=entry_fecha: VO.on_focus_in_entry(e))
                entry_fecha.bind("<FocusOut>", lambda event, e=entry_fecha: VO.on_focus_out_entry(e))

            else:
                entry = ctk.CTkEntry(fila, placeholder_text=campo, font=fuente_labels,
                                    fg_color="#181818", text_color="white")
                entry.pack(side="left", fill="x", expand=True)
                entradas.append(entry)
                entry.bind("<FocusIn>", lambda event, e=entry: VO.on_focus_in_entry(e))
                entry.bind("<FocusOut>", lambda event, e=entry: VO.on_focus_out_entry(e))

                # Campo para seleccionar imagen
        fila_imagen = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        fila_imagen.pack(fill="x", padx=int(window_height // 18.5), pady=int(window_height * 0.015))

        label_imagen = ctk.CTkLabel(fila_imagen, text="Imagen:", font=fuente_labels, width=160, anchor="w", text_color="white")
        label_imagen.pack(side="left", padx=int(window_height // 18.5))

        entry_ruta = ctk.CTkEntry(fila_imagen, placeholder_text="Ruta de la imagen", font=fuente_labels,
                                fg_color="#181818", text_color="white")
        entry_ruta.pack(side="left", fill="x", expand=True, padx=5)
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

                carpeta_destino = "imagenesCoches"
                if not os.path.exists(carpeta_destino):
                    os.makedirs(carpeta_destino)

                # Borrar imagen anterior si existe
                ruta_anterior = entry_ruta.get().strip()
                if ruta_anterior and os.path.exists(ruta_anterior):
                    try:
                        os.remove(ruta_anterior)
                    except Exception as e:
                        messagebox.showwarning("Advertencia", f"No se pudo eliminar la imagen anterior:\n{e}", parent=appAdd)

                extension = os.path.splitext(ruta_origen)[1]
                nuevo_nombre = f"{nombre_usuario}{extension}"
                ruta_destino = os.path.join(carpeta_destino, nuevo_nombre)

                try:
                    shutil.copyfile(ruta_origen, ruta_destino)
                    entry_ruta.delete(0, "end")
                    entry_ruta.insert(0, ruta_destino)
                except Exception as e:
                    messagebox.showerror("Error al copiar imagen", str(e), parent=appAdd)

        boton_imagen = ctk.CTkButton(fila_imagen, text="Seleccionar Imagen", font=fuente_labels,
                                    command=seleccionar_archivo,
                                    fg_color="#990404", hover_color="#540303", border_color="black",
                                    border_width=2)
        boton_imagen.pack(side="right", padx=(5, int(window_height // 18.5)))

        campos.append("rutaImagen")

        def guardar_nuevo_VO():
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
                                parent=appAdd
                            )
                            return
                else:
                    valores.append(contenido)

            matricula = valores[0]
            if not matricula:
                messagebox.showerror("Error de Validación", "El campo 'Matrícula' no puede estar vacío.", parent=appAdd)
                return
            
            expediente = valores[1]
            if not expediente:
                messagebox.showerror("Error de Validación", "El campo 'Nº Expediente' no puede estar vacío.", parent=appAdd)
                return

            try:
                with sqlite3.connect("bd/BDSellCars1.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute(f"""
                        INSERT INTO VO (
                            matriculaVO, numeroExpediente, marca, modelo, version, chasis,
                            anomatriculacion, FechaCompletaMatriculacion, AntiguedadVO, kilometros, CC, CV,
                            colorExterno, colorTapiceria, N_puertas, categoria, emisionCO2, tipoVO,
                            capacidadDeposito, TipoCombustible, situacion, DiasStock, ubicacionStock,
                            FechaDisponibleVenta, PrecioVentaVO, PrecioCompraVentaVO, FechaRecogidaVO,
                            DistintivoAmbiental, FechaSalidaVO, FechaTransferenciaCompleta, FechaITVhasta,
                            cifExpropietario, FechaReservaVO, rutaImagen
                        ) VALUES ({','.join(['?'] * len(valores))})
                    """, tuple(valores))
                    conn.commit()
                    VO.clear_search(frame_right, clear_frame_right, app)
                    VO.ventana_abierta = False
                    appAdd.destroy()

            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error de Base de Datos", f"Error al insertar VO:\n{e}", parent=appAdd)

        boton_guardar = ctk.CTkButton(
            main_frame,
            text="Guardar VO",
            font=fuente_boton,
            fg_color="#990404",
            hover_color="#540303",
            border_width=2,
            border_color="black",
            corner_radius=10,
            height=int(window_height * 0.065),
            command=guardar_nuevo_VO
        )
        boton_guardar.pack(pady=int(window_height * 0.03))

        def on_closing():
            VO.ventana_abierta = False
            VO.ventanas_secundarias.remove(appAdd)
            appAdd.destroy()

        appAdd.protocol("WM_DELETE_WINDOW", on_closing)
        appAdd.bind("<Return>", lambda event: guardar_nuevo_VO())
        appAdd.mainloop()

    highlight_color = "#c91706"  # Color cuando se selecciona (borde)
    default_border_color = "#565b5e"  # Color del borde por defecto
    default_fg_color = "#181818"  # Color de fondo por defecto
    
    def on_focus_in_entry(entry):
        entry.configure(border_color=VO.highlight_color)
        entry.configure(fg_color="#181818")

    def on_focus_out_entry(entry):
        entry.configure(border_color=VO.default_border_color)
        entry.configure(fg_color=VO.default_fg_color)

    @staticmethod
    def edit_VO(matriculaVO, frame_right, clear_frame_right, app):
        if VO.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        VO.ventana_abierta = True

        icon_path = "resources/logos/icon_logo.ico"
        conn = sqlite3.connect("bd/BDSellCars1.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM VO WHERE matriculaVO = ?", (matriculaVO,))
        VhOc = cursor.fetchone()
        conn.close()

        if not VhOc:
            messagebox.showerror("Error", f"No hay un vehículo seleccionado")
            VO.ventana_abierta = False
            return

        appModify = ctk.CTk()
        VO.ventanas_secundarias.append(appModify)

        if sys.platform == "win32":
            import ctypes
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            appModify.iconbitmap(VO.icon_path)

        appModify.title("Editar VO")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        if icon_path and os.path.exists(icon_path):
            app.iconbitmap(icon_path)

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

        titulo = ctk.CTkLabel(main_frame, text="Editar VO", font=fuente_titulo, text_color="white")
        titulo.pack(pady=(int(window_height // 37), 37))

        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True, padx=int(window_height // 37), pady=int(window_height // 37))

        campos = [
            ("Matricula", VhOc[0]),
            ("Nº Expediente", VhOc[1]),
            ("Marca", VhOc[2]),
            ("Modelo", VhOc[3]),
            ("Versión", VhOc[4]),
            ("Chasis", VhOc[5]),
            ("Año Matriculación", VhOc[6]),
            ("Fecha Matriculación", VhOc[7]),
            ("Antigüedad", VhOc[8]),
            ("Kilometros", VhOc[9]),
            ("CC", VhOc[10]),
            ("CV", VhOc[11]),
            ("Color", VhOc[12]),
            ("Tapiceria", VhOc[13]),
            ("Nº Puertas", VhOc[14]),
            ("Categoria", VhOc[15]),
            ("Emisiones CO2", VhOc[16]),
            ("Tipo VO", VhOc[17]),
            ("Capacidad Deposito", VhOc[18]),
            ("Tipo Combustible", VhOc[19]),
            ("Situacion", VhOc[20]),
            ("Dias en Stock", VhOc[21]),
            ("Ubicacion Stock", VhOc[22]),
            ("Fecha Disponible Venta", VhOc[23]),
            ("Precio Venta", VhOc[24]),
            ("Precio Compra-Venta", VhOc[25]),
            ("Fecha Recogida", VhOc[26]),
            ("Distintivo Ambiental", VhOc[27]),
            ("Fecha Salida", VhOc[28]),
            ("Fecha Transf Completa", VhOc[29]),
            ("Fecha ITV Hasta", VhOc[30]),
            ("DNI/CIF Expropietario", VhOc[31]),
            ("Fecha Reserva", VhOc[32]),
            ("Ruta Imagen", VhOc[33])
        ]

        opciones_tipo_vo = ["", "VO Garantía", "VO Ocasión", "KM 0", "Gerencia"]
        opciones_tipo_combustible = ["", "Gasolina", "Diésel", "Eléctrico", "Híbrido", "GLP", "GNC"]
        opciones_situacion = ["", "Disponible", "Reservado", "Vendido", "En trámite"]
        opciones_distintivo_ambiental = ["", "A", "B", "C", "ECO", "0"]

        entradas = []

        for idx, (texto, valor) in enumerate(campos):
            fila = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            fila.pack(fill="x", padx=int(window_height // 18.5), pady=int(window_height * 0.015))

            label = ctk.CTkLabel(fila, text=texto + ":", font=fuente_labels, width=160, anchor="w", text_color="white")
            label.pack(side="left", padx=int(window_height // 18.5))

            # Selector especial para Ruta Imagen
            if texto == "Ruta Imagen":
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

                        carpeta_destino = "imagenesCoches"
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


            elif "Fecha" in texto:
                entry_fecha = ctk.CTkEntry(fila, placeholder_text="dd/mm/yyyy", font=fuente_labels,
                                        fg_color="#181818", text_color="white")
                if valor:
                    try:
                        fecha_convertida = datetime.strptime(valor.strip(), "%Y-%m-%d").strftime("%d/%m/%Y")
                        entry_fecha.insert(0, fecha_convertida)
                    except ValueError:
                        entry_fecha.insert(0, valor.strip())  # Si ya está en otro formato
                entry_fecha.pack(side="left", fill="x", expand=True)
                entradas.append(entry_fecha)

                entry_fecha.bind("<FocusIn>", lambda event, e=entry_fecha: VO.on_focus_in_entry(e))
                entry_fecha.bind("<FocusOut>", lambda event, e=entry_fecha: VO.on_focus_out_entry(e))

            else:
                opciones = None
                if texto == "Tipo VO":
                    opciones = opciones_tipo_vo
                elif texto == "Tipo Combustible":
                    opciones = opciones_tipo_combustible
                elif texto == "Situacion":
                    opciones = opciones_situacion
                elif texto == "Distintivo Ambiental":
                    opciones = opciones_distintivo_ambiental

                if opciones:
                    var = ctk.StringVar(value=valor if valor in opciones else opciones[0])
                    option_menu = ctk.CTkOptionMenu(fila, values=opciones, variable=var,
                                                    font=fuente_labels, fg_color="#181818",
                                                    button_color="#990404", button_hover_color="#540303",
                                                    text_color="white")
                    option_menu.pack(side="left", fill="x", expand=True)
                    entradas.append(var)
                else:
                    entry = ctk.CTkEntry(fila, placeholder_text=texto, font=fuente_labels,
                                        fg_color="#181818", text_color="white")
                    entry.insert(0, valor if valor is not None else "")
                    entry.pack(side="left", fill="x", expand=True)
                    entradas.append(entry)
                    entry.bind("<FocusIn>", lambda event, e=entry: VO.on_focus_in_entry(e))
                    entry.bind("<FocusOut>", lambda event, e=entry: VO.on_focus_out_entry(e))


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
            command=lambda: guardar_cambios(matriculaVO)
        )
        boton_guardar.pack(pady=int(window_height * 0.03))


        def guardar_cambios(matriculaVO):
            valores = []
            ruta_imagen = None  # Variable para guardar la ruta de la imagen

            for idx, entrada in enumerate(entradas):
                label = campos[idx][0].replace(" ", "").replace("º", "").replace("-", "")
                contenido = entrada.get().strip()

                # Validamos la ruta de la imagen solo si es el campo "Ruta Imagen"
                if campos[idx][0] == "Ruta Imagen":
                    ruta_imagen = contenido  # Guardamos el valor del campo de imagen

                    # Si la ruta no está vacía, verificamos si existe
                    if contenido:
                        if not os.path.exists(contenido):
                            messagebox.showerror("Error", f"La ruta de la imagen '{contenido}' no es válida.")
                            return  # Abortamos el guardado si la ruta no es válida

                # Resto de la validación para fechas y otros campos
                elif "Fecha" in campos[idx][0]:
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
                                parent=appModify
                            )
                            return
                else:
                    valores.append(contenido)

            matricula = valores[0].strip()
            numexp = valores[1].strip()

            if not matricula:
                messagebox.showerror("Error de Validación", "El campo 'Matricula' no puede estar vacío.", parent=appModify)
                return


            expediente = valores[1].strip()
            if not expediente:
                messagebox.showerror("Error de Validación", "El campo 'Nº Expediente' no puede estar vacío.", parent=appModify)
                return

            # Si la ruta de la imagen fue cambiada, la añadimos al final de la lista de valores
            if ruta_imagen is not None:
                valores.append(ruta_imagen)
            else:
                valores.append("")  # Si no se proporciona una ruta, dejamos la cadena vacía

            try:
                with sqlite3.connect("bd/BDSellCars1.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE VO SET matriculaVO = ?, numeroExpediente = ?, marca = ?, modelo = ?, version = ?,
                            chasis = ?, anomatriculacion = ?, FechaCompletaMatriculacion = ?, AntiguedadVO = ?, kilometros = ?, CC = ?, CV = ?,
                            colorExterno = ?, colorTapiceria = ?, N_puertas = ?, categoria = ?, emisionCO2 = ?, tipoVO = ?,
                            capacidadDeposito = ?, TipoCombustible = ?, situacion = ?, DiasStock = ?, ubicacionStock = ?,
                            FechaDisponibleVenta = ?, PrecioVentaVO = ?, PrecioCompraVentaVO = ?, FechaRecogidaVO = ?,
                            DistintivoAmbiental = ?, FechaSalidaVO = ?, FechaTransferenciaCompleta = ?, FechaITVhasta = ?, cifExpropietario = ?,
                            FechaReservaVO = ?, rutaImagen = ?
                        WHERE matriculaVO = ?;
                    """, (*valores, matriculaVO))  # Incluyendo la ruta de la imagen
                    conn.commit()

                VO.clear_search(frame_right, clear_frame_right, app)
                VO.ventana_abierta = False
                appModify.destroy()

            except sqlite3.IntegrityError as e:
                messagebox.showerror("Error", f"Ya existe un VO con la misma matrícula: '{matricula}' o el mismo Nº de Expediente: '{numexp}'", parent=appModify)

            except sqlite3.OperationalError as e:
                messagebox.showerror("Error de Base de Datos", f"Ocurrió un error al guardar los cambios:\n{e}")


        def on_closing():
            VO.ventana_abierta = False
            VO.ventanas_secundarias.remove(appModify)
            appModify.destroy()

        appModify.protocol("WM_DELETE_WINDOW", on_closing)
        appModify.bind("<Return>", lambda event: guardar_cambios(matriculaVO))
        appModify.mainloop()



    @staticmethod
    def on_item_selected(tree):
        selected_item = tree.selection()
        if selected_item:
            VO.selected_VO = tree.item(selected_item, "values")[0]
    

    @staticmethod
    def delete_VO(selected_VO, frame_right, clear_frame_right, app):
        if not selected_VO:
            messagebox.showwarning("Aviso", "Selecciona un VO para borrar.")
            return

        respuesta = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Estás seguro de que deseas borrar al VO con Matricula: {selected_VO}?"
        )

        if respuesta:
            try:
                # Primero obtenemos la ruta de la imagen asociada al VO
                with sqlite3.connect("bd/BDSellCars1.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT rutaImagen FROM VO WHERE matriculaVO = ?", (selected_VO,))
                    ruta_imagen = cursor.fetchone()

                # Si existe una ruta de imagen, la borramos
                if ruta_imagen and os.path.exists(ruta_imagen[0]):
                    try:
                        os.remove(ruta_imagen[0])  # Borramos la imagen
                    except Exception as e:
                        messagebox.showwarning("Advertencia", f"No se pudo eliminar la imagen del VO:\n{e}")

                # Ahora borramos el VO de la base de datos
                with sqlite3.connect("bd/BDSellCars1.db") as conn:
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM VO WHERE matriculaVO = ?", (selected_VO,))
                    conn.commit()

                messagebox.showinfo("Éxito", f"VO con Matricula {selected_VO} y su imagen eliminados correctamente.")
                VO.clear_search(frame_right, clear_frame_right, app)

            except sqlite3.OperationalError as e:
                messagebox.showerror("Error de Base de Datos", f"No se pudo eliminar el VO:\n{e}")
        else:
            # El usuario eligió "No", no se hace nada
            return

    
    @staticmethod
    def obtener_datos_filtrados(columnas_sql):
        conn = sqlite3.connect("bd/BDSellCars1.db")
        cursor = conn.cursor()

        if VO.Filtro:
            if isinstance(VO.query_params, list):
                # Búsqueda avanzada
                cursor.execute(
                    f"SELECT {columnas_sql} FROM VO WHERE {VO.query}",
                    VO.query_params
                )
            else:
                # Búsqueda simple
                cursor.execute(
                    f"SELECT {columnas_sql} FROM VO WHERE {VO.search_column} LIKE ?",
                    (f"{VO.query}%",)
                )
        else:
            # Sin filtros
            cursor.execute(f"SELECT {columnas_sql} FROM VO")

        datos = cursor.fetchall()
        conn.close()
        return datos

    @staticmethod
    def generate_inform(app):
        if VO.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        VO.ventana_abierta = True

        def confirmar_guardado(event=None):
            nombre_archivo = entrada_nombre.get().strip()

            if not nombre_archivo:
                messagebox.showerror("Error", "Debes introducir un nombre para el informe.", parent=ventana_nombre)
                return

            if not check_predefinido.get() and not check_personalizado.get() and not check_grafico.get():
                messagebox.showerror("Error", "Debes seleccionar un tipo de informe (predefinido o personalizado).", parent=ventana_nombre)
                return

            if check_predefinido.get() and check_personalizado.get() and check_grafico.get():
                messagebox.showerror("Error", "Solo puedes seleccionar una opción.", parent=ventana_nombre)
                return

            if not nombre_archivo.endswith(".pdf"):
                nombre_archivo += ".pdf"

            ruta = os.path.join("informes", "Vehiculos", nombre_archivo)
            os.makedirs(os.path.dirname(ruta), exist_ok=True)

            try:
                if check_predefinido.get():
                    columnas_fijas = [
                        "matriculaVO", "marca", "modelo", "version", "chasis",
                        "kilometros", "CV", "colorExterno", "DistintivoAmbiental",
                        "TipoCombustible", "PrecioVentaVO"
                    ]
                    columnas_sql = ", ".join(columnas_fijas)
                    datos = VO.obtener_datos_filtrados(columnas_sql)
                    paginas = [datos[i:i + VO.rows_per_page] for i in range(0, len(datos), VO.rows_per_page)]
                    VO.generar_informe_pdf_fijo(paginas, ruta)
                elif check_grafico.get():
                    VO.generar_grafico_pdf(ruta)


                elif check_personalizado.get():
                    columnas_visibles = VO.visible_columns
                    columnas_sql = ", ".join(columnas_visibles)
                    columnas_texto = [VO.column_name_map[col] for col in columnas_visibles]
                    datos = VO.obtener_datos_filtrados(columnas_sql)
                    paginas = [datos[i:i + VO.rows_per_page] for i in range(0, len(datos), VO.rows_per_page)]
                    VO.generar_informe_pdf(paginas, columnas_texto, ruta)
                

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
            VO.ventana_abierta = False
            ventana_nombre.destroy()

        def toggle_check(tipo):
            if tipo == "predef":
                if check_predefinido.get():
                    check_personalizado.deselect()
                    check_grafico.deselect()
            elif tipo == "personal":
                if check_personalizado.get():
                    check_predefinido.deselect()
                    check_grafico.deselect()
            elif tipo == "grafico":
                if check_grafico.get():
                    check_predefinido.deselect()
                    check_personalizado.deselect()


        screen_w = app.winfo_screenwidth()
        screen_h = app.winfo_screenheight()
        ref_w, ref_h = 1920, 1080
        escala_w, escala_h = screen_w / ref_w, screen_h / ref_h
        ancho_ventana = int(500 * escala_w)
        alto_ventana = int(350 * escala_h)

        fuente_titulo_size = max(14, int(28 * escala_h))
        fuente_label_size = max(10, int(18 * escala_h))
        fuente_boton_size = max(12, int(22 * escala_h))
        entry_width = int(300 * escala_w)

        x_pos = int((screen_w - ancho_ventana) / 2)
        y_pos = int((screen_h - alto_ventana) / 2)

        ventana_nombre = ctk.CTk()
        VO.ventanas_secundarias.append(ventana_nombre)

        ventana_nombre.title("Guardar Informe de Vehículos")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        ventana_nombre.geometry(f"{ancho_ventana}x{alto_ventana}+{x_pos}+{y_pos}")
        ventana_nombre.resizable(False, False)

        icon_path = "resources/images/oldIcon.ico"
        if sys.platform == "win32":
            import ctypes
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

        label_titulo = ctk.CTkLabel(frame_principal, text="Informe de Vehículos", font=fuente_titulo, text_color="white")
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

        check_grafico = ctk.CTkCheckBox(
            frame_checks,
            text="Informe Gráfico",
            font=fuente_label,
            text_color="white",
            fg_color="#990404",
            hover_color="#540303",
            command=lambda: toggle_check("grafico")
        )
        check_grafico.pack(anchor="w")


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
    def sell_inform(app):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import cm
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from datetime import datetime
        import os
        import sqlite3
        from tkinter import messagebox

        if VO.selected_VO is None:
            messagebox.showerror("Error", "No hay coche seleccionado. No se puede generar la ficha de venta.", parent=app)
            return

        matricula = VO.selected_VO
        ruta_pdf = os.path.abspath(f"informes/fichas/ficha_{matricula}.pdf")

        if os.path.exists(ruta_pdf):
            respuesta = messagebox.askyesno(
                "Ficha ya existente",
                "La ficha para este vehículo ya existe.\n¿Quieres sobrescribirla?",
                parent=app
            )
            if not respuesta:
                try:
                    os.startfile(ruta_pdf)
                except Exception as e:
                    messagebox.showwarning("Advertencia", f"No se pudo abrir el PDF existente:\n{e}", parent=app)
                return

        conn = sqlite3.connect("bd/BDSellCars1.db")
        cursor = conn.cursor()
        cursor.execute("""
            SELECT matriculaVO, numeroExpediente, marca, modelo, version, CV, CC,
                kilometros, PrecioVentaVO, DistintivoAmbiental, rutaImagen
            FROM VO WHERE matriculaVO = ?
        """, (matricula,))
        row = cursor.fetchone()
        conn.close()

        if not row:
            messagebox.showerror("Error", f"No se encontró el vehículo con matrícula {matricula}", parent=app)
            return

        (matricula, expediente, marca, modelo, version, cv, cc, km, precio, distintivo, ruta_imagen) = row
        ruta_imagen = ruta_imagen if ruta_imagen and os.path.exists(ruta_imagen) else "imagenesCoches/noImage.jpg"
        os.makedirs(os.path.dirname(ruta_pdf), exist_ok=True)

        try:
            font_path = "resources/font/sans-sulex/SANSSULEX.ttf"
            pdfmetrics.registerFont(TTFont("Sans Sulex", font_path))

            c = canvas.Canvas(ruta_pdf, pagesize=A4)
            width, height = A4
            margin = 2 * cm

            # Título
            c.setFont("Sans Sulex", 22)
            c.drawCentredString(width / 2, height - margin / 2, "FICHA DE VEHÍCULO")

            # Matrícula destacada con poco margen
            matricula_box_height = 1.2 * cm
            c.setFont("Sans Sulex", 14)
            c.rect(margin, height - margin - matricula_box_height, width - 2 * margin, matricula_box_height, stroke=1, fill=0)
            c.drawCentredString(width / 2, height - margin - 0.9 * cm, f"Matrícula: {matricula}")

            # Imagen respetando proporciones
            try:
                imagen = ImageReader(ruta_imagen)
                img_max_width = width - 4 * cm
                img_max_height = 7 * cm
                iw, ih = imagen.getSize()
                aspect = iw / ih

                if iw > ih:
                    draw_width = img_max_width
                    draw_height = draw_width / aspect
                    if draw_height > img_max_height:
                        draw_height = img_max_height
                        draw_width = draw_height * aspect
                else:
                    draw_height = img_max_height
                    draw_width = draw_height * aspect
                    if draw_width > img_max_width:
                        draw_width = img_max_width
                        draw_height = draw_width / aspect

                y_image = height - margin - matricula_box_height - 0.5 * cm - draw_height
                c.drawImage(
                    imagen,
                    (width - draw_width) / 2,
                    y_image,
                    width=draw_width,
                    height=draw_height,
                    preserveAspectRatio=True
                )
            except Exception as e:
                print(f"No se pudo cargar la imagen: {e}")
                y_image = height - margin - matricula_box_height - 0.5 * cm

            # Posición inicial para los datos debajo de la imagen
            y_pos = y_image - 1.2 * cm
            spacing = 1.05 * cm
            c.setFont("Sans Sulex", 12)

            datos = [
                f"Expediente: {expediente or '-'}",
                f"Marca: {marca or '-'}",
                f"Modelo: {modelo or '-'}",
                f"Versión: {version or '-'}",
                f"CV: {cv or '-'}",
                f"CC: {cc or '-'}",
                f"Kilómetros: {km or '-'} km",
                f"Distintivo Ambiental: {distintivo or 'No disponible'}",
                f"Precio: {precio or '-'} €",
            ]

            for dato in datos:
                if y_pos < 2.5 * cm:
                    c.showPage()
                    y_pos = height - margin
                    c.setFont("Sans Sulex", 12)
                c.drawString(margin, y_pos, dato)
                y_pos -= spacing

            # Pie de página con fecha
            fecha = datetime.now().strftime("%d/%m/%Y %H:%M")
            c.setFont("Sans Sulex", 9)
            c.drawRightString(width - margin, 1.5 * cm, f"Generado el {fecha}")

            c.save()
            os.startfile(ruta_pdf)

        except Exception as e:
            messagebox.showerror("Error al generar o abrir PDF", f"Ocurrió un error:\n{e}", parent=app)



    @staticmethod
    def generar_informe_pdf_fijo(paginas, ruta_salida="informe_VO.pdf"):
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import landscape, A4
        from reportlab.lib import colors
        from reportlab.lib.units import cm
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from textwrap import wrap
        from datetime import datetime
        from babel.dates import format_datetime

        columnas = [
            "Matrícula",
            "Marca",
            "Modelo",
            "Versión",
            "Chasis",
            "Kilometros",
            "CV",
            "Color"
        ]

        pesos = {
            "Matrícula": 0.8,
            "Marca": 1,
            "Modelo": 1,
            "Versión": 1,
            "Chasis": 1.2,
            "Kilometros": 1,
            "CV": 0.8,
            "Color": 1
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
                logo_width = 4 * cm  # Ancho del logo
                logo_height = (orig_height / orig_width) * logo_width  # Calcular la altura proporcional
                x_logo = width - logo_width - 1 * cm  # Alinear el logo a la derecha con un margen de 1 cm
                y_logo = height - 1 * cm  # Mantener la misma posición vertical

                c.drawImage(logo, x_logo, y_logo - logo_height + 0.5 * cm, width=logo_width, height=logo_height, mask='auto')
            except Exception as e:
                print(f"Error cargando logo: {e}")

            # Ajustar espacio entre el logo y el título
            y -= 2 * cm

            # Dibujar el título
            c.setFont("Sans Sulex", 14)
            c.setFillColor(colors.black)
            c.drawString(1 * cm, y, "LISTADO DE VEHÍCULOS (VO)")

            y -= 1.4 * cm

            # Encabezado
            c.setFillColorRGB(0.27, 0.27, 0.27)
            c.rect(1 * cm - 0.1 * cm, y - 0.1 * cm, width - total_padding + 0.2 * cm, altura_encabezado, fill=True, stroke=False)
            c.setFillColor(colors.white)
            c.setFont("Sans Sulex", font_size + 1)

            col_x = 1 * cm
            for idx, col in enumerate(columnas):
                c.drawString(col_x, y + altura_encabezado / 2 - font_size / 2.5, col)
                col_x += espacio_col[idx]

            y -= altura_encabezado

            # Filas
            c.setFont("Sans Sulex", font_size)
            for fila_idx, fila in enumerate(datos_pagina):
                if not isinstance(fila, (list, tuple)):
                    fila = [str(fila)]

                fila = list(fila) + [''] * (len(columnas) - len(fila))  # Rellenar si falta algo
                fila = fila[:len(columnas)]  # Cortar si hay de más

                c.setFillColor(colors.whitesmoke if fila_idx % 2 == 0 else colors.lightgrey)
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
    def generar_grafico_pdf(ruta):
        import sqlite3
        import matplotlib.pyplot as plt
        from matplotlib import font_manager
        from fpdf import FPDF
        from datetime import datetime

        # ─── 1. Registrar la fuente personalizada ───
        font_path = "resources/font/sans-sulex/SANSSULEX.ttf"
        prop = font_manager.FontProperties(fname=font_path)
        plt.rcParams['font.family'] = prop.get_name()

        # ─── 2. Obtener datos ───
        conn = sqlite3.connect("bd/BDSellCars1.db")
        cursor = conn.cursor()

        cursor.execute("""
            SELECT LOWER(marca) AS marca_normalizada, COUNT(*) 
            FROM VO 
            WHERE LOWER(situacion) = 'disponible' 
            GROUP BY marca_normalizada
        """)
        resultados = cursor.fetchall()
        conn.close()

        if not resultados:
            raise ValueError("No hay datos disponibles para la situación 'Disponible'.")

        labels = [marca.capitalize() for marca, _ in resultados]
        sizes = [cantidad for _, cantidad in resultados]

        fig, ax = plt.subplots(figsize=(9, 6))

        def mostrar_cantidad(pct, allvals):
            total = sum(allvals)
            valor = int(round(pct * total / 100.0))
            return f'{valor}'

        wedges, texts, autotexts = ax.pie(
            sizes,
            autopct=lambda pct: mostrar_cantidad(pct, sizes),
            startangle=140
        )

        ax.legend(
            wedges,
            labels,
            title="Marcas",
            loc="center left",
            bbox_to_anchor=(1, 0.5),
            prop=prop
        )

        plt.tight_layout()

        imagen_path = "grafico_marcas.png"
        plt.savefig(imagen_path, bbox_inches='tight', dpi=300)
        plt.close()

        # ─── 3. Crear el PDF ───
        pdf = FPDF()
        pdf.add_page()

        pdf.add_font("SansSulex", "", font_path, uni=True)
        pdf.set_font("SansSulex", size=14)

        # Logo a la izquierda arriba
        pdf.image("resources/logos/hgcnegro.png", x=10, y=10, w=30)

        # Título más abajo
        pdf.set_y(35)
        pdf.cell(0, 10, "Gráfico de Marcas con Vehículos Disponibles", ln=True, align="C")

        # Imagen del gráfico (tamaño original restaurado)
        pdf.image(imagen_path, x=10, y=50, w=190)

        # Calcular Y después del gráfico (usando una altura estimada para la imagen)
        altura_estimacion = 135  # Aproximación del alto en mm
        y_pos_despues_imagen = 125 + altura_estimacion + 5

        # Fecha y hora debajo del gráfico
        now = datetime.now()
        fecha_hora = now.strftime("%d/%m/%Y %H:%M:%S")

        pdf.set_font("SansSulex", size=10)
        pdf.set_xy(10, y_pos_despues_imagen)
        pdf.cell(0, 10, f"Fecha de creación: {fecha_hora}", ln=True, align="L")

        pdf.output(ruta)
    
    @staticmethod
    def search_plus(frame_right, clear_frame_right, app):
        
        if VO.ventana_abierta:
            messagebox.showerror(
                "Ventana ya abierta",
                "Ya hay una ventana abierta. Ciérrala antes de abrir otra.",
                parent=app
            )
            return

        VO.ventana_abierta = True  # Marcamos la ventana como abierta
        
        
        # -------------------------------------
        # PRE-CÁLCULOS PARA EVITAR REPETICIÓN
        # -------------------------------------
        total_width = app.winfo_width()
        rel_size = total_width / 100  # si lo usas en otra parte, se mantiene

        monitors = screeninfo.get_monitors()
        main_monitor = next((m for m in monitors if m.is_primary), monitors[0])
        window_width = int(main_monitor.width * 0.55)
        window_height = int(main_monitor.height * 0.70)
        x_position = (main_monitor.width - window_width) // 2
        y_position = (main_monitor.height - window_height) // 2
        padding_relativo = int(window_height * 0.02)

        fuente_labels = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.022))
        fuente_boton = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.03))
        fuente_titulo = ctk.CTkFont(family="Sans Sulex", size=int(window_height * 0.045))


        # -------------------------------------
        # CREACIÓN DE LA VENTANA SECUNDARIA
        # -------------------------------------
        app_sp = ctk.CTk()
        VO.ventanas_secundarias.append(app_sp)
        
        if sys.platform == "win32":
            import ctypes
            myappid = "mycompany.myapp.sellcars.1.0"
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
            app_sp.iconbitmap(VO.icon_path)

        app_sp.title("Buscar VO")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        icon_path = "resources/logos/icon_logo.ico"
        if icon_path and os.path.exists(icon_path):
            app_sp.iconbitmap(icon_path)

        app_sp.geometry(f"{int(window_width*1.5)}x{int(window_height*1.2)}+{int(x_position*0.4)}+{int(y_position*0.4)}")
        app_sp.resizable(True,True)


        # -------------------------------------
        # FRAME PRINCIPAL
        # -------------------------------------
        main_frame = ctk.CTkFrame(app_sp, fg_color="#373737", corner_radius=0)
        main_frame.pack(pady=padding_relativo, padx=padding_relativo, fill="both", expand=True)

        titulo = ctk.CTkLabel(main_frame, text="Buscar VO", font=fuente_titulo, text_color="white")
        titulo.pack(pady=(int(window_height * 0.03), int(window_height * 0.015)))


        # -------------------------------------
        # FRAME CONTENIDO SCROLLABLE
        # -------------------------------------
        contenido_frame = ctk.CTkFrame(
            main_frame,
            fg_color="transparent",     
            width=window_width - 2*padding_relativo,
            height=int(window_height * 0.6)
        )
        contenido_frame.pack(expand=True, fill="both", padx=padding_relativo)
        

        # -------------------------------------
        # CAMPOS DE TEXTO
        # -------------------------------------
        campos_nombres = [
            "Matricula","Nº Expediente","Marca","Modelo","Versión","Chasis",
            "Color","Tapiceria","Nº Puertas","Categoria","Ubicacion Stock","DNI/CIF Expropietario"
        ]

        entradas = {}
        columnas_por_fila = 4
        fila_actual = ctk.CTkFrame(contenido_frame, fg_color="transparent")
        fila_actual.pack(pady=int(window_height * 0.01))

        for count, texto in enumerate(campos_nombres):
            if count and count % columnas_por_fila == 0:
                fila_actual = ctk.CTkFrame(contenido_frame, fg_color="transparent")
                fila_actual.pack(pady=int(window_height * 0.01))

            campo = ctk.CTkEntry(
                fila_actual,
                placeholder_text=texto,
                font=fuente_labels,
                fg_color="#181818",
                text_color="white",
                width=int(window_width * 0.27),
                height=int(window_width * 0.045)
            )
            campo.pack(side="left", padx=int(window_width * 0.01))
            entradas[texto] = campo
            
            # Bindings una sola vez
            campo.bind("<FocusIn>", lambda event, e=campo: VO.on_focus_in_entry(e))
            campo.bind("<FocusOut>", lambda event, e=campo: VO.on_focus_out_entry(e))


        # -------------------------------------
        # BLOQUES ESPECIALES
        # -------------------------------------
        opciones_tipo_vo = ["", "VO Garantía", "VO Ocasión", "KM 0", "Gerencia"]
        opciones_tipo_combustible = ["", "Gasolina", "Diésel", "Eléctrico", "Híbrido", "GLP", "GNC"]
        opciones_situacion = ["", "Disponible", "Reservado", "Vendido", "En trámite"]
        opciones_distintivo_ambiental = ["", "A", "B", "C", "ECO", "0"]

        bloques_especiales = [
            [("Antigüedad", "num"), ("Fecha Disponible Venta", "fecha"),("Kilometros", "num"), ("Fecha Transf Completa", "fecha")],
            [("Fecha Reserva", "fecha"), ("Fecha Salida", "fecha"),("Fecha Matriculación", "fecha"), ("Año Matriculación", "num")],
            [("CC", "num"), ("CV", "num"),("Emisiones CO2", "num"),("Capacidad Deposito", "num")],
            [("Dias en Stock", "num"), ("Precio Venta", "num"),("Precio Compra-Venta", "num"), ("Fecha ITV Hasta", "fecha")],
            [("Situacion", ctk.CTkOptionMenu, opciones_situacion), ("Tipo Combustible", ctk.CTkOptionMenu, opciones_tipo_combustible),("Tipo VO", ctk.CTkOptionMenu, opciones_tipo_vo), ("Distintivo Ambiental", ctk.CTkOptionMenu, opciones_distintivo_ambiental),]
        ]

        operadores_fecha = {"=": "=", "<": "<=", ">": ">="}
        condiciones_fecha = {}
        condiciones_num = {}

        especiales_frame = ctk.CTkFrame(contenido_frame, fg_color="transparent")
        especiales_frame.pack(pady=int(window_height * 0.01))

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

        def buscar():
            import sqlite3

            datos = {k: v.get().strip() for k, v in entradas.items()}
            print("Datos recogidos:", datos)

            db_path = "bd/BDSellCars1.db"

            try:
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()

                condiciones = []
                valores = []

                campos_db = {
                    "Matricula": "matriculaVO",
                    "Nº Expediente": "numeroExpediente",
                    "Marca": "marca",
                    "Modelo": "modelo",
                    "Versión": "version",
                    "Chasis": "chasis",
                    "Año Matriculación": "anomatriculacion",
                    "Fecha Matriculación": "FechaCompletaMatriculacion",
                    "Antigüedad": "AntiguedadVO",
                    "Kilometros": "kilometros",
                    "CC": "CC",
                    "CV": "CV",
                    "Color": "colorExterno",
                    "Tapiceria": "colorTapiceria",
                    "Nº Puertas": "N_puertas",
                    "Categoria": "categoria",
                    "Emisiones CO2": "emisionCO2",
                    "Tipo VO": "tipoVO",
                    "Capacidad Deposito": "capacidadDeposito",
                    "Tipo Combustible": "TipoCombustible",
                    "Situacion": "situacion",
                    "Dias en Stock": "DiasStock",
                    "Ubicacion Stock": "ubicacionStock",
                    "Fecha Disponible Venta": "FechaDisponibleVenta",
                    "Precio Venta": "PrecioVentaVO",
                    "Precio Compra-Venta": "PrecioCompraVentaVO",
                    "Fecha Recogida": "FechaRecogidaVO",
                    "Distintivo Ambiental": "DistintivoAmbiental",
                    "Fecha Salida": "FechaSalidaVO",
                    "Fecha Transf Completa": "FechaTransferenciaCompleta",
                    "Fecha ITV Hasta": "FechaITVhasta",
                    "DNI/CIF Expropietario": "cifExpropietario",
                    "Fecha Reserva": "FechaReservaVO"
                }


                for campo_ui, valor in datos.items():
                    if valor:
                        if campo_ui in condiciones_fecha:
                            operador_ui = condiciones_fecha[campo_ui].get()  # =, < o >
                            operador_sql = operadores_fecha.get(operador_ui, "=")  # =, <=, >=

                            try:
                                fecha_obj = datetime.strptime(valor, "%d/%m/%Y")
                                valor_sql = fecha_obj.strftime("%Y-%m-%d")
                            except ValueError:
                                valor_sql = valor

                            condiciones.append(f"{campos_db[campo_ui]} {operador_sql} ? AND {campos_db[campo_ui]} > '1800-01-01'")

                            valores.append(valor_sql)

                        elif campo_ui in condiciones_num:
                            operador_ui = condiciones_num[campo_ui].get()  # =, < o >
                            operador_sql = operadores_fecha.get(operador_ui, "=")  # =, <=, >=

                            condiciones.append(f"{campos_db[campo_ui]} {operador_sql} ? AND {campos_db[campo_ui]} < 9999999")
                            valor_sql=valor
                            valores.append(valor_sql)

                        else:
                            condiciones.append(f"{campos_db[campo_ui]} LIKE ?")
                            valores.append(f"{valor}%")

                where_clause = " AND ".join(condiciones) if condiciones else "1"

                VO.current_page = 1
                cursor.execute(f"SELECT COUNT(*) FROM VO WHERE {where_clause}", valores)
                total_rows = cursor.fetchone()[0]

                if total_rows == 0:
                    messagebox.showinfo(
                        "Sin Resultados",
                        "No se encontró ningún VO que cumpla con todos los criterios indicados.",
                        parent=app_sp
                    )
                    conn.close()
                    return

                total_pages = max((total_rows // VO.rows_per_page) + (1 if total_rows % VO.rows_per_page > 0 else 0), 1)
                offset = (VO.current_page - 1) * VO.rows_per_page

                cursor.execute(
                    f"SELECT * FROM VO WHERE {where_clause} LIMIT ? OFFSET ?",
                    valores + [VO.rows_per_page, offset]
                )
                data = cursor.fetchall()

                conn.close()

                VO.Filtro = bool(condiciones)
                VO.query = where_clause
                VO.query_params = valores
                VO.ventana_abierta = False
                VO.create_table(
                    VO.query,
                            [
                                "matriculaVO","numeroExpediente","marca","modelo","version","chasis",
                                "anomatriculacion","FechaCompletaMatriculacion","AntiguedadVO","kilometros","CC","CV",
                                "colorExterno","colorTapiceria","N_puertas","categoria","emisionCO2","tipoVO","capacidadDeposito","TipoCombustible",
                                "situacion","DiasStock","ubicacionStock","FechaDisponibleVenta","PrecioVentaVO","PrecioCompraVentaVO",
                                "FechaRecogidaVO","DistintivoAmbiental","FechaSalidaVO","FechaTransferenciaCompleta","FechaITVhasta","cifExpropietario","FechaReservaVO"
                            ],
                    data,
                    frame_right,
                    app,
                    clear_frame_right,
                    total_pages,
                    VO.Filtro
                )

                app_sp.destroy()

            except sqlite3.Error as e:
                print("Error al buscar VO:", e)

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
        
        def on_closing():
            VO.ventana_abierta = False
            VO.ventanas_secundarias.remove(app_sp)
            app_sp.destroy()

        boton_buscar.pack(pady=int(window_height * 0.03))
        app_sp.protocol("WM_DELETE_WINDOW", on_closing)
        app_sp.bind("<Return>", lambda event: buscar())

        app_sp.mainloop()

    
    @staticmethod
    def sort_by_column(column, frame_right, clear_frame_right, app):
        if VO.sort_column == column:
            VO.sort_ascending = not VO.sort_ascending
        else:
            VO.sort_column = column
            VO.sort_ascending = True

        VO.current_page = 1
        VO.load_data(frame_right, clear_frame_right, app)

    @staticmethod
    def update_sort_state(column):
        # Quitar estado de todas las columnas excepto la actual
        for col in VO.visible_columns:
            if col != column:
                VO.sort_states[col] = None

        current = VO.sort_states.get(column)

        if current == "asc":
            VO.sort_states[column] = "desc"
        elif current == "desc":
            VO.sort_states[column] = None
        else:
            VO.sort_states[column] = "asc"

        # Actualizar columna y orden actuales
        VO.sort_column = column if VO.sort_states[column] else None
        VO.sort_order = VO.sort_states[column] or ""



    @staticmethod
    def refresh_treeview_headings(tree, frame_right, clear_frame_right, app):
        from functools import partial

        for col in VO.visible_columns:
            sort_state = VO.sort_states.get(col)
            base_text = VO.column_name_map.get(col, col)

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
                command=partial(VO.sort_column_click, col, tree, frame_right, clear_frame_right, app)
        )


    @staticmethod
    def sort_column_click(col, tree, frame_right, clear_frame_right, app):
        VO.update_sort_state(col)
        VO.refresh_treeview_headings(tree, frame_right, clear_frame_right, app)  # ← aquí
        VO.load_data(frame_right, clear_frame_right, app)



