import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import tkinter.filedialog as fd
from PIL import Image, ImageTk
import pandas as pd
import mysql.connector
from sqlalchemy import create_engine
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge, Circle
import matplotlib.patches as mpatches
from datetime import datetime
import math
import numpy as np
import os
import json
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# ------------------------------
# CONFIGURACIÓN DE CONEXIÓN
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "1234",
    "database": "mi_base"
}

# Engine de SQLAlchemy para pandas
DB_ENGINE = create_engine(
    f"mysql+pymysql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@"
    f"{DB_CONFIG['host']}/{DB_CONFIG['database']}",
    pool_pre_ping=True,
    pool_recycle=3600
)
# ------------------------------
#fiscalizaciones1: OF (solo aqui cambia la tipografia del encabezado)
#fiscalizaciones2: OFR (Recaudación)
#fiscalizaciones3: AIs
#fiscalizaciones4: DTR (Detracciones OF)
#mypes:mypes (2 mill para cruce)
#fiscalizaciones5: AIR (Recaudación)
ultima_actualizacion = "Sin datos"
CONFIG_FILE = "config.json"

# ==========================
# PALETA DE COLORES
# ==========================
COLOR_PRIMARY = "#1E3A8A"      # Azul oscuro
COLOR_SECONDARY = "#4A90E2"    # Azul acento
COLOR_DANGER = "#DC2626"       # Rojo elegante
COLOR_GRAY_BG = "#F9FAFB"      # Fondo gris claro
COLOR_PANEL = "#E5E7EB"        # Panel lateral
COLOR_TEXT = "#111827"         # Texto oscuro
COLOR_BOX = "#E5E7EB"          # Caja gris clara para agrupación
COLOR_SUBBOX = "#F9FAFB"       # Caja más clara para fecha actualización
COLOR_WHITE = "#FFFFFF"        # Caja blanca para datos

# ==========================
# CONFIGURACIÓN JSON
# ==========================
def cargar_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def guardar_config():
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

config = cargar_config()

# ==========================
# INTERFAZ PRINCIPAL (CREACIÓN DE VENTANA)
# ==========================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

app = ctk.CTk()
app.title("Sistema de Reportes")
app.configure(fg_color=COLOR_GRAY_BG)

# ---- ENCABEZADO SUPERIOR ----
header = ctk.CTkFrame(app, fg_color="#feffff", height=100)
header.pack(fill="x")

# Logo (evita NameError en mostrar_logo)
logo_label = tk.Label(header, bg="#feffff", text="")
logo_label.pack(side="left", padx=8, pady=8)

# Banner principal
banner_label = tk.Label(header, bg="#feffff")
banner_label.pack(side="left", fill="both", expand=True)

header_modulo = ctk.CTkFrame(app, fg_color="#feffff", height=100)
banner_label_modulo = tk.Label(header_modulo, bg="#feffff")
banner_label_modulo.pack(fill="both", expand=True)

# ==========================
# FUNCIONES LOGO Y BANNERS (sin cambios)
# ==========================
def mostrar_logo(ruta):
    try:
        if ruta and os.path.exists(ruta):
            img = Image.open(ruta).resize((120, 60))
            logo_img = ImageTk.PhotoImage(img)
            logo_label.configure(image=logo_img, text="")
            logo_label.image = logo_img
    except Exception as e:
        print("Error al mostrar logo:", e)

def subir_logo():
    ruta = fd.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
    if ruta:
        config["logo_path"] = ruta
        guardar_config()
        mostrar_logo(ruta)

def mostrar_banner(ruta):
    try:
        if ruta and os.path.exists(ruta):
            img = Image.open(ruta).resize((1600, 100))
            banner_img = ImageTk.PhotoImage(img)
            banner_label.configure(image=banner_img, text="")
            banner_label.image = banner_img
    except Exception as e:
        print("Error al mostrar banner:", e)

def subir_banner():
    ruta = fd.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
    if ruta:
        config["banner_path"] = ruta
        guardar_config()
        mostrar_banner(ruta)

def mostrar_banner_modulo(ruta):
    try:
        if ruta and os.path.exists(ruta):
            img = Image.open(ruta).resize((1600, 150))
            banner_img = ImageTk.PhotoImage(img)
            banner_label_modulo.configure(image=banner_img, text="")
            banner_label_modulo.image = banner_img
    except Exception as e:
        print("Error al mostrar banner modulo:", e)

def subir_banner_modulo():
    ruta = fd.askopenfilename(filetypes=[("Imágenes", "*.png;*.jpg;*.jpeg")])
    if ruta:
        config["banner_modulo_path"] = ruta
        guardar_config()
        mostrar_banner_modulo(ruta)

def mostrar_banner_supervisores(ruta):
    try:
        if ruta and os.path.exists(ruta):
            img = Image.open(ruta).resize((1600, 150))
            banner_img = ImageTk.PhotoImage(img)
            banner_label_modulo.configure(image=banner_img, text="")
            banner_label_modulo.image = banner_img
    except Exception as e:
        print("Error al mostrar banner supervisores:", e)

# ==========================
# PANTALLAS / FRAMES PRINCIPALES
# ==========================
frame_inicio = ctk.CTkFrame(app, fg_color=COLOR_GRAY_BG)
frame_inicio.pack(fill="both", expand=True)

frame_modulo = ctk.CTkFrame(app, fg_color="white")

menu_visible = True

# --- Toggle sidebar ---
toggle_frame = ctk.CTkFrame(frame_modulo, fg_color=COLOR_PANEL, width=20)
toggle_frame.pack(side="left", fill="y")

toggle_button = ctk.CTkButton(
    toggle_frame, text="<", width=20,
    fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
    command=lambda: toggle_menu()
)
toggle_button.pack(pady=10)

menu_frame = ctk.CTkFrame(frame_modulo, fg_color=COLOR_PANEL, width=220)
menu_frame.pack(side="left", fill="y", padx=0, pady=0)

ctk.CTkLabel(menu_frame, text="Menú", font=("Segoe UI", 16, "bold"), text_color=COLOR_TEXT).pack(pady=15)

ctk.CTkButton(menu_frame, text="Resumen", width=200,
              fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
              command=lambda: mostrar_dashboard_completo()).pack(pady=5)

ctk.CTkButton(menu_frame, text="Metas", width=200,
              fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
              command=lambda: mostrar_dashboard_metas()).pack(pady=5)

ctk.CTkButton(menu_frame, text="Resultados de OF para Supervisores", width=200,
              fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
              command=lambda: dashboard_supervisores()).pack(pady=5)

ctk.CTkButton(menu_frame, text="Resultados de Acciones Inductivas", width=200,
              fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
              command=lambda: dashboard_acciones_inductivas()).pack(pady=5)
              
ctk.CTkButton(menu_frame, text="Control saldo Detracciones", width=200,
              fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
              command=lambda: dashboard_control_detracciones()).pack(pady=5)

def pedir_password():
    pw = ctk.CTkInputDialog(text="Ingrese la contraseña:", title="Protegido").get_input()
    if pw == "1234":
        subir_excel()
    else:
        messagebox.showerror("Acceso denegado", "Contraseña incorrecta")

ctk.CTkButton(menu_frame, text="📂Subir Excel", command=pedir_password, width=200,
              fg_color="#6B7280", hover_color="#4B5563").pack(pady=5)

# --- Panel derecho ---
right_frame = ctk.CTkFrame(frame_modulo, fg_color=COLOR_BOX)
right_frame.pack(side="left", fill="both", expand=True, padx=10, pady=10)

preview_frame = ctk.CTkFrame(right_frame, fg_color=COLOR_WHITE, corner_radius=10)
preview_frame.pack(fill="both", expand=True, padx=10, pady=(5,10))

dashboard_frame = ctk.CTkFrame(right_frame, fg_color=COLOR_WHITE, corner_radius=10)
dashboard_frame.pack_forget()  # inicialmente oculto

# --- preview content ---
fecha_frame = ctk.CTkFrame(preview_frame, fg_color=COLOR_SUBBOX, corner_radius=10)
fecha_frame.pack(fill="x", pady=(10,5), padx=10)

barra_label = ctk.CTkLabel(fecha_frame, text="Última actualización: Sin datos",
                           font=("Segoe UI", 14), text_color=COLOR_TEXT)
barra_label.pack(padx=10, pady=10)

table_frame = ctk.CTkFrame(preview_frame, fg_color=COLOR_WHITE, corner_radius=10)
table_frame.pack(fill="both", expand=True, padx=10, pady=(5,10))

columns = ("NUM_ORD_FI", "DDP_NOMBRE", "Anio_Emis", "Estado")
tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)

for col in columns:
    tree.heading(col, text=col)
    tree.column(col, anchor="center", width=150)

tree.pack(fill="both", expand=True, padx=10, pady=10)

# ==========================
# FUNCIONES PRINCIPALES (sin cambios)
# ==========================
def limpiar_valor(columna, valor):
    if valor in ["NA", "S/R", None, ""]:
        return None
    if columna == "Porc_PARTIC_MTO_RIESGO":
        if isinstance(valor, str) and "%" in valor:
            try:
                return round(float(valor.replace("%", "")) / 100, 2)
            except:
                return None
        try:
            return round(float(valor), 2)
        except:
            return None
    if "FEC" in columna.upper() or "FECHA" in columna.upper():
        try:
            fecha = pd.to_datetime(valor, errors="coerce")
            return fecha.strftime("%Y-%m-%d") if pd.notna(fecha) else None
        except:
            return None
    if columna.upper().startswith("MTO_") or columna.upper().startswith("MONTO") or columna.upper().startswith("DIAS"):
        try:
            return float(valor)
        except:
            return None
    return valor

def subir_excel():
    global ultima_actualizacion
    ruta = fd.askopenfilename(filetypes=[("Excel files", "*.xlsx")])
    if not ruta:
        return

    try:
        # Leer el archivo Excel con todas las hojas
        excel_file = pd.ExcelFile(ruta)
        hoja = excel_file.sheet_names[0].strip().upper()  # Obtener el nombre de la primera hoja

        # Seleccionar la hoja
        df = pd.read_excel(ruta, sheet_name=hoja, header=None)
        df = df.iloc[1:]  # Omitir la primera fila (encabezado)
        df = df.where(pd.notnull(df), None)

        # Determinar la tabla y columnas según el nombre de la hoja
        if hoja == "OF":
            tabla = "fiscalizaciones1"
            columnas = [
                "NUM_ORD_FI","NUM_DOCSEL","DDP_NOMBRE","COD_PROGFI","COD_TIPACT",
                "COD_GRP_TR","COD_METODO","FEC_EMISIO","FEC_NOTIFI","FEC_TERMIN",
                "MTO_PAG_IN","MTO_PAG_RE","MTO_VAL_DE","MTO_VAL_CR","Rendimiento_dia",
                "COD_REG_ES","NUM_CARGA","Des_eta_of","des_est_of","dias_asignados",
                "dias_empleados","Exceso","Resultado_dias","REG_AUDITOR","NOMBRE_AUDITOR",
                "Categoria_Auditor","REG_SUPERVISOR","NOMBRE_SUPERVISOR","des_cod",
                "Tipo_Fiscalizacion","SISCOR","REQUERIMIENTO_INICIAL","FEC_VENC",
                "Ult_requerimiento","Fec_ini_ult_req","Dias_ult_req","Estado",
                "Anio_Emis","Mes_Emis","Anio_Termino","Mes_termino","Periodos_Revisados",
                "Denuncia","Centralizada","Cant_AF_ESSALUD","MTG","Exp_Electronico",
                "SIP_05","MTO_SIP_05","Monto_Comp2_SIP05","Porc_Rend_Incons_SIP05",
                "Porc_PARTIC_MTO_RIESGO","Stock_AUD_25","Componente_PNC_R12_2024",
                "Monto_PNC_R12_2024","Stock_AUD_25_Tot","Rendimiento_OF"
            ]

        elif hoja == "OFR":
            tabla = "fiscalizaciones2"
            columnas = [
                "NUM_ORD_FI","COD_TIPIDE","NUM_DOCSEL","IND_TIP_DE","IND_TIP_IN",
                "COD_FOR","NUM_DOC","COD_TRI","PER_DOC","FEC_DOC","MTO_PAG",
                "MTO_REC_OR","MTO_REC_RE","IND_EST_IN","COD_REG_AC","FEC_ACT","MES",
                "des_func","num_bol","bol_ing_rec","reimputado","des_ai","mes_registro",
                "RID","fec_notificacion","periodo","corriente"
            ]

        elif hoja == "AI":
            tabla = "fiscalizaciones3"
            columnas = ["COD_ACC_IN","COD_PROGFI","COD_GRP_TR","IND_EST_AC","NUM_ACC_IN","NUM_DOCSEL",
                "FEC_TER","FEC_NOT","IND_EST_RE","COD_METODO","NUM_CARGA","FEC_GEN","COD_VER","COD_SUP",
                "COD_REG_ES","FLG_PASE_F","MES","DES_NOMB_VER","DES_NOMB_SUP","DES_NOMB_PROG","DES_TIPO_AI",
                "Estado","Anio_Emis","Mes_Emis","Anio_Termino","Mes_termino","Periodos_Revisados","Pago_AI","Rect_AI",
                "Total","Dias","Fec_limite","FCJMMS","ESSALUD","SIP_05","MTO_SIP_05","Monto_Comp3_SIP05","Porc_Rend_Incons_SIP05"
            ]
            
        elif hoja == "DTR":
            tabla = "fiscalizaciones4"
            columnas = ["cod_cta","cod_periodo","fec_saldo","num_ruc","nom_ruc","num_cargos","mto_cargos","num_abonos",
                "mto_abonos","ind_signo","mto_saldo","fec_hor_act","cod_dep"
            ]
        elif hoja == "AIR":
            tabla = "fiscalizaciones5"
            columnas = ["NUM_ACC_IN","COD_TIPIDE","NUM_DOCSEL","IND_TIP_IN","COD_FOR","NUM_DOC","COD_TRI",
                "PER_DOC","FEC_PRE_DO","MTO_PAG_IN","MTO_REC_OR","MTO_REC_IN","COD_REG_VE","FEC_ACT",
                "MTO_FRA_IN","MES","nomb_ver","des_ai","num_boleta","rec_mep", "reimputado","tipo_ai","RID","mes_registro",
                "fec_notificacion","periodo","corriente"
            ]

        elif hoja == "MYPE":
            tabla = "mypes"
            columnas = ["ruc"]  # Solo una columna en la tabla
            
            # Extraer columnas A y B (índices 0 y 1)
            columna_a = df.iloc[:, 0].dropna().tolist()  # Columna A
            columna_b = df.iloc[:, 1].dropna().tolist()  # Columna B
            
            # Combinar ambas columnas en una sola lista
            todos_rucs = columna_a + columna_b
            
            # Crear un nuevo DataFrame con todos los RUCs
            df = pd.DataFrame({'ruc': todos_rucs})
            
            # CONVERTIR A TIPOS DE PYTHON NATIVOS
            df['ruc'] = df['ruc'].astype(str)  # Convertir a string
            # O si prefieres mantenerlos como enteros:
            # df['ruc'] = df['ruc'].astype(object)
            
            df = df.where(pd.notnull(df), None)

        else:
            messagebox.showerror("Hoja desconocida", f"La hoja '{hoja}' no coincide con OF, OFR, AI, DTR ni MYPE.")
            return

        # Conexión a la base de datos
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Generar parte dinámica del UPDATE
        columnas_update = [f"{col}=VALUES({col})" for col in columnas if col != "NUM_ORD_FI"]

        sql = f"""
            INSERT INTO {tabla} ({', '.join(columnas)})
            VALUES ({', '.join(['%s'] * len(columnas))})
            ON DUPLICATE KEY UPDATE {', '.join(columnas_update)}
        """

        insertados = 0
        actualizados = 0

        for _, row in df.iterrows():
            valores = [limpiar_valor(col, row[i]) for i, col in enumerate(columnas)]
            try:
                cursor.execute(sql, tuple(valores))
                if cursor.rowcount == 2:
                    actualizados += 1
                else:
                    insertados += 1
            except mysql.connector.Error as err:
                print(f"Error en NUM_ORD_FI={valores[0]} -> {err.msg}")

        conn.commit()
        conn.close()

        ultima_actualizacion = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        actualizar_barra()
        mostrar_datos()

        messagebox.showinfo(
            "Carga completa",
            f"📄 Hoja detectada: {hoja}\n📂 Tabla destino: {tabla}\n\n✅ Insertados: {insertados}\n🔁 Actualizados: {actualizados}\n📅 Total: {len(df)}"
        )

    except mysql.connector.Error as err:
        messagebox.showerror("Error MySQL", f"Código: {err.errno}\nDetalle: {err.msg}")
    except Exception as e:
        messagebox.showerror("Error inesperado", str(e))

def ver_reportes():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql("SELECT Anio_Emis, COUNT(*) AS cantidad FROM fiscalizaciones1 GROUP BY Anio_Emis", DB_ENGINE)
        conn.close()

        plt.bar(df["Anio_Emis"], df["cantidad"])
        plt.title("Cantidad de registros por Año de Emisión")
        plt.xlabel("Año")
        plt.ylabel("Cantidad")
        plt.show()
    except Exception as e:
        messagebox.showerror("Error ver reportes", str(e))

# ==========================
# TABLAS RECREADAS para RESULTADOS DE OF PARA SUPERVISORES
# ==========================
MESES = {
    1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
    5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
    9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
}

def get_conexion():
    return mysql.connector.connect(**DB_CONFIG)

def ejecutar_read_sql(query, conexion=None):
    """Ejecuta consultas SQL con pandas usando SQLAlchemy"""
    return pd.read_sql(query, DB_ENGINE)

# ------------------------------
# Generar tabla asignadas
def ajustar_altura_treeview(tree, total_filas, max_filas=25):
    """
    Ajusta dinámicamente la altura del Treeview según el número de filas.
    Si total_filas <= max_filas, se muestra todo sin scroll.
    Si total_filas > max_filas, se fija en max_filas y se usa el scrollbar.
    """
    if total_filas <= max_filas:
        tree.config(height=total_filas)
    else:
        tree.config(height=max_filas)


def generar_tabla_asignadas(parent_frame, conexion=None, anio=None):
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=10)

    ctk.CTkLabel(filtro_frame,
                 text="📅 Selecciona Año:",
                 font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=10)

    combo_anio = ttk.Combobox(filtro_frame, state="readonly", width=12, font=("Segoe UI", 11))
    combo_anio.pack(side="left", padx=5)

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=12)

    # Variable para almacenar los datos actuales
    datos_actuales = {
        "df_completo": None,
        "tabla_formateada": None,
        "año_filtrado": None
    }

    try:
        años_df = ejecutar_read_sql(
            "SELECT DISTINCT Anio_Emis FROM fiscalizaciones1 WHERE Anio_Emis IS NOT NULL ORDER BY Anio_Emis DESC;",
            conexion
        )
        años = [int(x) for x in años_df["Anio_Emis"].tolist()] if not años_df.empty else []
    except Exception as e:
        ctk.CTkLabel(tabla_frame, text=f"⚠ Error cargando años: {e}", text_color="red").pack(pady=15)
        return

    default_year = anio if (anio is not None and anio in años) else (2025 if 2025 in años else (max(años) if años else 2025))
    combo_anio["values"] = años if años else [default_year]
    combo_anio.set(default_year)

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            año_sel = datos_actuales["año_filtrado"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"OF_Asignadas_{año_sel}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:
                return

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_tabla(anio_sel):
        try:
            anio_num = int(str(anio_sel).strip())
        except (ValueError, TypeError, AttributeError):
            print(f"Error: anio_sel no es válido: {anio_sel}, tipo: {type(anio_sel)}")
            anio_num = 2025

        # Guardar año filtrado
        datos_actuales["año_filtrado"] = anio_num

        for w in tabla_frame.winfo_children():
            w.destroy()

        # Consulta completa
        query_completo = f"""
            SELECT * FROM fiscalizaciones1
            WHERE Anio_Emis = {anio_num}
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%';
        """

        query = f"""
            SELECT 
                NOMBRE_SUPERVISOR, 
                Tipo_Fiscalizacion, 
                Mes_Emis, 
                Anio_Emis, 
                des_cod, 
                NUM_ORD_FI
            FROM fiscalizaciones1
            WHERE Anio_Emis = {anio_num}
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%';
        """

        try:
            df = ejecutar_read_sql(query, conexion)
            df_completo = ejecutar_read_sql(query_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            ctk.CTkLabel(tabla_frame, text=f"⚠ No hay datos para {anio_sel}", text_color="red").pack(pady=15)
            return

        df["Mes_Emis"] = df["Mes_Emis"].astype(int)
        pivot = pd.pivot_table(
            df,
            index=["NOMBRE_SUPERVISOR", "Tipo_Fiscalizacion"],
            columns="Mes_Emis",
            values="NUM_ORD_FI",
            aggfunc="count",
            fill_value=0
        )
        meses_numeros = list(range(1, 13))
        pivot = pivot.reindex(columns=meses_numeros, fill_value=0)
        pivot["Total"] = pivot.sum(axis=1)
        total_general = pivot.sum(axis=0)
        rename_map = {m: MESES[m] for m in meses_numeros}
        pivot.rename(columns=rename_map, inplace=True)
        meses_cols = [MESES[m] for m in meses_numeros]
        pivot_reset = pivot.reset_index()

        # Crear tabla formateada para exportación
        tabla_formateada_rows = []
        
        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "Tipo_Fiscalizacion"]).sum(axis=0)
            
            row_sup = {"Supervisor": supervisor, "Tipo Fiscalización": ""}
            for m in meses_cols:
                row_sup[m] = int(subtotal.get(m, 0))
            row_sup["Total"] = int(subtotal.get("Total", 0))
            tabla_formateada_rows.append(row_sup)
            
            for _, row in df_sup.iterrows():
                row_tipo = {"Supervisor": "", "Tipo Fiscalización": row["Tipo_Fiscalizacion"]}
                for m in meses_cols:
                    row_tipo[m] = int(row.get(m, 0))
                row_tipo["Total"] = int(row.get("Total", 0))
                tabla_formateada_rows.append(row_tipo)
        
        row_total = {"Supervisor": "TOTAL GENERAL", "Tipo Fiscalización": ""}
        for m in meses_numeros:
            row_total[MESES[m]] = int(total_general.get(m, 0))
        row_total["Total"] = int(total_general.get("Total", 0))
        tabla_formateada_rows.append(row_total)
        
        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        frame_tabla_inner = ctk.CTkFrame(tabla_frame, corner_radius=15, fg_color="#ffffff")
        frame_tabla_inner.pack(fill="both", expand=True, padx=10, pady=8)

        ctk.CTkLabel(frame_tabla_inner,
                     text=f"📊 OF ASIGNADAS - {anio_sel}",
                     font=("Segoe UI", 14, "bold"),
                     text_color="#a51c30").pack(anchor="w", padx=12, pady=6)

        container = ctk.CTkFrame(frame_tabla_inner, fg_color="white")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        cols = ["NOMBRE_SUPERVISOR", "Tipo_Fiscalizacion"] + meses_cols + ["Total"]
        tree_local = ttk.Treeview(container, columns=cols, show="headings")

        vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
        tree_local.configure(yscrollcommand=vsb.set)

        tree_local.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for col in cols:
            if col == "NOMBRE_SUPERVISOR":
                text, width = "Supervisor", 220
            elif col == "Tipo_Fiscalizacion":
                text, width = "Tipo Fiscalización", 180
            elif col == "Total":
                text, width = "Total", 90
            else:
                text, width = col, 65
            tree_local.heading(col, text=text)
            tree_local.column(col, width=width, anchor="center")

        total_filas = 0

        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "Tipo_Fiscalizacion"]).sum(axis=0)
            parent_vals = [supervisor, ""] + [int(subtotal.get(m, 0)) for m in meses_cols] + [int(subtotal.get("Total", 0))]
            parent = tree_local.insert("", "end", values=parent_vals, tags=("supervisor",))
            total_filas += 1

            for _, row in df_sup.iterrows():
                child_vals = ["", row["Tipo_Fiscalizacion"]] + [int(row.get(m, 0)) for m in meses_cols] + [int(row.get("Total", 0))]
                tree_local.insert(parent, "end", values=child_vals, tags=("tipo",))
                total_filas += 1

        total_vals = ["TOTAL GENERAL", ""] + [int(total_general.get(m, 0)) for m in meses_numeros] + [int(total_general.get("Total", 0))]
        tree_local.insert("", "end", values=total_vals, tags=("total",))
        total_filas += 1

        ajustar_altura_treeview(tree_local, total_filas)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree_local.tag_configure("supervisor", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree_local.tag_configure("tipo", background="white", font=("Segoe UI", 10))
        tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

    combo_anio.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(int(combo_anio.get()) if combo_anio.get() else default_year))
    cargar_tabla(int(combo_anio.get()) if combo_anio.get() else default_year)
# ------------------------------
# Generar tabla OF DETERMINATIVAS - TERMINADOS

def generar_tabla_determinadas(parent_frame, conexion=None, cod_tipact_default="06", anio_default=2025):
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=5)

    ctk.CTkLabel(filtro_frame,
                 text="🔎 Selecciona COD_TIPACT:",
                 font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=10)
    combo_tipact = ttk.Combobox(filtro_frame, state="readonly", width=10, font=("Segoe UI", 11))
    combo_tipact.pack(side="left", padx=5)

    ctk.CTkLabel(filtro_frame,
                 text="📅 Selecciona Año:",
                 font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=10)
    combo_anio = ttk.Combobox(filtro_frame, state="readonly", width=10, font=("Segoe UI", 11))
    combo_anio.pack(side="left", padx=5)

    # ✅ Botón de Promedio
    btn_promedio = ctk.CTkButton(
        filtro_frame,
        text="📊 Calcular Promedio",
        font=("Segoe UI", 12, "bold"),
        fg_color="#1e88e5",
        hover_color="#1565c0",
        width=160,
        height=32,
        corner_radius=8
    )
    btn_promedio.pack(side="left", padx=15)

    # ✅ Frame para mostrar el promedio al costado
    promedio_frame = ctk.CTkFrame(filtro_frame, corner_radius=8, fg_color="#e3f2fd", width=180, height=32)
    promedio_frame.pack(side="left", padx=5)
    promedio_frame.pack_propagate(False)

    promedio_label = ctk.CTkLabel(
        promedio_frame,
        text="Promedio: --",
        font=("Segoe UI", 12, "bold"),
        text_color="#1565c0"
    )
    promedio_label.pack(expand=True)

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=10)

    # Variable para almacenar el tree actual y datos
    tree_actual = {"tree": None, "pivot_reset": None, "meses_cols": None}
    
    datos_actuales = {
        "df_completo": None,
        "tabla_formateada": None,
        "cod_tipact_filtrado": None,
        "año_filtrado": None
    }

    try:
        tipact_df = ejecutar_read_sql("SELECT DISTINCT COD_TIPACT FROM fiscalizaciones1 WHERE COD_TIPACT IS NOT NULL;", conexion)
        tipacts = sorted(tipact_df["COD_TIPACT"].astype(str).tolist()) if not tipact_df.empty else []

        try:
            cod_default_str = str(cod_tipact_default).zfill(2)
        except Exception:
            cod_default_str = str(cod_tipact_default)

        combo_tipact["values"] = ["06"]
        combo_tipact.set("06" if "06" in combo_tipact["values"] else (cod_default_str if cod_default_str in combo_tipact["values"] else (tipacts[0] if tipacts else cod_default_str)))

        años_df = ejecutar_read_sql("SELECT DISTINCT Anio_Termino FROM fiscalizaciones1 WHERE Anio_Termino IS NOT NULL ORDER BY Anio_Termino DESC;", conexion)
        años = [int(x) for x in años_df["Anio_Termino"].tolist()] if not años_df.empty else []
        combo_anio["values"] = años if años else [anio_default]
        combo_anio.set(anio_default if anio_default in años else (max(años) if años else anio_default))
    except Exception as e:
        ctk.CTkLabel(tabla_frame, text=f"⚠ Error cargando filtros: {e}", text_color="red").pack(pady=15)
        return

    def calcular_y_colorear_promedio():
        """Calcula el promedio, lo muestra y colorea las filas automáticamente"""
        if tree_actual["tree"] is None or tree_actual["pivot_reset"] is None:
            promedio_label.configure(text="⚠ Sin datos")
            return

        tree = tree_actual["tree"]
        pivot_reset = tree_actual["pivot_reset"]
        
        total_general = pivot_reset["Total"].sum()
        num_auditores = len(pivot_reset)
        
        if num_auditores == 0:
            promedio_label.configure(text="⚠ Sin auditores")
            return
        
        promedio = round(total_general / num_auditores)
        promedio_label.configure(text=f"Promedio: {promedio}")
        
        for item in tree.get_children():
            valores = tree.item(item, "values")
            
            if tree.parent(item) == "":
                if valores[0] == "TOTAL GENERAL":
                    continue
                
                for child in tree.get_children(item):
                    child_valores = tree.item(child, "values")
                    if child_valores[1]:
                        total_auditor = int(child_valores[-1]) if child_valores[-1] else 0
                        
                        if total_auditor > promedio:
                            tree.item(child, tags=("supera",))
                        elif total_auditor < promedio:
                            tree.item(child, tags=("no_cumple",))
                        else:
                            tree.item(child, tags=("tipo",))
        
        tree.tag_configure("supera", background="#c8e6c9", font=("Segoe UI", 10, "bold"))
        tree.tag_configure("no_cumple", background="#ffcdd2", font=("Segoe UI", 10))

    btn_promedio.configure(command=calcular_y_colorear_promedio)

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            cod_sel = datos_actuales["cod_tipact_filtrado"]
            año_sel = datos_actuales["año_filtrado"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"OF_Determinativas_Terminados_{cod_sel}_{año_sel}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:
                return

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_tabla(cod_tipact_sel, anio_sel):
        try:
            anio_num = int(str(anio_sel).strip())
        except (ValueError, TypeError, AttributeError):
            print(f"Error: anio_sel no es válido: {anio_sel}, tipo: {type(anio_sel)}")
            anio_num = 2025

        # Guardar filtros aplicados
        datos_actuales["cod_tipact_filtrado"] = cod_tipact_sel
        datos_actuales["año_filtrado"] = anio_num

        for w in tabla_frame.winfo_children():
            w.destroy()

        promedio_label.configure(text="Promedio: --")

        # Consulta completa
        query_completo = f"""
            SELECT * FROM fiscalizaciones1
            WHERE COD_TIPACT = '{cod_tipact_sel}'
              AND Anio_Termino = {anio_num}
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%';
        """

        query = f"""
            SELECT 
                NOMBRE_SUPERVISOR, 
                NOMBRE_AUDITOR, 
                Mes_termino, 
                NUM_ORD_FI
            FROM fiscalizaciones1
            WHERE COD_TIPACT = '{cod_tipact_sel}'
              AND Anio_Termino = {anio_num}
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%';
        """

        try:
            df = ejecutar_read_sql(query, conexion)
            df_completo = ejecutar_read_sql(query_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            ctk.CTkLabel(tabla_frame, text=f"⚠ No hay datos para {cod_tipact_sel} - {anio_sel}", text_color="red").pack(pady=15)
            return

        df["Mes_termino"] = df["Mes_termino"].astype(int)
        pivot = pd.pivot_table(
            df,
            index=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"],
            columns="Mes_termino",
            values="NUM_ORD_FI",
            aggfunc="count",
            fill_value=0
        )

        meses_numeros = list(range(1, 13))
        pivot = pivot.reindex(columns=meses_numeros, fill_value=0)
        pivot["Total"] = pivot.sum(axis=1)
        total_general = pivot.sum(axis=0)

        rename_map = {m: MESES[m] for m in meses_numeros}
        pivot.rename(columns=rename_map, inplace=True)
        meses_cols = [MESES[m] for m in meses_numeros]
        pivot_reset = pivot.reset_index()

        # Crear tabla formateada para exportación
        tabla_formateada_rows = []
        
        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]).sum(axis=0)
            
            row_sup = {"Supervisor": supervisor, "Auditor": ""}
            for m in meses_cols:
                row_sup[m] = int(subtotal.get(m, 0))
            row_sup["Total"] = int(subtotal.get("Total", 0))
            tabla_formateada_rows.append(row_sup)
            
            for _, row in df_sup.iterrows():
                row_aud = {"Supervisor": "", "Auditor": row["NOMBRE_AUDITOR"]}
                for m in meses_cols:
                    row_aud[m] = int(row.get(m, 0))
                row_aud["Total"] = int(row.get("Total", 0))
                tabla_formateada_rows.append(row_aud)
        
        row_total = {"Supervisor": "TOTAL GENERAL", "Auditor": ""}
        for m in meses_numeros:
            row_total[MESES[m]] = int(total_general.get(m, 0))
        row_total["Total"] = int(total_general.get("Total", 0))
        tabla_formateada_rows.append(row_total)
        
        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        frame_tabla_inner = ctk.CTkFrame(tabla_frame, corner_radius=15, fg_color="#ffffff")
        frame_tabla_inner.pack(fill="both", expand=True, padx=10, pady=8)

        ctk.CTkLabel(frame_tabla_inner,
                     text=f"📊 OF DETERMINATIVAS - TERMINADOS ({anio_sel})",
                     font=("Segoe UI", 14, "bold"),
                     text_color="#a51c30").pack(anchor="w", padx=12, pady=6)

        container = ctk.CTkFrame(frame_tabla_inner, fg_color="white")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        cols = ["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"] + meses_cols + ["Total"]
        tree_local = ttk.Treeview(container, columns=cols, show="headings")

        vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
        tree_local.configure(yscrollcommand=vsb.set)

        tree_local.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for col in cols:
            if col == "NOMBRE_SUPERVISOR":
                text, width = "Supervisor", 220
            elif col == "NOMBRE_AUDITOR":
                text, width = "Nombre del auditor", 180
            elif col == "Total":
                text, width = "Total", 90
            else:
                text, width = col, 65
            tree_local.heading(col, text=text)
            tree_local.column(col, width=width, anchor="center")

        total_filas = 0

        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]).sum(axis=0)
            parent_vals = [supervisor, ""] + [int(subtotal.get(m, 0)) for m in meses_cols] + [int(subtotal.get("Total", 0))]
            parent = tree_local.insert("", "end", values=parent_vals, tags=("supervisor",))
            total_filas += 1

            for _, row in df_sup.iterrows():
                child_vals = ["", row["NOMBRE_AUDITOR"]] + [int(row.get(m, 0)) for m in meses_cols] + [int(row.get("Total", 0))]
                tree_local.insert(parent, "end", values=child_vals, tags=("tipo",))
                total_filas += 1

        total_vals = ["TOTAL GENERAL", ""] + [int(total_general.get(m, 0)) for m in meses_numeros] + [int(total_general.get("Total", 0))]
        tree_local.insert("", "end", values=total_vals, tags=("total",))
        total_filas += 1

        ajustar_altura_treeview(tree_local, total_filas)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree_local.tag_configure("supervisor", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree_local.tag_configure("tipo", background="white", font=("Segoe UI", 10))
        tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

        tree_actual["tree"] = tree_local
        tree_actual["pivot_reset"] = pivot_reset
        tree_actual["meses_cols"] = meses_cols

    combo_tipact.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_tipact.get(), int(combo_anio.get()) if combo_anio.get() else anio_default))
    combo_anio.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_tipact.get(), int(combo_anio.get()) if combo_anio.get() else anio_default))

    inicio_cod = combo_tipact.get() if combo_tipact.get() else "06"
    inicio_anio = int(combo_anio.get()) if combo_anio.get() else anio_default
    cargar_tabla(inicio_cod, inicio_anio)

# OF NO DETERMINATIVAS-TERMINADOS
#---------------------------------------
def generar_tabla_no_determinativas(parent_frame, conexion=None, anio_default=2025):
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=5)

    # Label y ComboBox COD_TIPACT
    ctk.CTkLabel(filtro_frame,
                 text="🔎 Selecciona COD_TIPACT:",
                 font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=10)

    combo_tipact = ttk.Combobox(filtro_frame, state="readonly", width=16, font=("Segoe UI", 11))
    combo_tipact.pack(side="left", padx=5)

    # Label y ComboBox Año
    ctk.CTkLabel(filtro_frame,
                 text="📅 Selecciona Año:",
                 font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=10)

    combo_anio = ttk.Combobox(filtro_frame, state="readonly", width=10, font=("Segoe UI", 11))
    combo_anio.pack(side="left", padx=5)

    # ✅ Botón de Promedio
    btn_promedio = ctk.CTkButton(
        filtro_frame,
        text="📊 Calcular Promedio",
        font=("Segoe UI", 12, "bold"),
        fg_color="#1e88e5",
        hover_color="#1565c0",
        width=160,
        height=32,
        corner_radius=8
    )
    btn_promedio.pack(side="left", padx=15)

    # ✅ Frame para mostrar el promedio al costado
    promedio_frame = ctk.CTkFrame(filtro_frame, corner_radius=8, fg_color="#e3f2fd", width=180, height=32)
    promedio_frame.pack(side="left", padx=5)
    promedio_frame.pack_propagate(False)

    promedio_label = ctk.CTkLabel(
        promedio_frame,
        text="Promedio: --",
        font=("Segoe UI", 12, "bold"),
        text_color="#1565c0"
    )
    promedio_label.pack(expand=True)

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=10)

    # Variable para almacenar el tree actual y datos
    tree_actual = {"tree": None, "pivot_reset": None, "meses_cols": None}
    
    datos_actuales = {
        "df_completo": None,
        "tabla_formateada": None,
        "cod_tipact_filtrado": None,
        "año_filtrado": None
    }

    try:
        # Opciones permitidas
        codigos_permitidos = ["03", "07", "08"]
        combo_tipact["values"] = ["Todos (03,07,08)"] + codigos_permitidos
        combo_tipact.set("Todos (03,07,08)")  # al inicio se selecciona todos

        # Años disponibles
        años_df = ejecutar_read_sql("SELECT DISTINCT Anio_Termino FROM fiscalizaciones1 "
                                    "WHERE Anio_Termino IS NOT NULL ORDER BY Anio_Termino DESC;", conexion)
        años = [int(x) for x in años_df["Anio_Termino"].tolist()] if not años_df.empty else []
        combo_anio["values"] = años if años else [anio_default]
        combo_anio.set(anio_default if anio_default in años else (max(años) if años else anio_default))
    except Exception as e:
        ctk.CTkLabel(tabla_frame, text=f"⚠ Error cargando filtros: {e}", text_color="red").pack(pady=15)
        return

    def calcular_y_colorear_promedio():
        """Calcula el promedio, lo muestra y colorea las filas automáticamente"""
        if tree_actual["tree"] is None or tree_actual["pivot_reset"] is None:
            promedio_label.configure(text="⚠ Sin datos")
            return

        tree = tree_actual["tree"]
        pivot_reset = tree_actual["pivot_reset"]
        
        total_general = pivot_reset["Total"].sum()
        num_auditores = len(pivot_reset)
        
        if num_auditores == 0:
            promedio_label.configure(text="⚠ Sin auditores")
            return
        
        promedio = round(total_general / num_auditores)
        promedio_label.configure(text=f"Promedio: {promedio}")
        
        for item in tree.get_children():
            valores = tree.item(item, "values")
            
            if tree.parent(item) == "":
                if valores[0] == "TOTAL GENERAL":
                    continue
                
                for child in tree.get_children(item):
                    child_valores = tree.item(child, "values")
                    if child_valores[1]:
                        total_auditor = int(child_valores[-1]) if child_valores[-1] else 0
                        
                        if total_auditor > promedio:
                            tree.item(child, tags=("supera",))
                        elif total_auditor < promedio:
                            tree.item(child, tags=("no_cumple",))
                        else:
                            tree.item(child, tags=("tipo",))
        
        tree.tag_configure("supera", background="#c8e6c9", font=("Segoe UI", 10, "bold"))
        tree.tag_configure("no_cumple", background="#ffcdd2", font=("Segoe UI", 10))

    btn_promedio.configure(command=calcular_y_colorear_promedio)

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            cod_sel = datos_actuales["cod_tipact_filtrado"]
            año_sel = datos_actuales["año_filtrado"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"OF_No_Determinativas_Terminados_{cod_sel}_{año_sel}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:
                return

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_tabla(cod_tipact_sel, anio_sel):
        try:
            anio_num = int(str(anio_sel).strip())
        except (ValueError, TypeError, AttributeError):
            print(f"Error: anio_sel no es válido: {anio_sel}, tipo: {type(anio_sel)}")
            anio_num = 2025

        # Guardar filtros aplicados
        datos_actuales["cod_tipact_filtrado"] = cod_tipact_sel
        datos_actuales["año_filtrado"] = anio_num

        for w in tabla_frame.winfo_children():
            w.destroy()

        promedio_label.configure(text="Promedio: --")

        # Helper local para ajustar altura dinámica
        def ajustar_altura_treeview(tree, total_filas, max_filas=25):
            if total_filas <= max_filas:
                tree.config(height=total_filas)
            else:
                tree.config(height=max_filas)

        # Filtro de COD_TIPACT
        if cod_tipact_sel.startswith("Todos"):
            filtro_cod = "COD_TIPACT IN ('03','07','08')"
        else:
            filtro_cod = f"COD_TIPACT = '{cod_tipact_sel}'"

        # Consulta completa
        query_completo = f"""
            SELECT * FROM fiscalizaciones1
            WHERE {filtro_cod}
              AND Anio_Termino = {anio_num}
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%';
        """

        query = f"""
            SELECT 
                NOMBRE_SUPERVISOR, 
                NOMBRE_AUDITOR, 
                Mes_termino, 
                NUM_ORD_FI
            FROM fiscalizaciones1
            WHERE {filtro_cod}
              AND Anio_Termino = {anio_num}
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%';
        """

        try:
            df = ejecutar_read_sql(query, conexion)
            df_completo = ejecutar_read_sql(query_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            ctk.CTkLabel(tabla_frame, text=f"⚠ No hay datos para {cod_tipact_sel} - {anio_sel}",
                         text_color="red").pack(pady=15)
            return

        df["Mes_termino"] = df["Mes_termino"].astype(int)
        pivot = pd.pivot_table(
            df,
            index=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"],
            columns="Mes_termino",
            values="NUM_ORD_FI",
            aggfunc="count",
            fill_value=0
        )

        meses_numeros = list(range(1, 13))
        pivot = pivot.reindex(columns=meses_numeros, fill_value=0)
        pivot["Total"] = pivot.sum(axis=1)
        total_general = pivot.sum(axis=0)

        rename_map = {m: MESES[m] for m in meses_numeros}
        pivot.rename(columns=rename_map, inplace=True)
        meses_cols = [MESES[m] for m in meses_numeros]
        pivot_reset = pivot.reset_index()

        # Crear tabla formateada para exportación
        tabla_formateada_rows = []
        
        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]).sum(axis=0)
            
            row_sup = {"Supervisor": supervisor, "Auditor": ""}
            for m in meses_cols:
                row_sup[m] = int(subtotal.get(m, 0))
            row_sup["Total"] = int(subtotal.get("Total", 0))
            tabla_formateada_rows.append(row_sup)
            
            for _, row in df_sup.iterrows():
                row_aud = {"Supervisor": "", "Auditor": row["NOMBRE_AUDITOR"]}
                for m in meses_cols:
                    row_aud[m] = int(row.get(m, 0))
                row_aud["Total"] = int(row.get("Total", 0))
                tabla_formateada_rows.append(row_aud)
        
        row_total = {"Supervisor": "TOTAL GENERAL", "Auditor": ""}
        for m in meses_numeros:
            row_total[MESES[m]] = int(total_general.get(m, 0))
        row_total["Total"] = int(total_general.get("Total", 0))
        tabla_formateada_rows.append(row_total)
        
        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        frame_tabla_inner = ctk.CTkFrame(tabla_frame, corner_radius=15, fg_color="#ffffff")
        frame_tabla_inner.pack(fill="both", expand=True, padx=10, pady=8)

        ctk.CTkLabel(frame_tabla_inner,
                     text=f"📊 OF NO DETERMINATIVAS - TERMINADOS ({anio_sel})",
                     font=("Segoe UI", 14, "bold"),
                     text_color="#a51c30").pack(anchor="w", padx=12, pady=6)

        cols = ["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"] + meses_cols + ["Total"]

        container = ctk.CTkFrame(frame_tabla_inner, fg_color="white")
        container.pack(fill="both", expand=True)

        tree_local = ttk.Treeview(container, columns=cols, show="headings")
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
        tree_local.configure(yscrollcommand=vsb.set)

        tree_local.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for col in cols:
            if col == "NOMBRE_SUPERVISOR":
                text, width = "Supervisor", 220
            elif col == "NOMBRE_AUDITOR":
                text, width = "Nombre del auditor", 180
            elif col == "Total":
                text, width = "Total", 90
            else:
                text, width = col, 65
            tree_local.heading(col, text=text)
            tree_local.column(col, width=width, anchor="center")

        total_filas = 0
        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]).sum(axis=0)
            parent_vals = [supervisor, ""] + [int(subtotal.get(m, 0)) for m in meses_cols] + [int(subtotal.get("Total", 0))]
            parent = tree_local.insert("", "end", values=parent_vals, tags=("supervisor",))
            total_filas += 1

            for _, row in df_sup.iterrows():
                child_vals = ["", row["NOMBRE_AUDITOR"]] + [int(row.get(m, 0)) for m in meses_cols] + [int(row.get("Total", 0))]
                tree_local.insert(parent, "end", values=child_vals, tags=("tipo",))
                total_filas += 1

        total_vals = ["TOTAL GENERAL", ""] + [int(total_general.get(m, 0)) for m in meses_numeros] + [int(total_general.get("Total", 0))]
        tree_local.insert("", "end", values=total_vals, tags=("total",))
        total_filas += 1

        ajustar_altura_treeview(tree_local, total_filas)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree_local.tag_configure("supervisor", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree_local.tag_configure("tipo", background="white", font=("Segoe UI", 10))
        tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

        tree_actual["tree"] = tree_local
        tree_actual["pivot_reset"] = pivot_reset
        tree_actual["meses_cols"] = meses_cols

    combo_tipact.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_tipact.get(), int(combo_anio.get()) if combo_anio.get() else anio_default))
    combo_anio.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_tipact.get(), int(combo_anio.get()) if combo_anio.get() else anio_default))

    inicio_cod = combo_tipact.get() if combo_tipact.get() else "Todos (03,07,08)"
    inicio_anio = int(combo_anio.get()) if combo_anio.get() else anio_default
    cargar_tabla(inicio_cod, inicio_anio)
#-------------------------
#OF DETERMINATIVAS - PENDIENTES 
def generar_tabla_determinativas_pendientes(parent_frame, conexion=None, cod_tipact_default="06"):
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=5)

    ctk.CTkLabel(filtro_frame,
                 text="🔎 Selecciona COD_TIPACT:",
                 font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=10)

    combo_tipact = ttk.Combobox(filtro_frame, state="readonly", width=10, font=("Segoe UI", 11))
    combo_tipact.pack(side="left", padx=5)
    combo_tipact["values"] = ["06"]
    combo_tipact.set("06")

    ctk.CTkLabel(filtro_frame,
                 text="📌 Selecciona Estado:",
                 font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=10)

    combo_estado = ttk.Combobox(filtro_frame, state="readonly", width=15, font=("Segoe UI", 11))
    combo_estado.pack(side="left", padx=5)

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    try:
        estados_df = ejecutar_read_sql("SELECT DISTINCT Estado FROM fiscalizaciones1 WHERE Estado IS NOT NULL;", conexion)
        estados = [str(x).strip() for x in estados_df["Estado"].tolist()] if not estados_df.empty else []
    except Exception:
        estados = []

    if estados:
        combo_estado["values"] = estados
        if "pendiente" in [e.lower() for e in estados]:
            combo_estado.set("PENDIENTE")
        else:
            combo_estado.set(estados[0])
    else:
        combo_estado["values"] = ["PENDIENTE"]
        combo_estado.set("PENDIENTE")

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=10)

    datos_actuales = {
        "df_completo": None,
        "tabla_formateada": None,
        "cod_tipact_filtrado": None,
        "estado_filtrado": None
    }

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            cod_sel = datos_actuales["cod_tipact_filtrado"]
            estado_sel = datos_actuales["estado_filtrado"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"OF_Determinativas_Pendientes_{cod_sel}_{estado_sel}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:
                return

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_tabla(cod_tipact_sel, estado_sel):
        datos_actuales["cod_tipact_filtrado"] = cod_tipact_sel
        datos_actuales["estado_filtrado"] = estado_sel

        for w in tabla_frame.winfo_children():
            w.destroy()

        query_completo = f"""
            SELECT * FROM fiscalizaciones1
            WHERE COD_TIPACT = '{cod_tipact_sel}'
              AND Estado = '{estado_sel}'
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%';
        """

        query = f"""
            SELECT 
                NOMBRE_SUPERVISOR, 
                NOMBRE_AUDITOR, 
                Anio_Emis, 
                NUM_ORD_FI
            FROM fiscalizaciones1
            WHERE COD_TIPACT = '{cod_tipact_sel}'
              AND Estado = '{estado_sel}'
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%';
        """

        try:
            df = ejecutar_read_sql(query, conexion)
            df_completo = ejecutar_read_sql(query_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            ctk.CTkLabel(tabla_frame, text=f"⚠ No hay datos para {cod_tipact_sel} - {estado_sel}", text_color="red").pack(pady=15)
            return

        df["Anio_Emis"] = df["Anio_Emis"].astype(int)
        pivot = pd.pivot_table(
            df,
            index=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"],
            columns="Anio_Emis",
            values="NUM_ORD_FI",
            aggfunc="count",
            fill_value=0
        )

        años = sorted(df["Anio_Emis"].unique().tolist())
        pivot = pivot.reindex(columns=años, fill_value=0)
        pivot["Total"] = pivot.sum(axis=1)
        total_general = pivot.sum(axis=0)
        pivot_reset = pivot.reset_index()

        # Crear tabla formateada
        tabla_formateada_rows = []
        
        for supervisor in df["NOMBRE_SUPERVISOR"].unique():
            df_sup = df[df["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.groupby("Anio_Emis")["NUM_ORD_FI"].count().reindex(años, fill_value=0)
            total_sup = subtotal.sum()

            row_sup = {"Supervisor": supervisor, "Auditor": ""}
            for a in años:
                row_sup[str(a)] = int(subtotal.get(a, 0))
            row_sup["Total"] = int(total_sup)
            tabla_formateada_rows.append(row_sup)

            for auditor in df_sup["NOMBRE_AUDITOR"].unique():
                df_aud = df_sup[df_sup["NOMBRE_AUDITOR"] == auditor]
                subtotal_aud = df_aud.groupby("Anio_Emis")["NUM_ORD_FI"].count().reindex(años, fill_value=0)
                total_aud = subtotal_aud.sum()

                row_aud = {"Supervisor": "", "Auditor": auditor}
                for a in años:
                    row_aud[str(a)] = int(subtotal_aud.get(a, 0))
                row_aud["Total"] = int(total_aud)
                tabla_formateada_rows.append(row_aud)

        row_total = {"Supervisor": "TOTAL GENERAL", "Auditor": ""}
        for a in años:
            row_total[str(a)] = int(total_general.get(a, 0))
        row_total["Total"] = int(total_general.get("Total", 0))
        tabla_formateada_rows.append(row_total)

        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        frame_tabla_inner = ctk.CTkFrame(tabla_frame, corner_radius=15, fg_color="#ffffff")
        frame_tabla_inner.pack(fill="both", expand=True, padx=10, pady=8)

        ctk.CTkLabel(frame_tabla_inner,
                     text=f"📊 OF DETERMINATIVAS - PENDIENTES",
                     font=("Segoe UI", 14, "bold"),
                     text_color="#a51c30").pack(anchor="w", padx=12, pady=6)

        cols = ["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"] + [str(a) for a in años] + ["Total"]

        def ajustar_altura_treeview(tree, total_filas, max_filas=25):
            if total_filas <= max_filas:
                tree.config(height=total_filas)
            else:
                tree.config(height=max_filas)

        container = ctk.CTkFrame(frame_tabla_inner, fg_color="white")
        container.pack(fill="both", expand=True)

        tree_local = ttk.Treeview(container, columns=cols, show="headings")
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
        tree_local.configure(yscrollcommand=vsb.set)
        tree_local.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for col in cols:
            if col == "NOMBRE_SUPERVISOR":
                text, width = "Supervisor", 220
            elif col == "NOMBRE_AUDITOR":
                text, width = "Nombre del auditor", 180
            elif col == "Total":
                text, width = "Total", 90
            else:
                text, width = col, 65
            tree_local.heading(col, text=text)
            tree_local.column(col, width=width, anchor="center")

        total_filas = 0

        for supervisor in df["NOMBRE_SUPERVISOR"].unique():
            df_sup = df[df["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.groupby("Anio_Emis")["NUM_ORD_FI"].count().reindex(años, fill_value=0)
            total_sup = subtotal.sum()

            parent_vals = [supervisor, ""] + [int(subtotal.get(a, 0)) for a in años] + [int(total_sup)]
            parent = tree_local.insert("", "end", values=parent_vals, tags=("supervisor",))
            total_filas += 1

            for auditor in df_sup["NOMBRE_AUDITOR"].unique():
                df_aud = df_sup[df_sup["NOMBRE_AUDITOR"] == auditor]
                subtotal_aud = df_aud.groupby("Anio_Emis")["NUM_ORD_FI"].count().reindex(años, fill_value=0)
                total_aud = subtotal_aud.sum()

                child_vals = ["", auditor] + [int(subtotal_aud.get(a, 0)) for a in años] + [int(total_aud)]
                child = tree_local.insert(parent, "end", values=child_vals, tags=("tipo",))
                total_filas += 1

                for _ in range(len(df_aud)):
                    detalle_vals = ["", "", "• Registro", "", "", "", ""]
                    tree_local.insert(child, "end", values=detalle_vals, tags=("detalle",))
                    total_filas += 1

        total_vals = ["TOTAL GENERAL", ""] + [int(total_general.get(a, 0)) for a in años] + [int(total_general.get("Total", 0))]
        tree_local.insert("", "end", values=total_vals, tags=("total",))
        total_filas += 1

        ajustar_altura_treeview(tree_local, total_filas)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree_local.tag_configure("supervisor", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree_local.tag_configure("tipo", background="white", font=("Segoe UI", 10))
        tree_local.tag_configure("detalle", background="#ffffff", font=("Segoe UI", 9, "italic"), foreground="#555")
        tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

    combo_estado.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_tipact.get(), combo_estado.get()))
    cargar_tabla(combo_tipact.get(), combo_estado.get())
    #--------------------
    #OF NO DETERMINATIVAS - PENDIENTES 

def generar_tabla_no_determinativas_pendientes(parent_frame, conexion=None, anio_default=2025):
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=5)

    ctk.CTkLabel(
        filtro_frame,
        text="🔎 Selecciona COD_TIPACT:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=10)

    combo_tipact = ttk.Combobox(filtro_frame, state="readonly", width=18, font=("Segoe UI", 11))
    combo_tipact.pack(side="left", padx=5)

    codigos_permitidos = ["03", "07", "08"]
    combo_tipact["values"] = ["Todos (03,07,08)"] + codigos_permitidos
    combo_tipact.set("Todos (03,07,08)")

    ctk.CTkLabel(
        filtro_frame,
        text="📌 Selecciona Estado:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=10)

    combo_estado = ttk.Combobox(filtro_frame, state="readonly", width=18, font=("Segoe UI", 11))
    combo_estado.pack(side="left", padx=5)

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    try:
        estados_df = ejecutar_read_sql("SELECT DISTINCT Estado FROM fiscalizaciones1 WHERE Estado IS NOT NULL;", conexion)
        estados = [str(x).strip() for x in estados_df["Estado"].tolist()] if not estados_df.empty else []
    except Exception:
        estados = []

    if estados:
        combo_estado["values"] = estados
        if "pendiente" in [e.lower() for e in estados]:
            combo_estado.set("PENDIENTE")
        else:
            combo_estado.set(estados[0])
    else:
        combo_estado["values"] = ["PENDIENTE"]
        combo_estado.set("PENDIENTE")

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=10)

    datos_actuales = {
        "df_completo": None,
        "tabla_formateada": None,
        "cod_tipact_filtrado": None,
        "estado_filtrado": None
    }

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            cod_sel = datos_actuales["cod_tipact_filtrado"]
            estado_sel = datos_actuales["estado_filtrado"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"OF_No_Determinativas_Pendientes_{cod_sel}_{estado_sel}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:
                return

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_tabla(cod_tipact_sel, estado_sel):
        datos_actuales["cod_tipact_filtrado"] = cod_tipact_sel
        datos_actuales["estado_filtrado"] = estado_sel

        for w in tabla_frame.winfo_children():
            w.destroy()

        if str(cod_tipact_sel).startswith("Todos"):
            filtro_cod = "COD_TIPACT IN (3,7,8)"
        else:
            try:
                filtro_cod = f"COD_TIPACT = {int(str(cod_tipact_sel))}"
            except Exception:
                filtro_cod = "COD_TIPACT IN (3,7,8)"

        query_completo = f"""
            SELECT * FROM fiscalizaciones1
            WHERE {filtro_cod}
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
              AND LOWER(IFNULL(Estado,'')) = LOWER('{estado_sel}')
        """

        query = f"""
            SELECT
                NOMBRE_SUPERVISOR,
                NOMBRE_AUDITOR,
                Anio_Emis,
                NUM_ORD_FI
            FROM fiscalizaciones1
            WHERE {filtro_cod}
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
              AND LOWER(IFNULL(Estado,'')) = LOWER('{estado_sel}')
        """

        try:
            df = ejecutar_read_sql(query, conexion)
            df_completo = ejecutar_read_sql(query_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            ctk.CTkLabel(tabla_frame, text=f"⚠ No hay datos para COD_TIPACT={cod_tipact_sel} Estado={estado_sel}", text_color="red").pack(pady=15)
            return

        df["Anio_Emis"] = df["Anio_Emis"].astype(int)
        años_presentes = sorted(df["Anio_Emis"].dropna().unique().tolist())

        pivot = pd.pivot_table(
            df,
            index=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"],
            columns="Anio_Emis",
            values="NUM_ORD_FI",
            aggfunc="count",
            fill_value=0
        )

        pivot = pivot.reindex(columns=años_presentes, fill_value=0)
        pivot["Total"] = pivot.sum(axis=1)
        total_general = pivot.sum(axis=0)

        rename_map = {y: str(y) for y in años_presentes}
        pivot.rename(columns=rename_map, inplace=True)
        year_cols = [str(y) for y in años_presentes]
        pivot_reset = pivot.reset_index()

        # Crear tabla formateada
        tabla_formateada_rows = []
        
        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]).sum(axis=0)
            
            row_sup = {"Supervisor": supervisor, "Auditor": ""}
            for y in year_cols:
                row_sup[y] = int(subtotal.get(y, 0))
            row_sup["Total"] = int(subtotal.get("Total", 0))
            tabla_formateada_rows.append(row_sup)
            
            for _, row in df_sup.iterrows():
                row_aud = {"Supervisor": "", "Auditor": row["NOMBRE_AUDITOR"]}
                for y in year_cols:
                    row_aud[y] = int(row.get(y, 0))
                row_aud["Total"] = int(row.get("Total", 0))
                tabla_formateada_rows.append(row_aud)
        
        total_col_list = [int(total_general.get(y, 0)) for y in años_presentes]
        row_total = {"Supervisor": "TOTAL GENERAL", "Auditor": ""}
        for i, y in enumerate(year_cols):
            row_total[y] = total_col_list[i] if i < len(total_col_list) else 0
        row_total["Total"] = int(total_general.get("Total", 0))
        tabla_formateada_rows.append(row_total)

        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        frame_tabla_inner = ctk.CTkFrame(tabla_frame, corner_radius=15, fg_color="#ffffff")
        frame_tabla_inner.pack(fill="both", expand=True, padx=10, pady=8)

        ctk.CTkLabel(
            frame_tabla_inner,
            text=f"📊 OF NO DETERMINATIVAS - PENDIENTES",
            font=("Segoe UI", 14, "bold"),
            text_color="#a51c30"
        ).pack(anchor="w", padx=12, pady=6)

        cols = ["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"] + year_cols + ["Total"]

        container = ctk.CTkFrame(frame_tabla_inner, fg_color="white")
        container.pack(fill="both", expand=True)

        tree_local = ttk.Treeview(container, columns=cols, show="headings")

        vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
        tree_local.configure(yscrollcommand=vsb.set)

        tree_local.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for col in cols:
            if col == "NOMBRE_SUPERVISOR":
                text, width = "Supervisor", 220
            elif col == "NOMBRE_AUDITOR":
                text, width = "Nombre del auditor", 180
            elif col == "Total":
                text, width = "Total", 90
            else:
                text, width = col, 65
            tree_local.heading(col, text=text)
            tree_local.column(col, width=width, anchor="center")

        total_filas = 0

        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]).sum(axis=0)
            parent_vals = [supervisor, ""] + [int(subtotal.get(y, 0)) for y in year_cols] + [int(subtotal.get("Total", 0))]
            parent = tree_local.insert("", "end", values=parent_vals, tags=("supervisor",))
            total_filas += 1

            for _, row in df_sup.iterrows():
                child_vals = ["", row["NOMBRE_AUDITOR"]] + [int(row.get(y, 0)) for y in year_cols] + [int(row.get("Total", 0))]
                tree_local.insert(parent, "end", values=child_vals, tags=("tipo",))
                total_filas += 1

        total_col_list = [int(total_general.get(y, 0)) for y in años_presentes]
        total_vals = ["TOTAL GENERAL", ""] + total_col_list + [int(total_general.get("Total", 0))]
        tree_local.insert("", "end", values=total_vals, tags=("total",))
        total_filas += 1

        if total_filas <= 25:
            tree_local.config(height=total_filas)
        else:
            tree_local.config(height=25)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree_local.tag_configure("supervisor", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree_local.tag_configure("tipo", background="white", font=("Segoe UI", 10))
        tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

    combo_tipact.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_tipact.get(), combo_estado.get()))
    combo_estado.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_tipact.get(), combo_estado.get()))

    inicio_cod = combo_tipact.get() if combo_tipact.get() else "Todos (03,07,08)"
    inicio_estado = combo_estado.get() if combo_estado.get() else "PENDIENTE"
    cargar_tabla(inicio_cod, inicio_estado)
#------------------------------------------------------------
#RENDIMIENTO DE OFS TERMINADAS
def generar_tabla_rendimiento_terminadas(parent_frame, conexion=None, anio_default=2025):
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=5)

    ctk.CTkLabel(
        filtro_frame,
        text="🔎 Selecciona COD_TIPACT:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=10)

    combo_tipact = ttk.Combobox(filtro_frame, state="readonly", width=20, font=("Segoe UI", 11))
    combo_tipact.pack(side="left", padx=5)

    try:
        cod_df = ejecutar_read_sql("SELECT DISTINCT COD_TIPACT FROM fiscalizaciones1 WHERE COD_TIPACT IS NOT NULL;", conexion)
        codigos = sorted([str(x).strip() for x in cod_df["COD_TIPACT"].tolist() if str(x).strip()])
    except Exception:
        codigos = []

    combo_tipact["values"] = ["Todos"] + codigos
    combo_tipact.set("Todos")

    ctk.CTkLabel(
        filtro_frame,
        text="📅 Año de término:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=10)

    combo_anio = ttk.Combobox(filtro_frame, state="readonly", width=10, font=("Segoe UI", 11))
    combo_anio.pack(side="left", padx=5)

    try:
        anio_df = ejecutar_read_sql("SELECT DISTINCT Anio_Termino FROM fiscalizaciones1 WHERE Anio_Termino IS NOT NULL;", conexion)
        años = sorted([int(a) for a in anio_df["Anio_Termino"].dropna().unique()])
    except Exception:
        años = []

    if años:
        combo_anio["values"] = años
        if anio_default in años:
            combo_anio.set(anio_default)
        else:
            combo_anio.set(años[-1])
    else:
        combo_anio["values"] = [anio_default]
        combo_anio.set(anio_default)

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=10)

    datos_actuales = {
        "df_completo": None,
        "tabla_formateada": None,
        "cod_tipact_filtrado": None,
        "año_filtrado": None
    }

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            cod_sel = datos_actuales["cod_tipact_filtrado"]
            año_sel = datos_actuales["año_filtrado"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"Rendimiento_OFS_Terminadas_{cod_sel}_{año_sel}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:
                return

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_tabla(cod_tipact_sel, anio_sel):
        try:
            anio_num = int(str(anio_sel).strip())
        except (ValueError, TypeError, AttributeError):
            print(f"Error: anio_sel no es válido: {anio_sel}, tipo: {type(anio_sel)}")
            anio_num = 2025

        datos_actuales["cod_tipact_filtrado"] = cod_tipact_sel
        datos_actuales["año_filtrado"] = anio_num

        for w in tabla_frame.winfo_children():
            w.destroy()

        if cod_tipact_sel == "Todos":
            filtro_cod = ""
        else:
            filtro_cod = f"AND COD_TIPACT = '{cod_tipact_sel}'"

        query_completo = f"""
            SELECT * FROM fiscalizaciones1
            WHERE LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
              AND Anio_Termino = {anio_num}
              {filtro_cod}
        """

        query = f"""
            SELECT
                NOMBRE_SUPERVISOR,
                NOMBRE_AUDITOR,
                MTO_PAG_IN,
                MTO_PAG_RE,
                MTO_VAL_DE,
                Rendimiento_OF
            FROM fiscalizaciones1
            WHERE LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
              AND Anio_Termino = {anio_num}
              {filtro_cod}
        """

        try:
            df = ejecutar_read_sql(query, conexion)
            df_completo = ejecutar_read_sql(query_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            ctk.CTkLabel(tabla_frame, text="⚠ No hay datos para los filtros seleccionados.", text_color="red").pack(pady=15)
            return

        for col in ["MTO_PAG_IN", "MTO_PAG_RE", "MTO_VAL_DE", "Rendimiento_OF"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

        df_group = df.groupby(["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"], as_index=False)[
            ["MTO_PAG_IN", "MTO_PAG_RE", "MTO_VAL_DE", "Rendimiento_OF"]
        ].sum()

        total_general = df_group[["MTO_PAG_IN", "MTO_PAG_RE", "MTO_VAL_DE", "Rendimiento_OF"]].sum()

        # Crear tabla formateada
        tabla_formateada_rows = []
        
        for supervisor in df_group["NOMBRE_SUPERVISOR"].unique():
            df_sup = df_group[df_group["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup[["MTO_PAG_IN", "MTO_PAG_RE", "MTO_VAL_DE", "Rendimiento_OF"]].sum()
            
            row_sup = {
                "Supervisor": supervisor,
                "Auditor": "",
                "Pago Inducido": round(subtotal["MTO_PAG_IN"], 2),
                "Rectificatoria": round(subtotal["MTO_PAG_RE"], 2),
                "Valores": round(subtotal["MTO_VAL_DE"], 2),
                "Rendimiento Total": round(subtotal["Rendimiento_OF"], 2)
            }
            tabla_formateada_rows.append(row_sup)
            
            for _, row in df_sup.iterrows():
                row_aud = {
                    "Supervisor": "",
                    "Auditor": row["NOMBRE_AUDITOR"],
                    "Pago Inducido": round(row["MTO_PAG_IN"], 2),
                    "Rectificatoria": round(row["MTO_PAG_RE"], 2),
                    "Valores": round(row["MTO_VAL_DE"], 2),
                    "Rendimiento Total": round(row["Rendimiento_OF"], 2)
                }
                tabla_formateada_rows.append(row_aud)
        
        row_total = {
            "Supervisor": "TOTAL GENERAL",
            "Auditor": "",
            "Pago Inducido": round(total_general["MTO_PAG_IN"], 2),
            "Rectificatoria": round(total_general["MTO_PAG_RE"], 2),
            "Valores": round(total_general["MTO_VAL_DE"], 2),
            "Rendimiento Total": round(total_general["Rendimiento_OF"], 2)
        }
        tabla_formateada_rows.append(row_total)

        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        ctk.CTkLabel(
            tabla_frame,
            text=f"📊 RENDIMIENTO DE OFS TERMINADAS ({anio_sel})",
            font=("Segoe UI", 14, "bold"),
            text_color="#a51c30"
        ).pack(anchor="w", padx=12, pady=6)

        container = ctk.CTkFrame(tabla_frame, fg_color="white")
        container.pack(fill="both", expand=True)

        cols = [
            "NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR",
            "MTO_PAG_IN", "MTO_PAG_RE", "MTO_VAL_DE", "Rendimiento_OF"
        ]

        tree_local = ttk.Treeview(container, columns=cols, show="headings")

        vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
        tree_local.configure(yscrollcommand=vsb.set)
        tree_local.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        headers = {
            "NOMBRE_SUPERVISOR": "Supervisor",
            "NOMBRE_AUDITOR": "Auditor",
            "MTO_PAG_IN": "Pago Inducido",
            "MTO_PAG_RE": "Rectificatoria",
            "MTO_VAL_DE": "Valores",
            "Rendimiento_OF": "Rendimiento Total"
        }
        widths = {
            "NOMBRE_SUPERVISOR": 220,
            "NOMBRE_AUDITOR": 180,
            "MTO_PAG_IN": 120,
            "MTO_PAG_RE": 120,
            "MTO_VAL_DE": 120,
            "Rendimiento_OF": 130
        }

        for col in cols:
            tree_local.heading(col, text=headers[col])
            tree_local.column(col, width=widths[col], anchor="center")

        total_filas = 0

        for supervisor in df_group["NOMBRE_SUPERVISOR"].unique():
            df_sup = df_group[df_group["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup[["MTO_PAG_IN", "MTO_PAG_RE", "MTO_VAL_DE", "Rendimiento_OF"]].sum()
            parent_vals = [
                supervisor, "",
                round(subtotal["MTO_PAG_IN"], 2),
                round(subtotal["MTO_PAG_RE"], 2),
                round(subtotal["MTO_VAL_DE"], 2),
                round(subtotal["Rendimiento_OF"], 2)
            ]
            parent = tree_local.insert("", "end", values=parent_vals, tags=("supervisor",))
            total_filas += 1

            for _, row in df_sup.iterrows():
                vals = [
                    "",
                    row["NOMBRE_AUDITOR"],
                    round(row["MTO_PAG_IN"], 2),
                    round(row["MTO_PAG_RE"], 2),
                    round(row["MTO_VAL_DE"], 2),
                    round(row["Rendimiento_OF"], 2)
                ]
                tree_local.insert(parent, "end", values=vals, tags=("tipo",))
                total_filas += 1

        total_vals = [
            "TOTAL GENERAL", "",
            round(total_general["MTO_PAG_IN"], 2),
            round(total_general["MTO_PAG_RE"], 2),
            round(total_general["MTO_VAL_DE"], 2),
            round(total_general["Rendimiento_OF"], 2)
        ]
        tree_local.insert("", "end", values=total_vals, tags=("total",))

        tree_local.config(height=min(total_filas + 1, 25))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree_local.tag_configure("supervisor", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree_local.tag_configure("tipo", background="white", font=("Segoe UI", 10))
        tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

    combo_tipact.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_tipact.get(), combo_anio.get()))
    combo_anio.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_tipact.get(), combo_anio.get()))

    cargar_tabla(combo_tipact.get(), combo_anio.get())

# ==========================
#SIP 05 - Nivel de cumplimiento de cobertura y monto impactado de los tratamientos de los riesgos identificados
def generar_tabla_sip05(parent_frame, conexion=None, anio_default=2025):
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=5)

    ctk.CTkLabel(
        filtro_frame,
        text="🔎 SIP_05  - Seleccione filtros:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=10)

    combo_sip05 = ttk.Combobox(filtro_frame, state="readonly", width=20, font=("Segoe UI", 11))
    combo_sip05.pack(side="left", padx=6)

    ctk.CTkLabel(filtro_frame, text="Estado:", font=("Segoe UI", 13, "bold"), text_color="#002e6d").pack(side="left", padx=10)
    combo_estado = ttk.Combobox(filtro_frame, state="readonly", width=18, font=("Segoe UI", 11))
    combo_estado.pack(side="left", padx=6)

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    try:
        sip_df = ejecutar_read_sql("SELECT SIP_05, COUNT(NUM_ORD_FI) AS cantidad FROM fiscalizaciones1 GROUP BY SIP_05;", conexion)
        sip_vals = [str(v).strip() for v in sip_df["SIP_05"]]
        combo_sip05["values"] = ["Todos"] + sip_vals

        seleccionado = None
        for v, c in zip(sip_df["SIP_05"], sip_df["cantidad"]):
            if str(v).strip().lower() == "si":
                seleccionado = f"{v}"
                break
        combo_sip05.set(seleccionado or "Todos")
    except Exception:
        combo_sip05["values"] = ["Todos"]
        combo_sip05.set("Todos")

    try:
        estado_df = ejecutar_read_sql("SELECT DISTINCT Estado FROM fiscalizaciones1 WHERE Estado IS NOT NULL;", conexion)
        estados = sorted([str(x).strip() for x in estado_df["Estado"].tolist() if str(x).strip()])
        combo_estado["values"] = estados
        combo_estado.set("Pendiente" if "Pendiente" in estados else (estados[0] if estados else ""))
    except Exception:
        combo_estado["values"] = []
        combo_estado.set("")

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=10)

    datos_actuales = {
        "df_completo": None,
        "tabla_formateada": None,
        "sip_filtrado": None,
        "estado_filtrado": None
    }

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            sip_sel = datos_actuales["sip_filtrado"]
            estado_sel = datos_actuales["estado_filtrado"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"SIP05_Cumplimiento_{sip_sel}_{estado_sel}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:
                return

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_tabla(sip_sel, estado_sel):
        datos_actuales["sip_filtrado"] = sip_sel
        datos_actuales["estado_filtrado"] = estado_sel

        for w in tabla_frame.winfo_children():
            w.destroy()

        sip_val = None if sip_sel in (None, "", "Todos") else sip_sel.split(" ")[0]
        estado_val = None if estado_sel in (None, "") else estado_sel

        sql_completo = "SELECT * FROM fiscalizaciones1 WHERE LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'"
        if sip_val:
            sql_completo += f" AND SIP_05 = '{sip_val}'"
        if estado_val:
            sql_completo += f" AND Estado = '{estado_val}'"

        sql = """
            SELECT
                NOMBRE_SUPERVISOR,
                NOMBRE_AUDITOR,
                Anio_Emis,
                COUNT(NUM_ORD_FI) AS OFs,
                SUM(MTO_SIP_05) AS Monto_SIP
            FROM fiscalizaciones1
            WHERE LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
        """
        if sip_val:
            sql += f" AND SIP_05 = '{sip_val}'"
        if estado_val:
            sql += f" AND Estado = '{estado_val}'"
        sql += " GROUP BY NOMBRE_SUPERVISOR, NOMBRE_AUDITOR, Anio_Emis ORDER BY NOMBRE_SUPERVISOR, NOMBRE_AUDITOR;"

        try:
            df = ejecutar_read_sql(sql, conexion)
            df_completo = ejecutar_read_sql(sql_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            ctk.CTkLabel(tabla_frame, text="⚠ No hay datos para los filtros seleccionados.", text_color="red").pack(pady=15)
            return

        df["Anio_Emis"] = df["Anio_Emis"].fillna(0).astype(int)
        df["OFs"] = pd.to_numeric(df.get("OFs", 0), errors="coerce").fillna(0).astype(int)
        df["Monto_SIP"] = pd.to_numeric(df.get("Monto_SIP", 0.0), errors="coerce").fillna(0.0)

        años = sorted(df["Anio_Emis"].unique().tolist())

        cols = ["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]
        for a in años:
            cols.append(f"{a} OFs")
            cols.append(f"{a} Monto SIP")
        cols += ["Total OFs", "Total Monto SIP"]

        estructura = {}
        for _, row in df.iterrows():
            sup, aud, anio = row["NOMBRE_SUPERVISOR"], row["NOMBRE_AUDITOR"], int(row["Anio_Emis"])
            ofs, monto = int(row["OFs"]), float(row["Monto_SIP"] or 0.0)

            if sup not in estructura:
                estructura[sup] = {"aud": {}, "tot_of": 0, "tot_monto": 0.0}
            if aud not in estructura[sup]["aud"]:
                estructura[sup]["aud"][aud] = {"por_anio": {}, "tot_of": 0, "tot_monto": 0.0}
            estructura[sup]["aud"][aud]["por_anio"].setdefault(anio, {"ofs": 0, "monto": 0.0})
            estructura[sup]["aud"][aud]["por_anio"][anio]["ofs"] += ofs
            estructura[sup]["aud"][aud]["por_anio"][anio]["monto"] += monto
            estructura[sup]["aud"][aud]["tot_of"] += ofs
            estructura[sup]["aud"][aud]["tot_monto"] += monto
            estructura[sup]["tot_of"] += ofs
            estructura[sup]["tot_monto"] += monto

        # Crear tabla formateada
        tabla_formateada_rows = []
        
        for sup, datos_sup in estructura.items():
            row_sup = {"Supervisor": sup, "Auditor": ""}
            for a in años:
                ofs_a = sum(datos_sup["aud"][x]["por_anio"].get(a, {}).get("ofs", 0) for x in datos_sup["aud"])
                monto_a = sum(datos_sup["aud"][x]["por_anio"].get(a, {}).get("monto", 0.0) for x in datos_sup["aud"])
                row_sup[f"{a} OFs"] = ofs_a
                row_sup[f"{a} Monto SIP"] = monto_a
            row_sup["Total OFs"] = datos_sup["tot_of"]
            row_sup["Total Monto SIP"] = datos_sup["tot_monto"]
            tabla_formateada_rows.append(row_sup)

            for aud, d in datos_sup["aud"].items():
                row_aud = {"Supervisor": "", "Auditor": aud}
                for a in años:
                    v = d["por_anio"].get(a, {"ofs": 0, "monto": 0.0})
                    row_aud[f"{a} OFs"] = v["ofs"]
                    row_aud[f"{a} Monto SIP"] = v["monto"]
                row_aud["Total OFs"] = d["tot_of"]
                row_aud["Total Monto SIP"] = d["tot_monto"]
                tabla_formateada_rows.append(row_aud)

        total_general_ofs = sum(estructura[s]["tot_of"] for s in estructura)
        total_general_monto = sum(estructura[s]["tot_monto"] for s in estructura)

        row_total = {"Supervisor": "TOTAL GENERAL", "Auditor": ""}
        for a in años:
            ofs_t = sum(
                estructura[s]["aud"][x]["por_anio"].get(a, {}).get("ofs", 0)
                for s in estructura for x in estructura[s]["aud"]
            )
            monto_t = sum(
                estructura[s]["aud"][x]["por_anio"].get(a, {}).get("monto", 0.0)
                for s in estructura for x in estructura[s]["aud"]
            )
            row_total[f"{a} OFs"] = ofs_t
            row_total[f"{a} Monto SIP"] = monto_t
        row_total["Total OFs"] = total_general_ofs
        row_total["Total Monto SIP"] = total_general_monto
        tabla_formateada_rows.append(row_total)

        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        ctk.CTkLabel(
            tabla_frame,
            text=f"📊 SIP 05 - Nivel de cumplimiento de cobertura y monto impactado",
            font=("Segoe UI", 14, "bold"),
            text_color="#a51c30"
        ).pack(anchor="w", padx=12, pady=(6, 8))

        container = ctk.CTkFrame(tabla_frame, fg_color="white")
        container.pack(fill="both", expand=True)

        tree = ttk.Treeview(container, columns=cols, show="headings")

        vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        vsb.grid(row=0, column=1, sticky="ns")

        if len(cols) > 13:
            hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
            tree.configure(xscrollcommand=hsb.set)
            hsb.grid(row=1, column=0, sticky="ew")

        tree.grid(row=0, column=0, sticky="nsew")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        headers = {"NOMBRE_SUPERVISOR": "Supervisor", "NOMBRE_AUDITOR": "Auditor"}
        widths = {"NOMBRE_SUPERVISOR": 220, "NOMBRE_AUDITOR": 180}
        for a in años:
            headers[f"{a} OFs"] = f"{a} OFs"
            headers[f"{a} Monto SIP"] = f"{a} Monto SIP"
            widths[f"{a} OFs"] = 100
            widths[f"{a} Monto SIP"] = 140
        headers["Total OFs"] = "Total OFs"
        headers["Total Monto SIP"] = "Total Monto SIP"
        widths["Total OFs"] = 110
        widths["Total Monto SIP"] = 150

        for col in cols:
            tree.heading(col, text=headers.get(col, col))
            tree.column(col, width=widths.get(col, 100),
                        anchor="center" if "OFs" in col or "Total" in col else "w")

        total_rows = 0
        total_general_ofs = 0
        total_general_monto = 0.0

        for sup, datos_sup in estructura.items():
            fila_sup = [sup, ""]
            for a in años:
                ofs_a = sum(datos_sup["aud"][x]["por_anio"].get(a, {}).get("ofs", 0) for x in datos_sup["aud"])
                monto_a = sum(datos_sup["aud"][x]["por_anio"].get(a, {}).get("monto", 0.0) for x in datos_sup["aud"])
                fila_sup.append(ofs_a)
                fila_sup.append(f"{monto_a:,.2f}")
            fila_sup.append(datos_sup["tot_of"])
            fila_sup.append(f"{datos_sup['tot_monto']:,.2f}")

            parent = tree.insert("", "end", values=fila_sup, tags=("supervisor",))
            total_rows += 1

            for aud, d in datos_sup["aud"].items():
                fila_aud = ["", aud]
                for a in años:
                    v = d["por_anio"].get(a, {"ofs": 0, "monto": 0.0})
                    fila_aud.append(v["ofs"])
                    fila_aud.append(f"{v['monto']:,.2f}")
                fila_aud.append(d["tot_of"])
                fila_aud.append(f"{d['tot_monto']:,.2f}")
                tree.insert(parent, "end", values=fila_aud, tags=("auditor",))
                total_rows += 1

            total_general_ofs += datos_sup["tot_of"]
            total_general_monto += datos_sup["tot_monto"]

        fila_total = ["TOTAL GENERAL", ""]
        for a in años:
            ofs_t = sum(
                estructura[s]["aud"][x]["por_anio"].get(a, {}).get("ofs", 0)
                for s in estructura for x in estructura[s]["aud"]
            )
            monto_t = sum(
                estructura[s]["aud"][x]["por_anio"].get(a, {}).get("monto", 0.0)
                for s in estructura for x in estructura[s]["aud"]
            )
            fila_total.append(ofs_t)
            fila_total.append(f"{monto_t:,.2f}")
        fila_total.append(total_general_ofs)
        fila_total.append(f"{total_general_monto:,.2f}")
        tree.insert("", "end", values=fila_total, tags=("total",))

        tree.config(height=min(total_rows + 3, 25))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree.tag_configure("supervisor", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree.tag_configure("auditor", background="white", font=("Segoe UI", 10))
        tree.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

    combo_sip05.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_sip05.get(), combo_estado.get()))
    combo_estado.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_sip05.get(), combo_estado.get()))

    cargar_tabla(combo_sip05.get(), combo_estado.get())

#-----------------------
#SIP 05 - OF TERMINADA 
def generar_tabla_sip05_terminada(parent_frame, conexion=None):
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=10)

    icono_llave = "🔑"
    ctk.CTkLabel(
        filtro_frame,
        text=f"{icono_llave} SIP_05:",
        font=("Segoe UI", 12, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(12, 4))
    combo_sip = ttk.Combobox(filtro_frame, state="readonly", width=8, font=("Segoe UI", 11))
    combo_sip.pack(side="left", padx=6)

    ctk.CTkLabel(
        filtro_frame,
        text="Estado:",
        font=("Segoe UI", 12, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(12, 4))
    combo_estado = ttk.Combobox(filtro_frame, state="readonly", width=14, font=("Segoe UI", 11))
    combo_estado.pack(side="left", padx=6)

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=12)

    datos_actuales = {
        "df_completo": None,
        "tabla_formateada": None,
        "sip_filtrado": None,
        "estado_filtrado": None
    }

    try:
        sip_df = ejecutar_read_sql("SELECT DISTINCT IFNULL(SIP_05,'') AS SIP_05 FROM fiscalizaciones1;", conexion)
        sip_vals = sorted([str(x).strip() for x in sip_df["SIP_05"].tolist() if str(x).strip()])
    except Exception:
        sip_vals = []
    combo_sip["values"] = sip_vals

    try:
        estado_df = ejecutar_read_sql("SELECT DISTINCT IFNULL(Estado,'') AS Estado FROM fiscalizaciones1;", conexion)
        estado_vals = sorted([str(x).strip() for x in estado_df["Estado"].tolist() if str(x).strip()])
    except Exception:
        estado_vals = []
    combo_estado["values"] = estado_vals

    if "SI" in sip_vals:
        combo_sip.set("SI")
    elif sip_vals:
        combo_sip.set(sip_vals[0])

    if "Terminado" in estado_vals:
        combo_estado.set("Terminado")
    elif estado_vals:
        combo_estado.set(estado_vals[0])

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            sip_sel = datos_actuales["sip_filtrado"]
            estado_sel = datos_actuales["estado_filtrado"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"SIP05_OF_Terminada_{sip_sel}_{estado_sel}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:
                return

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_tabla(sip_sel, estado_sel):
        datos_actuales["sip_filtrado"] = sip_sel
        datos_actuales["estado_filtrado"] = estado_sel

        for w in tabla_frame.winfo_children():
            w.destroy()

        query_completo = f"""
            SELECT * FROM fiscalizaciones1
            WHERE UPPER(IFNULL(SIP_05,'')) = UPPER('{sip_sel}')
              AND UPPER(IFNULL(Estado,'')) = UPPER('{estado_sel}')
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%';
        """

        query = f"""
            SELECT NOMBRE_SUPERVISOR, NOMBRE_AUDITOR, Mes_termino, NUM_ORD_FI, des_cod
            FROM fiscalizaciones1
            WHERE UPPER(IFNULL(SIP_05,'')) = UPPER('{sip_sel}')
              AND UPPER(IFNULL(Estado,'')) = UPPER('{estado_sel}')
              AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%';
        """

        try:
            df = ejecutar_read_sql(query, conexion)
            df_completo = ejecutar_read_sql(query_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            ctk.CTkLabel(tabla_frame, text=f"⚠ No hay datos para SIP_05={sip_sel} y Estado={estado_sel}", text_color="red").pack(pady=15)
            return

        df["Mes_termino"] = pd.to_numeric(df["Mes_termino"], errors="coerce")
        df = df[df["Mes_termino"].notna()]
        df["Mes_termino"] = df["Mes_termino"].astype(int)
        df = df[(df["Mes_termino"] >= 1) & (df["Mes_termino"] <= 12)]

        pivot = pd.pivot_table(
            df,
            index=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"],
            columns="Mes_termino",
            values="NUM_ORD_FI",
            aggfunc="count",
            fill_value=0
        )

        meses_numeros = list(range(1, 13))
        pivot = pivot.reindex(columns=meses_numeros, fill_value=0)
        pivot["Total"] = pivot.sum(axis=1)
        total_general = pivot.sum(axis=0)

        rename_map = {m: MESES[m] for m in meses_numeros}
        pivot.rename(columns=rename_map, inplace=True)
        meses_cols = [MESES[m] for m in meses_numeros]
        pivot_reset = pivot.reset_index()

        # Crear tabla formateada
        tabla_formateada_rows = []
        
        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]).sum(axis=0)
            
            row_sup = {"Supervisor": supervisor, "Auditor": ""}
            for m in meses_cols:
                row_sup[m] = int(subtotal.get(m, 0))
            row_sup["OFs"] = int(subtotal.get("Total", 0))
            tabla_formateada_rows.append(row_sup)
            
            for _, row in df_sup.iterrows():
                row_aud = {"Supervisor": "", "Auditor": row["NOMBRE_AUDITOR"]}
                for m in meses_cols:
                    row_aud[m] = int(row.get(m, 0))
                row_aud["OFs"] = int(row.get("Total", 0))
                tabla_formateada_rows.append(row_aud)
        
        row_total = {"Supervisor": "TOTAL GENERAL", "Auditor": ""}
        for m in meses_numeros:
            row_total[MESES[m]] = int(total_general.get(m, 0))
        row_total["OFs"] = int(total_general.get("Total", 0))
        tabla_formateada_rows.append(row_total)

        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        frame_tabla_inner = ctk.CTkFrame(tabla_frame, corner_radius=15, fg_color="#ffffff")
        frame_tabla_inner.pack(fill="both", expand=True, padx=10, pady=8)

        ctk.CTkLabel(frame_tabla_inner,
                     text=f"📊 SIP 05 - OF TERMINADA",
                     font=("Segoe UI", 14, "bold"),
                     text_color="#a51c30").pack(anchor="w", padx=12, pady=6)

        container = ctk.CTkFrame(frame_tabla_inner, fg_color="white")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        cols = ["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"] + meses_cols + ["OFs"]
        tree_local = ttk.Treeview(container, columns=cols, show="headings")
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
        tree_local.configure(yscrollcommand=vsb.set)
        tree_local.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for col in cols:
            if col == "NOMBRE_SUPERVISOR":
                text, width = "Supervisor", 220
            elif col == "NOMBRE_AUDITOR":
                text, width = "Auditor", 180
            elif col == "OFs":
                text, width = "OFs", 90
            else:
                text, width = col, 65
            tree_local.heading(col, text=text)
            tree_local.column(col, width=width, anchor="center")

        total_filas = 0
        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]).sum(axis=0)
            parent_vals = [supervisor, ""] + [int(subtotal.get(m,0)) for m in meses_cols] + [int(subtotal.get("Total",0))]
            parent = tree_local.insert("", "end", values=parent_vals, tags=("supervisor",))
            total_filas += 1

            for _, row in df_sup.iterrows():
                child_vals = ["", row["NOMBRE_AUDITOR"]] + [int(row.get(m,0)) for m in meses_cols] + [int(row.get("Total",0))]
                tree_local.insert(parent, "end", values=child_vals, tags=("auditor",))
                total_filas += 1

        total_vals = ["TOTAL GENERAL", ""] + [int(total_general.get(m,0)) for m in meses_numeros] + [int(total_general.get("Total",0))]
        tree_local.insert("", "end", values=total_vals, tags=("total",))
        total_filas += 1

        ajustar_altura_treeview(tree_local, total_filas)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree_local.tag_configure("supervisor", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree_local.tag_configure("auditor", background="white", font=("Segoe UI", 10))
        tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

    cargar_tabla(combo_sip.get(), combo_estado.get())
#----------------------------------
#SIP 05 - MONTO DE OF TERMINADA 
def generar_tabla_sip05_monto_of_terminada(parent_frame, conexion=None):
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os
    import re

    MAX_COLS_SIN_HSCROLL = 13

    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=5)

    ctk.CTkLabel(
        filtro_frame,
        text="🔎 SIP_05  - Seleccione filtros:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=10)

    combo_sip05 = ttk.Combobox(filtro_frame, state="readonly", width=20, font=("Segoe UI", 11))
    combo_sip05.pack(side="left", padx=6)

    ctk.CTkLabel(filtro_frame, text="Estado:", font=("Segoe UI", 13, "bold"), text_color="#002e6d").pack(side="left", padx=10)
    combo_estado = ttk.Combobox(filtro_frame, state="readonly", width=18, font=("Segoe UI", 11))
    combo_estado.pack(side="left", padx=6)

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    try:
        sip_df = ejecutar_read_sql("SELECT SIP_05, COUNT(*) AS cantidad FROM fiscalizaciones1 GROUP BY SIP_05;", conexion)
        sip_vals = [str(v).strip() for v in sip_df["SIP_05"]]
        combo_sip05["values"] = ["Todos"] + sip_vals
        seleccionado = None
        for v in sip_vals:
            if str(v).strip().lower() == "si":
                seleccionado = v
                break
        combo_sip05.set(seleccionado or ("Si" if "Si" in sip_vals else "Todos"))
    except Exception:
        combo_sip05["values"] = ["Todos"]
        combo_sip05.set("Si")

    try:
        estado_df = ejecutar_read_sql("SELECT DISTINCT Estado FROM fiscalizaciones1 WHERE Estado IS NOT NULL;", conexion)
        estados = sorted([str(x).strip() for x in estado_df["Estado"].tolist() if str(x).strip()])
        combo_estado["values"] = estados
        combo_estado.set("Terminado" if "Terminado" in estados else (estados[0] if estados else ""))
    except Exception:
        combo_estado["values"] = []
        combo_estado.set("Terminado")

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=10)

    datos_actuales = {
        "df_completo": None,
        "tabla_formateada": None,
        "sip_filtrado": None,
        "estado_filtrado": None
    }

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            sip_sel = datos_actuales["sip_filtrado"]
            estado_sel = datos_actuales["estado_filtrado"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"SIP05_Monto_OF_Terminada_{sip_sel}_{estado_sel}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:
                return

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_tabla(sip_sel, estado_sel):
        datos_actuales["sip_filtrado"] = sip_sel
        datos_actuales["estado_filtrado"] = estado_sel

        for w in tabla_frame.winfo_children():
            w.destroy()

        sip_val = None if sip_sel in (None, "", "Todos") else sip_sel
        estado_val = None if estado_sel in (None, "") else estado_sel

        sql_completo = "SELECT * FROM fiscalizaciones1 WHERE LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'"
        if sip_val:
            sql_completo += f" AND SIP_05 = '{sip_val}'"
        if estado_val:
            sql_completo += f" AND Estado = '{estado_val}'"

        sql = """
            SELECT
                NOMBRE_SUPERVISOR,
                NOMBRE_AUDITOR,
                Mes_termino,
                SUM(IFNULL(MTO_SIP_05,0)) AS MTO_SIP_05,
                SUM(IFNULL(Monto_Comp2_SIP05,0)) AS Monto_Comp2_SIP05
            FROM fiscalizaciones1
            WHERE LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
        """
        if sip_val:
            sql += f" AND SIP_05 = '{sip_val}'"
        if estado_val:
            sql += f" AND Estado = '{estado_val}'"
        sql += " GROUP BY NOMBRE_SUPERVISOR, NOMBRE_AUDITOR, Mes_termino"
        sql += " ORDER BY NOMBRE_SUPERVISOR, NOMBRE_AUDITOR, Mes_termino;"

        try:
            df = ejecutar_read_sql(sql, conexion)
            df_completo = ejecutar_read_sql(sql_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            ctk.CTkLabel(tabla_frame, text="⚠ No hay datos para los filtros seleccionados.", text_color="red").pack(pady=15)
            return

        df["MTO_SIP_05"] = pd.to_numeric(df.get("MTO_SIP_05", 0.0), errors="coerce").fillna(0.0)
        df["Monto_Comp2_SIP05"] = pd.to_numeric(df.get("Monto_Comp2_SIP05", 0.0), errors="coerce").fillna(0.0)
        df["Mes_termino"] = df["Mes_termino"].fillna("").astype(str)

        month_map = {
            'ene':1,'enero':1, 'feb':2,'febrero':2, 'mar':3,'marzo':3, 'abr':4,'abril':4,
            'may':5,'mayo':5, 'jun':6,'junio':6, 'jul':7,'julio':7, 'ago':8,'agosto':8,
            'sep':9,'set':9,'septiembre':9,'setiembre':9, 'oct':10,'octubre':10,
            'nov':11,'noviembre':11, 'dic':12,'diciembre':12
        }
        month_labels = {0: "Otros", 1: "ene", 2: "feb", 3: "mar", 4: "abr", 5: "may", 6: "jun",
                        7: "jul", 8: "ago", 9: "sep", 10: "oct", 11: "nov", 12: "dic"}

        def mes_a_num(s):
            s_orig = str(s).strip()
            if s_orig == "":
                return 0
            try:
                n = int(s_orig)
                if 1 <= n <= 12:
                    return n
            except:
                pass
            s_low = re.sub(r'[^a-z0-9]', '', s_orig.lower())
            digits = re.search(r'(\d{1,2})', s_low)
            if digits:
                n = int(digits.group(1))
                if 1 <= n <= 12:
                    return n
            if s_low in month_map:
                return month_map[s_low]
            return 0

        df["Mes_num"] = df["Mes_termino"].apply(mes_a_num)
        df["Mes_label"] = df["Mes_num"].apply(lambda x: month_labels.get(x, "Otros"))

        meses_unicos = sorted(df["Mes_num"].unique())
        meses = [m for m in meses_unicos if m != 0]
        if 0 in meses_unicos:
            meses.append(0)

        cols = ["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]
        for m in meses:
            label = month_labels.get(m, f"m{m}")
            cols.append(f"{label} MTO_SIP_05")
            cols.append(f"{label} Monto_Comp2")
        cols += ["Total MTO_SIP_05", "Total Monto_Comp2"]

        estructura = {}
        for _, row in df.iterrows():
            sup = row["NOMBRE_SUPERVISOR"]
            aud = row["NOMBRE_AUDITOR"]
            mes_num = int(row["Mes_num"] or 0)
            mto = float(row["MTO_SIP_05"])
            comp2 = float(row["Monto_Comp2_SIP05"])

            estructura.setdefault(sup, {"aud": {}, "tot_mto": 0.0, "tot_comp2": 0.0})
            estructura[sup]["aud"].setdefault(aud, {"por_mes": {}, "tot_mto": 0.0, "tot_comp2": 0.0})
            estructura[sup]["aud"][aud]["por_mes"].setdefault(mes_num, {"mto": 0.0, "comp2": 0.0})
            estructura[sup]["aud"][aud]["por_mes"][mes_num]["mto"] += mto
            estructura[sup]["aud"][aud]["por_mes"][mes_num]["comp2"] += comp2

            estructura[sup]["aud"][aud]["tot_mto"] += mto
            estructura[sup]["aud"][aud]["tot_comp2"] += comp2
            estructura[sup]["tot_mto"] += mto
            estructura[sup]["tot_comp2"] += comp2

        # Crear tabla formateada
        tabla_formateada_rows = []
        
        for sup, datos_sup in estructura.items():
            row_sup = {"Supervisor": sup, "Auditor": ""}
            for m in meses:
                label = month_labels.get(m, f"m{m}")
                mto_mes = sum(datos_sup["aud"][x]["por_mes"].get(m, {}).get("mto", 0.0) for x in datos_sup["aud"])
                comp2_mes = sum(datos_sup["aud"][x]["por_mes"].get(m, {}).get("comp2", 0.0) for x in datos_sup["aud"])
                row_sup[f"{label} MTO"] = mto_mes
                row_sup[f"{label} Comp2"] = comp2_mes
            row_sup["Total MTO"] = datos_sup["tot_mto"]
            row_sup["Total Comp2"] = datos_sup["tot_comp2"]
            tabla_formateada_rows.append(row_sup)

            for aud, d in datos_sup["aud"].items():
                row_aud = {"Supervisor": "", "Auditor": aud}
                for m in meses:
                    label = month_labels.get(m, f"m{m}")
                    v = d["por_mes"].get(m, {"mto": 0.0, "comp2": 0.0})
                    row_aud[f"{label} MTO"] = v["mto"]
                    row_aud[f"{label} Comp2"] = v["comp2"]
                row_aud["Total MTO"] = d["tot_mto"]
                row_aud["Total Comp2"] = d["tot_comp2"]
                tabla_formateada_rows.append(row_aud)

        total_general_mto = sum(estructura[s]["tot_mto"] for s in estructura)
        total_general_comp2 = sum(estructura[s]["tot_comp2"] for s in estructura)

        row_total = {"Supervisor": "TOTAL GENERAL", "Auditor": ""}
        for m in meses:
            label = month_labels.get(m, f"m{m}")
            mto_t = sum(
                estructura[s]["aud"][x]["por_mes"].get(m, {}).get("mto", 0.0)
                for s in estructura for x in estructura[s]["aud"]
            )
            comp2_t = sum(
                estructura[s]["aud"][x]["por_mes"].get(m, {}).get("comp2", 0.0)
                for s in estructura for x in estructura[s]["aud"]
            )
            row_total[f"{label} MTO"] = mto_t
            row_total[f"{label} Comp2"] = comp2_t
        row_total["Total MTO"] = total_general_mto
        row_total["Total Comp2"] = total_general_comp2
        tabla_formateada_rows.append(row_total)

        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        ctk.CTkLabel(
            tabla_frame,
            text=f"📊 SIP 05 - MONTO DE OF TERMINADA",
            font=("Segoe UI", 14, "bold"),
            text_color="#a51c30"
        ).pack(anchor="w", padx=12, pady=(6, 8))

        container = ctk.CTkFrame(tabla_frame, fg_color="white")
        container.pack(fill="both", expand=True)

        tree = ttk.Treeview(container, columns=cols, show="headings")
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree.yview)
        hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        if len(cols) > MAX_COLS_SIN_HSCROLL:
            hsb.grid(row=1, column=0, sticky="ew")

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        headers = {"NOMBRE_SUPERVISOR": "Supervisor", "NOMBRE_AUDITOR": "Auditor"}
        widths = {"NOMBRE_SUPERVISOR": 220, "NOMBRE_AUDITOR": 180}
        for m in meses:
            label = month_labels.get(m, f"m{m}")
            headers[f"{label} MTO_SIP_05"] = f"{label} MTO"
            headers[f"{label} Monto_Comp2"] = f"{label} Comp2"
            widths[f"{label} MTO_SIP_05"] = 120
            widths[f"{label} Monto_Comp2"] = 140
        headers["Total MTO_SIP_05"] = "Total MTO"
        headers["Total Monto_Comp2"] = "Total Comp2"
        widths["Total MTO_SIP_05"] = 130
        widths["Total Monto_Comp2"] = 150

        for col in cols:
            tree.heading(col, text=headers.get(col, col))
            anchor = "center" if ("MTO" in col or "Total" in col or "Comp2" in col) else "w"
            tree.column(col, width=widths.get(col, 100), anchor=anchor)

        total_rows = 0
        total_general_mto = 0.0
        total_general_comp2 = 0.0

        for sup, datos_sup in estructura.items():
            fila_sup = [sup, ""]
            for m in meses:
                mto_mes = sum(datos_sup["aud"][x]["por_mes"].get(m, {}).get("mto", 0.0) for x in datos_sup["aud"])
                comp2_mes = sum(datos_sup["aud"][x]["por_mes"].get(m, {}).get("comp2", 0.0) for x in datos_sup["aud"])
                fila_sup.append(f"{mto_mes:,.2f}")
                fila_sup.append(f"{comp2_mes:,.2f}")
            fila_sup.append(f"{datos_sup['tot_mto']:,.2f}")
            fila_sup.append(f"{datos_sup['tot_comp2']:,.2f}")

            parent = tree.insert("", "end", values=fila_sup, tags=("supervisor",))
            total_rows += 1

            for aud, d in datos_sup["aud"].items():
                fila_aud = ["", aud]
                for m in meses:
                    v = d["por_mes"].get(m, {"mto": 0.0, "comp2": 0.0})
                    fila_aud.append(f"{v['mto']:,.2f}")
                    fila_aud.append(f"{v['comp2']:,.2f}")
                fila_aud.append(f"{d['tot_mto']:,.2f}")
                fila_aud.append(f"{d['tot_comp2']:,.2f}")
                tree.insert(parent, "end", values=fila_aud, tags=("auditor",))
                total_rows += 1

            total_general_mto += datos_sup["tot_mto"]
            total_general_comp2 += datos_sup["tot_comp2"]

        fila_total = ["TOTAL GENERAL", ""]
        for m in meses:
            mto_t = sum(
                estructura[s]["aud"][x]["por_mes"].get(m, {}).get("mto", 0.0)
                for s in estructura for x in estructura[s]["aud"]
            )
            comp2_t = sum(
                estructura[s]["aud"][x]["por_mes"].get(m, {}).get("comp2", 0.0)
                for s in estructura for x in estructura[s]["aud"]
            )
            fila_total.append(f"{mto_t:,.2f}")
            fila_total.append(f"{comp2_t:,.2f}")
        fila_total.append(f"{total_general_mto:,.2f}")
        fila_total.append(f"{total_general_comp2:,.2f}")
        tree.insert("", "end", values=fila_total, tags=("total",))

        tree.config(height=min(total_rows + 4, 25))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree.tag_configure("supervisor", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree.tag_configure("auditor", background="white", font=("Segoe UI", 10))
        tree.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

    combo_sip05.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_sip05.get(), combo_estado.get()))
    combo_estado.bind("<<ComboboxSelected>>", lambda e: cargar_tabla(combo_sip05.get(), combo_estado.get()))

    cargar_tabla(combo_sip05.get(), combo_estado.get())

#---------------------------------------------------------------------
#STOCK DE ORDENES DE FISCALIZACIÓN- INDICADOR
def generar_tabla_stock_indicador(parent_frame, conexion=None):
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=10)

    ctk.CTkLabel(
        filtro_frame,
        text="📁 Estado OF:",
        font=("Segoe UI", 12, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(12, 4))
    combo_desest = ttk.Combobox(filtro_frame, state="readonly", width=28, font=("Segoe UI", 11))
    combo_desest.pack(side="left", padx=6)

    ctk.CTkLabel(
        filtro_frame,
        text="Estado:",
        font=("Segoe UI", 12, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(12, 4))
    combo_estado = ttk.Combobox(filtro_frame, state="readonly", width=16, font=("Segoe UI", 11))
    combo_estado.pack(side="left", padx=6)

    ctk.CTkLabel(
        filtro_frame,
        text="Stock AUD 25:",
        font=("Segoe UI", 12, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(12, 4))
    combo_stock = ttk.Combobox(filtro_frame, state="readonly", width=10, font=("Segoe UI", 11))
    combo_stock.pack(side="left", padx=6)

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=12)

    datos_actuales = {
        "df_completo": None,
        "tabla_formateada": None,
        "desest_filtrado": None,
        "estado_filtrado": None,
        "stock_filtrado": None
    }

    try:
        df_desest = ejecutar_read_sql("SELECT DISTINCT IFNULL(des_est_of,'') AS des_est_of FROM fiscalizaciones1;", conexion)
        desest_vals = sorted([str(x).strip() for x in df_desest["des_est_of"].tolist() if str(x).strip()])
    except Exception:
        desest_vals = []
    combo_desest["values"] = ["Todos"] + desest_vals
    combo_desest.set("Todos")

    try:
        df_estado = ejecutar_read_sql("SELECT DISTINCT IFNULL(Estado,'') AS Estado FROM fiscalizaciones1;", conexion)
        estado_vals = sorted([str(x).strip() for x in df_estado["Estado"].tolist() if str(x).strip()])
    except Exception:
        estado_vals = []
    combo_estado["values"] = ["Todos"] + estado_vals
    if "Pendiente" in estado_vals:
        combo_estado.set("Pendiente")
    elif estado_vals:
        combo_estado.set(estado_vals[0])
    else:
        combo_estado.set("Todos")

    try:
        df_stock = ejecutar_read_sql("SELECT DISTINCT IFNULL(Stock_AUD_25,'') AS Stock_AUD_25 FROM fiscalizaciones1;", conexion)
        stock_vals = sorted([str(x).strip() for x in df_stock["Stock_AUD_25"].tolist() if str(x).strip()])
    except Exception:
        stock_vals = []
    stock_base = ["1", "2", "3"]
    for s in stock_vals:
        if s not in stock_base:
            stock_base.append(s)
    combo_stock["values"] = ["Todos"] + stock_base
    combo_stock.set("1, 2, 3")

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            desest_sel = datos_actuales["desest_filtrado"]
            estado_sel = datos_actuales["estado_filtrado"]
            stock_sel = datos_actuales["stock_filtrado"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"Stock_Indicador_{desest_sel}_{estado_sel}_{stock_sel}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:
                return

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_tabla(desest_sel, estado_sel, stock_sel):
        datos_actuales["desest_filtrado"] = desest_sel
        datos_actuales["estado_filtrado"] = estado_sel
        datos_actuales["stock_filtrado"] = stock_sel

        for w in tabla_frame.winfo_children():
            w.destroy()

        def esc(s):
            return str(s).replace("'", "''").strip()

        stock_condition = ""
        stock_sel_text = str(stock_sel).strip()
        if stock_sel_text and stock_sel_text.lower() != "todos":
            stock_items = [it.strip() for it in stock_sel_text.split(",") if it.strip()]
            if stock_items:
                if len(stock_items) == 1:
                    stock_val = esc(stock_items[0])
                    stock_condition = f"AND UPPER(IFNULL(Stock_AUD_25,'')) = UPPER('{stock_val}')"
                else:
                    stock_vals_escaped = ",".join([f"'{esc(i)}'" for i in stock_items])
                    stock_condition = f"AND UPPER(IFNULL(Stock_AUD_25,'')) IN ({stock_vals_escaped})"

        query_completo = f"""
            SELECT * FROM fiscalizaciones1
            WHERE LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
              AND ('{esc(desest_sel)}' = 'Todos' OR IFNULL(des_est_of,'') = '{esc(desest_sel)}')
              AND ('{esc(estado_sel)}' = 'Todos' OR IFNULL(Estado,'') = '{esc(estado_sel)}')
              {stock_condition};
        """

        query = f"""
            SELECT NOMBRE_SUPERVISOR, NOMBRE_AUDITOR, NUM_ORD_FI, Estado, Stock_AUD_25
            FROM fiscalizaciones1
            WHERE LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
              AND ('{esc(desest_sel)}' = 'Todos' OR IFNULL(des_est_of,'') = '{esc(desest_sel)}')
              AND ('{esc(estado_sel)}' = 'Todos' OR IFNULL(Estado,'') = '{esc(estado_sel)}')
              {stock_condition};
        """

        try:
            df = ejecutar_read_sql(query, conexion)
            df_completo = ejecutar_read_sql(query_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            ctk.CTkLabel(tabla_frame, text="⚠ No hay datos con los filtros seleccionados.", text_color="red").pack(pady=15)
            return

        df["Stock_AUD_25"] = df["Stock_AUD_25"].astype(str).str.strip()
        df["NOMBRE_SUPERVISOR"] = df["NOMBRE_SUPERVISOR"].astype(str).str.strip()
        df["NOMBRE_AUDITOR"] = df["NOMBRE_AUDITOR"].astype(str).str.strip()

        pivot = pd.pivot_table(
            df,
            index=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"],
            columns="Stock_AUD_25",
            values="NUM_ORD_FI",
            aggfunc="count",
            fill_value=0
        )

        try:
            pivot.columns = sorted(pivot.columns, key=lambda x: int(x) if str(x).isdigit() else str(x))
        except:
            pivot.columns = sorted(pivot.columns)

        pivot["Total"] = pivot.sum(axis=1)
        total_general = pivot.sum(axis=0)
        pivot_reset = pivot.reset_index()

        # Crear tabla formateada
        tabla_formateada_rows = []
        
        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]).sum(axis=0)
            
            row_sup = {"Supervisor": supervisor, "Auditor": ""}
            for c in pivot.columns:
                row_sup[str(c)] = int(subtotal.get(c, 0))
            tabla_formateada_rows.append(row_sup)
            
            for _, row in df_sup.iterrows():
                row_aud = {"Supervisor": "", "Auditor": row["NOMBRE_AUDITOR"]}
                for c in pivot.columns:
                    row_aud[str(c)] = int(row.get(c, 0))
                tabla_formateada_rows.append(row_aud)
        
        row_total = {"Supervisor": "TOTAL GENERAL", "Auditor": ""}
        for c in pivot.columns:
            row_total[str(c)] = int(total_general.get(c, 0))
        tabla_formateada_rows.append(row_total)

        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        frame_tabla_inner = ctk.CTkFrame(tabla_frame, corner_radius=15, fg_color="#ffffff")
        frame_tabla_inner.pack(fill="both", expand=True, padx=10, pady=8)

        ctk.CTkLabel(frame_tabla_inner,
                     text="📊 STOCK DE ORDENES DE FISCALIZACIÓN - INDICADOR",
                     font=("Segoe UI", 14, "bold"),
                     text_color="#a51c30").pack(anchor="w", padx=12, pady=6)

        container = ctk.CTkFrame(frame_tabla_inner, fg_color="white")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        cols = ["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"] + list(pivot.columns)
        tree_local = ttk.Treeview(container, columns=cols, show="headings")
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
        tree_local.configure(yscrollcommand=vsb.set)
        tree_local.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for col in cols:
            if col == "NOMBRE_SUPERVISOR":
                text, width = "Supervisor", 220
            elif col == "NOMBRE_AUDITOR":
                text, width = "Auditor", 180
            elif col == "Total":
                text, width = "Total", 90
            else:
                text, width = col, 65
            tree_local.heading(col, text=text)
            tree_local.column(col, width=width, anchor="center")

        total_filas = 0
        for supervisor in pivot_reset["NOMBRE_SUPERVISOR"].unique():
            df_sup = pivot_reset[pivot_reset["NOMBRE_SUPERVISOR"] == supervisor]
            subtotal = df_sup.drop(columns=["NOMBRE_SUPERVISOR", "NOMBRE_AUDITOR"]).sum(axis=0)
            parent_vals = [supervisor, ""] + [int(subtotal.get(c, 0)) for c in pivot.columns]
            parent = tree_local.insert("", "end", values=parent_vals, tags=("supervisor",))
            total_filas += 1

            for _, row in df_sup.iterrows():
                child_vals = ["", row["NOMBRE_AUDITOR"]] + [int(row.get(c, 0)) for c in pivot.columns]
                tree_local.insert(parent, "end", values=child_vals, tags=("auditor",))
                total_filas += 1

        total_vals = ["TOTAL GENERAL", ""] + [int(total_general.get(c, 0)) for c in pivot.columns]
        tree_local.insert("", "end", values=total_vals, tags=("total",))
        total_filas += 1

        ajustar_altura_treeview(tree_local, total_filas)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree_local.tag_configure("supervisor", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree_local.tag_configure("auditor", background="white", font=("Segoe UI", 10))
        tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

    cargar_tabla(combo_desest.get(), combo_estado.get(), combo_stock.get())

    def on_filter_change(event=None):
        cargar_tabla(combo_desest.get(), combo_estado.get(), combo_stock.get())

    combo_desest.bind("<<ComboboxSelected>>", on_filter_change)
    combo_estado.bind("<<ComboboxSelected>>", on_filter_change)
    combo_stock.bind("<<ComboboxSelected>>", on_filter_change)

#---------------------------------------------------------------------------------------
#PAGOS REALIZADOS EN OFS
def generar_tabla_pagos_realizados(parent_frame, conexion=None):
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os
    import tkinter as tk
    from tkinter import ttk
    import customtkinter as ctk

    MESES = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
        7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }

    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=10)

    class MultiSelectCombo(ctk.CTkFrame):
        def __init__(self, parent, label_text, opciones, width=170, height=30, callback=None, **kwargs):
            super().__init__(parent, fg_color="#f5f6fa", **kwargs)
            self.callback = callback
            self.opciones = list(opciones)
            self.selected = []
            ctk.CTkLabel(self, text=label_text, font=("Segoe UI", 12, "bold"), text_color="#002e6d").pack(side="left", padx=(12,4))
            self._textvar = tk.StringVar(value="Seleccionar...")
            self.button = ctk.CTkButton(self, textvariable=self._textvar, width=width, height=height,
                                        fg_color="#ffffff", text_color="#000000", anchor="w",
                                        hover_color="#f0f0f0", border_width=1, border_color="#d0d0d0",
                                        corner_radius=6, command=self._toggle_list)
            self.button.pack(side="left", padx=6)
            self.list_frame = ctk.CTkFrame(self, fg_color="#ffffff", corner_radius=8)
            self._vars = {}
            self._var_todos = tk.IntVar(value=0)
            self._build_list(self.opciones)

        def _build_list(self, opciones_lista):
            for w in self.list_frame.winfo_children():
                w.destroy()
            self._vars.clear()
            self.selected.clear()
            def on_todos_change():
                if self._var_todos.get() == 1:
                    for k, v in self._vars.items():
                        v.set(1)
                    self.selected[:] = list(self._vars.keys())
                else:
                    for k, v in self._vars.items():
                        v.set(0)
                    self.selected[:] = []
                self._update_text()
            chk_all = ctk.CTkCheckBox(self.list_frame, text="Todos", variable=self._var_todos, command=on_todos_change, font=("Segoe UI", 11))
            chk_all.pack(anchor="w", padx=8, pady=3)
            for val in opciones_lista:
                v = tk.IntVar(value=0)
                def make_cmd(value=val, var=v):
                    def cmd():
                        if var.get() == 1:
                            if value not in self.selected:
                                self.selected.append(value)
                        else:
                            if value in self.selected:
                                self.selected.remove(value)
                        if self._var_todos.get() == 1 and len(self.selected) != len(opciones_lista):
                            self._var_todos.set(0)
                        self._update_text()
                    return cmd
                chk = ctk.CTkCheckBox(self.list_frame, text=str(val), variable=v, command=make_cmd(), font=("Segoe UI", 11))
                chk.pack(anchor="w", padx=12, pady=2)
                self._vars[val] = v

        def _toggle_list(self):
            if self.list_frame.winfo_ismapped():
                self.list_frame.pack_forget()
            else:
                self.list_frame.pack(fill="both", pady=(6,6))
        def _update_text(self):
            if not self.selected:
                self._textvar.set("Seleccionar...")
            elif len(self.selected) == len(self.opciones):
                self._textvar.set("Todos")
            else:
                text = ", ".join(self.selected)
                self._textvar.set(text if len(text) <= 30 else text[:27] + "...")
            if self.callback:
                try:
                    self.callback(self.selected)
                except Exception:
                    pass
        def rebuild_options(self, nuevas_opciones):
            self.opciones = list(nuevas_opciones)
            self._var_todos.set(0)
            self._build_list(self.opciones)
            self._update_text()
        def get_selected(self):
            return list(self.selected)

    def obtener_opciones(col):
        try:
            df = ejecutar_read_sql(f"SELECT DISTINCT IFNULL({col},'') AS v FROM fiscalizaciones2;", conexion)
            vals = sorted([str(x).strip() for x in df["v"].tolist() if str(x).strip()])
            return vals
        except Exception:
            return []

    opciones_reimputado = obtener_opciones("reimputado")
    opciones_des_ai = obtener_opciones("des_ai")
    opciones_corriente = obtener_opciones("corriente")

    ms_reimputado = MultiSelectCombo(filtro_frame, "Reimputado:", opciones_reimputado, width=180,
                                     callback=lambda sel: cargar_tabla_wrapper())
    ms_reimputado.pack(side="left", padx=0)

    ms_des_ai = MultiSelectCombo(filtro_frame, "Des AI:", opciones_des_ai, width=180,
                                 callback=lambda sel: cargar_tabla_wrapper())
    ms_des_ai.pack(side="left", padx=0)

    ms_corriente = MultiSelectCombo(filtro_frame, "Corriente:", opciones_corriente, width=140,
                                    callback=lambda sel: cargar_tabla_wrapper())
    ms_corriente.pack(side="left", padx=0)

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=12)

    datos_actuales = {
        "df_completo": None,
        "tabla_formateada": None,
        "reimputado_filtrado": None,
        "des_ai_filtrado": None,
        "corriente_filtrado": None
    }

    def esc(s):
        return str(s).replace("'", "''")
    def lista_a_in(lista):
        if not lista:
            return None
        items = [f"'{esc(x)}'" for x in lista]
        return ",".join(items)

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            reimp_sel = datos_actuales["reimputado_filtrado"]
            desai_sel = datos_actuales["des_ai_filtrado"]
            corr_sel = datos_actuales["corriente_filtrado"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            reimp_txt = "_".join(reimp_sel) if reimp_sel else "Todos"
            desai_txt = "_".join(desai_sel) if desai_sel else "Todos"
            corr_txt = "_".join(corr_sel) if corr_sel else "Todos"
            
            filename_default = f"Pagos_Realizados_{reimp_txt}_{desai_txt}_{corr_txt}_{timestamp}.xlsx"

            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:
                return

            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    def cargar_tabla_wrapper():
        cargar_tabla()

    def cargar_tabla():
        for w in tabla_frame.winfo_children():
            w.destroy()

        sel_reimputado = ms_reimputado.get_selected()
        sel_des_ai = ms_des_ai.get_selected()
        sel_corriente = ms_corriente.get_selected()

        datos_actuales["reimputado_filtrado"] = sel_reimputado
        datos_actuales["des_ai_filtrado"] = sel_des_ai
        datos_actuales["corriente_filtrado"] = sel_corriente

        conds = []
        in_reimputado = lista_a_in(sel_reimputado)
        if in_reimputado:
            conds.append(f"reimputado IN ({in_reimputado})")
        in_desai = lista_a_in(sel_des_ai)
        if in_desai:
            conds.append(f"des_ai IN ({in_desai})")
        in_corr = lista_a_in(sel_corriente)
        if in_corr:
            conds.append(f"corriente IN ({in_corr})")

        where_clause = ("WHERE " + " AND ".join(conds)) if conds else ""

        query_completo = f"""
            SELECT * FROM fiscalizaciones2
            {where_clause}
        """

        query = f"""
            SELECT des_func, MES, SUM(COALESCE(MTO_PAG,0)) AS MTO_PAG
            FROM fiscalizaciones2
            {where_clause}
            GROUP BY des_func, MES
            ORDER BY des_func, MES;
        """

        try:
            df = ejecutar_read_sql(query, conexion)
            df_completo = ejecutar_read_sql(query_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df is None or df.empty:
            ctk.CTkLabel(tabla_frame, text="⚠ No hay datos para los filtros seleccionados.", text_color="red").pack(pady=15)
            return

        df["MES"] = pd.to_numeric(df["MES"], errors="coerce").fillna(0).astype(int)
        df["MTO_PAG"] = pd.to_numeric(df["MTO_PAG"], errors="coerce").fillna(0)
        df["des_func"] = df["des_func"].astype(str).fillna("").str.strip()

        pivot = pd.pivot_table(
            df,
            index="des_func",
            columns="MES",
            values="MTO_PAG",
            aggfunc="sum",
            fill_value=0
        )

        meses_numeros = list(range(1,13))
        pivot = pivot.reindex(columns=meses_numeros, fill_value=0)
        pivot.rename(columns=MESES, inplace=True)

        pivot["Total"] = pivot.sum(axis=1)
        total_general = pivot.sum(axis=0)
        pivot_reset = pivot.reset_index()

        # Crear tabla formateada
        tabla_formateada_rows = []
        
        for _, row in pivot_reset.iterrows():
            row_data = {"Función": row["des_func"]}
            for c in pivot.columns:
                row_data[c] = row.get(c, 0)
            tabla_formateada_rows.append(row_data)
        
        row_total = {"Función": "TOTAL GENERAL"}
        for c in pivot.columns:
            row_total[c] = total_general.get(c, 0)
        tabla_formateada_rows.append(row_total)

        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        frame_tabla_inner = ctk.CTkFrame(tabla_frame, corner_radius=15, fg_color="#ffffff")
        frame_tabla_inner.pack(fill="both", expand=True, padx=10, pady=8)

        ctk.CTkLabel(frame_tabla_inner,
                     text=f"💰 PAGOS REALIZADOS EN OFS",
                     font=("Segoe UI", 14, "bold"),
                     text_color="#a51c30").pack(anchor="w", padx=12, pady=6)

        container = ctk.CTkFrame(frame_tabla_inner, fg_color="white")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        cols = ["des_func"] + list(pivot.columns)
        tree_local = ttk.Treeview(container, columns=cols, show="headings")
        vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
        tree_local.configure(yscrollcommand=vsb.set)
        tree_local.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        for col in cols:
            if col == "des_func":
                text, width = "Función", 280
            elif col == "Total":
                text, width = "Total", 110
            else:
                text, width = col, 75
            tree_local.heading(col, text=text)
            tree_local.column(col, width=width, anchor="center")

        total_filas = 0
        for _, row in pivot_reset.iterrows():
            vals = [row["des_func"]] + [f"{row.get(c,0):,.2f}" for c in pivot.columns]
            tree_local.insert("", "end", values=vals, tags=("normal",))
            total_filas += 1

        total_vals = ["TOTAL GENERAL"] + [f"{total_general.get(c,0):,.2f}" for c in pivot.columns]
        tree_local.insert("", "end", values=total_vals, tags=("total",))
        total_filas += 1

        ajustar_altura_treeview(tree_local, total_filas)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))
        tree_local.tag_configure("normal", background="white", font=("Segoe UI", 10))

    cargar_tabla()
# ==========================
# DASHBOARD RESULTADOS DE OF PARA SUPERVISORES con SCROLL
# ==========================
def dashboard_supervisores():
    ocultar_menu()

    try:
        preview_frame.pack_forget()
    except Exception:
        pass
    dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)

    for widget in dashboard_frame.winfo_children():
        widget.destroy()

    if "banner_supervisores_path" in config:
        mostrar_banner_supervisores(config["banner_supervisores_path"])

    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql("SELECT * FROM fiscalizaciones1", DB_ENGINE)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el dashboard:\n{e}")
        return

    # ====================
    # CONTENEDOR CON SCROLL
    # ====================
    scroll_container = ctk.CTkFrame(dashboard_frame, fg_color=COLOR_WHITE)
    scroll_container.pack(fill="both", expand=True, padx=15, pady=15)

    canvas = tk.Canvas(scroll_container, bg=COLOR_WHITE, highlightthickness=0)
    vscroll = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)

    # 🎨 Scrollbar pastel
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Vertical.TScrollbar",
                    background="#cce7f0",
                    troughcolor="#eaf6fb",
                    arrowcolor="#4a4a4a",
                    gripcount=0,
                    relief="flat")

    canvas.configure(yscrollcommand=vscroll.set)

    vscroll.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # usar un Frame de tkinter (no CTkFrame) dentro del canvas suele ser más estable
    inner_frame = tk.Frame(canvas, bg=COLOR_WHITE)
    canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    def _on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        try:
            canvas.itemconfig(canvas_window, width=event.width)
        except Exception:
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        canvas.update_idletasks()

    inner_frame.bind("<Configure>", _on_frame_configure)

    # permitir scroll con rueda del mouse (multiplataforma)
    def _on_mousewheel(event):
        if event.delta:  # Windows / MacOS
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:  # Linux (event.num)
            if event.num == 5:
                canvas.yview_scroll(1, "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", _on_mousewheel)
    canvas.bind_all("<Button-5>", _on_mousewheel)

    # ====================
    # MÉTRICAS + ÍNDICE LATERAL (arriba)
    # ====================
    top_container = ctk.CTkFrame(inner_frame, fg_color=COLOR_WHITE)
    top_container.pack(pady=15, padx=15, fill="x")

    # Frame para métricas (lado izquierdo)
    metrics_frame = ctk.CTkFrame(top_container, fg_color=COLOR_WHITE, corner_radius=15)
    metrics_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

    # Frame para índice (lado derecho) - mantenemos en el top para que esté visible arriba
    # Hacer el panel índice más ancho para mostrar mejor los nombres
    index_frame = ctk.CTkFrame(top_container, fg_color="#f7f9fb", corner_radius=12, width=240)
    # Evitar que el contenido reduzca el tamaño del frame: mantener el ancho fijo
    try:
        index_frame.pack_propagate(False)
    except Exception:
        pass
    index_frame.pack(side="right", anchor="n", pady=2, padx=(10,0))

    # función para crear cards de métricas
    def crear_card(parent, icono, texto, valor, color_fondo, color_hover):
        frame = ctk.CTkFrame(parent, corner_radius=15, fg_color=color_fondo)
        frame.pack(side="left", padx=12, pady=10, ipadx=16, ipady=10)

        def on_enter(e): frame.configure(fg_color=color_hover)
        def on_leave(e): frame.configure(fg_color=color_fondo)
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)

        ctk.CTkLabel(frame, text=icono, font=("Segoe UI Emoji", 26)).grid(row=0, column=0, rowspan=2, padx=8)
        ctk.CTkLabel(frame, text=texto, font=("Segoe UI", 11, "bold")).grid(row=0, column=1, sticky="w", pady=(6,0))
        ctk.CTkLabel(frame, text=str(valor), font=("Segoe UI", 16, "bold")).grid(row=1, column=1, sticky="w")
        return frame

    # === métricas calculadas ===
    total_of = len(df)
    total_supervisores = df["NOMBRE_SUPERVISOR"].nunique() if "NOMBRE_SUPERVISOR" in df.columns else 0
    of_cerradas = df[df["Estado"].str.upper() == "TERMINADO"].shape[0] if "Estado" in df.columns else 0
    of_pendientes = df[df["Estado"].str.upper() == "PENDIENTE"].shape[0] if "Estado" in df.columns else 0

    crear_card(metrics_frame, "📊", "Total OF", total_of, "#c2e9fb", "#90cdf4")
    crear_card(metrics_frame, "👨‍💼", "Supervisores", total_supervisores, "#d4a5f9", "#b784f2")
    crear_card(metrics_frame, "✅", "Cerradas", of_cerradas, "#a3f7bf", "#7ae3a1")
    crear_card(metrics_frame, "⏳", "Pendientes", of_pendientes, "#fcd5ce", "#f8a29e")

    # ====================
    # PANEL ÍNDICE (botones) - se coloca en index_frame
    # ====================
    # 🔹 Aumentar el ancho visible del índice de tablas
    # --- Índice de Tablas (2 columnas) ---
# ====================
    # PANEL ÍNDICE (botones) - Organizado por grupos en 2 columnas
    # ====================
    index_frame.configure(width=700)
    index_frame.pack_propagate(False)

    ctk.CTkLabel(index_frame, text="📚 Índice de Tablas", font=("Segoe UI", 14, "bold")).pack(pady=(10,8))

    # contenedor con scrollbar propio para el índice
    idx_container = tk.Frame(index_frame, bg="#f7f9fb")
    idx_container.pack(fill="both", expand=True, padx=10, pady=(0,8))

    idx_canvas = tk.Canvas(idx_container, bg="#f7f9fb", highlightthickness=0, height=300)
    idx_v = ttk.Scrollbar(idx_container, orient="vertical", command=idx_canvas.yview)
    idx_v.pack(side="right", fill="y")
    idx_canvas.pack(side="left", fill="both", expand=True)
    idx_canvas.configure(yscrollcommand=idx_v.set)

    idx_inner = tk.Frame(idx_canvas, bg="#f7f9fb")
    idx_window = idx_canvas.create_window((0,0), window=idx_inner, anchor="nw")

    def _idx_config(e):
        idx_canvas.configure(scrollregion=idx_canvas.bbox("all"))
        try:
            idx_canvas.itemconfig(idx_window, width=e.width)
        except Exception:
            pass

    idx_inner.bind("<Configure>", _idx_config)
    idx_container.bind("<Configure>", _idx_config)

    # Configurar 2 columnas iguales
    idx_inner.grid_columnconfigure(0, weight=1, uniform="col")
    idx_inner.grid_columnconfigure(1, weight=1, uniform="col")

    # mapping nombre -> frame objeto
    tablas_frames = {}

    # función que desplaza el canvas principal hacia el frame objetivo
    def ir_a_tabla(nombre):
        target = tablas_frames.get(nombre)
        if not target:
            return
        inner_frame.update_idletasks()
        target.update_idletasks()

        target_y = target.winfo_y()
        inner_h = inner_frame.winfo_height()
        canvas_h = canvas.winfo_height()

        max_scroll = max(1, inner_h - canvas_h)
        fraction = target_y / max_scroll
        fraction = max(0.0, min(1.0, fraction))
        try:
            canvas.yview_moveto(fraction)
        except Exception:
            try:
                target.focus_set()
            except Exception:
                pass

    # helper para crear un grupo completo
    def crear_grupo(parent, row, col, titulo, icono, color_bg, lista_tablas):
        # Frame contenedor del grupo
        grupo_frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=10)
        grupo_frame.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
        
        # Título del grupo
        titulo_frame = ctk.CTkFrame(grupo_frame, fg_color=color_bg, corner_radius=8)
        titulo_frame.pack(fill="x", padx=8, pady=8)
        
        label = ctk.CTkLabel(
            titulo_frame, 
            text=f"{icono}  {titulo}", 
            font=("Segoe UI", 11, "bold"),
            text_color="#01579b"
        )
        label.pack(pady=6)
        
        # Botones del grupo
        for nombre_tabla in lista_tablas:
            btn = ctk.CTkButton(
                grupo_frame,
                text=nombre_tabla,
                height=30,
                corner_radius=6,
                fg_color="#ffffff",
                hover_color="#d3eeff",
                text_color="#003366",
                border_width=1,
                border_color="#cce7ff",
                anchor="w",
                font=("Segoe UI", 9),
                command=lambda n=nombre_tabla: ir_a_tabla(n)
            )
            btn.pack(fill="x", padx=8, pady=3)
        
        # Espaciador al final
        ctk.CTkLabel(grupo_frame, text="", height=5).pack()

    # ====================
    # GRUPO 1: Gestión de Órdenes de Fiscalización (Columna 0, Fila 0)
    # ====================
    crear_grupo(
        idx_inner, 
        row=0, 
        col=0,
        titulo="Gestión de Órdenes", 
        icono="📋", 
        color_bg="#e8f5e9",
        lista_tablas=[
            "OF Asignadas",
            "OF Determinadas",
            "OF No Determinativas",
            "OF Determinativas - Pendientes",
            "OF No Determinativas - Pendientes"
        ]
    )

    # ====================
    # GRUPO 2: Rendimiento y Pagos Realizados (Columna 1, Fila 0)
    # ====================
    crear_grupo(
        idx_inner, 
        row=0, 
        col=1,
        titulo="Rendimiento y Pagos", 
        icono="💰", 
        color_bg="#fff3e0",
        lista_tablas=[
            "Rendimiento Terminadas",
            "Pagos Realizados"
        ]
    )

    # ====================
    # GRUPO 3: Gestión de Indicadores (Columna 0, Fila 1, span 2 columnas)
    # ====================
    crear_grupo(
        idx_inner, 
        row=1, 
        col=0,
        titulo="Gestión de Indicadores", 
        icono="📊", 
        color_bg="#f3e5f5",
        lista_tablas=[
            "SIP 05",
            "SIP 05 - OF Terminada",
            "SIP 05 - Monto OF Terminada",
            "Stock Indicador"
        ]
    )
    
    # Hacer que el grupo 3 ocupe las 2 columnas
    idx_inner.grid_rowconfigure(1, weight=1)

    # ====================
    # TABLAS (dentro del scroll) — aquí añadimos frames y guardamos en tablas_frames
    # ====================
    try:
        frame_asignadas = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_asignadas.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_asignadas(frame_asignadas, conexion=conn, anio=2025)
        tablas_frames["OF Asignadas"] = frame_asignadas
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla OF Asignadas:\n{e}")

    try:
        frame_determinadas = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_determinadas.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_determinadas(frame_determinadas, conexion=conn, cod_tipact_default="06", anio_default=2025)
        tablas_frames["OF Determinadas"] = frame_determinadas
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla OF Determinadas:\n{e}")

    try:
        frame_no_determinativas = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_no_determinativas.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_no_determinativas(frame_no_determinativas, conexion=conn)
        tablas_frames["OF No Determinativas"] = frame_no_determinativas
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla OF NO DETERMINATIVAS:\n{e}")

    try:
        frame_determinativas_pendientes = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_determinativas_pendientes.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_determinativas_pendientes(frame_determinativas_pendientes, conexion=conn)
        tablas_frames["OF Determinativas - Pendientes"] = frame_determinativas_pendientes
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla OF DETERMINATIVAS - PENDIENTES:\n{e}")

    try:
        frame_no_determinativas_pendientes = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_no_determinativas_pendientes.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_no_determinativas_pendientes(frame_no_determinativas_pendientes, conexion=conn)
        tablas_frames["OF No Determinativas - Pendientes"] = frame_no_determinativas_pendientes
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla OF NO DETERMINATIVAS - PENDIENTES:\n{e}")

    try:
        frame_rendimiento_terminadas = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_rendimiento_terminadas.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_rendimiento_terminadas(frame_rendimiento_terminadas, conexion=conn, anio_default=2025)
        tablas_frames["Rendimiento Terminadas"] = frame_rendimiento_terminadas
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla RENDIMIENTO DE OFS TERMINADAS:\n{e}")

    # SIP 05 - general
    try:
        frame_sip05_general = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_sip05_general.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_sip05(frame_sip05_general, conexion=conn)
        tablas_frames["SIP 05"] = frame_sip05_general
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla SIP 05:\n{e}")

    # SIP 05 - OF terminada
    try:
        frame_sip05_terminada = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_sip05_terminada.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_sip05_terminada(frame_sip05_terminada, conexion=conn)
        tablas_frames["SIP 05 - OF Terminada"] = frame_sip05_terminada
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla SIP 05 - OF TERMINADA:\n{e}")

    # SIP 05 - monto de OF terminada
    try:
        frame_sip05_monto = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_sip05_monto.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_sip05_monto_of_terminada(frame_sip05_monto, conexion=conn)
        tablas_frames["SIP 05 - Monto OF Terminada"] = frame_sip05_monto
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla SIP 05 - MONTO DE OF TERMINADA:\n{e}")

    # STOCK INDICADOR
    try:
        frame_stock_indicador = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_stock_indicador.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_stock_indicador(frame_stock_indicador, conexion=conn)
        tablas_frames["Stock Indicador"] = frame_stock_indicador
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla STOCK DE ORDENES DE FISCALIZACIÓN - INDICADOR:\n{e}")

    # PAGOS REALIZADOS
    try:
        frame_pagos_realizados = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_pagos_realizados.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_pagos_realizados(frame_pagos_realizados, conexion=conn)
        tablas_frames["Pagos Realizados"] = frame_pagos_realizados
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla PAGOS REALIZADOS EN OFS:\n{e}")

    # ====================
    # Hover en encabezados de tablas (Treeview)
    # ====================
    style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"), foreground="white", background="#002855")
    style.map("Treeview.Heading",
              foreground=[("active", "black")],
              background=[("active", "#f0f0f0")])

    # ====================
    # Forzar redraw (varias pasadas)
    # ====================
    def _force_redraw():
        try:
            # Verificar que los widgets todavía existen antes de actualizarlos
            if canvas.winfo_exists() and inner_frame.winfo_exists():
                inner_frame.update_idletasks()
                canvas.itemconfig(canvas_window, width=canvas.winfo_width())
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.update()
                canvas.yview_moveto(0)
        except Exception:
            pass

    # Guardar IDs de los callbacks para poder cancelarlos si es necesario
    try:
        if canvas.winfo_exists():
            canvas.after(50, _force_redraw)
            canvas.after(200, _force_redraw)
            canvas.after(500, _force_redraw)
            _force_redraw()
    except Exception:
        pass

    conn.close()


# ================================================================
# TABLAS ACCIONES INDUCTIVAS
# ================================================================
def generar_tabla_AI_asignadas(parent_frame, conexion=None, anio=None):
    """
    Genera la vista 'AIs ASIGNADAS' a partir de la tabla fiscalizaciones3.
    Agrupa por DES_TIPO_AI (nivel padre) y DES_NOMB_SUP (nivel hijo),
    contabilizando COD_ACC_IN por mes (Mes_Emis). 
    Mantiene diseño original; cambia color del título a azul.
    """
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    MESES = {
        1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr",
        5: "May", 6: "Jun", 7: "Jul", 8: "Ago",
        9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"
    }

    # === Filtro de año ===
    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=10)

    ctk.CTkLabel(
        filtro_frame,
        text="📅 Año de emisión:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(10, 4))

    anio_button_text = tk.StringVar(value="2025")
    btn_anios = ctk.CTkButton(filtro_frame, textvariable=anio_button_text, width=140,
                              command=lambda: toggle_dropdown_anios())
    btn_anios.pack(side="left", padx=(0, 8))

    dropdown_win = {"win": None}
    check_vars = {}
    available_years = []

    # Botón de exportación
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=12)

    # Variable para almacenar los datos actuales
    datos_actuales = {
        "df_completo": None,  # Datos completos con todas las columnas
        "tabla_formateada": None,  # Tabla tal como se ve en pantalla
        "años_filtrados": None
    }

    # === Obtener años disponibles ===
    try:
        años_df = ejecutar_read_sql(
            "SELECT DISTINCT Anio_Emis FROM fiscalizaciones3 WHERE Anio_Emis IS NOT NULL ORDER BY Anio_Emis DESC;",
            conexion
        )
        años = [int(x) for x in años_df["Anio_Emis"].tolist()] if not años_df.empty else []
    except Exception as e:
        ctk.CTkLabel(tabla_frame, text=f"⚠ Error cargando años: {e}", text_color="red").pack(pady=15)
        return

    available_years = años

    # Inicializar checkboxes - SOLO 2025 seleccionado por defecto
    check_vars["(Todos)"] = tk.IntVar(value=0)
    for y in available_years:
        # Solo 2025 viene seleccionado
        check_vars[str(y)] = tk.IntVar(value=1 if y == 2025 else 0)

    # ---------------------------- FUNCIONES DEL DROPDOWN (YEARS) ----------------------------
    def abrir_dropdown_anios():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            return

        win = tk.Toplevel(parent_frame)
        dropdown_win["win"] = win
        win.wm_overrideredirect(True)
        win.attributes("-topmost", 1)

        x = btn_anios.winfo_rootx()
        y = btn_anios.winfo_rooty() + btn_anios.winfo_height()
        win.geometry(f"+{x}+{y}")

        frame = tk.Frame(win, bg="white", bd=1, relief="solid")
        frame.pack(fill="both", expand=True)

        var_all = check_vars.get("(Todos)", tk.IntVar(value=0))
        check_vars["(Todos)"] = var_all

        def on_all_toggle():
            val = var_all.get()
            for yr in available_years:
                v = check_vars.get(str(yr))
                if v:
                    v.set(val)
            update_button_label()
            cargar_tabla()

        chk_all = tk.Checkbutton(frame, text="(Todos)", variable=var_all, bg="white", anchor="w",
                                 command=on_all_toggle)
        chk_all.pack(fill="x", padx=8, pady=(6, 2))

        sep = ttk.Separator(frame, orient="horizontal")
        sep.pack(fill="x", padx=6, pady=4)

        for y in available_years:
            key = str(y)
            var = check_vars.get(key, tk.IntVar(value=0))
            check_vars[key] = var

            def make_cmd(k=key, v=var):
                def cmd():
                    if v.get() == 0 and "(Todos)" in check_vars:
                        check_vars["(Todos)"].set(0)
                    if all((check_vars[str(yy)].get() == 1) for yy in available_years):
                        check_vars["(Todos)"].set(1)
                    update_button_label()
                    cargar_tabla()
                return cmd

            chk = tk.Checkbutton(frame, text=key, variable=var, bg="white", anchor="w", command=make_cmd())
            chk.pack(fill="x", padx=8, pady=2)

        def on_focus_out(event):
            if dropdown_win["win"] and not dropdown_win["win"].focus_displayof():
                cerrar_dropdown()
        win.bind("<FocusOut>", on_focus_out)

    def cerrar_dropdown():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            try:
                dropdown_win["win"].destroy()
            except:
                pass
        dropdown_win["win"] = None

    def toggle_dropdown_anios():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            cerrar_dropdown()
        else:
            abrir_dropdown_anios()

    def update_button_label():
        sel = obtener_anios_seleccionados(return_labels=True)
        if sel is None:
            anio_button_text.set("(Todos)")
        else:
            if len(sel) == 1:
                anio_button_text.set(sel[0])
            elif len(sel) <= 3:
                anio_button_text.set(", ".join(sel))
            else:
                anio_button_text.set(f"{len(sel)} seleccionados")

    def obtener_anios_seleccionados(return_labels=False):
        if "(Todos)" in check_vars and check_vars["(Todos)"].get() == 1:
            return None
        selected = [k for k, v in check_vars.items() if k != "(Todos)" and v.get() == 1]
        if not selected:
            return None
        if return_labels:
            return selected
        try:
            return [int(x) for x in selected]
        except:
            return None

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            años_sel = datos_actuales["años_filtrados"]
            años_texto = "_".join(str(a) for a in sorted(años_sel))
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"AIs_Asignadas_{años_texto}_{timestamp}.xlsx"

            # Abrir diálogo para elegir ubicación
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:  # Usuario canceló
                return

            # Crear el archivo Excel con múltiples hojas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja 1: Tabla formateada (como se ve en pantalla)
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                # Hoja 2: Datos completos filtrados (todas las columnas de la BD)
                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                # Ajustar anchos de columnas para ambas hojas
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    # === Función para cargar tabla ===
    def cargar_tabla():
        for w in tabla_frame.winfo_children():
            w.destroy()

        años_sel = obtener_anios_seleccionados()
        
        # Si no hay años seleccionados, usar 2025 por defecto
        if años_sel is None:
            años_sel = available_years
        
        if not años_sel:
            ctk.CTkLabel(tabla_frame, text="⚠ Seleccione al menos un año", text_color="red").pack(pady=15)
            return

        # Guardar años filtrados
        datos_actuales["años_filtrados"] = años_sel

        # Construir query con TODAS las columnas
        años_str = ",".join(str(a) for a in años_sel)
        query = f"""
            SELECT *
            FROM fiscalizaciones3
            WHERE Anio_Emis IN ({años_str});
        """

        try:
            df_completo = ejecutar_read_sql(query, conexion)
        except Exception as e:
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df_completo.empty:
            años_texto = ", ".join(str(a) for a in años_sel)
            ctk.CTkLabel(tabla_frame, text=f"⚠ No hay datos para {años_texto}", text_color="red").pack(pady=15)
            return

        # Guardar datos completos filtrados
        datos_actuales["df_completo"] = df_completo.copy()

        # Trabajar con las columnas necesarias para la visualización
        df = df_completo[["COD_ACC_IN", "DES_NOMB_SUP", "DES_TIPO_AI", "Anio_Emis", "Mes_Emis"]].copy()

        # Limpieza de Mes_Emis
        df["Mes_Emis"] = pd.to_numeric(df["Mes_Emis"], errors="coerce")
        df = df[df["Mes_Emis"].between(1, 12)]

        # Pivot principal
        pivot = pd.pivot_table(
            df,
            index=["DES_TIPO_AI", "DES_NOMB_SUP"],
            columns="Mes_Emis",
            values="COD_ACC_IN",
            aggfunc="count",
            fill_value=0
        )

        meses_numeros = list(range(1, 13))
        pivot = pivot.reindex(columns=meses_numeros, fill_value=0)
        pivot["Total"] = pivot.sum(axis=1)
        total_general = pivot.sum(axis=0)

        rename_map = {m: MESES[m] for m in meses_numeros}
        pivot.rename(columns=rename_map, inplace=True)
        meses_cols = [MESES[m] for m in meses_numeros]
        pivot_reset = pivot.reset_index()

        # Crear tabla formateada para exportar (estructura jerárquica)
        tabla_formateada_rows = []
        
        for tipo_ai in pivot_reset["DES_TIPO_AI"].unique():
            df_tipo = pivot_reset[pivot_reset["DES_TIPO_AI"] == tipo_ai]
            subtotal = df_tipo.drop(columns=["DES_TIPO_AI", "DES_NOMB_SUP"]).sum(axis=0)
            
            # Fila padre (Tipo AI)
            row_tipo = {"Tipo de AI": tipo_ai, "Supervisor": ""}
            for m in meses_cols:
                row_tipo[m] = int(subtotal.get(m, 0))
            row_tipo["Total"] = int(subtotal.get("Total", 0))
            tabla_formateada_rows.append(row_tipo)
            
            # Filas hijas (Supervisores)
            for _, row in df_tipo.iterrows():
                row_sup = {"Tipo de AI": "", "Supervisor": row["DES_NOMB_SUP"]}
                for m in meses_cols:
                    row_sup[m] = int(row.get(m, 0))
                row_sup["Total"] = int(row.get("Total", 0))
                tabla_formateada_rows.append(row_sup)
        
        # Fila total general
        row_total = {"Tipo de AI": "TOTAL GENERAL", "Supervisor": ""}
        for m in meses_numeros:
            row_total[MESES[m]] = int(total_general.get(m, 0))
        row_total["Total"] = int(total_general.get("Total", 0))
        tabla_formateada_rows.append(row_total)
        
        # Convertir a DataFrame
        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        # === Contenedor principal ===
        frame_tabla_inner = ctk.CTkFrame(tabla_frame, corner_radius=15, fg_color="#ffffff")
        frame_tabla_inner.pack(fill="both", expand=True, padx=10, pady=8)

        años_texto = ", ".join(str(a) for a in sorted(años_sel))
        ctk.CTkLabel(frame_tabla_inner,
                     text=f"📊 AIs ASIGNADAS - {años_texto}",
                     font=("Segoe UI", 14, "bold"),
                     text_color="#a51c30").pack(anchor="w", padx=12, pady=6)

        # === Scroll y Treeview ===
        container = ctk.CTkFrame(frame_tabla_inner, fg_color="white")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        cols = ["DES_TIPO_AI", "DES_NOMB_SUP"] + meses_cols + ["Total"]
        tree_local = ttk.Treeview(container, columns=cols, show="headings")

        vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
        tree_local.configure(yscrollcommand=vsb.set)
        tree_local.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        # Encabezados y anchos
        for col in cols:
            if col == "DES_TIPO_AI":
                text, width = "Tipo de AI", 200
            elif col == "DES_NOMB_SUP":
                text, width = "Supervisor", 220
            elif col == "Total":
                text, width = "Total", 90
            else:
                text, width = col, 65
            tree_local.heading(col, text=text)
            tree_local.column(col, width=width, anchor="center")

        total_filas = 0

        # Agrupación: Tipo AI → Supervisores
        for tipo_ai in pivot_reset["DES_TIPO_AI"].unique():
            df_tipo = pivot_reset[pivot_reset["DES_TIPO_AI"] == tipo_ai]
            subtotal = df_tipo.drop(columns=["DES_TIPO_AI", "DES_NOMB_SUP"]).sum(axis=0)
            parent_vals = [tipo_ai, ""] + [int(subtotal.get(m, 0)) for m in meses_cols] + [int(subtotal.get("Total", 0))]
            parent = tree_local.insert("", "end", values=parent_vals, tags=("tipo_ai",))
            total_filas += 1

            for _, row in df_tipo.iterrows():
                child_vals = ["", row["DES_NOMB_SUP"]] + [int(row.get(m, 0)) for m in meses_cols] + [int(row.get("Total", 0))]
                tree_local.insert(parent, "end", values=child_vals, tags=("supervisor",))
                total_filas += 1

        # Total general
        total_vals = ["TOTAL GENERAL", ""] + [int(total_general.get(m, 0)) for m in meses_numeros] + [int(total_general.get("Total", 0))]
        tree_local.insert("", "end", values=total_vals, tags=("total",))
        total_filas += 1

        ajustar_altura_treeview(tree_local, total_filas)

        # === Estilos ===
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree_local.tag_configure("tipo_ai", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree_local.tag_configure("supervisor", background="white", font=("Segoe UI", 10))
        tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

    # === Carga inicial ===
    update_button_label()
    cargar_tabla()
    
def generar_tabla_ai_pendientes(parent_frame, conexion=None, anio_default=2025):
    """
    📊 AIs Pendientes
    Muestra los AIs agrupados por Tipo de AI, Supervisor y Auditor.
    Filtros automáticos con checkboxes. Tabla limpia con Treeview.
    """
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    # ---------------------------- FILTROS ----------------------------
    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=5)

    # ----------------- ESTADO (botón desplegable con checkboxes) -----------------
    ctk.CTkLabel(
        filtro_frame,
        text="🔎 Estado:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(6, 4))

    estado_button_text = tk.StringVar(value="(Todos)")
    btn_estado = ctk.CTkButton(filtro_frame, textvariable=estado_button_text, width=160,
                               command=lambda: toggle_dropdown_estado())
    btn_estado.pack(side="left", padx=(0, 12))

    dropdown_estado_win = {"win": None}
    check_estado_vars = {}
    available_estados = []

    # ----------------- AÑO (botón desplegable con checkboxes) -----------------
    ctk.CTkLabel(
        filtro_frame,
        text="📅 Año:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(4, 6))

    anio_button_text = tk.StringVar(value="(Todos)")
    btn_anios = ctk.CTkButton(filtro_frame, textvariable=anio_button_text, width=140,
                              command=lambda: toggle_dropdown_anios())
    btn_anios.pack(side="left", padx=(0, 8))

    dropdown_win = {"win": None}
    check_vars = {}
    available_years = []

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    # ---------------------------- TÍTULO ----------------------------
    titulo_label = ctk.CTkLabel(
        parent_frame,
        text="📊 AIs Pendientes",
        font=("Segoe UI", 14, "bold"),
        text_color="#a51c30"
    )
    titulo_label.pack(anchor="w", padx=12, pady=(8, 6))

    # ---------------------------- CONTENEDOR DINÁMICO ----------------------------
    contenedor_tabla = {"frame": None}

    # Variable para almacenar los datos actuales
    datos_actuales = {
        "df_completo": None,  # Datos completos con todas las columnas
        "tabla_formateada": None,  # Tabla tal como se ve en pantalla
        "estados_filtrados": None,
        "años_filtrados": None
    }

    # ---------------------------- FUNCIONES DEL DROPDOWN (YEARS) ----------------------------
    def abrir_dropdown_anios():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            return

        win = tk.Toplevel(parent_frame)
        dropdown_win["win"] = win
        win.wm_overrideredirect(True)
        win.attributes("-topmost", 1)

        x = btn_anios.winfo_rootx()
        y = btn_anios.winfo_rooty() + btn_anios.winfo_height()
        win.geometry(f"+{x}+{y}")

        frame = tk.Frame(win, bg="white", bd=1, relief="solid")
        frame.pack(fill="both", expand=True)

        var_all = tk.IntVar(value=1 if (not available_years) else 0)
        check_vars["(Todos)"] = var_all

        def on_all_toggle():
            val = var_all.get()
            for yr in available_years:
                v = check_vars.get(str(yr))
                if v:
                    v.set(val)
            update_button_label()
            cargar_tabla()

        chk_all = tk.Checkbutton(frame, text="(Todos)", variable=var_all, bg="white", anchor="w",
                                 command=on_all_toggle)
        chk_all.pack(fill="x", padx=8, pady=(6, 2))

        sep = ttk.Separator(frame, orient="horizontal")
        sep.pack(fill="x", padx=6, pady=4)

        for y in available_years:
            key = str(y)
            var = check_vars.get(key, tk.IntVar(value=0))
            check_vars[key] = var

            def make_cmd(k=key, v=var):
                def cmd():
                    if v.get() == 0 and "(Todos)" in check_vars:
                        check_vars["(Todos)"].set(0)
                    if all((check_vars[str(yy)].get() == 1) for yy in available_years):
                        check_vars["(Todos)"].set(1)
                    update_button_label()
                    cargar_tabla()
                return cmd

            chk = tk.Checkbutton(frame, text=key, variable=var, bg="white", anchor="w", command=make_cmd())
            chk.pack(fill="x", padx=8, pady=2)

        def on_focus_out(event):
            if dropdown_win["win"] and not dropdown_win["win"].focus_displayof():
                cerrar_dropdown()
        win.bind("<FocusOut>", on_focus_out)

    def cerrar_dropdown():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            try:
                dropdown_win["win"].destroy()
            except:
                pass
        dropdown_win["win"] = None

    def toggle_dropdown_anios():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            cerrar_dropdown()
        else:
            abrir_dropdown_anios()

    def update_button_label():
        sel = obtener_anios_seleccionados(return_labels=True)
        if sel is None:
            anio_button_text.set("(Todos)")
        else:
            if len(sel) == 1:
                anio_button_text.set(sel[0])
            elif len(sel) <= 3:
                anio_button_text.set(", ".join(sel))
            else:
                anio_button_text.set(f"{len(sel)} seleccionados")

    def obtener_anios_seleccionados(return_labels=False):
        if "(Todos)" in check_vars and check_vars["(Todos)"].get() == 1:
            return None
        selected = [k for k, v in check_vars.items() if k != "(Todos)" and v.get() == 1]
        if not selected:
            return None
        if return_labels:
            return selected
        try:
            return [int(x) for x in selected]
        except:
            return None

    # ---------------------------- FUNCIONES DEL DROPDOWN (ESTADOS) ----------------------------
    def abrir_dropdown_estado():
        if dropdown_estado_win["win"] and tk.Toplevel.winfo_exists(dropdown_estado_win["win"]):
            return

        win = tk.Toplevel(parent_frame)
        dropdown_estado_win["win"] = win
        win.wm_overrideredirect(True)
        win.attributes("-topmost", 1)

        x = btn_estado.winfo_rootx()
        y = btn_estado.winfo_rooty() + btn_estado.winfo_height()
        win.geometry(f"+{x}+{y}")

        frame = tk.Frame(win, bg="white", bd=1, relief="solid")
        frame.pack(fill="both", expand=True)

        var_all = tk.IntVar(value=1 if (not available_estados) else 0)
        check_estado_vars["(Todos)"] = var_all

        def on_all_toggle_estado():
            val = var_all.get()
            for est in available_estados:
                v = check_estado_vars.get(est)
                if v:
                    v.set(val)
            update_estado_label()
            cargar_anios_por_estado()
            cargar_tabla()

        chk_all = tk.Checkbutton(frame, text="(Todos)", variable=var_all, bg="white", anchor="w",
                                 command=on_all_toggle_estado)
        chk_all.pack(fill="x", padx=8, pady=(6, 2))

        sep = ttk.Separator(frame, orient="horizontal")
        sep.pack(fill="x", padx=6, pady=4)

        for est in available_estados:
            var = check_estado_vars.get(est, tk.IntVar(value=0))
            check_estado_vars[est] = var

            def make_cmd(e=est, v=var):
                def cmd():
                    if v.get() == 0 and "(Todos)" in check_estado_vars:
                        check_estado_vars["(Todos)"].set(0)
                    if all((check_estado_vars[ee].get() == 1) for ee in available_estados):
                        check_estado_vars["(Todos)"].set(1)
                    update_estado_label()
                    cargar_anios_por_estado()
                    cargar_tabla()
                return cmd

            chk = tk.Checkbutton(frame, text=est, variable=var, bg="white", anchor="w", command=make_cmd())
            chk.pack(fill="x", padx=8, pady=2)

        def on_focus_out(event):
            if dropdown_estado_win["win"] and not dropdown_estado_win["win"].focus_displayof():
                cerrar_dropdown_estado()
        win.bind("<FocusOut>", on_focus_out)

    def cerrar_dropdown_estado():
        if dropdown_estado_win["win"] and tk.Toplevel.winfo_exists(dropdown_estado_win["win"]):
            try:
                dropdown_estado_win["win"].destroy()
            except:
                pass
        dropdown_estado_win["win"] = None

    def toggle_dropdown_estado():
        if dropdown_estado_win["win"] and tk.Toplevel.winfo_exists(dropdown_estado_win["win"]):
            cerrar_dropdown_estado()
        else:
            abrir_dropdown_estado()

    def update_estado_label():
        sel = obtener_estados_seleccionados(return_labels=True)
        if sel is None:
            estado_button_text.set("(Todos)")
        else:
            if len(sel) == 1:
                estado_button_text.set(sel[0])
            elif len(sel) <= 3:
                estado_button_text.set(", ".join(sel))
            else:
                estado_button_text.set(f"{len(sel)} seleccionados")

    def obtener_estados_seleccionados(return_labels=False):
        if "(Todos)" in check_estado_vars and check_estado_vars["(Todos)"].get() == 1:
            return None
        selected = [k for k, v in check_estado_vars.items() if k != "(Todos)" and v.get() == 1]
        if not selected:
            return None
        if return_labels:
            return selected
        return selected

    # ---------------------------- CARGAR OPCIONES ----------------------------
    def cargar_filtros():
        nonlocal available_estados
        try:
            estado_df = ejecutar_read_sql("SELECT DISTINCT Estado FROM fiscalizaciones3 WHERE Estado IS NOT NULL;", conexion)
            estados = sorted([str(x).strip() for x in estado_df["Estado"].tolist() if str(x).strip()])
        except Exception:
            estados = []

        available_estados = estados

        check_estado_vars.clear()
        check_estado_vars["(Todos)"] = tk.IntVar(value=1 if (len(available_estados) == 0) else 0)
        for est in available_estados:
            check_estado_vars[est] = tk.IntVar(value=1 if est == "Pendiente" else 0)

        update_estado_label()
        cargar_anios_por_estado()

    def cargar_anios_por_estado(*_):
        nonlocal available_years
        estados_sel = obtener_estados_seleccionados()
        try:
            if estados_sel:
                estados_list = ",".join(f"'{e}'" for e in estados_sel)
                q = f"SELECT DISTINCT Anio_Emis FROM fiscalizaciones3 WHERE Estado IN ({estados_list}) AND Anio_Emis IS NOT NULL ORDER BY Anio_Emis;"
            else:
                q = "SELECT DISTINCT Anio_Emis FROM fiscalizaciones3 WHERE Anio_Emis IS NOT NULL ORDER BY Anio_Emis;"
            anio_df = ejecutar_read_sql(q, conexion)
            años = [int(x) for x in anio_df["Anio_Emis"].tolist()]
        except Exception:
            años = []

        available_years = años

        check_vars.clear()
        # ✅ CAMBIO: Todos los años seleccionados por defecto
        check_vars["(Todos)"] = tk.IntVar(value=1)
        for y in available_years:
            v = tk.IntVar(value=1)  # ✅ Todos marcados
            check_vars[str(y)] = v

        update_button_label()

        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            cerrar_dropdown()
            abrir_dropdown_anios()

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            estados_sel = datos_actuales["estados_filtrados"]
            años_sel = datos_actuales["años_filtrados"]
            
            # Construir nombre del archivo
            estados_texto = "_".join(estados_sel) if estados_sel else "Todos"
            años_texto = "_".join(str(a) for a in sorted(años_sel)) if años_sel else "Todos"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"AIs_Pendientes_{estados_texto}_{años_texto}_{timestamp}.xlsx"

            # Abrir diálogo para elegir ubicación
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:  # Usuario canceló
                return

            # Crear el archivo Excel con múltiples hojas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja 1: Tabla formateada (como se ve en pantalla)
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                # Hoja 2: Datos completos filtrados (todas las columnas de la BD)
                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                # Ajustar anchos de columnas para ambas hojas
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    # ---------------------------- FUNCIÓN PRINCIPAL CON TREEVIEW ----------------------------
    def cargar_tabla():
        if contenedor_tabla["frame"] is not None:
            contenedor_tabla["frame"].destroy()

        estados_sel = obtener_estados_seleccionados()
        años_sel = obtener_anios_seleccionados()

        # Guardar filtros aplicados
        datos_actuales["estados_filtrados"] = estados_sel if estados_sel else []
        datos_actuales["años_filtrados"] = años_sel if años_sel else []

        # Consulta para datos completos (todas las columnas)
        sql_completo = "SELECT * FROM fiscalizaciones3 WHERE COD_ACC_IN IS NOT NULL"
        
        if estados_sel:
            estados_str = "', '".join(estados_sel)
            sql_completo += f" AND Estado IN ('{estados_str}')"
        if años_sel:
            years_list = ",".join(str(int(y)) for y in años_sel)
            sql_completo += f" AND Anio_Emis IN ({years_list})"

        # Consulta para visualización
        sql = """
            SELECT
                DES_TIPO_AI,
                DES_NOMB_SUP,
                DES_NOMB_VER,
                Anio_Emis,
                Mes_Emis,
                COUNT(COD_ACC_IN) AS Total_AI
            FROM fiscalizaciones3
            WHERE COD_ACC_IN IS NOT NULL
        """

        if estados_sel:
            estados_str = "', '".join(estados_sel)
            sql += f" AND Estado IN ('{estados_str}')"
        if años_sel:
            years_list = ",".join(str(int(y)) for y in años_sel)
            sql += f" AND Anio_Emis IN ({years_list})"

        sql += """
            GROUP BY DES_TIPO_AI, DES_NOMB_SUP, DES_NOMB_VER, Anio_Emis, Mes_Emis
            ORDER BY DES_TIPO_AI, DES_NOMB_SUP, DES_NOMB_VER, Anio_Emis, Mes_Emis;
        """

        try:
            df = ejecutar_read_sql(sql, conexion)
            df_completo = ejecutar_read_sql(sql_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
            tabla_frame.pack(fill="x", padx=15, pady=5)
            contenedor_tabla["frame"] = tabla_frame
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
            tabla_frame.pack(fill="x", padx=15, pady=5)
            contenedor_tabla["frame"] = tabla_frame
            ctk.CTkLabel(tabla_frame, text="⚠ No hay datos para los filtros seleccionados.", text_color="red").pack(pady=15)
            return

        df["Anio_Emis"] = df["Anio_Emis"].fillna(0).astype(int)
        df["Mes_Emis"] = df["Mes_Emis"].fillna(0).astype(int)
        df["Total_AI"] = pd.to_numeric(df["Total_AI"], errors="coerce").fillna(0).astype(int)

        meses_map = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
                     7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

        años = sorted(df["Anio_Emis"].unique().tolist())

        # --------------------- ESTRUCTURA ---------------------
        estructura = {}
        for _, row in df.iterrows():
            tipo, sup, aud = row["DES_TIPO_AI"], row["DES_NOMB_SUP"], row["DES_NOMB_VER"]
            anio, mes, total = row["Anio_Emis"], row["Mes_Emis"], int(row["Total_AI"])
            mes_txt = meses_map.get(mes, str(mes))

            estructura.setdefault(tipo, {}).setdefault(sup, {}).setdefault(aud, {}).setdefault(anio, {})[mes_txt] = total

        # --------------------- COLUMNAS ---------------------
        cols = ["DES_TIPO_AI", "DES_NOMB_SUP", "DES_NOMB_VER"]
        meses_por_anio = {}
        columnas_total_anual = []  # ✅ Para identificar columnas de totales anuales
        
        for a in años:
            meses_con_datos = sorted(df.loc[df["Anio_Emis"] == a, "Mes_Emis"].unique().tolist())
            meses_txt = [meses_map[m] for m in meses_con_datos if m in meses_map]
            meses_por_anio[a] = meses_txt
            for m in meses_txt:
                cols.append(f"{a}-{m}")
            cols.append(f"Total {a}")
            columnas_total_anual.append(f"Total {a}")  # ✅ Guardamos las columnas de total
        cols.append("Total General")

        # Crear tabla formateada para exportación
        tabla_formateada_rows = []
        
        for tipo, supervisores in estructura.items():
            # Fila Tipo AI
            row_tipo = {"Tipo de AI": tipo, "Supervisor": "", "Auditor": ""}
            for a in años:
                for m in meses_por_anio[a]:
                    total_mes = sum(
                        estructura[tipo][sup][aud].get(a, {}).get(m, 0)
                        for sup in supervisores
                        for aud in supervisores[sup]
                    )
                    row_tipo[f"{a}-{m}"] = total_mes
                total_anual = sum(
                    estructura[tipo][sup][aud].get(a, {}).get(m, 0)
                    for sup in supervisores
                    for aud in supervisores[sup]
                    for m in meses_por_anio[a]
                )
                row_tipo[f"Total {a}"] = total_anual
            row_tipo["Total General"] = sum([v for k, v in row_tipo.items() if k not in ["Tipo de AI", "Supervisor", "Auditor"]])
            tabla_formateada_rows.append(row_tipo)
            
            # Filas Supervisor
            for sup, auditores in supervisores.items():
                row_sup = {"Tipo de AI": "", "Supervisor": sup, "Auditor": ""}
                for a in años:
                    for m in meses_por_anio[a]:
                        total_mes = sum(auditores[aud].get(a, {}).get(m, 0) for aud in auditores)
                        row_sup[f"{a}-{m}"] = total_mes
                    row_sup[f"Total {a}"] = sum(auditores[aud].get(a, {}).get(m, 0)
                                                 for aud in auditores
                                                 for m in meses_por_anio[a])
                row_sup["Total General"] = sum([v for k, v in row_sup.items() if k not in ["Tipo de AI", "Supervisor", "Auditor"]])
                tabla_formateada_rows.append(row_sup)
                
                # Filas Auditor
                for aud, datos_aud in auditores.items():
                    row_aud = {"Tipo de AI": "", "Supervisor": "", "Auditor": aud}
                    for a in años:
                        total_anual_aud = 0
                        for m in meses_por_anio[a]:
                            total_mes = datos_aud.get(a, {}).get(m, 0)
                            row_aud[f"{a}-{m}"] = total_mes
                            total_anual_aud += total_mes
                        row_aud[f"Total {a}"] = total_anual_aud
                    row_aud["Total General"] = sum([v for k, v in row_aud.items() if k not in ["Tipo de AI", "Supervisor", "Auditor"]])
                    tabla_formateada_rows.append(row_aud)
        
        # Fila total general
        row_total = {"Tipo de AI": "TOTAL GENERAL", "Supervisor": "", "Auditor": ""}
        totales_por_anio = {a: 0 for a in años}
        for a in años:
            for m in meses_por_anio[a]:
                total_mes = df.loc[
                    (df["Anio_Emis"] == a) &
                    (df["Mes_Emis"] == list(meses_map.keys())[list(meses_map.values()).index(m)]),
                    "Total_AI"
                ].sum()
                row_total[f"{a}-{m}"] = total_mes
                totales_por_anio[a] += total_mes
            row_total[f"Total {a}"] = totales_por_anio[a]
        row_total["Total General"] = sum(totales_por_anio.values())
        tabla_formateada_rows.append(row_total)
        
        # Convertir a DataFrame
        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        # CREAR tabla_frame
        tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
        tabla_frame.pack(fill="both", expand=True, padx=15, pady=5)
        contenedor_tabla["frame"] = tabla_frame

        # --------------------- TREEVIEW (sin scroll vertical) ---------------------
        container = ctk.CTkFrame(tabla_frame, fg_color="white")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        tree = ttk.Treeview(container, columns=cols, show="headings")

        # Solo scroll horizontal si hay muchas columnas
        if len(cols) > 15:
            hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
            tree.configure(xscrollcommand=hsb.set)
            hsb.pack(side="bottom", fill="x")

        tree.pack(fill="both", expand=True)

        # ✅ HEADERS CON SEPARADORES VISUALES PARA TOTALES
        headers = {
            "DES_TIPO_AI": "Tipo de AI",
            "DES_NOMB_SUP": "Supervisor",
            "DES_NOMB_VER": "Auditor"
        }
        widths = {"DES_TIPO_AI": 180, "DES_NOMB_SUP": 200, "DES_NOMB_VER": 200}
        
        for a in años:
            for m in meses_por_anio[a]:
                headers[f"{a}-{m}"] = f"{a} {m}"
                widths[f"{a}-{m}"] = 85
            # ✅ OPCIÓN C: Agregar separadores visuales para totales anuales
            headers[f"Total {a}"] = f"║ TOTAL {a} ║"
            widths[f"Total {a}"] = 110
        
        # ✅ Total General también con separadores
        headers["Total General"] = "║ TOTAL GENERAL ║"
        widths["Total General"] = 130

        for col in cols:
            tree.heading(col, text=headers.get(col, col))
            tree.column(col, width=widths.get(col, 100), anchor="center")

        # --------------------- LLENADO ---------------------
        total_filas = 0
        totales_por_anio = {a: 0 for a in años}

        for tipo, supervisores in estructura.items():
            fila_tipo = [tipo, "", ""]
            total_general_tipo = 0
            for a in años:
                for m in meses_por_anio[a]:
                    total_mes = sum(
                        estructura[tipo][sup][aud].get(a, {}).get(m, 0)
                        for sup in supervisores
                        for aud in supervisores[sup]
                    )
                    fila_tipo.append(total_mes)
                    totales_por_anio[a] += total_mes
                total_anual = sum(
                    estructura[tipo][sup][aud].get(a, {}).get(m, 0)
                    for sup in supervisores
                    for aud in supervisores[sup]
                    for m in meses_por_anio[a]
                )
                fila_tipo.append(total_anual)
                total_general_tipo += total_anual  # Sumar solo totales anuales
            fila_tipo.append(total_general_tipo)  # Total general = suma de totales anuales
            parent = tree.insert("", "end", values=fila_tipo, tags=("tipo_ai",))
            total_filas += 1

            for sup, auditores in supervisores.items():
                fila_sup = ["", sup, ""]
                total_general_sup = 0
                for a in años:
                    for m in meses_por_anio[a]:
                        total_mes = sum(auditores[aud].get(a, {}).get(m, 0) for aud in auditores)
                        fila_sup.append(total_mes)
                    total_anual_sup = sum(auditores[aud].get(a, {}).get(m, 0)
                                        for aud in auditores
                                        for m in meses_por_anio[a])
                    fila_sup.append(total_anual_sup)
                    total_general_sup += total_anual_sup
                fila_sup.append(total_general_sup)
                sup_parent = tree.insert(parent, "end", values=fila_sup, tags=("supervisor",))
                total_filas += 1

                for aud, datos_aud in auditores.items():
                    fila_aud = ["", "", aud]
                    total_general_aud = 0
                    for a in años:
                        total_anual_aud = 0
                        for m in meses_por_anio[a]:
                            total_mes = datos_aud.get(a, {}).get(m, 0)
                            fila_aud.append(total_mes)
                            total_anual_aud += total_mes
                        fila_aud.append(total_anual_aud)
                        total_general_aud += total_anual_aud  # Sumar solo totales anuales
                    fila_aud.append(total_general_aud)  # Total general = suma de totales anuales
                    tree.insert(sup_parent, "end", values=fila_aud, tags=("auditor",))
                    total_filas += 1

        total_general = sum(totales_por_anio.values())

        fila_total = ["TOTAL GENERAL", "", ""]
        for a in años:
            for m in meses_por_anio[a]:
                total_mes = df.loc[
                    (df["Anio_Emis"] == a) &
                    (df["Mes_Emis"] == list(meses_map.keys())[list(meses_map.values()).index(m)]),
                    "Total_AI"
                ].sum()
                fila_total.append(total_mes)
            fila_total.append(totales_por_anio[a])
        fila_total.append(total_general)
        tree.insert("", "end", values=fila_total, tags=("total",))
        total_filas += 1

        # Ajustar height dinámicamente
        tree.config(height=total_filas)

        # --------------------- ESTILO ---------------------
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree.tag_configure("tipo_ai", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree.tag_configure("supervisor", background="#ffffff", font=("Segoe UI", 10, "bold"))
        tree.tag_configure("auditor", background="#f9f9f9", font=("Segoe UI", 10))
        tree.tag_configure("total", background="#f2f2f2", foreground="black", font=("Segoe UI", 11, "bold"))

    # ---------------------------- INICIALIZACIÓN ----------------------------
    cargar_filtros()
    cargar_tabla()

def generar_tabla_ai_terminadas(parent_frame, conexion=None, anio_default=2025):
    """
    📊 AIs Terminadas
    Muestra los AIs agrupados por Tipo de AI, Supervisor y Auditor.
    Los meses se agrupan independientemente del año seleccionado.
    """
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    # ---------------------------- FILTROS ----------------------------
    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=5)

    # ----------------- ESTADO (botón desplegable con checkboxes) -----------------
    ctk.CTkLabel(
        filtro_frame,
        text="🔎 Estado:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(6, 4))

    estado_button_text = tk.StringVar(value="(Todos)")
    btn_estado = ctk.CTkButton(filtro_frame, textvariable=estado_button_text, width=160,
                               command=lambda: toggle_dropdown_estado())
    btn_estado.pack(side="left", padx=(0, 12))

    dropdown_estado_win = {"win": None}
    check_estado_vars = {}
    available_estados = []

    # ----------------- AÑO TÉRMINO (botón desplegable con checkboxes) -----------------
    ctk.CTkLabel(
        filtro_frame,
        text="📅 Año Término:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(4, 6))

    anio_button_text = tk.StringVar(value="(Todos)")
    btn_anios = ctk.CTkButton(filtro_frame, textvariable=anio_button_text, width=140,
                              command=lambda: toggle_dropdown_anios())
    btn_anios.pack(side="left", padx=(0, 8))

    dropdown_win = {"win": None}
    check_vars = {}
    available_years = []

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    # ---------------------------- TÍTULO ----------------------------
    titulo_label = ctk.CTkLabel(
        parent_frame,
        text="📊 AIs Terminadas",
        font=("Segoe UI", 14, "bold"),
        text_color="#a51c30"
    )
    titulo_label.pack(anchor="w", padx=12, pady=(8, 6))

    # ---------------------------- CONTENEDOR DINÁMICO ----------------------------
    contenedor_tabla = {"frame": None}

    # Variable para almacenar los datos actuales
    datos_actuales = {
        "df_completo": None,  # Datos completos con todas las columnas
        "tabla_formateada": None,  # Tabla tal como se ve en pantalla
        "estados_filtrados": None,
        "años_filtrados": None
    }

    # ---------------------------- FUNCIONES DEL DROPDOWN (YEARS) ----------------------------
    def abrir_dropdown_anios():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            return

        win = tk.Toplevel(parent_frame)
        dropdown_win["win"] = win
        win.wm_overrideredirect(True)
        win.attributes("-topmost", 1)

        x = btn_anios.winfo_rootx()
        y = btn_anios.winfo_rooty() + btn_anios.winfo_height()
        win.geometry(f"+{x}+{y}")

        frame = tk.Frame(win, bg="white", bd=1, relief="solid")
        frame.pack(fill="both", expand=True)

        var_all = tk.IntVar(value=1 if (not available_years) else 0)
        check_vars["(Todos)"] = var_all

        def on_all_toggle():
            val = var_all.get()
            for yr in available_years:
                v = check_vars.get(str(yr))
                if v:
                    v.set(val)
            update_button_label()
            cargar_tabla()

        chk_all = tk.Checkbutton(frame, text="(Todos)", variable=var_all, bg="white", anchor="w",
                                 command=on_all_toggle)
        chk_all.pack(fill="x", padx=8, pady=(6, 2))

        sep = ttk.Separator(frame, orient="horizontal")
        sep.pack(fill="x", padx=6, pady=4)

        for y in available_years:
            key = str(y)
            var = check_vars.get(key, tk.IntVar(value=0))
            check_vars[key] = var

            def make_cmd(k=key, v=var):
                def cmd():
                    if v.get() == 0 and "(Todos)" in check_vars:
                        check_vars["(Todos)"].set(0)
                    if all((check_vars[str(yy)].get() == 1) for yy in available_years):
                        check_vars["(Todos)"].set(1)
                    update_button_label()
                    cargar_tabla()
                return cmd

            chk = tk.Checkbutton(frame, text=key, variable=var, bg="white", anchor="w", command=make_cmd())
            chk.pack(fill="x", padx=8, pady=2)

        def on_focus_out(event):
            if dropdown_win["win"] and not dropdown_win["win"].focus_displayof():
                cerrar_dropdown()
        win.bind("<FocusOut>", on_focus_out)

    def cerrar_dropdown():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            try:
                dropdown_win["win"].destroy()
            except:
                pass
        dropdown_win["win"] = None

    def toggle_dropdown_anios():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            cerrar_dropdown()
        else:
            abrir_dropdown_anios()

    def update_button_label():
        sel = obtener_anios_seleccionados(return_labels=True)
        if sel is None:
            anio_button_text.set("(Todos)")
        else:
            if len(sel) == 1:
                anio_button_text.set(sel[0])
            elif len(sel) <= 3:
                anio_button_text.set(", ".join(sel))
            else:
                anio_button_text.set(f"{len(sel)} seleccionados")

    def obtener_anios_seleccionados(return_labels=False):
        if "(Todos)" in check_vars and check_vars["(Todos)"].get() == 1:
            return None
        selected = [k for k, v in check_vars.items() if k != "(Todos)" and v.get() == 1]
        if not selected:
            return None
        if return_labels:
            return selected
        try:
            return [int(x) for x in selected]
        except:
            return None

    # ---------------------------- FUNCIONES DEL DROPDOWN (ESTADOS) ----------------------------
    def abrir_dropdown_estado():
        if dropdown_estado_win["win"] and tk.Toplevel.winfo_exists(dropdown_estado_win["win"]):
            return

        win = tk.Toplevel(parent_frame)
        dropdown_estado_win["win"] = win
        win.wm_overrideredirect(True)
        win.attributes("-topmost", 1)

        x = btn_estado.winfo_rootx()
        y = btn_estado.winfo_rooty() + btn_estado.winfo_height()
        win.geometry(f"+{x}+{y}")

        frame = tk.Frame(win, bg="white", bd=1, relief="solid")
        frame.pack(fill="both", expand=True)

        var_all = tk.IntVar(value=1 if (not available_estados) else 0)
        check_estado_vars["(Todos)"] = var_all

        def on_all_toggle_estado():
            val = var_all.get()
            for est in available_estados:
                v = check_estado_vars.get(est)
                if v:
                    v.set(val)
            update_estado_label()
            cargar_anios_por_estado()
            cargar_tabla()

        chk_all = tk.Checkbutton(frame, text="(Todos)", variable=var_all, bg="white", anchor="w",
                                 command=on_all_toggle_estado)
        chk_all.pack(fill="x", padx=8, pady=(6, 2))

        sep = ttk.Separator(frame, orient="horizontal")
        sep.pack(fill="x", padx=6, pady=4)

        for est in available_estados:
            var = check_estado_vars.get(est, tk.IntVar(value=0))
            check_estado_vars[est] = var

            def make_cmd(e=est, v=var):
                def cmd():
                    if v.get() == 0 and "(Todos)" in check_estado_vars:
                        check_estado_vars["(Todos)"].set(0)
                    if all((check_estado_vars[ee].get() == 1) for ee in available_estados):
                        check_estado_vars["(Todos)"].set(1)
                    update_estado_label()
                    cargar_anios_por_estado()
                    cargar_tabla()
                return cmd

            chk = tk.Checkbutton(frame, text=est, variable=var, bg="white", anchor="w", command=make_cmd())
            chk.pack(fill="x", padx=8, pady=2)

        def on_focus_out(event):
            if dropdown_estado_win["win"] and not dropdown_estado_win["win"].focus_displayof():
                cerrar_dropdown_estado()
        win.bind("<FocusOut>", on_focus_out)

    def cerrar_dropdown_estado():
        if dropdown_estado_win["win"] and tk.Toplevel.winfo_exists(dropdown_estado_win["win"]):
            try:
                dropdown_estado_win["win"].destroy()
            except:
                pass
        dropdown_estado_win["win"] = None

    def toggle_dropdown_estado():
        if dropdown_estado_win["win"] and tk.Toplevel.winfo_exists(dropdown_estado_win["win"]):
            cerrar_dropdown_estado()
        else:
            abrir_dropdown_estado()

    def update_estado_label():
        sel = obtener_estados_seleccionados(return_labels=True)
        if sel is None:
            estado_button_text.set("(Todos)")
        else:
            if len(sel) == 1:
                estado_button_text.set(sel[0])
            elif len(sel) <= 3:
                estado_button_text.set(", ".join(sel))
            else:
                estado_button_text.set(f"{len(sel)} seleccionados")

    def obtener_estados_seleccionados(return_labels=False):
        if "(Todos)" in check_estado_vars and check_estado_vars["(Todos)"].get() == 1:
            return None
        selected = [k for k, v in check_estado_vars.items() if k != "(Todos)" and v.get() == 1]
        if not selected:
            return None
        if return_labels:
            return selected
        return selected

    # ---------------------------- CARGAR OPCIONES ----------------------------
    def cargar_filtros():
        nonlocal available_estados
        try:
            estado_df = ejecutar_read_sql("SELECT DISTINCT Estado FROM fiscalizaciones3 WHERE Estado IS NOT NULL;", conexion)
            estados = sorted([str(x).strip() for x in estado_df["Estado"].tolist() if str(x).strip()])
        except Exception:
            estados = []

        available_estados = estados

        check_estado_vars.clear()
        check_estado_vars["(Todos)"] = tk.IntVar(value=1 if (len(available_estados) == 0) else 0)
        for est in available_estados:
            check_estado_vars[est] = tk.IntVar(value=1 if est == "Terminado" else 0)

        update_estado_label()
        cargar_anios_por_estado()

    def cargar_anios_por_estado(*_):
        nonlocal available_years
        estados_sel = obtener_estados_seleccionados()
        try:
            if estados_sel:
                estados_list = ",".join(f"'{e}'" for e in estados_sel)
                q = f"SELECT DISTINCT Anio_Termino FROM fiscalizaciones3 WHERE Estado IN ({estados_list}) AND Anio_Termino IS NOT NULL ORDER BY Anio_Termino;"
            else:
                q = "SELECT DISTINCT Anio_Termino FROM fiscalizaciones3 WHERE Anio_Termino IS NOT NULL ORDER BY Anio_Termino;"
            anio_df = ejecutar_read_sql(q, conexion)
            años = [int(x) for x in anio_df["Anio_Termino"].tolist()]
        except Exception:
            años = []

        available_years = años

        check_vars.clear()
        check_vars["(Todos)"] = tk.IntVar(value=1 if (len(available_years) == 0) else 0)
        for y in available_years:
            v = tk.IntVar(value=1 if (y == anio_default) else 0)
            check_vars[str(y)] = v

        update_button_label()

        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            cerrar_dropdown()
            abrir_dropdown_anios()

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            estados_sel = datos_actuales["estados_filtrados"]
            años_sel = datos_actuales["años_filtrados"]
            
            # Construir nombre del archivo
            estados_texto = "_".join(estados_sel) if estados_sel else "Todos"
            años_texto = "_".join(str(a) for a in sorted(años_sel)) if años_sel else "Todos"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"AIs_Terminadas_{estados_texto}_{años_texto}_{timestamp}.xlsx"

            # Abrir diálogo para elegir ubicación
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:  # Usuario canceló
                return

            # Crear el archivo Excel con múltiples hojas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja 1: Tabla formateada (como se ve en pantalla)
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                # Hoja 2: Datos completos filtrados (todas las columnas de la BD)
                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                # Ajustar anchos de columnas para ambas hojas
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    # ---------------------------- FUNCIÓN PRINCIPAL (CARGAR TABLA CON MESES AGRUPADOS) ----------------------------
    def cargar_tabla():
        # Destruir frame anterior si existe
        if contenedor_tabla["frame"] is not None:
            contenedor_tabla["frame"].destroy()

        estados_sel = obtener_estados_seleccionados()
        años_sel = obtener_anios_seleccionados()

        # Guardar filtros aplicados
        datos_actuales["estados_filtrados"] = estados_sel if estados_sel else []
        datos_actuales["años_filtrados"] = años_sel if años_sel else []

        # Consulta para datos completos (todas las columnas)
        sql_completo = "SELECT * FROM fiscalizaciones3 WHERE COD_ACC_IN IS NOT NULL"
        
        if estados_sel:
            estados_str = "', '".join(estados_sel)
            sql_completo += f" AND Estado IN ('{estados_str}')"
        if años_sel:
            years_list = ",".join(str(int(y)) for y in años_sel)
            sql_completo += f" AND Anio_Termino IN ({years_list})"

        # Construir SQL para visualización
        sql = """
            SELECT
                COD_ACC_IN,
                DES_TIPO_AI,
                DES_NOMB_SUP,
                DES_NOMB_VER,
                Estado,
                Anio_Termino,
                Mes_termino
            FROM fiscalizaciones3
            WHERE COD_ACC_IN IS NOT NULL
        """
        if estados_sel:
            estados_str = "', '".join(estados_sel)
            sql += f" AND Estado IN ('{estados_str}')"
        if años_sel:
            years_list = ",".join(str(int(y)) for y in años_sel)
            sql += f" AND Anio_Termino IN ({years_list})"
        sql += " ORDER BY DES_TIPO_AI, DES_NOMB_SUP, DES_NOMB_VER, Mes_termino;"

        try:
            df = ejecutar_read_sql(sql, conexion)
            df_completo = ejecutar_read_sql(sql_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
            tabla_frame.pack(fill="x", padx=15, pady=5)
            contenedor_tabla["frame"] = tabla_frame
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df.empty:
            tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
            tabla_frame.pack(fill="x", padx=15, pady=5)
            contenedor_tabla["frame"] = tabla_frame
            ctk.CTkLabel(tabla_frame, text="⚠ No hay datos para los filtros seleccionados.", text_color="red").pack(pady=15)
            return

        df["Anio_Termino"] = pd.to_numeric(df["Anio_Termino"], errors="coerce").fillna(0).astype(int)
        df["Mes_termino"] = pd.to_numeric(df["Mes_termino"], errors="coerce").fillna(0).astype(int)

        meses_map = {1:"Ene",2:"Feb",3:"Mar",4:"Abr",5:"May",6:"Jun",
                     7:"Jul",8:"Ago",9:"Sep",10:"Oct",11:"Nov",12:"Dic"}

        # --------------------- ESTRUCTURA (AGRUPADA POR MES SIN IMPORTAR AÑO) ---------------------
        estructura = {}
        for _, row in df.iterrows():
            tipo, sup, ver = row["DES_TIPO_AI"], row["DES_NOMB_SUP"], row["DES_NOMB_VER"]
            mes = row["Mes_termino"]
            mes_txt = meses_map.get(mes, str(mes))

            if tipo not in estructura:
                estructura[tipo] = {}
            if sup not in estructura[tipo]:
                estructura[tipo][sup] = {}
            if ver not in estructura[tipo][sup]:
                estructura[tipo][sup][ver] = {}
            # Acumular por mes, sin importar el año
            estructura[tipo][sup][ver][mes_txt] = estructura[tipo][sup][ver].get(mes_txt, 0) + 1

        # --------------------- COLUMNAS (Meses agrupados + Total) ---------------------
        # Obtener todos los meses que tienen datos
        meses_con_datos = sorted(df["Mes_termino"].unique().tolist())
        meses_txt_ordenados = [meses_map[m] for m in meses_con_datos if m in meses_map]

        cols = ["DES_TIPO_AI", "DES_NOMB_SUP", "DES_NOMB_VER"]
        for m in meses_txt_ordenados:
            cols.append(m)
        cols.append("Total")

        # Crear tabla formateada para exportación
        tabla_formateada_rows = []
        
        for tipo, supervisores in estructura.items():
            # Fila Tipo AI
            row_tipo = {"Tipo de AI": tipo, "Supervisor": "", "Auditor": ""}
            for m in meses_txt_ordenados:
                total_mes = sum(
                    estructura[tipo][sup][ver].get(m, 0)
                    for sup in supervisores
                    for ver in supervisores[sup]
                )
                row_tipo[m] = total_mes
            row_tipo["Total"] = sum([v for k, v in row_tipo.items() if k not in ["Tipo de AI", "Supervisor", "Auditor"]])
            tabla_formateada_rows.append(row_tipo)
            
            # Filas Supervisor
            for sup, auditores in supervisores.items():
                row_sup = {"Tipo de AI": "", "Supervisor": sup, "Auditor": ""}
                for m in meses_txt_ordenados:
                    total_mes = sum(auditores[ver].get(m, 0) for ver in auditores)
                    row_sup[m] = total_mes
                row_sup["Total"] = sum([v for k, v in row_sup.items() if k not in ["Tipo de AI", "Supervisor", "Auditor"]])
                tabla_formateada_rows.append(row_sup)
                
                # Filas Auditor
                for ver, datos in auditores.items():
                    row_ver = {"Tipo de AI": "", "Supervisor": "", "Auditor": ver}
                    for m in meses_txt_ordenados:
                        total_mes = datos.get(m, 0)
                        row_ver[m] = total_mes
                    row_ver["Total"] = sum([v for k, v in row_ver.items() if k not in ["Tipo de AI", "Supervisor", "Auditor"]])
                    tabla_formateada_rows.append(row_ver)
        
        # Fila total general
        row_total = {"Tipo de AI": "TOTAL GENERAL", "Supervisor": "", "Auditor": ""}
        totales_por_mes = {m: 0 for m in meses_txt_ordenados}
        for _, row in df.iterrows():
            mes = row["Mes_termino"]
            mes_txt = meses_map.get(mes, str(mes))
            if mes_txt in totales_por_mes:
                totales_por_mes[mes_txt] += 1
        
        for m in meses_txt_ordenados:
            row_total[m] = totales_por_mes[m]
        row_total["Total"] = sum(totales_por_mes.values())
        tabla_formateada_rows.append(row_total)
        
        # Convertir a DataFrame
        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        # CREAR el tabla_frame SOLO cuando hay datos
        tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
        tabla_frame.pack(fill="both", expand=True, padx=15, pady=5)
        contenedor_tabla["frame"] = tabla_frame

        # --------------------- TREEVIEW (sin scroll vertical) ---------------------
        container = ctk.CTkFrame(tabla_frame, fg_color="white")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        tree = ttk.Treeview(container, columns=cols, show="headings")

        # Solo scroll horizontal si hay muchas columnas
        if len(cols) > 15:
            hsb = ttk.Scrollbar(container, orient="horizontal", command=tree.xview)
            tree.configure(xscrollcommand=hsb.set)
            hsb.pack(side="bottom", fill="x")

        tree.pack(fill="both", expand=True)

        headers = {"DES_TIPO_AI": "Tipo de AI", "DES_NOMB_SUP": "Supervisor", "DES_NOMB_VER": "Auditor", "Total": "Total"}
        widths = {"DES_TIPO_AI": 200, "DES_NOMB_SUP": 200, "DES_NOMB_VER": 200, "Total": 100}
        for m in meses_txt_ordenados:
            headers[m] = m
            widths[m] = 85

        for col in cols:
            tree.heading(col, text=headers.get(col, col))
            tree.column(col, width=widths.get(col, 100), anchor="center")

        # --------------------- LLENADO ---------------------
        total_filas = 0
        total_general = 0
        totales_por_mes = {m: 0 for m in meses_txt_ordenados}

        for tipo, supervisores in estructura.items():
            fila_tipo = [tipo, "", ""]
            suma_tipo = 0
            for m in meses_txt_ordenados:
                total_mes_tipo = sum(
                    estructura[tipo][sup][ver].get(m, 0)
                    for sup in supervisores
                    for ver in supervisores[sup]
                )
                fila_tipo.append(total_mes_tipo)
                suma_tipo += total_mes_tipo
                totales_por_mes[m] += total_mes_tipo
            fila_tipo.append(suma_tipo)
            total_general += suma_tipo
            parent_tipo = tree.insert("", "end", values=fila_tipo, tags=("tipo_ai",))
            total_filas += 1

            for sup, auditores in supervisores.items():
                fila_sup = ["", sup, ""]
                suma_sup = 0
                for m in meses_txt_ordenados:
                    total_mes_sup = sum(auditores[ver].get(m, 0) for ver in auditores)
                    fila_sup.append(total_mes_sup)
                    suma_sup += total_mes_sup
                fila_sup.append(suma_sup)
                parent_sup = tree.insert(parent_tipo, "end", values=fila_sup, tags=("supervisor",))
                total_filas += 1

                for ver, datos in auditores.items():
                    fila_ver = ["", "", ver]
                    suma_ver = 0
                    for m in meses_txt_ordenados:
                        total_mes_ver = datos.get(m, 0)
                        fila_ver.append(total_mes_ver)
                        suma_ver += total_mes_ver
                    fila_ver.append(suma_ver)
                    tree.insert(parent_sup, "end", values=fila_ver, tags=("auditor",))
                    total_filas += 1

        # Fila total general
        fila_total = ["TOTAL GENERAL", "", ""]
        for m in meses_txt_ordenados:
            fila_total.append(totales_por_mes[m])
        fila_total.append(total_general)
        tree.insert("", "end", values=fila_total, tags=("total",))
        total_filas += 1

        # Ajustar height dinámicamente
        tree.config(height=total_filas)

        # --------------------- ESTILOS ---------------------
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=28,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree.tag_configure("tipo_ai", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree.tag_configure("supervisor", background="white", font=("Segoe UI", 10))
        tree.tag_configure("auditor", background="#fafafa", font=("Segoe UI", 10))
        tree.tag_configure("total", background="#f2f2f2", foreground="black", font=("Segoe UI", 11, "bold"))

    # ---------------------------- INICIALIZACIÓN ----------------------------
    cargar_filtros()
    cargar_tabla()

def generar_tabla_ai_rendimiento(parent_frame, conexion=None, anio_default=2025):
    """
    📊 AIs Rendimiento (con filtros automáticos)
    Muestra rendimiento por Tipo -> Supervisor -> Auditor.
    Filtros se aplican automáticamente al seleccionar/deseleccionar checkboxes.
    """
    import pandas as pd
    from tkinter import messagebox, filedialog
    from datetime import datetime
    import os

    # ---------------------------- FILTROS ----------------------------
    filtro_frame = ctk.CTkFrame(parent_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_frame.pack(fill="x", padx=12, pady=5)

    # ----------------- ESTADO (botón desplegable con checkboxes) -----------------
    ctk.CTkLabel(
        filtro_frame,
        text="🔎 Estado:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(6, 4))

    estado_button_text = tk.StringVar(value="(Todos)")
    btn_estado = ctk.CTkButton(filtro_frame, textvariable=estado_button_text, width=160,
                               command=lambda: toggle_dropdown_estado())
    btn_estado.pack(side="left", padx=(0, 12))

    dropdown_estado_win = {"win": None}
    check_estado_vars = {}
    available_estados = []

    # ----------------- AÑO TÉRMINO (botón desplegable con checkboxes) -----------------
    ctk.CTkLabel(
        filtro_frame,
        text="📅 Año Término:",
        font=("Segoe UI", 13, "bold"),
        text_color="#002e6d"
    ).pack(side="left", padx=(4, 6))

    anio_button_text = tk.StringVar(value="(Todos)")
    btn_anios = ctk.CTkButton(filtro_frame, textvariable=anio_button_text, width=140,
                              command=lambda: toggle_dropdown_anios())
    btn_anios.pack(side="left", padx=(0, 8))

    dropdown_win = {"win": None}
    check_vars = {}
    available_years = []

    # ----------------- BOTÓN DE EXPORTACIÓN -----------------
    btn_exportar = ctk.CTkButton(
        filtro_frame,
        text="📥 Exportar a Excel",
        font=("Segoe UI", 12, "bold"),
        fg_color="#28a745",
        hover_color="#218838",
        width=160,
        command=lambda: exportar_excel()
    )
    btn_exportar.pack(side="right", padx=10)

    # ---------------------------- TÍTULO ----------------------------
    titulo = ctk.CTkLabel(
        parent_frame,
        text="📊 AIs Rendimiento",
        font=("Segoe UI", 14, "bold"),
        text_color="#a51c30"
    )
    titulo.pack(anchor="w", padx=12, pady=(8, 6))

    # ---------------------------- CONTENEDOR DINÁMICO ----------------------------
    contenedor_tabla = {"frame": None}

    # Variable para almacenar los datos actuales
    datos_actuales = {
        "df_completo": None,  # Datos completos con todas las columnas
        "tabla_formateada": None,  # Tabla tal como se ve en pantalla
        "estados_filtrados": None,
        "años_filtrados": None
    }

    # ---------------------------- FUNCIONES DEL DROPDOWN (YEARS) ----------------------------
    def abrir_dropdown_anios():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            return

        win = tk.Toplevel(parent_frame)
        dropdown_win["win"] = win
        win.wm_overrideredirect(True)
        win.attributes("-topmost", 1)

        x = btn_anios.winfo_rootx()
        y = btn_anios.winfo_rooty() + btn_anios.winfo_height()
        win.geometry(f"+{x}+{y}")

        frame = tk.Frame(win, bg="white", bd=1, relief="solid")
        frame.pack(fill="both", expand=True)

        # "(Todos)" checkbox
        var_all = tk.IntVar(value=1 if (not available_years) else 0)
        check_vars["(Todos)"] = var_all

        def on_all_toggle():
            val = var_all.get()
            for yr in available_years:
                v = check_vars.get(str(yr))
                if v:
                    v.set(val)
            update_button_label()
            cargar_tabla()  # ✅ Actualización automática

        chk_all = tk.Checkbutton(frame, text="(Todos)", variable=var_all, bg="white", anchor="w",
                                 command=on_all_toggle)
        chk_all.pack(fill="x", padx=8, pady=(6, 2))

        sep = ttk.Separator(frame, orient="horizontal")
        sep.pack(fill="x", padx=6, pady=4)

        for y in available_years:
            key = str(y)
            var = check_vars.get(key, tk.IntVar(value=0))
            check_vars[key] = var

            def make_cmd(k=key, v=var):
                def cmd():
                    if v.get() == 0 and "(Todos)" in check_vars:
                        check_vars["(Todos)"].set(0)
                    if all((check_vars[str(yy)].get() == 1) for yy in available_years):
                        check_vars["(Todos)"].set(1)
                    update_button_label()
                    cargar_tabla()  # ✅ Actualización automática
                return cmd

            chk = tk.Checkbutton(frame, text=key, variable=var, bg="white", anchor="w", command=make_cmd())
            chk.pack(fill="x", padx=8, pady=2)

        # ❌ Se eliminaron los botones "Aplicar" y "Cerrar"

        def on_focus_out(event):
            if dropdown_win["win"] and not dropdown_win["win"].focus_displayof():
                cerrar_dropdown()
        win.bind("<FocusOut>", on_focus_out)

    def cerrar_dropdown():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            try:
                dropdown_win["win"].destroy()
            except:
                pass
        dropdown_win["win"] = None

    def toggle_dropdown_anios():
        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            cerrar_dropdown()
        else:
            abrir_dropdown_anios()

    def update_button_label():
        sel = obtener_anios_seleccionados(return_labels=True)
        if sel is None:
            anio_button_text.set("(Todos)")
        else:
            if len(sel) == 1:
                anio_button_text.set(sel[0])
            elif len(sel) <= 3:
                anio_button_text.set(", ".join(sel))
            else:
                anio_button_text.set(f"{len(sel)} seleccionados")

    def obtener_anios_seleccionados(return_labels=False):
        if "(Todos)" in check_vars and check_vars["(Todos)"].get() == 1:
            return None
        selected = [k for k, v in check_vars.items() if k != "(Todos)" and v.get() == 1]
        if not selected:
            return None
        if return_labels:
            return selected
        try:
            return [int(x) for x in selected]
        except:
            return None

    # ---------------------------- FUNCIONES DEL DROPDOWN (ESTADOS) ----------------------------
    def abrir_dropdown_estado():
        if dropdown_estado_win["win"] and tk.Toplevel.winfo_exists(dropdown_estado_win["win"]):
            return

        win = tk.Toplevel(parent_frame)
        dropdown_estado_win["win"] = win
        win.wm_overrideredirect(True)
        win.attributes("-topmost", 1)

        x = btn_estado.winfo_rootx()
        y = btn_estado.winfo_rooty() + btn_estado.winfo_height()
        win.geometry(f"+{x}+{y}")

        frame = tk.Frame(win, bg="white", bd=1, relief="solid")
        frame.pack(fill="both", expand=True)

        # "(Todos)" checkbox
        var_all = tk.IntVar(value=1 if (not available_estados) else 0)
        check_estado_vars["(Todos)"] = var_all

        def on_all_toggle_estado():
            val = var_all.get()
            for est in available_estados:
                v = check_estado_vars.get(est)
                if v:
                    v.set(val)
            update_estado_label()
            cargar_anios_por_estado()
            cargar_tabla()  # ✅ Actualización automática

        chk_all = tk.Checkbutton(frame, text="(Todos)", variable=var_all, bg="white", anchor="w",
                                 command=on_all_toggle_estado)
        chk_all.pack(fill="x", padx=8, pady=(6, 2))

        sep = ttk.Separator(frame, orient="horizontal")
        sep.pack(fill="x", padx=6, pady=4)

        for est in available_estados:
            var = check_estado_vars.get(est, tk.IntVar(value=0))
            check_estado_vars[est] = var

            def make_cmd(e=est, v=var):
                def cmd():
                    if v.get() == 0 and "(Todos)" in check_estado_vars:
                        check_estado_vars["(Todos)"].set(0)
                    if all((check_estado_vars[ee].get() == 1) for ee in available_estados):
                        check_estado_vars["(Todos)"].set(1)
                    update_estado_label()
                    cargar_anios_por_estado()
                    cargar_tabla()  # ✅ Actualización automática
                return cmd

            chk = tk.Checkbutton(frame, text=est, variable=var, bg="white", anchor="w", command=make_cmd())
            chk.pack(fill="x", padx=8, pady=2)

        # ❌ Se eliminaron los botones - el dropdown se cierra al perder foco
        def on_focus_out(event):
            if dropdown_estado_win["win"] and not dropdown_estado_win["win"].focus_displayof():
                cerrar_dropdown_estado()
        win.bind("<FocusOut>", on_focus_out)

    def cerrar_dropdown_estado():
        if dropdown_estado_win["win"] and tk.Toplevel.winfo_exists(dropdown_estado_win["win"]):
            try:
                dropdown_estado_win["win"].destroy()
            except:
                pass
        dropdown_estado_win["win"] = None

    def toggle_dropdown_estado():
        if dropdown_estado_win["win"] and tk.Toplevel.winfo_exists(dropdown_estado_win["win"]):
            cerrar_dropdown_estado()
        else:
            abrir_dropdown_estado()

    def update_estado_label():
        sel = obtener_estados_seleccionados(return_labels=True)
        if sel is None:
            estado_button_text.set("(Todos)")
        else:
            if len(sel) == 1:
                estado_button_text.set(sel[0])
            elif len(sel) <= 3:
                estado_button_text.set(", ".join(sel))
            else:
                estado_button_text.set(f"{len(sel)} seleccionados")

    def obtener_estados_seleccionados(return_labels=False):
        if "(Todos)" in check_estado_vars and check_estado_vars["(Todos)"].get() == 1:
            return None
        selected = [k for k, v in check_estado_vars.items() if k != "(Todos)" and v.get() == 1]
        if not selected:
            return None
        if return_labels:
            return selected
        return selected

    # ---------------------------- CARGAR OPCIONES ----------------------------
    def cargar_filtros():
        nonlocal available_estados
        try:
            estado_df = ejecutar_read_sql("SELECT DISTINCT Estado FROM fiscalizaciones3 WHERE Estado IS NOT NULL;", conexion)
            estados = sorted([str(x).strip() for x in estado_df["Estado"].tolist() if str(x).strip()])
        except Exception:
            estados = []

        available_estados = estados

        check_estado_vars.clear()
        check_estado_vars["(Todos)"] = tk.IntVar(value=1 if (len(available_estados) == 0) else 0)
        for est in available_estados:
            check_estado_vars[est] = tk.IntVar(value=1 if est == "Terminado" else 0)

        update_estado_label()
        cargar_anios_por_estado()

    def cargar_anios_por_estado(*_):
        nonlocal available_years
        estados_sel = obtener_estados_seleccionados()
        try:
            if estados_sel:
                estados_list = ",".join(f"'{e}'" for e in estados_sel)
                q = f"SELECT DISTINCT Anio_Termino FROM fiscalizaciones3 WHERE Estado IN ({estados_list}) AND Anio_Termino IS NOT NULL ORDER BY Anio_Termino;"
            else:
                q = "SELECT DISTINCT Anio_Termino FROM fiscalizaciones3 WHERE Anio_Termino IS NOT NULL ORDER BY Anio_Termino;"
            anio_df = ejecutar_read_sql(q, conexion)
            años = [int(x) for x in anio_df["Anio_Termino"].tolist()]
        except Exception:
            años = []

        available_years = años

        check_vars.clear()
        check_vars["(Todos)"] = tk.IntVar(value=1 if (len(available_years) == 0) else 0)
        for y in available_years:
            v = tk.IntVar(value=1 if (y == anio_default) else 0)
            check_vars[str(y)] = v

        update_button_label()

        if dropdown_win["win"] and tk.Toplevel.winfo_exists(dropdown_win["win"]):
            cerrar_dropdown()
            abrir_dropdown_anios()

    # ---------------------------- FUNCIÓN DE EXPORTACIÓN ----------------------------
    def exportar_excel():
        if datos_actuales["df_completo"] is None or datos_actuales["tabla_formateada"] is None:
            messagebox.showwarning("Sin datos", "No hay datos para exportar. Por favor cargue la tabla primero.")
            return

        try:
            estados_sel = datos_actuales["estados_filtrados"]
            años_sel = datos_actuales["años_filtrados"]
            
            # Construir nombre del archivo
            estados_texto = "_".join(estados_sel) if estados_sel else "Todos"
            años_texto = "_".join(str(a) for a in sorted(años_sel)) if años_sel else "Todos"
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename_default = f"AIs_Rendimiento_{estados_texto}_{años_texto}_{timestamp}.xlsx"

            # Abrir diálogo para elegir ubicación
            filepath = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                initialfile=filename_default,
                title="Guardar archivo Excel"
            )

            if not filepath:  # Usuario canceló
                return

            # Crear el archivo Excel con múltiples hojas
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                # Hoja 1: Tabla formateada (como se ve en pantalla)
                tabla_export = datos_actuales["tabla_formateada"].copy()
                tabla_export.to_excel(writer, sheet_name='Tabla Visualizada', index=False)

                # Hoja 2: Datos completos filtrados (todas las columnas de la BD)
                df_completo_export = datos_actuales["df_completo"].copy()
                df_completo_export.to_excel(writer, sheet_name='Datos Completos Filtrados', index=False)

                # Ajustar anchos de columnas para ambas hojas
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width

            messagebox.showinfo(
                "Exportación exitosa",
                f"✅ Archivo exportado correctamente:\n\n{os.path.basename(filepath)}\n\n"
                f"📊 Hoja 1: Tabla Visualizada (con filtros aplicados)\n"
                f"📋 Hoja 2: Datos Completos Filtrados (todas las columnas)"
            )

        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar: {str(e)}")

    # ---------------------------- FUNCIÓN PRINCIPAL ----------------------------
    def cargar_tabla():
        if contenedor_tabla["frame"] is not None:
            contenedor_tabla["frame"].destroy()

        estados_sel = obtener_estados_seleccionados()
        años_sel = obtener_anios_seleccionados()

        # Guardar filtros aplicados
        datos_actuales["estados_filtrados"] = estados_sel if estados_sel else []
        datos_actuales["años_filtrados"] = años_sel if años_sel else []

        # Consulta para datos completos (todas las columnas)
        sql_completo = "SELECT * FROM fiscalizaciones3 WHERE COD_ACC_IN IS NOT NULL"
        
        if estados_sel:
            estados_str = "', '".join(estados_sel)
            sql_completo += f" AND Estado IN ('{estados_str}')"
        if años_sel:
            years_list = ",".join(str(int(y)) for y in años_sel)
            sql_completo += f" AND Anio_Termino IN ({years_list})"

        sql = """
            SELECT
                DES_TIPO_AI,
                DES_NOMB_SUP,
                DES_NOMB_VER,
                COUNT(COD_ACC_IN) AS Cantidad,
                SUM(IFNULL(Pago_AI,0)) AS Pago_AI,
                SUM(IFNULL(Rect_AI,0)) AS Rect_AI,
                SUM(IFNULL(Total,0)) AS Rendimiento
            FROM fiscalizaciones3
            WHERE COD_ACC_IN IS NOT NULL
        """
        if estados_sel:
            estados_str = "', '".join(estados_sel)
            sql += f" AND Estado IN ('{estados_str}')"
        if años_sel:
            years_list = ",".join(str(int(y)) for y in años_sel)
            sql += f" AND Anio_Termino IN ({years_list})"
        sql += """
            GROUP BY DES_TIPO_AI, DES_NOMB_SUP, DES_NOMB_VER
            ORDER BY DES_TIPO_AI, DES_NOMB_SUP, DES_NOMB_VER;
        """

        try:
            df = ejecutar_read_sql(sql, conexion)
            df_completo = ejecutar_read_sql(sql_completo, conexion)
            datos_actuales["df_completo"] = df_completo.copy()
        except Exception as e:
            tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
            tabla_frame.pack(fill="x", padx=15, pady=5)
            contenedor_tabla["frame"] = tabla_frame
            ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
            return

        if df is None or df.empty:
            tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
            tabla_frame.pack(fill="x", padx=15, pady=5)
            contenedor_tabla["frame"] = tabla_frame
            ctk.CTkLabel(tabla_frame, text="⚠ No hay datos para los filtros seleccionados.", text_color="red").pack(pady=15)
            return

        df["Cantidad"] = pd.to_numeric(df.get("Cantidad", 0), errors="coerce").fillna(0).astype(int)
        df["Pago_AI"] = pd.to_numeric(df.get("Pago_AI", 0.0), errors="coerce").fillna(0.0)
        df["Rect_AI"] = pd.to_numeric(df.get("Rect_AI", 0.0), errors="coerce").fillna(0.0)
        df["Rendimiento"] = pd.to_numeric(df.get("Rendimiento", 0.0), errors="coerce").fillna(0.0)

        tipos = df["DES_TIPO_AI"].fillna("SIN TIPO").unique().tolist()

        cols = ["DES_TIPO_AI", "DES_NOMB_SUP", "DES_NOMB_VER", "Cantidad", "Pago_AI", "Rect_AI", "Rendimiento"]
        
        # Crear tabla formateada para exportación
        tabla_formateada_rows = []
        
        for tipo in tipos:
            df_tipo = df[df["DES_TIPO_AI"].fillna("SIN TIPO") == tipo]
            suma_cant = int(df_tipo["Cantidad"].sum())
            suma_pago = float(df_tipo["Pago_AI"].sum())
            suma_rect = float(df_tipo["Rect_AI"].sum())
            suma_rend = float(df_tipo["Rendimiento"].sum())

            # Fila Tipo
            row_tipo = {
                "Tipo de AI": tipo,
                "Supervisor": "",
                "Auditor": "",
                "Cantidad": suma_cant,
                "Pago AI": suma_pago,
                "Rect AI": suma_rect,
                "Rendimiento": suma_rend
            }
            tabla_formateada_rows.append(row_tipo)

            supervisores = df_tipo["DES_NOMB_SUP"].fillna("SIN SUP").unique().tolist()
            for sup in supervisores:
                df_sup = df_tipo[df_tipo["DES_NOMB_SUP"].fillna("SIN SUP") == sup]
                suma_cant_sup = int(df_sup["Cantidad"].sum())
                suma_pago_sup = float(df_sup["Pago_AI"].sum())
                suma_rect_sup = float(df_sup["Rect_AI"].sum())
                suma_rend_sup = float(df_sup["Rendimiento"].sum())

                # Fila Supervisor
                row_sup = {
                    "Tipo de AI": "",
                    "Supervisor": sup,
                    "Auditor": "",
                    "Cantidad": suma_cant_sup,
                    "Pago AI": suma_pago_sup,
                    "Rect AI": suma_rect_sup,
                    "Rendimiento": suma_rend_sup
                }
                tabla_formateada_rows.append(row_sup)

                # Filas Auditor
                df_sup_aud = df_sup.copy()
                for _, row in df_sup_aud.iterrows():
                    aud = row.get("DES_NOMB_VER") or ""
                    cant = int(row.get("Cantidad", 0))
                    pago = float(row.get("Pago_AI", 0.0))
                    rect = float(row.get("Rect_AI", 0.0))
                    rend = float(row.get("Rendimiento", 0.0))
                    
                    row_aud = {
                        "Tipo de AI": "",
                        "Supervisor": "",
                        "Auditor": aud,
                        "Cantidad": cant,
                        "Pago AI": pago,
                        "Rect AI": rect,
                        "Rendimiento": rend
                    }
                    tabla_formateada_rows.append(row_aud)

        # Fila total general
        row_total = {
            "Tipo de AI": "TOTAL GENERAL",
            "Supervisor": "",
            "Auditor": "",
            "Cantidad": int(df["Cantidad"].sum()),
            "Pago AI": float(df["Pago_AI"].sum()),
            "Rect AI": float(df["Rect_AI"].sum()),
            "Rendimiento": float(df["Rendimiento"].sum())
        }
        tabla_formateada_rows.append(row_total)

        # Convertir a DataFrame
        tabla_formateada_df = pd.DataFrame(tabla_formateada_rows)
        datos_actuales["tabla_formateada"] = tabla_formateada_df

        tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
        tabla_frame.pack(fill="both", expand=True, padx=15, pady=5)
        contenedor_tabla["frame"] = tabla_frame
        
        container = ctk.CTkFrame(tabla_frame, fg_color="white")
        container.pack(fill="both", expand=True, padx=5, pady=5)

        tree = ttk.Treeview(container, columns=cols, show="headings")
        tree.pack(fill="both", expand=True)

        headers = {
            "DES_TIPO_AI": "Tipo de AI",
            "DES_NOMB_SUP": "Supervisor",
            "DES_NOMB_VER": "Auditor",
            "Cantidad": "Cantidad",
            "Pago_AI": "Pago AI",
            "Rect_AI": "Rect AI",
            "Rendimiento": "Rendimiento"
        }
        widths = {"DES_TIPO_AI": 200, "DES_NOMB_SUP": 180, "DES_NOMB_VER": 180,
                  "Cantidad": 90, "Pago_AI": 120, "Rect_AI": 120, "Rendimiento": 130}
        for col in cols:
            tree.heading(col, text=headers.get(col, col))
            tree.column(col, width=widths.get(col, 100),
                        anchor="center" if col in ("Cantidad", "Pago_AI", "Rect_AI", "Rendimiento") else "w")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                        background="#ffffff",
                        foreground="#4a4a4a",
                        rowheight=26,
                        fieldbackground="#ffffff",
                        font=("Segoe UI", 10))
        style.configure("Treeview.Heading",
                        background="#002e6d",
                        foreground="white",
                        font=("Segoe UI", 10, "bold"))
        style.map("Treeview",
                  background=[("selected", "#a51c30")],
                  foreground=[("selected", "white")])

        tree.tag_configure("tipo", background="#f0f4fa", font=("Segoe UI", 10, "bold"))
        tree.tag_configure("supervisor", background="white", font=("Segoe UI", 10, "bold"))
        tree.tag_configure("auditor", background="#fafafa", font=("Segoe UI", 10))
        tree.tag_configure("total", background="#f2f2f2", font=("Segoe UI", 11, "bold"))

        total_filas = 0
        
        total_general = {"Cantidad": 0, "Pago_AI": 0.0, "Rect_AI": 0.0, "Rendimiento": 0.0}
        for tipo in tipos:
            df_tipo = df[df["DES_TIPO_AI"].fillna("SIN TIPO") == tipo]
            suma_cant = int(df_tipo["Cantidad"].sum())
            suma_pago = float(df_tipo["Pago_AI"].sum())
            suma_rect = float(df_tipo["Rect_AI"].sum())
            suma_rend = float(df_tipo["Rendimiento"].sum())

            fila_tipo = [tipo, "", "", suma_cant, f"{suma_pago:,.2f}", f"{suma_rect:,.2f}", f"{suma_rend:,.2f}"]
            parent_tipo = tree.insert("", "end", values=fila_tipo, tags=("tipo",))
            total_filas += 1

            total_general["Cantidad"] += suma_cant
            total_general["Pago_AI"] += suma_pago
            total_general["Rect_AI"] += suma_rect
            total_general["Rendimiento"] += suma_rend

            supervisores = df_tipo["DES_NOMB_SUP"].fillna("SIN SUP").unique().tolist()
            for sup in supervisores:
                df_sup = df_tipo[df_tipo["DES_NOMB_SUP"].fillna("SIN SUP") == sup]
                suma_cant_sup = int(df_sup["Cantidad"].sum())
                suma_pago_sup = float(df_sup["Pago_AI"].sum())
                suma_rect_sup = float(df_sup["Rect_AI"].sum())
                suma_rend_sup = float(df_sup["Rendimiento"].sum())

                fila_sup = ["", sup, "", suma_cant_sup, f"{suma_pago_sup:,.2f}", f"{suma_rect_sup:,.2f}", f"{suma_rend_sup:,.2f}"]
                parent_sup = tree.insert(parent_tipo, "end", values=fila_sup, tags=("supervisor",))
                total_filas += 1

                df_sup_aud = df_sup.copy()
                for _, row in df_sup_aud.iterrows():
                    aud = row.get("DES_NOMB_VER") or ""
                    cant = int(row.get("Cantidad", 0))
                    pago = float(row.get("Pago_AI", 0.0))
                    rect = float(row.get("Rect_AI", 0.0))
                    rend = float(row.get("Rendimiento", 0.0))
                    fila_aud = ["", "", aud, cant, f"{pago:,.2f}", f"{rect:,.2f}", f"{rend:,.2f}"]
                    tree.insert(parent_sup, "end", values=fila_aud, tags=("auditor",))
                    total_filas += 1

        fila_total = [
            "TOTAL GENERAL", "", "",
            total_general["Cantidad"],
            f"{total_general['Pago_AI']:,.2f}",
            f"{total_general['Rect_AI']:,.2f}",
            f"{total_general['Rendimiento']:,.2f}"
        ]
        tree.insert("", "end", values=fila_total, tags=("total",))
        total_filas += 1

        tree.config(height=total_filas)

    # ---------------------------- INICIALIZACIÓN ----------------------------
    cargar_filtros()
    cargar_tabla()
# ================================================================
# DASHBOARD: RESULTADOS DE ACCIONES INDUCTIVAS (NUEVO FORMATO)
# ================================================================
def dashboard_acciones_inductivas():
    ocultar_menu()

    try:
        preview_frame.pack_forget()
    except Exception:
        pass
    dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # limpiar contenido previo
    for widget in dashboard_frame.winfo_children():
        widget.destroy()

    # === Mostrar banner personalizado ===
    banner_path = config.get("banner_accionesinductivas_path", "banner3.jpg")
    if banner_path and os.path.exists(banner_path):
        mostrar_banner_modulo(banner_path)
    else:
        banner_label_modulo.configure(
            text="BANNER ACCIONES INDUCTIVAS",
            bg="#f0f4ff",
            fg="black",
            font=("Segoe UI", 16, "bold")
        )

    # === Conexión a BD y carga de datos ===
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql("SELECT * FROM fiscalizaciones3", DB_ENGINE)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar el dashboard:\n{e}")
        return

    # =====================================================
    # CONTENEDOR SCROLLEABLE PRINCIPAL
    # =====================================================
    scroll_container = ctk.CTkFrame(dashboard_frame, fg_color="white")
    scroll_container.pack(fill="both", expand=True, padx=15, pady=15)

    canvas = tk.Canvas(scroll_container, bg="white", highlightthickness=0)
    vscroll = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)

    # 🎨 Scrollbar pastel
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Vertical.TScrollbar",
                    background="#cce7f0",
                    troughcolor="#eaf6fb",
                    arrowcolor="#4a4a4a",
                    gripcount=0,
                    relief="flat")

    canvas.configure(yscrollcommand=vscroll.set)
    vscroll.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    inner_frame = tk.Frame(canvas, bg="white")
    canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    def _resize_canvas(event=None):
        """Ajusta el ancho del contenido al ancho visible del canvas."""
        canvas_width = canvas.winfo_width()
        canvas.itemconfig(canvas_window, width=canvas_width)
        canvas.configure(scrollregion=canvas.bbox("all"))

    # Vincular eventos de cambio de tamaño y configuración
    canvas.bind("<Configure>", _resize_canvas)
    inner_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))


    # scroll con rueda del mouse
    def _on_mousewheel(event):
        if event.delta:
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            if event.num == 5:
                canvas.yview_scroll(1, "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", _on_mousewheel)
    canvas.bind_all("<Button-5>", _on_mousewheel)

    # =====================================================
    # MÉTRICAS + ÍNDICE SUPERIOR
    # =====================================================
    top_container = ctk.CTkFrame(inner_frame, fg_color="white")
    top_container.pack(pady=15, padx=15, fill="x")

    metrics_frame = ctk.CTkFrame(top_container, fg_color="white", corner_radius=15)
    metrics_frame.pack(side="left", fill="x", expand=True, padx=(0, 10))

    index_frame = ctk.CTkFrame(top_container, fg_color="#f7f9fb", corner_radius=12, width=240)
    index_frame.pack_propagate(False)
    index_frame.pack(side="right", anchor="n", pady=2, padx=(10,0))

    # --- Crear cards de métricas ---
    def crear_card(parent, icono, texto, valor, color_fondo, color_hover):
        frame = ctk.CTkFrame(parent, corner_radius=15, fg_color=color_fondo)
        frame.pack(side="left", padx=12, pady=10, ipadx=16, ipady=10)
        frame.bind("<Enter>", lambda e: frame.configure(fg_color=color_hover))
        frame.bind("<Leave>", lambda e: frame.configure(fg_color=color_fondo))
        ctk.CTkLabel(frame, text=icono, font=("Segoe UI Emoji", 26)).grid(row=0, column=0, rowspan=2, padx=8)
        ctk.CTkLabel(frame, text=texto, font=("Segoe UI", 11, "bold")).grid(row=0, column=1, sticky="w", pady=(6,0))
        ctk.CTkLabel(frame, text=str(valor), font=("Segoe UI", 16, "bold")).grid(row=1, column=1, sticky="w")
        return frame

    # --- Calcular métricas ---
    total_ai = len(df)
    pendientes = df[df["Estado"].str.upper() == "PENDIENTE"].shape[0] if "Estado" in df.columns else 0
    terminadas = df[df["Estado"].str.upper() == "TERMINADO"].shape[0] if "Estado" in df.columns else 0

    crear_card(metrics_frame, "📊", "Total AIs", total_ai, "#c2e9fb", "#90cdf4")
    crear_card(metrics_frame, "✅", "Terminadas", terminadas, "#a3f7bf", "#7ae3a1")
    crear_card(metrics_frame, "⏳", "Pendientes", pendientes, "#fcd5ce", "#f8a29e")

    # =====================================================
    # ÍNDICE DE TABLAS (2 columnas)
    # =====================================================
    index_frame.configure(width=700)
    index_frame.pack_propagate(False)

    ctk.CTkLabel(index_frame, text="📚 Índice de Tablas", font=("Segoe UI", 12, "bold")).pack(pady=(8,6))

    idx_container = tk.Frame(index_frame, bg="#f7f9fb")
    idx_container.pack(fill="both", expand=True, padx=10, pady=(0,8))

    idx_canvas = tk.Canvas(idx_container, bg="#f7f9fb", highlightthickness=0, height=300)
    idx_v = ttk.Scrollbar(idx_container, orient="vertical", command=idx_canvas.yview)
    idx_v.pack(side="right", fill="y")
    idx_canvas.pack(side="left", fill="both", expand=True)
    idx_canvas.configure(yscrollcommand=idx_v.set)

    idx_inner = tk.Frame(idx_canvas, bg="#f7f9fb")
    idx_window = idx_canvas.create_window((0,0), window=idx_inner, anchor="nw")

    def _idx_config(e):
        idx_canvas.configure(scrollregion=idx_canvas.bbox("all"))
        try:
            idx_canvas.itemconfig(idx_window, width=e.width)
        except Exception:
            pass

    idx_inner.bind("<Configure>", _idx_config)
    idx_container.bind("<Configure>", _idx_config)

    tablas_frames = {}

    def ir_a_tabla(nombre):
        target = tablas_frames.get(nombre)
        if not target:
            return
        inner_frame.update_idletasks()
        target.update_idletasks()
        target_y = target.winfo_y()
        inner_h = inner_frame.winfo_height()
        canvas_h = canvas.winfo_height()
        max_scroll = max(1, inner_h - canvas_h)
        fraction = target_y / max_scroll
        fraction = max(0.0, min(1.0, fraction))
        try:
            canvas.yview_moveto(fraction)
        except Exception:
            pass

    idx_inner.grid_columnconfigure(0, weight=1, uniform="col")
    idx_inner.grid_columnconfigure(1, weight=1, uniform="col")

    def agregar_boton_indice(nombre, index):
        columnas = 2
        fila = index // columnas
        columna = index % columnas
        btn = ctk.CTkButton(
            idx_inner,
            text=nombre,
            height=34,
            corner_radius=8,
            fg_color="#eaf6ff",
            hover_color="#d3eeff",
            text_color="#1E3A8A",
            command=lambda n=nombre: ir_a_tabla(n)
        )
        btn.grid(row=fila, column=columna, padx=8, pady=6, sticky="nsew")
        idx_inner.grid_columnconfigure(columna, weight=1, uniform="col")

    nombres_tablas = ["AIs Asignadas","AIs Pendientes","AIs Terminadas","AIs Rendimiento"]
    for i, n in enumerate(nombres_tablas):
        agregar_boton_indice(n, i)

    # =====================================================
    # TABLAS 
    # =====================================================
    try:
        frame_AI_asignadas = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_AI_asignadas.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_AI_asignadas(frame_AI_asignadas, conexion=conn, anio=2025)
        tablas_frames["AIs Asignadas"] = frame_AI_asignadas
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla AIs Asignadas:\n{e}")
       # -------------------AIs Pendientes-------------------
    try:
        frame_AI_pendientes = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_AI_pendientes.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_ai_pendientes(frame_AI_pendientes, conexion=conn, anio_default=2025)
        tablas_frames["AIs Pendientes"] = frame_AI_pendientes
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla AIs Pendientes:\n{e}")

        #AIs TERMNADAS ---------------------------------

    try:
        frame_AI_terminadas = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_AI_terminadas.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_ai_terminadas(frame_AI_terminadas, conexion=conn, anio_default=2025)
        tablas_frames["AIs Terminadas"] = frame_AI_terminadas
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla AIs Terminadas:\n{e}")

#Ais rendimiento ------------------------------------------------------------
    try:
        frame_AI_rendimiento = ctk.CTkFrame(inner_frame, fg_color="white", corner_radius=12)
        frame_AI_rendimiento.pack(pady=20, anchor="center", fill="both", expand=True)
        generar_tabla_ai_rendimiento(frame_AI_rendimiento, conexion=conn)
        tablas_frames["AIs Rendimiento"] = frame_AI_rendimiento
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla AIs Rendimiento:\n{e}")



#--------------------------------------------------
def volver_inicio():
    frame_modulo.pack_forget()
    header_modulo.pack_forget()
    header.pack(fill="x")
    frame_inicio.pack(fill="both", expand=True)
    app.geometry("550x375")

ctk.CTkButton(menu_frame, text="⬅ Volver",
              command=volver_inicio,
              width=200, fg_color=COLOR_DANGER, hover_color="#B91C1C").pack(pady=20)
#--------------------------------------------------
#DASHBOAR GENERAL
#--------------------------------------------------
#
# --------------------------------------------------
# ---------------- Mostrar Dashboard Completo (uno por cada reporte principal) ----------------
# ============================================================================
# DASHBOARD COMPLETO DE FISCALIZACIONES - DISEÑO PROFESIONAL INTERACTIVO
# ============================================================================

# Configuración de colores del diseño
# Configuración de colores del diseño
COLOR_ROSA = '#EC4899'
COLOR_AZUL = '#3B82F6'
COLOR_MORADO = '#8B5CF6'
COLOR_VERDE = '#10B981'
COLOR_NARANJA = '#F59E0B'
COLOR_GRIS_OSCURO = '#1F2937'
COLOR_GRIS_CLARO = '#F3F4F6'

# Configuración matplotlib
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.sans-serif'] = ['Arial', 'Helvetica']

def unbind_mousewheel_recursive(widget):
    """Desvincula eventos mousewheel recursivamente"""
    try:
        widget.unbind_all("<MouseWheel>")
        for child in widget.winfo_children():
            unbind_mousewheel_recursive(child)
    except:
        pass

# ============================================================================
# CLASE MEJORADA PARA FILTRO MULTI-SELECT
# ============================================================================
class MultiSelectCombobox:
    """Widget optimizado para selección múltiple con checkboxes"""
    def __init__(self, parent, values, default_text="Seleccionar...", width=200, callback=None):
        self.parent = parent
        self.all_values = values if values else []
        self.selected_values = set()
        self.callback = callback
        self.width = width
        self.default_text = default_text
        
        self.frame = ctk.CTkFrame(parent, fg_color="white", corner_radius=6, 
                                border_width=1, border_color="#D1D5DB")
        
        self.button = ctk.CTkButton(
            self.frame,
            text=default_text,
            width=width,
            height=30,
            fg_color="white",
            text_color="#374151",
            hover_color="#F3F4F6",
            border_width=0,
            anchor="w",
            font=("Arial", 9),
            command=self.toggle_dropdown
        )
        self.button.pack(padx=2, pady=2)
        
        self.dropdown = None
        self.is_open = False
        self.check_vars = {}
        
    def toggle_dropdown(self):
        if self.is_open:
            self.close_dropdown()
        else:
            self.open_dropdown()
    
    def open_dropdown(self):
        if self.is_open or not self.all_values:
            return
            
        self.is_open = True
        
        # Crear ventana dropdown
        self.dropdown = ctk.CTkToplevel(self.parent)
        self.dropdown.withdraw()
        self.dropdown.overrideredirect(True)
        self.dropdown.configure(fg_color="white", border_width=1, border_color="#D1D5DB")
        
        # Frame scrollable
        max_height = min(300, len(self.all_values) * 30 + 80)
        scroll_frame = ctk.CTkScrollableFrame(
            self.dropdown,
            width=self.width - 20,
            height=max_height,
            fg_color="white"
        )
        scroll_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Checkbox "Todos"
        todos_var = ctk.BooleanVar(value=(len(self.selected_values) == 0 or 
                                          len(self.selected_values) == len(self.all_values)))
        
        def toggle_todos():
            if todos_var.get():
                # Seleccionar todos
                self.selected_values = set(self.all_values)
                for var in self.check_vars.values():
                    var.set(True)
            else:
                # Deseleccionar todos
                self.selected_values.clear()
                for var in self.check_vars.values():
                    var.set(False)
            self.update_button_text()
            if self.callback:
                self.callback()
        
        todos_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        todos_frame.pack(fill="x", pady=2)
        
        ctk.CTkCheckBox(
            todos_frame,
            text="📋 Todos",
            variable=todos_var,
            command=toggle_todos,
            font=("Arial", 9, "bold"),
            text_color="#002e6d",
            fg_color=COLOR_ROSA,
            hover_color="#BE185D"
        ).pack(anchor="w", padx=5)
        
        ctk.CTkFrame(scroll_frame, height=1, fg_color="#E5E7EB").pack(fill="x", pady=5)
        
        # Limpiar check_vars anteriores
        self.check_vars.clear()
        
        # Crear checkboxes para cada valor
        for value in self.all_values:
            is_selected = value in self.selected_values
            var = ctk.BooleanVar(value=is_selected)
            self.check_vars[value] = var
            
            def make_toggle_func(v, var_ref, todos_ref):
                def toggle():
                    if var_ref.get():
                        self.selected_values.add(v)
                    else:
                        self.selected_values.discard(v)
                    
                    # Actualizar "Todos"
                    if len(self.selected_values) == len(self.all_values):
                        todos_ref.set(True)
                    else:
                        todos_ref.set(False)
                    
                    self.update_button_text()
                    if self.callback:
                        self.callback()
                return toggle
            
            item_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
            item_frame.pack(fill="x", pady=1)
            
            ctk.CTkCheckBox(
                item_frame,
                text=str(value)[:40] + ("..." if len(str(value)) > 40 else ""),
                variable=var,
                command=make_toggle_func(value, var, todos_var),
                font=("Arial", 9),
                text_color="#374151",
                fg_color=COLOR_ROSA,
                hover_color="#BE185D"
            ).pack(anchor="w", padx=5)
        
        # Posicionar dropdown
        try:
            self.button.update_idletasks()
            button_x = self.button.winfo_rootx()
            button_y = self.button.winfo_rooty()
            button_height = self.button.winfo_height()
            
            # Verificar si hay espacio abajo, sino mostrar arriba
            screen_height = self.dropdown.winfo_screenheight()
            if button_y + button_height + max_height > screen_height:
                # Mostrar arriba
                self.dropdown.geometry(f"+{button_x}+{button_y - max_height - 5}")
            else:
                # Mostrar abajo
                self.dropdown.geometry(f"+{button_x}+{button_y + button_height + 2}")
            
            self.dropdown.deiconify()
            self.dropdown.lift()
            self.dropdown.focus_set()
        except:
            self.close_dropdown()
            return
        
        # Cerrar al hacer clic fuera
        def on_focus_out(event):
            try:
                if event.widget == self.dropdown:
                    return
                # Verificar si el clic fue dentro del dropdown
                x, y = self.dropdown.winfo_pointerxy()
                widget = self.dropdown.winfo_containing(x, y)
                if widget is None or not str(widget).startswith(str(self.dropdown)):
                    self.close_dropdown()
            except:
                pass
        
        self.dropdown.bind("<FocusOut>", on_focus_out)
        
        # Cerrar con Escape
        self.dropdown.bind("<Escape>", lambda e: self.close_dropdown())
    
    def close_dropdown(self):
        if self.dropdown:
            try:
                self.dropdown.destroy()
            except:
                pass
            self.dropdown = None
        self.is_open = False
        self.check_vars.clear()
    
    def update_button_text(self):
        """Actualiza el texto del botón según la selección"""
        if len(self.selected_values) == 0 or len(self.selected_values) == len(self.all_values):
            text = f"📋 Todos ({len(self.all_values)})"
        elif len(self.selected_values) == 1:
            value = list(self.selected_values)[0]
            text = f"✓ {str(value)[:30]}" + ("..." if len(str(value)) > 30 else "")
        else:
            text = f"✓ {len(self.selected_values)} seleccionados"
        self.button.configure(text=text)
    
    def get_selected(self):
        """Retorna lista de seleccionados"""
        return list(self.selected_values)
    
    def reset(self):
        """Reinicia la selección"""
        self.selected_values.clear()
        self.update_button_text()
        if self.callback:
            self.callback()
    
    def set_values(self, new_values):
        """Actualizar lista de valores disponibles"""
        self.all_values = new_values if new_values else []
        # Mantener solo selecciones válidas
        self.selected_values = {v for v in self.selected_values if v in self.all_values}
        self.update_button_text()
    
    def pack(self, **kwargs):
        self.frame.pack(**kwargs)
    
    def pack_forget(self):
        self.close_dropdown()
        self.frame.pack_forget()

# ============================================================================
# FUNCIONES AUXILIARES
# ============================================================================
def crear_kpi_card(parent, icono, texto, valor, subtexto, color_bg, color_hover):
    """Crear tarjeta KPI simple"""
    card = ctk.CTkFrame(parent, fg_color=color_bg, corner_radius=15,
                       border_width=2, border_color="#E5E7EB")
    card.pack(side="left", fill="both", expand=True, padx=8)
    
    def on_enter(e):
        card.configure(fg_color=color_hover, border_color=color_bg)
    def on_leave(e):
        card.configure(fg_color=color_bg, border_color="#E5E7EB")
    
    card.bind("<Enter>", on_enter)
    card.bind("<Leave>", on_leave)
    
    content = ctk.CTkFrame(card, fg_color="transparent")
    content.pack(fill="both", expand=True, padx=20, pady=20)
    
    ctk.CTkLabel(content, text=icono, font=("Arial", 32)).pack(pady=(0, 5))
    ctk.CTkLabel(content, text=texto, font=("Arial", 11, "bold"),
                text_color="#1F2937", wraplength=150, justify="center").pack(pady=(0, 10))
    ctk.CTkLabel(content, text=valor, font=("Arial", 36, "bold"),
                text_color="#1F2937").pack(pady=5)
    ctk.CTkLabel(content, text=subtexto, font=("Arial", 9),
                text_color="#6B7280", wraplength=150, justify="center").pack(pady=(5, 0))

def exportar_grafico_imagen(fig, nombre_base, filtros_texto):
    """Exporta el gráfico matplotlib como imagen PNG"""
    from tkinter import filedialog
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{nombre_base}_{timestamp}.png"
    
    filepath = filedialog.asksaveasfilename(
        defaultextension=".png",
        filetypes=[("PNG files", "*.png"), ("All files", "*.*")],
        initialfile=filename,
        title="Guardar gráfico como imagen"
    )
    
    if filepath:
        try:
            fig.text(0.5, 0.02, f"Filtros: {filtros_texto}", 
                    ha='center', fontsize=8, style='italic', color='gray')
            fig.savefig(filepath, dpi=300, bbox_inches='tight', facecolor='white')
            messagebox.showinfo("Éxito", f"✅ Gráfico exportado correctamente:\n\n{filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}")

def exportar_datos_excel(query, nombre_base, filtros_texto):
    """Exporta los datos completos a Excel"""
    from tkinter import filedialog
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{nombre_base}_{timestamp}.xlsx"
    
    filepath = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
        initialfile=filename,
        title="Guardar datos en Excel"
    )
    
    if filepath:
        try:
            df_export = pd.read_sql(query, DB_ENGINE)
            
            with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
                df_export.to_excel(writer, sheet_name='Datos Completos', index=False)
                
                df_info = pd.DataFrame({
                    'Parámetro': ['Filtros Aplicados', 'Fecha de Exportación', 'Total Registros'],
                    'Valor': [filtros_texto, 
                             datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                             len(df_export)]
                })
                df_info.to_excel(writer, sheet_name='Info Exportación', index=False)
                
                # Ajustar ancho de columnas
                for sheet_name in writer.sheets:
                    worksheet = writer.sheets[sheet_name]
                    for column in worksheet.columns:
                        max_length = 0
                        column_letter = column[0].column_letter
                        for cell in column:
                            try:
                                if len(str(cell.value)) > max_length:
                                    max_length = len(str(cell.value))
                            except:
                                pass
                        adjusted_width = min(max_length + 2, 50)
                        worksheet.column_dimensions[column_letter].width = adjusted_width
            
            messagebox.showinfo(
                "Éxito", 
                f"✅ Datos exportados correctamente:\n\n{filepath}\n\n"
                f"📊 Total registros: {len(df_export)}\n"
                f"📋 Columnas: {len(df_export.columns)}"
            )
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo exportar:\n{e}")

# ============================================================================
# CACHE DE DATOS
# ============================================================================
class DataCache:
    """Cache simple para datos del dashboard"""
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
        self.ttl = 300  # 5 minutos
    
    def get(self, key):
        """Obtener datos del cache"""
        import time
        if key in self.cache:
            if time.time() - self.timestamps.get(key, 0) < self.ttl:
                return self.cache[key]
        return None
    
    def set(self, key, value):
        """Guardar datos en cache"""
        import time
        self.cache[key] = value
        self.timestamps[key] = time.time()
    
    def clear(self):
        """Limpiar cache"""
        self.cache.clear()
        self.timestamps.clear()

# Instancia global de cache
data_cache = DataCache()

# ============================================================================
# FUNCIÓN PRINCIPAL DEL DASHBOARD
# ============================================================================
def mostrar_dashboard_completo(conexion=None):
    """
    Dashboard Control de OFs - AIs
    Vista inicial muestra datos de OF con filtros interactivos
    ✅ VERSIÓN OPTIMIZADA - CARGA RÁPIDA Y FILTROS FUNCIONALES
    """
    global dashboard_frame, preview_frame
    
    # Desvincular eventos mousewheel
    try:
        unbind_mousewheel_recursive(dashboard_frame)
    except:
        pass

    # Ocultar preview
    try:
        preview_frame.pack_forget()
    except:
        pass
    
    # Ocultar el banner principal
    try:
        header.pack_forget()
    except:
        pass
    
    # Ocultar menú lateral
    ocultar_menu()
    
    dashboard_frame.pack(fill="both", expand=True, padx=0, pady=0)

    # Limpiar contenido anterior
    for w in dashboard_frame.winfo_children():
        w.destroy()

    # ===================== CONTENEDOR PRINCIPAL =====================
    main_container = ctk.CTkFrame(dashboard_frame, fg_color=COLOR_GRIS_CLARO, corner_radius=0)
    main_container.pack(fill="both", expand=True)

    # ===================== BARRA SUPERIOR (HEADER FIJO) =====================
    header_dash = ctk.CTkFrame(main_container, fg_color=COLOR_GRIS_OSCURO, corner_radius=0, height=60)
    header_dash.pack(fill="x", padx=0, pady=0)
    header_dash.pack_propagate(False)

    # Botón toggle menú
    toggle_frame = ctk.CTkFrame(header_dash, fg_color="transparent")
    toggle_frame.pack(side="left", padx=10)
    
    toggle_btn = ctk.CTkButton(
        toggle_frame,
        text="☰",
        width=40,
        height=40,
        fg_color=COLOR_SECONDARY,
        hover_color=COLOR_PRIMARY,
        font=("Arial", 20),
        command=toggle_menu
    )
    toggle_btn.pack()

    # Título principal
    title_container = ctk.CTkFrame(header_dash, fg_color="transparent")
    title_container.pack(side="left", padx=20)
    
    ctk.CTkLabel(
        title_container,
        text="Control de OFs - AIs",
        font=("Arial", 16, "bold"),
        text_color="white"
    ).pack(anchor="w")
    
    ctk.CTkLabel(
        title_container,
        text="Sistema de Control y Seguimiento",
        font=("Arial", 9),
        text_color="#D1D5DB"
    ).pack(anchor="w")

    # Botones de navegación OF / AI
    nav_frame = ctk.CTkFrame(header_dash, fg_color="transparent")
    nav_frame.pack(side="right", padx=20)
    
    active_tab = {"current": "OF"}
    
    def cambiar_a_of():
        active_tab["current"] = "OF"
        btn_of.configure(fg_color=COLOR_ROSA, hover_color="#BE185D")
        btn_ai.configure(fg_color="#6B7280", hover_color="#4B5563")
        cargar_contenido_of()
    
    def cambiar_a_ai():
        active_tab["current"] = "AI"
        btn_ai.configure(fg_color=COLOR_ROSA, hover_color="#BE185D")
        btn_of.configure(fg_color="#6B7280", hover_color="#4B5563")
        messagebox.showinfo("Información", "Vista de AIs - En desarrollo")
    
    btn_of = ctk.CTkButton(
        nav_frame,
        text="OF",
        width=120,
        height=35,
        fg_color=COLOR_ROSA,
        hover_color="#BE185D",
        font=("Arial", 12, "bold"),
        corner_radius=6,
        command=cambiar_a_of
    )
    btn_of.pack(side="left", padx=5)
    
    btn_ai = ctk.CTkButton(
        nav_frame,
        text="AI",
        width=120,
        height=35,
        fg_color="#6B7280",
        hover_color="#4B5563",
        font=("Arial", 12, "bold"),
        corner_radius=6,
        command=cambiar_a_ai
    )
    btn_ai.pack(side="left", padx=5)

    # ===================== ÁREA DE SCROLL =====================
    scroll_container = ctk.CTkScrollableFrame(main_container, fg_color=COLOR_GRIS_CLARO)
    scroll_container.pack(fill="both", expand=True, padx=15, pady=15)

    # ===================== FUNCIONES DE REDIRECCIÓN A TABLAS =====================
    def ir_a_tabla_determinadas(filtros):
        """Redirige a la tabla de OF Determinadas con filtros aplicados"""
        try:
            for w in dashboard_frame.winfo_children():
                w.destroy()
            
            tabla_container = ctk.CTkFrame(dashboard_frame, fg_color="white")
            tabla_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            btn_volver = ctk.CTkButton(
                tabla_container,
                text="← Volver al Dashboard",
                command=lambda: mostrar_dashboard_completo(),
                fg_color=COLOR_SECONDARY,
                hover_color=COLOR_PRIMARY,
                font=("Arial", 11, "bold"),
                width=200,
                height=35
            )
            btn_volver.pack(anchor="w", padx=15, pady=10)
            
            conn_tabla = mysql.connector.connect(**DB_CONFIG)
            anio_tabla = int(filtros['anio']) if filtros['anio'] else 2025
            
            generar_tabla_determinadas(tabla_container, conexion=conn_tabla, 
                                      cod_tipact_default="06", anio_default=anio_tabla)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la tabla:\n{e}")
    
    def ir_a_tabla_no_determinativas(filtros):
        """Redirige a la tabla de OF No Determinativas con filtros aplicados"""
        try:
            for w in dashboard_frame.winfo_children():
                w.destroy()
            
            tabla_container = ctk.CTkFrame(dashboard_frame, fg_color="white")
            tabla_container.pack(fill="both", expand=True, padx=10, pady=10)
            
            btn_volver = ctk.CTkButton(
                tabla_container,
                text="← Volver al Dashboard",
                command=lambda: mostrar_dashboard_completo(),
                fg_color=COLOR_SECONDARY,
                hover_color=COLOR_PRIMARY,
                font=("Arial", 11, "bold"),
                width=200,
                height=35
            )
            btn_volver.pack(anchor="w", padx=15, pady=10)
            
            conn_tabla = mysql.connector.connect(**DB_CONFIG)
            anio_tabla = int(filtros['anio']) if filtros['anio'] else 2025
            
            generar_tabla_no_determinativas(tabla_container, conexion=conn_tabla, anio_default=anio_tabla)
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la tabla:\n{e}")

    def ir_a_tabla_stock(filtros):
        """Redirige a la tabla Stock de Órdenes de Fiscalización"""
        try:
            for w in dashboard_frame.winfo_children():
                w.destroy()

            tabla_container = ctk.CTkFrame(dashboard_frame, fg_color="white")
            tabla_container.pack(fill="both", expand=True, padx=10, pady=10)

            btn_volver = ctk.CTkButton(
                tabla_container,
                text="← Volver al Dashboard",
                command=lambda: mostrar_dashboard_completo(),
                fg_color=COLOR_SECONDARY,
                hover_color=COLOR_PRIMARY,
                font=("Arial", 11, "bold"),
                width=200,
                height=35
            )
            btn_volver.pack(anchor="w", padx=15, pady=10)

            conn_tabla = mysql.connector.connect(**DB_CONFIG)
            generar_tabla_stock_indicador(tabla_container, conexion=conn_tabla)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la tabla:\n{e}")

    def ir_a_tabla_rendimiento_terminadas(filtros):
        """Redirige a la tabla de Rendimiento de OFs Terminadas"""
        try:
            for w in dashboard_frame.winfo_children():
                w.destroy()

            tabla_container = ctk.CTkFrame(dashboard_frame, fg_color="white")
            tabla_container.pack(fill="both", expand=True, padx=10, pady=10)

            btn_volver = ctk.CTkButton(
                tabla_container,
                text="← Volver al Dashboard",
                command=lambda: mostrar_dashboard_completo(),
                fg_color=COLOR_SECONDARY,
                hover_color=COLOR_PRIMARY,
                font=("Arial", 11, "bold"),
                width=200,
                height=35
            )
            btn_volver.pack(anchor="w", padx=15, pady=10)

            conn_tabla = mysql.connector.connect(**DB_CONFIG)
            anio_tabla = int(filtros['anio']) if filtros['anio'] else 2025

            generar_tabla_rendimiento_terminadas(tabla_container, conexion=conn_tabla, anio_default=anio_tabla)

        except Exception as e:
            messagebox.showerror("Error", f"No se pudo cargar la tabla:\n{e}")

    # ===================== FUNCIÓN PARA CARGAR CONTENIDO OF =====================
    def cargar_contenido_of():
        """Carga el contenido principal del dashboard de OFs con carga progresiva"""
        
        # Limpiar scroll_container
        for widget in scroll_container.winfo_children():
            widget.destroy()

        # Mostrar indicador de carga
        loading_frame = ctk.CTkFrame(scroll_container, fg_color="transparent")
        loading_frame.pack(expand=True, pady=50)
        
        ctk.CTkLabel(
            loading_frame,
            text="⏳ Cargando dashboard...",
            font=("Arial", 14, "bold"),
            text_color="#002e6d"
        ).pack()
        
        # Actualizar la interfaz
        scroll_container.update()

        # ===== CARGAR DATOS INICIALES =====
        try:
            # KPIs básicos (cache de 5 minutos)
            kpi_cache_key = "kpis_basicos"
            kpis_data = data_cache.get(kpi_cache_key)
            
            if kpis_data is None:
                query_total = "SELECT COUNT(*) as total FROM fiscalizaciones1"
                total_ofs = pd.read_sql(query_total, DB_ENGINE).iloc[0, 0]
                
                query_terminadas = "SELECT COUNT(*) as total FROM fiscalizaciones1 WHERE LOWER(Estado) = 'terminado'"
                ofs_terminadas = pd.read_sql(query_terminadas, DB_ENGINE).iloc[0, 0]
                
                query_pendientes = "SELECT COUNT(*) as total FROM fiscalizaciones1 WHERE LOWER(Estado) = 'pendiente'"
                ofs_pendientes = pd.read_sql(query_pendientes, DB_ENGINE).iloc[0, 0]
                
                kpis_data = {
                    'total': total_ofs,
                    'terminadas': ofs_terminadas,
                    'pendientes': ofs_pendientes
                }
                data_cache.set(kpi_cache_key, kpis_data)
            
            total_ofs = kpis_data['total']
            ofs_terminadas = kpis_data['terminadas']
            ofs_pendientes = kpis_data['pendientes']
            
            # Años disponibles (cache)
            anios_cache_key = "anios_disponibles"
            anios_data = data_cache.get(anios_cache_key)
            
            if anios_data is None:
                df_anios_termino = pd.read_sql(
                    "SELECT DISTINCT Anio_Termino FROM fiscalizaciones1 WHERE Anio_Termino IS NOT NULL ORDER BY Anio_Termino DESC", 
                    DB_ENGINE
                )
                anios_termino = [str(int(a)) for a in df_anios_termino['Anio_Termino'].tolist()]
                
                df_anios_emis = pd.read_sql(
                    "SELECT DISTINCT Anio_Emis FROM fiscalizaciones1 WHERE Anio_Emis IS NOT NULL ORDER BY Anio_Emis DESC", 
                    DB_ENGINE
                )
                anios_emis = [str(int(a)) for a in df_anios_emis['Anio_Emis'].tolist()]
                
                anios_data = {
                    'termino': anios_termino,
                    'emision': anios_emis
                }
                data_cache.set(anios_cache_key, anios_data)
            
            anios_termino = anios_data['termino']
            anios_emision = anios_data['emision']
            
        except Exception as e:
            print(f"Error cargando datos iniciales: {e}")
            total_ofs = 0
            ofs_terminadas = 0
            ofs_pendientes = 0
            anios_termino = ["2025"]
            anios_emision = ["2025"]

        # Limpiar indicador de carga
        loading_frame.destroy()

        # ===== INDICADORES PRINCIPALES =====
        kpi_row = ctk.CTkFrame(scroll_container, fg_color="transparent")
        kpi_row.pack(fill="x", pady=(0, 15))

        porc_terminadas = (ofs_terminadas / total_ofs * 100) if total_ofs > 0 else 0
        porc_pendientes = (ofs_pendientes / total_ofs * 100) if total_ofs > 0 else 0

        crear_kpi_card(
            kpi_row, 
            "📋", 
            "Total Órdenes de Fiscalización", 
            f"{total_ofs:,}",
            "Sistema Completo",
            "#E0F2FE",
            "#BAE6FD"
        )

        crear_kpi_card(
            kpi_row,
            "✅",
            "OF Terminadas",
            f"{ofs_terminadas:,}",
            f"{porc_terminadas:.1f}% del total",
            "#D1FAE5",
            "#A7F3D0"
        )

        crear_kpi_card(
            kpi_row,
            "⏳",
            "OF Pendientes",
            f"{ofs_pendientes:,}",
            f"{porc_pendientes:.1f}% del total",
            "#FED7AA",
            "#FDBA74"
        )

        # ===== ESTRUCTURA DE GRÁFICOS =====
        
        # FILA 1: Determinativas
        fila1_container = ctk.CTkFrame(scroll_container, fg_color="transparent")
        fila1_container.pack(fill="x", pady=(0, 15))

        frame_determinativas = ctk.CTkFrame(fila1_container, fg_color="white", corner_radius=12,
                                            border_width=2, border_color="#E5E7EB")
        frame_determinativas.pack(side="left", fill="both", expand=True, padx=(0, 8))

        frame_progreso_det = ctk.CTkFrame(fila1_container, fg_color="white", corner_radius=12,
                                          border_width=2, border_color="#E5E7EB")
        frame_progreso_det.pack(side="left", fill="both", expand=True, padx=(8, 0))

        # FILA 2: No Determinativas
        fila2_container = ctk.CTkFrame(scroll_container, fg_color="transparent")
        fila2_container.pack(fill="x", pady=(0, 15))

        frame_no_determinativas = ctk.CTkFrame(fila2_container, fg_color="white", corner_radius=12,
                                               border_width=2, border_color="#E5E7EB")
        frame_no_determinativas.pack(side="left", fill="both", expand=True, padx=(0, 8))

        frame_progreso_no_det = ctk.CTkFrame(fila2_container, fg_color="white", corner_radius=12,
                                             border_width=2, border_color="#E5E7EB")
        frame_progreso_no_det.pack(side="left", fill="both", expand=True, padx=(8, 0))

        # FILA 3: Stock
        fila3_container = ctk.CTkFrame(scroll_container, fg_color="transparent")
        fila3_container.pack(fill="x", pady=(0, 15))

        frame_stock_pastel = ctk.CTkFrame(fila3_container, fg_color="white", corner_radius=12,
                                          border_width=2, border_color="#E5E7EB")
        frame_stock_pastel.pack(side="left", fill="both", expand=True, padx=(0, 8))

        frame_stock_barras = ctk.CTkFrame(fila3_container, fg_color="white", corner_radius=12,
                                          border_width=2, border_color="#E5E7EB")
        frame_stock_barras.pack(side="left", fill="both", expand=True, padx=(8, 0))

        # FILA 4: Rendimiento
        fila4_container = ctk.CTkFrame(scroll_container, fg_color="transparent")
        fila4_container.pack(fill="x", pady=(0, 15))

        frame_rendimiento = ctk.CTkFrame(fila4_container, fg_color="white", corner_radius=12,
                                        border_width=2, border_color="#E5E7EB")
        frame_rendimiento.pack(fill="both", expand=True)

        # ===================== ESTADO COMPARTIDO DE FILTROS =====================
        estado_filtros = {
            'det_pastel': {'anios': ['2025']},  # Lista de años
            'det_progreso': {'anios': ['2025'], 'supervisores': [], 'auditores': []},  # Lista de años
            'no_det_pastel': {'anios': ['2025']},  # Lista de años
            'no_det_progreso': {'anios': ['2025'], 'supervisores': [], 'auditores': []},  # Lista de años
            'stock_pastel': {'anio_emis': []},  # Todos por defecto
            'stock_barras': {'anio_emis': [], 'estado': 'PENDIENTE', 'supervisores': [], 'auditores': []},
            'rendimiento': {'anios': ['2025'], 'cod': [], 'supervisores': [], 'auditores': []}  # Lista de años
        }

        # ===================== GRÁFICO 1: DETERMINATIVAS PASTEL =====================
        # Filtro: años (Anio_Termino), default [2025]
        def actualizar_grafico_determinativas():
            """Gráfico de pastel - OF Determinativas por supervisor"""
            anios_sel = estado_filtros['det_pastel']['anios']

            # Si no hay años seleccionados, usar 2025 por defecto
            if not anios_sel or len(anios_sel) == 0:
                anios_sel = ['2025']
                estado_filtros['det_pastel']['anios'] = ['2025']

            for widget in frame_determinativas.winfo_children():
                widget.destroy()

            header_det = ctk.CTkFrame(frame_determinativas, fg_color="transparent")
            header_det.pack(fill="x", padx=15, pady=(15, 5))
            
            ctk.CTkLabel(
                header_det,
                text="📊 OF Determinativas (Tipo 06)",
                font=("Arial", 12, "bold"),
                text_color="#002e6d"
            ).pack(anchor="center")

            controles_det = ctk.CTkFrame(frame_determinativas, fg_color="transparent")
            controles_det.pack(pady=8)

            # Filtro: Año
            filter_frame = ctk.CTkFrame(controles_det, fg_color="transparent")
            filter_frame.pack(side="left", padx=5)

            ctk.CTkLabel(filter_frame, text="📅 Años:", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))

            def on_anio_change():
                anios_nuevos = multi_anio_det.get_selected()
                if anios_nuevos and len(anios_nuevos) > 0:
                    estado_filtros['det_pastel']['anios'] = anios_nuevos
                else:
                    estado_filtros['det_pastel']['anios'] = ['2025']
                actualizar_grafico_determinativas()

            multi_anio_det = MultiSelectCombobox(
                filter_frame,
                anios_termino,
                default_text="Seleccionar años...",
                width=150,
                callback=on_anio_change
            )
            multi_anio_det.selected_values = set(anios_sel)
            multi_anio_det.update_button_text()
            multi_anio_det.pack(side="left")

            # Botón ver tabla
            ctk.CTkButton(
                controles_det,
                text="📋 Ver Tabla Completa",
                width=140,
                height=30,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                font=("Arial", 9, "bold"),
                command=lambda: ir_a_tabla_determinadas({'anio': anios_sel[0] if anios_sel else 2025})
            ).pack(side="left", padx=5)

            # Query y gráfico
            try:
                # Construir filtro de años
                anios_str = ", ".join([str(int(a)) for a in anios_sel])
                anio_texto = ", ".join(anios_sel[:3])
                if len(anios_sel) > 3:
                    anio_texto += f" +{len(anios_sel)-3}"

                query_det = f"""
                    SELECT NOMBRE_SUPERVISOR, COUNT(*) as total
                    FROM fiscalizaciones1
                    WHERE LOWER(Estado) = 'terminado'
                    AND COD_TIPACT = '06'
                    AND Anio_Termino IN ({anios_str})
                    GROUP BY NOMBRE_SUPERVISOR
                    ORDER BY total DESC
                    LIMIT 10
                """

                query_det_completa = f"""
                    SELECT *
                    FROM fiscalizaciones1
                    WHERE LOWER(Estado) = 'terminado'
                    AND COD_TIPACT = '06'
                    AND Anio_Termino IN ({anios_str})
                """
                
                df_det = pd.read_sql(query_det, DB_ENGINE)
                
                if not df_det.empty:
                    fig_det, ax_det = plt.subplots(figsize=(4.5, 3.5), facecolor='white')
                    
                    colores_det = ['#EC4899', '#3B82F6', '#8B5CF6', '#10B981', '#F59E0B', 
                                  '#06B6D4', '#F97316', '#14B8A6', '#8B5CF6', '#F43F5E']
                    
                    wedges, texts, autotexts = ax_det.pie(
                        df_det['total'],
                        labels=None,
                        autopct='%1.1f%%',
                        colors=colores_det[:len(df_det)],
                        startangle=90,
                        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
                    )
                    
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontsize(8)
                        autotext.set_fontweight('bold')
                    
                    ax_det.legend(
                        df_det['NOMBRE_SUPERVISOR'].tolist(),
                        loc='center left',
                        bbox_to_anchor=(1, 0.5),
                        fontsize=7,
                        frameon=False
                    )
                    
                    plt.tight_layout()
                    
                    canvas_det = FigureCanvasTkAgg(fig_det, master=frame_determinativas)
                    canvas_det.draw()
                    canvas_det.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
                    
                    # Botones de exportación
                    export_frame_det = ctk.CTkFrame(frame_determinativas, fg_color="transparent")
                    export_frame_det.pack(pady=(0, 10))

                    filtros_texto = f"Años: {anio_texto}"
                    
                    ctk.CTkButton(
                        export_frame_det,
                        text="💾 PNG",
                        width=90,
                        height=28,
                        fg_color="#10B981",
                        hover_color="#059669",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_grafico_imagen(fig_det, "OF_Determinativas", filtros_texto)
                    ).pack(side="left", padx=3)
                    
                    ctk.CTkButton(
                        export_frame_det,
                        text="📥 Excel",
                        width=90,
                        height=28,
                        fg_color="#F59E0B",
                        hover_color="#D97706",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_datos_excel(query_det_completa, "OF_Determinativas_Datos", filtros_texto)
                    ).pack(side="left", padx=3)
                else:
                    ctk.CTkLabel(frame_determinativas, text="Sin datos disponibles", 
                                font=("Arial", 11), text_color="#9CA3AF").pack(pady=50)
                    
            except Exception as e:
                print(f"Error en determinativas: {e}")
                ctk.CTkLabel(frame_determinativas, text=f"Error: {str(e)}", 
                            font=("Arial", 10), text_color="red").pack(pady=20)

        # ===================== GRÁFICO 2: PROGRESO DETERMINATIVAS =====================
        # Filtros: años (Anio_Termino, default [2025]), supervisor (multi), auditor (multi)
        def actualizar_progreso_determinativas():
            """Gráfico de progreso mensual - Determinativas"""
            anios_sel = estado_filtros['det_progreso']['anios']
            supervisores_sel = estado_filtros['det_progreso']['supervisores']
            auditores_sel = estado_filtros['det_progreso']['auditores']

            # Si no hay años seleccionados, usar 2025 por defecto
            if not anios_sel or len(anios_sel) == 0:
                anios_sel = ['2025']
                estado_filtros['det_progreso']['anios'] = ['2025']

            for widget in frame_progreso_det.winfo_children():
                widget.destroy()

            header_prog_det = ctk.CTkFrame(frame_progreso_det, fg_color="transparent")
            header_prog_det.pack(fill="x", padx=15, pady=(15, 5))
            
            ctk.CTkLabel(
                header_prog_det,
                text="📈 Progreso Mensual - Determinativas",
                font=("Arial", 12, "bold"),
                text_color="#002e6d"
            ).pack(anchor="center")

            # Obtener datos dinámicos para filtros
            try:
                anios_str = ", ".join([str(int(a)) for a in anios_sel])

                query_sup = f"""
                    SELECT DISTINCT NOMBRE_SUPERVISOR
                    FROM fiscalizaciones1
                    WHERE NOMBRE_SUPERVISOR IS NOT NULL
                    AND COD_TIPACT = '06'
                    AND Anio_Termino IN ({anios_str})
                    ORDER BY NOMBRE_SUPERVISOR
                """
                df_sup_anio = pd.read_sql(query_sup, DB_ENGINE)
                supervisores_anio = df_sup_anio['NOMBRE_SUPERVISOR'].tolist()

                query_aud = f"""
                    SELECT DISTINCT NOMBRE_AUDITOR
                    FROM fiscalizaciones1
                    WHERE NOMBRE_AUDITOR IS NOT NULL
                    AND COD_TIPACT = '06'
                    AND Anio_Termino IN ({anios_str})
                    ORDER BY NOMBRE_AUDITOR
                """
                df_aud_anio = pd.read_sql(query_aud, DB_ENGINE)
                auditores_anio = df_aud_anio['NOMBRE_AUDITOR'].tolist()

            except Exception as e:
                print(f"Error cargando filtros: {e}")
                supervisores_anio = []
                auditores_anio = []

            controles_prog = ctk.CTkFrame(frame_progreso_det, fg_color="transparent")
            controles_prog.pack(pady=8)

            # Fila 1: Años
            fila1 = ctk.CTkFrame(controles_prog, fg_color="transparent")
            fila1.pack(pady=3)

            ctk.CTkLabel(fila1, text="📅 Años:", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))

            def on_anio_prog_change():
                anios_nuevos = multi_anio_prog.get_selected()
                # Solo resetear otros filtros si los años realmente cambiaron
                if set(anios_nuevos) != set(estado_filtros['det_progreso']['anios']):
                    if anios_nuevos and len(anios_nuevos) > 0:
                        estado_filtros['det_progreso']['anios'] = anios_nuevos
                    else:
                        estado_filtros['det_progreso']['anios'] = ['2025']
                    estado_filtros['det_progreso']['supervisores'] = []
                    estado_filtros['det_progreso']['auditores'] = []
                actualizar_progreso_determinativas()

            multi_anio_prog = MultiSelectCombobox(
                fila1,
                anios_termino,
                default_text="Seleccionar años...",
                width=150,
                callback=on_anio_prog_change
            )
            multi_anio_prog.selected_values = set(anios_sel)
            multi_anio_prog.update_button_text()
            multi_anio_prog.pack(side="left")

            # Fila 2: Supervisor y Auditor
            fila2 = ctk.CTkFrame(controles_prog, fg_color="transparent")
            fila2.pack(pady=3)

            ctk.CTkLabel(fila2, text="👤 Supervisor:", font=("Arial", 10)).pack(side="left", padx=(0, 5))

            def on_supervisor_change():
                estado_filtros['det_progreso']['supervisores'] = multi_supervisor.get_selected()
                actualizar_progreso_determinativas()

            multi_supervisor = MultiSelectCombobox(
                fila2,
                supervisores_anio,
                default_text="Seleccionar...",
                width=220,
                callback=on_supervisor_change
            )
            if supervisores_sel:
                multi_supervisor.selected_values = set([s for s in supervisores_sel if s in supervisores_anio])
                multi_supervisor.update_button_text()
            multi_supervisor.pack(side="left", padx=(0, 10))

            ctk.CTkLabel(fila2, text="👨‍💼 Auditor:", font=("Arial", 10)).pack(side="left", padx=(0, 5))

            def on_auditor_change():
                estado_filtros['det_progreso']['auditores'] = multi_auditor.get_selected()
                actualizar_progreso_determinativas()

            multi_auditor = MultiSelectCombobox(
                fila2,
                auditores_anio,
                default_text="Seleccionar...",
                width=220,
                callback=on_auditor_change
            )
            if auditores_sel:
                multi_auditor.selected_values = set([a for a in auditores_sel if a in auditores_anio])
                multi_auditor.update_button_text()
            multi_auditor.pack(side="left")

            # Fila 3: Botón tabla
            fila3 = ctk.CTkFrame(controles_prog, fg_color="transparent")
            fila3.pack(pady=3)
            
            ctk.CTkButton(
                fila3,
                text="📋 Ver Tabla Completa",
                width=180,
                height=30,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                font=("Arial", 9, "bold"),
                command=lambda: ir_a_tabla_determinadas({
                    'anio': anios_sel[0] if anios_sel else 2025,
                    'supervisor': supervisores_sel if supervisores_sel else None,
                    'auditor': auditores_sel if auditores_sel else None
                })
            ).pack()

            # Query y gráfico
            try:
                anios_str = ", ".join([str(int(a)) for a in anios_sel])
                anio_texto = ", ".join(anios_sel[:3])
                if len(anios_sel) > 3:
                    anio_texto += f" +{len(anios_sel)-3}"

                where_clauses = [
                    "LOWER(Estado) = 'terminado'",
                    "COD_TIPACT = '06'",
                    f"Anio_Termino IN ({anios_str})"
                ]
                
                # Aplicar filtros de supervisor y auditor solo si hay selección
                if supervisores_sel and len(supervisores_sel) > 0:
                    supervisores_str = "', '".join([s.replace("'", "''") for s in supervisores_sel])
                    where_clauses.append(f"NOMBRE_SUPERVISOR IN ('{supervisores_str}')")

                if auditores_sel and len(auditores_sel) > 0:
                    auditores_str = "', '".join([a.replace("'", "''") for a in auditores_sel])
                    where_clauses.append(f"NOMBRE_AUDITOR IN ('{auditores_str}')")
                
                where_str = " AND ".join(where_clauses)
                
                query_prog = f"""
                    SELECT Mes_termino, COUNT(*) as total
                    FROM fiscalizaciones1
                    WHERE {where_str}
                    GROUP BY Mes_termino
                    ORDER BY Mes_termino
                """
                
                query_prog_completa = f"SELECT * FROM fiscalizaciones1 WHERE {where_str}"
                
                df_prog = pd.read_sql(query_prog, DB_ENGINE)
                
                if not df_prog.empty:
                    meses = list(range(1, 13))
                    valores = []
                    
                    for mes in meses:
                        if mes in df_prog['Mes_termino'].values:
                            valores.append(int(df_prog[df_prog['Mes_termino'] == mes]['total'].iloc[0]))
                        else:
                            valores.append(0)
                    
                    fig_prog, ax_prog = plt.subplots(figsize=(5, 3.5), facecolor='white')
                    
                    ax_prog.fill_between(meses, valores, alpha=0.3, color='#8B5CF6', linewidth=0)
                    ax_prog.plot(meses, valores, color='#8B5CF6', linewidth=2.5, marker='o', 
                                markersize=6, markerfacecolor='#8B5CF6', markeredgecolor='white', 
                                markeredgewidth=2)
                    
                    ax_prog.set_xlabel('Mes', fontsize=9, fontweight='bold')
                    ax_prog.set_ylabel('Casos Resueltos', fontsize=9, fontweight='bold')
                    ax_prog.set_xticks(meses)
                    ax_prog.set_xticklabels(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                                             'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'], 
                                            fontsize=8)
                    ax_prog.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
                    ax_prog.set_facecolor('#F9FAFB')
                    
                    max_val = max(valores) if valores else 1
                    ax_prog.set_ylim(0, max_val * 1.1)
                    
                    ax_prog.spines['top'].set_visible(False)
                    ax_prog.spines['right'].set_visible(False)
                    ax_prog.spines['left'].set_color('#D1D5DB')
                    ax_prog.spines['bottom'].set_color('#D1D5DB')
                    
                    plt.tight_layout()
                    
                    canvas_prog = FigureCanvasTkAgg(fig_prog, master=frame_progreso_det)
                    canvas_prog.draw()
                    canvas_prog.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
                    
                    # Botones exportación
                    export_frame_prog = ctk.CTkFrame(frame_progreso_det, fg_color="transparent")
                    export_frame_prog.pack(pady=(0, 10))

                    filtros_texto = f"Años: {anio_texto}"
                    if supervisores_sel and len(supervisores_sel) > 0:
                        filtros_texto += f" | Supervisores: {', '.join(supervisores_sel[:2])}"
                        if len(supervisores_sel) > 2:
                            filtros_texto += f" +{len(supervisores_sel)-2}"
                    if auditores_sel and len(auditores_sel) > 0:
                        filtros_texto += f" | Auditores: {', '.join(auditores_sel[:2])}"
                        if len(auditores_sel) > 2:
                            filtros_texto += f" +{len(auditores_sel)-2}"
                    
                    ctk.CTkButton(
                        export_frame_prog,
                        text="💾 PNG",
                        width=90,
                        height=28,
                        fg_color="#10B981",
                        hover_color="#059669",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_grafico_imagen(fig_prog, "Progreso_Determinativas", filtros_texto)
                    ).pack(side="left", padx=3)
                    
                    ctk.CTkButton(
                        export_frame_prog,
                        text="📥 Excel",
                        width=90,
                        height=28,
                        fg_color="#F59E0B",
                        hover_color="#D97706",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_datos_excel(query_prog_completa, "Progreso_Determinativas_Datos", filtros_texto)
                    ).pack(side="left", padx=3)
                else:
                    ctk.CTkLabel(frame_progreso_det, text="Sin datos disponibles", 
                                font=("Arial", 10), text_color="#9CA3AF").pack(pady=50)
                    
            except Exception as e:
                print(f"Error en progreso determinativas: {e}")
                import traceback
                traceback.print_exc()
                ctk.CTkLabel(frame_progreso_det, text=f"Error: {str(e)}", 
                            font=("Arial", 9), text_color="red").pack(pady=20)

        # ===================== GRÁFICO 3: NO DETERMINATIVAS PASTEL =====================
        # Filtro: años (Anio_Termino), default [2025]
        def actualizar_grafico_no_determinativas():
            """Gráfico de pastel - OF No Determinativas por supervisor"""
            anios_sel = estado_filtros['no_det_pastel']['anios']

            # Si no hay años seleccionados, usar 2025 por defecto
            if not anios_sel or len(anios_sel) == 0:
                anios_sel = ['2025']
                estado_filtros['no_det_pastel']['anios'] = ['2025']

            for widget in frame_no_determinativas.winfo_children():
                widget.destroy()

            header_no_det = ctk.CTkFrame(frame_no_determinativas, fg_color="transparent")
            header_no_det.pack(fill="x", padx=15, pady=(15, 5))
            
            ctk.CTkLabel(
                header_no_det,
                text="📊 OF No Determinativas (Tipo 03, 07, 08)",
                font=("Arial", 12, "bold"),
                text_color="#002e6d"
            ).pack(anchor="center")

            controles_no_det = ctk.CTkFrame(frame_no_determinativas, fg_color="transparent")
            controles_no_det.pack(pady=8)

            # Filtro: Año
            filter_frame = ctk.CTkFrame(controles_no_det, fg_color="transparent")
            filter_frame.pack(side="left", padx=5)

            ctk.CTkLabel(filter_frame, text="📅 Años:", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))

            def on_anio_no_det_change():
                anios_nuevos = multi_anio_no_det.get_selected()
                if anios_nuevos and len(anios_nuevos) > 0:
                    estado_filtros['no_det_pastel']['anios'] = anios_nuevos
                else:
                    estado_filtros['no_det_pastel']['anios'] = ['2025']
                actualizar_grafico_no_determinativas()

            multi_anio_no_det = MultiSelectCombobox(
                filter_frame,
                anios_termino,
                default_text="Seleccionar años...",
                width=150,
                callback=on_anio_no_det_change
            )
            multi_anio_no_det.selected_values = set(anios_sel)
            multi_anio_no_det.update_button_text()
            multi_anio_no_det.pack(side="left")

            # Botón ver tabla
            ctk.CTkButton(
                controles_no_det,
                text="📋 Ver Tabla Completa",
                width=140,
                height=30,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                font=("Arial", 9, "bold"),
                command=lambda: ir_a_tabla_no_determinativas({'anio': anios_sel[0] if anios_sel else 2025})
            ).pack(side="left", padx=5)

            # Query y gráfico
            try:
                anios_str = ", ".join([str(int(a)) for a in anios_sel])
                anio_texto = ", ".join(anios_sel[:3])
                if len(anios_sel) > 3:
                    anio_texto += f" +{len(anios_sel)-3}"

                query_no_det = f"""
                    SELECT NOMBRE_SUPERVISOR, COUNT(*) as total
                    FROM fiscalizaciones1
                    WHERE LOWER(Estado) = 'terminado'
                    AND COD_TIPACT IN ('03', '07', '08')
                    AND Anio_Termino IN ({anios_str})
                    GROUP BY NOMBRE_SUPERVISOR
                    ORDER BY total DESC
                    LIMIT 10
                """

                query_no_det_completa = f"""
                    SELECT *
                    FROM fiscalizaciones1
                    WHERE LOWER(Estado) = 'terminado'
                    AND COD_TIPACT IN ('03', '07', '08')
                    AND Anio_Termino IN ({anios_str})
                """
                
                df_no_det = pd.read_sql(query_no_det, DB_ENGINE)
                
                if not df_no_det.empty:
                    fig_no_det, ax_no_det = plt.subplots(figsize=(4.5, 3.5), facecolor='white')
                    
                    colores_no_det = ['#8B5CF6', '#06B6D4', '#F59E0B', '#EC4899', '#10B981',
                                     '#3B82F6', '#F97316', '#14B8A6', '#F43F5E', '#8B5CF6']
                    
                    wedges, texts, autotexts = ax_no_det.pie(
                        df_no_det['total'],
                        labels=None,
                        autopct='%1.1f%%',
                        colors=colores_no_det[:len(df_no_det)],
                        startangle=90,
                        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
                    )
                    
                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontsize(8)
                        autotext.set_fontweight('bold')
                    
                    ax_no_det.legend(
                        df_no_det['NOMBRE_SUPERVISOR'].tolist(),
                        loc='center left',
                        bbox_to_anchor=(1, 0.5),
                        fontsize=7,
                        frameon=False
                    )
                    
                    plt.tight_layout()
                    
                    canvas_no_det = FigureCanvasTkAgg(fig_no_det, master=frame_no_determinativas)
                    canvas_no_det.draw()
                    canvas_no_det.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
                    
                    # Botones exportación
                    export_frame_no_det = ctk.CTkFrame(frame_no_determinativas, fg_color="transparent")
                    export_frame_no_det.pack(pady=(0, 10))

                    filtros_texto = f"Años: {anio_texto}"
                    
                    ctk.CTkButton(
                        export_frame_no_det,
                        text="💾 PNG",
                        width=90,
                        height=28,
                        fg_color="#10B981",
                        hover_color="#059669",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_grafico_imagen(fig_no_det, "OF_No_Determinativas", filtros_texto)
                    ).pack(side="left", padx=3)
                    
                    ctk.CTkButton(
                        export_frame_no_det,
                        text="📥 Excel",
                        width=90,
                        height=28,
                        fg_color="#F59E0B",
                        hover_color="#D97706",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_datos_excel(query_no_det_completa, "OF_No_Determinativas_Datos", filtros_texto)
                    ).pack(side="left", padx=3)
                else:
                    ctk.CTkLabel(frame_no_determinativas, text="Sin datos disponibles", 
                                font=("Arial", 11), text_color="#9CA3AF").pack(pady=50)
                    
            except Exception as e:
                print(f"Error en no determinativas: {e}")
                ctk.CTkLabel(frame_no_determinativas, text=f"Error: {str(e)}", 
                            font=("Arial", 10), text_color="red").pack(pady=20)

        # ===================== GRÁFICO 4: PROGRESO NO DETERMINATIVAS =====================
        # Filtros: años (Anio_Termino, default [2025]), supervisor (multi), auditor (multi)
        def actualizar_progreso_no_determinativas():
            """Gráfico de progreso mensual - No Determinativas"""
            anios_sel = estado_filtros['no_det_progreso']['anios']
            supervisores_sel = estado_filtros['no_det_progreso']['supervisores']
            auditores_sel = estado_filtros['no_det_progreso']['auditores']

            # Si no hay años seleccionados, usar 2025 por defecto
            if not anios_sel or len(anios_sel) == 0:
                anios_sel = ['2025']
                estado_filtros['no_det_progreso']['anios'] = ['2025']

            for widget in frame_progreso_no_det.winfo_children():
                widget.destroy()

            header_prog_no_det = ctk.CTkFrame(frame_progreso_no_det, fg_color="transparent")
            header_prog_no_det.pack(fill="x", padx=15, pady=(15, 5))
            
            ctk.CTkLabel(
                header_prog_no_det,
                text="📈 Progreso Mensual - No Determinativas",
                font=("Arial", 12, "bold"),
                text_color="#002e6d"
            ).pack(anchor="center")

            # Obtener datos dinámicos para filtros
            try:
                anios_str = ", ".join([str(int(a)) for a in anios_sel])

                query_sup = f"""
                    SELECT DISTINCT NOMBRE_SUPERVISOR
                    FROM fiscalizaciones1
                    WHERE NOMBRE_SUPERVISOR IS NOT NULL
                    AND COD_TIPACT IN ('03', '07', '08')
                    AND Anio_Termino IN ({anios_str})
                    ORDER BY NOMBRE_SUPERVISOR
                """
                df_sup_anio = pd.read_sql(query_sup, DB_ENGINE)
                supervisores_anio = df_sup_anio['NOMBRE_SUPERVISOR'].tolist()

                query_aud = f"""
                    SELECT DISTINCT NOMBRE_AUDITOR
                    FROM fiscalizaciones1
                    WHERE NOMBRE_AUDITOR IS NOT NULL
                    AND COD_TIPACT IN ('03', '07', '08')
                    AND Anio_Termino IN ({anios_str})
                    ORDER BY NOMBRE_AUDITOR
                """
                df_aud_anio = pd.read_sql(query_aud, DB_ENGINE)
                auditores_anio = df_aud_anio['NOMBRE_AUDITOR'].tolist()

            except Exception as e:
                print(f"Error cargando filtros: {e}")
                supervisores_anio = []
                auditores_anio = []

            controles_prog_no = ctk.CTkFrame(frame_progreso_no_det, fg_color="transparent")
            controles_prog_no.pack(pady=8)

            # Fila 1: Años
            fila1 = ctk.CTkFrame(controles_prog_no, fg_color="transparent")
            fila1.pack(pady=3)

            ctk.CTkLabel(fila1, text="📅 Años:", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))

            def on_anio_prog_no_change():
                anios_nuevos = multi_anio_prog_no.get_selected()
                # Solo resetear otros filtros si los años realmente cambiaron
                if set(anios_nuevos) != set(estado_filtros['no_det_progreso']['anios']):
                    if anios_nuevos and len(anios_nuevos) > 0:
                        estado_filtros['no_det_progreso']['anios'] = anios_nuevos
                    else:
                        estado_filtros['no_det_progreso']['anios'] = ['2025']
                    estado_filtros['no_det_progreso']['supervisores'] = []
                    estado_filtros['no_det_progreso']['auditores'] = []
                actualizar_progreso_no_determinativas()

            multi_anio_prog_no = MultiSelectCombobox(
                fila1,
                anios_termino,
                default_text="Seleccionar años...",
                width=150,
                callback=on_anio_prog_no_change
            )
            multi_anio_prog_no.selected_values = set(anios_sel)
            multi_anio_prog_no.update_button_text()
            multi_anio_prog_no.pack(side="left")

            # Fila 2: Supervisor y Auditor
            fila2 = ctk.CTkFrame(controles_prog_no, fg_color="transparent")
            fila2.pack(pady=3)

            ctk.CTkLabel(fila2, text="👤 Supervisor:", font=("Arial", 10)).pack(side="left", padx=(0, 5))

            def on_supervisor_no_change():
                estado_filtros['no_det_progreso']['supervisores'] = multi_supervisor_no.get_selected()
                actualizar_progreso_no_determinativas()

            multi_supervisor_no = MultiSelectCombobox(
                fila2,
                supervisores_anio,
                default_text="Seleccionar...",
                width=220,
                callback=on_supervisor_no_change
            )
            if supervisores_sel:
                multi_supervisor_no.selected_values = set([s for s in supervisores_sel if s in supervisores_anio])
                multi_supervisor_no.update_button_text()
            multi_supervisor_no.pack(side="left", padx=(0, 10))

            ctk.CTkLabel(fila2, text="👨‍💼 Auditor:", font=("Arial", 10)).pack(side="left", padx=(0, 5))

            def on_auditor_no_change():
                estado_filtros['no_det_progreso']['auditores'] = multi_auditor_no.get_selected()
                actualizar_progreso_no_determinativas()

            multi_auditor_no = MultiSelectCombobox(
                fila2,
                auditores_anio,
                default_text="Seleccionar...",
                width=220,
                callback=on_auditor_no_change
            )
            if auditores_sel:
                multi_auditor_no.selected_values = set([a for a in auditores_sel if a in auditores_anio])
                multi_auditor_no.update_button_text()
            multi_auditor_no.pack(side="left")

            # Fila 3: Botón tabla
            fila3 = ctk.CTkFrame(controles_prog_no, fg_color="transparent")
            fila3.pack(pady=3)
            
            ctk.CTkButton(
                fila3,
                text="📋 Ver Tabla Completa",
                width=180,
                height=30,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                font=("Arial", 9, "bold"),
                command=lambda: ir_a_tabla_no_determinativas({
                    'anio': anios_sel[0] if anios_sel else 2025,
                    'supervisor': supervisores_sel if supervisores_sel else None,
                    'auditor': auditores_sel if auditores_sel else None
                })
            ).pack()

            # Query y gráfico
            try:
                anios_str = ", ".join([str(int(a)) for a in anios_sel])
                anio_texto = ", ".join(anios_sel[:3])
                if len(anios_sel) > 3:
                    anio_texto += f" +{len(anios_sel)-3}"

                where_clauses = [
                    "LOWER(Estado) = 'terminado'",
                    "COD_TIPACT IN ('03', '07', '08')",
                    f"Anio_Termino IN ({anios_str})"
                ]
                
                if supervisores_sel and len(supervisores_sel) > 0:
                    supervisores_str = "', '".join([s.replace("'", "''") for s in supervisores_sel])
                    where_clauses.append(f"NOMBRE_SUPERVISOR IN ('{supervisores_str}')")

                if auditores_sel and len(auditores_sel) > 0:
                    auditores_str = "', '".join([a.replace("'", "''") for a in auditores_sel])
                    where_clauses.append(f"NOMBRE_AUDITOR IN ('{auditores_str}')")
                
                where_str = " AND ".join(where_clauses)
                
                query_prog_no = f"""
                    SELECT Mes_termino, COUNT(*) as total
                    FROM fiscalizaciones1
                    WHERE {where_str}
                    GROUP BY Mes_termino
                    ORDER BY Mes_termino
                """
                
                query_prog_no_completa = f"SELECT * FROM fiscalizaciones1 WHERE {where_str}"
                
                df_prog_no = pd.read_sql(query_prog_no, DB_ENGINE)
                
                if not df_prog_no.empty:
                    meses = list(range(1, 13))
                    valores = []
                    
                    for mes in meses:
                        if mes in df_prog_no['Mes_termino'].values:
                            valores.append(int(df_prog_no[df_prog_no['Mes_termino'] == mes]['total'].iloc[0]))
                        else:
                            valores.append(0)
                    
                    fig_prog_no, ax_prog_no = plt.subplots(figsize=(5, 3.5), facecolor='white')
                    
                    ax_prog_no.fill_between(meses, valores, alpha=0.3, color='#06B6D4', linewidth=0)
                    ax_prog_no.plot(meses, valores, color='#06B6D4', linewidth=2.5, marker='o', 
                                   markersize=6, markerfacecolor='#06B6D4', markeredgecolor='white', 
                                   markeredgewidth=2)
                    
                    ax_prog_no.set_xlabel('Mes', fontsize=9, fontweight='bold')
                    ax_prog_no.set_ylabel('Casos Resueltos', fontsize=9, fontweight='bold')
                    ax_prog_no.set_xticks(meses)
                    ax_prog_no.set_xticklabels(['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 
                                                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'], 
                                               fontsize=8)
                    ax_prog_no.grid(True, alpha=0.2, linestyle='--', linewidth=0.5)
                    ax_prog_no.set_facecolor('#F9FAFB')
                    
                    max_val = max(valores) if valores else 1
                    ax_prog_no.set_ylim(0, max_val * 1.1)
                    
                    ax_prog_no.spines['top'].set_visible(False)
                    ax_prog_no.spines['right'].set_visible(False)
                    ax_prog_no.spines['left'].set_color('#D1D5DB')
                    ax_prog_no.spines['bottom'].set_color('#D1D5DB')
                    
                    plt.tight_layout()
                    
                    canvas_prog_no = FigureCanvasTkAgg(fig_prog_no, master=frame_progreso_no_det)
                    canvas_prog_no.draw()
                    canvas_prog_no.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
                    
                    # Botones exportación
                    export_frame_prog_no = ctk.CTkFrame(frame_progreso_no_det, fg_color="transparent")
                    export_frame_prog_no.pack(pady=(0, 10))

                    filtros_texto = f"Años: {anio_texto}"
                    if supervisores_sel and len(supervisores_sel) > 0:
                        filtros_texto += f" | Supervisores: {', '.join(supervisores_sel[:2])}"
                        if len(supervisores_sel) > 2:
                            filtros_texto += f" +{len(supervisores_sel)-2}"
                    if auditores_sel and len(auditores_sel) > 0:
                        filtros_texto += f" | Auditores: {', '.join(auditores_sel[:2])}"
                        if len(auditores_sel) > 2:
                            filtros_texto += f" +{len(auditores_sel)-2}"
                    
                    ctk.CTkButton(
                        export_frame_prog_no,
                        text="💾 PNG",
                        width=90,
                        height=28,
                        fg_color="#10B981",
                        hover_color="#059669",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_grafico_imagen(fig_prog_no, "Progreso_No_Determinativas", filtros_texto)
                    ).pack(side="left", padx=3)
                    
                    ctk.CTkButton(
                        export_frame_prog_no,
                        text="📥 Excel",
                        width=90,
                        height=28,
                        fg_color="#F59E0B",
                        hover_color="#D97706",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_datos_excel(query_prog_no_completa, "Progreso_No_Determinativas_Datos", filtros_texto)
                    ).pack(side="left", padx=3)
                else:
                    ctk.CTkLabel(frame_progreso_no_det, text="Sin datos disponibles", 
                                font=("Arial", 10), text_color="#9CA3AF").pack(pady=50)
                    
            except Exception as e:
                print(f"Error en progreso no determinativas: {e}")
                import traceback
                traceback.print_exc()
                ctk.CTkLabel(frame_progreso_no_det, text=f"Error: {str(e)}", 
                            font=("Arial", 9), text_color="red").pack(pady=20)

        # ===================== GRÁFICO 5: STOCK PASTEL =====================
        # Filtro: año emisión (Anio_Emis), todos por defecto
        def actualizar_grafico_stock_pastel():
            """Gráfico de pastel - Distribución de tipos stock"""
            anios_emis_sel = estado_filtros['stock_pastel']['anio_emis']
            
            for widget in frame_stock_pastel.winfo_children():
                widget.destroy()

            header_stock = ctk.CTkFrame(frame_stock_pastel, fg_color="transparent")
            header_stock.pack(fill="x", padx=15, pady=(15, 5))
            
            ctk.CTkLabel(
                header_stock,
                text="📊 Distribución de Tipos Stock",
                font=("Arial", 12, "bold"),
                text_color="#002e6d"
            ).pack(anchor="center")

            controles_stock = ctk.CTkFrame(frame_stock_pastel, fg_color="transparent")
            controles_stock.pack(pady=8)

            # Filtro: Año Emisión
            filter_frame = ctk.CTkFrame(controles_stock, fg_color="transparent")
            filter_frame.pack(side="left", padx=5)

            ctk.CTkLabel(filter_frame, text="📅 Año Emisión:", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))

            def on_anio_stock_change():
                estado_filtros['stock_pastel']['anio_emis'] = multi_anio_stock.get_selected()
                actualizar_grafico_stock_pastel()

            multi_anio_stock = MultiSelectCombobox(
                filter_frame,
                anios_emision,
                default_text="Seleccionar años...",
                width=150,
                callback=on_anio_stock_change
            )
            # Todos seleccionados por defecto si no hay selección
            if not anios_emis_sel:
                multi_anio_stock.selected_values = set()
            else:
                multi_anio_stock.selected_values = set([str(a) for a in anios_emis_sel if str(a) in anios_emision])
            multi_anio_stock.update_button_text()
            multi_anio_stock.pack(side="left")

            # Botón ver tabla
            ctk.CTkButton(
                controles_stock,
                text="📋 Ver Tabla Stock",
                width=140,
                height=30,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                font=("Arial", 9, "bold"),
                command=lambda: ir_a_tabla_stock({'anio_emis': anios_emis_sel})
            ).pack(side="left", padx=5)

            # Query y gráfico
            try:
                # Determinar filtro de año
                if not anios_emis_sel or len(anios_emis_sel) == len(anios_emision):
                    filtro_anio = ""
                    anio_texto = "Todos"
                else:
                    anios_str = ", ".join([str(int(a)) for a in anios_emis_sel])
                    filtro_anio = f"AND Anio_Emis IN ({anios_str})"
                    anio_texto = ", ".join([str(a) for a in anios_emis_sel[:3]])
                    if len(anios_emis_sel) > 3:
                        anio_texto += f" +{len(anios_emis_sel)-3}"
                
                query_stock = f"""
                    SELECT CAST(Stock_AUD_25 AS CHAR) as tipo, COUNT(*) as total
                    FROM fiscalizaciones1
                    WHERE CAST(Stock_AUD_25 AS CHAR) IN ('1', '2', '3')
                    {filtro_anio}
                    AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
                    GROUP BY CAST(Stock_AUD_25 AS CHAR)
                    ORDER BY CAST(Stock_AUD_25 AS CHAR)
                """

                query_stock_completa = f"""
                    SELECT *
                    FROM fiscalizaciones1
                    WHERE CAST(Stock_AUD_25 AS CHAR) IN ('1', '2', '3')
                    {filtro_anio}
                    AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
                """

                df_stock = pd.read_sql(query_stock, DB_ENGINE)

                if not df_stock.empty:
                    fig_stock, ax_stock = plt.subplots(figsize=(4.5, 3.5), facecolor='white')

                    colores_stock = ['#EC4899', '#3B82F6', '#8B5CF6']
                    labels_stock = [f'Tipo {t}' for t in df_stock['tipo']]

                    wedges, texts, autotexts = ax_stock.pie(
                        df_stock['total'],
                        labels=None,
                        autopct='%1.1f%%',
                        colors=colores_stock[:len(df_stock)],
                        startangle=90,
                        wedgeprops=dict(width=0.4, edgecolor='white', linewidth=2)
                    )

                    for autotext in autotexts:
                        autotext.set_color('white')
                        autotext.set_fontsize(10)
                        autotext.set_fontweight('bold')

                    ax_stock.legend(
                        labels_stock,
                        loc='center left',
                        bbox_to_anchor=(1, 0.5),
                        fontsize=9,
                        frameon=False
                    )

                    plt.tight_layout()

                    canvas_stock = FigureCanvasTkAgg(fig_stock, master=frame_stock_pastel)
                    canvas_stock.draw()
                    canvas_stock.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

                    # Botones exportación
                    export_frame_stock = ctk.CTkFrame(frame_stock_pastel, fg_color="transparent")
                    export_frame_stock.pack(pady=(0, 10))

                    filtros_texto = f"Año Emisión: {anio_texto}"

                    ctk.CTkButton(
                        export_frame_stock,
                        text="💾 PNG",
                        width=90,
                        height=28,
                        fg_color="#10B981",
                        hover_color="#059669",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_grafico_imagen(fig_stock, "Stock_Tipos_Distribucion", filtros_texto)
                    ).pack(side="left", padx=3)

                    ctk.CTkButton(
                        export_frame_stock,
                        text="📥 Excel",
                        width=90,
                        height=28,
                        fg_color="#F59E0B",
                        hover_color="#D97706",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_datos_excel(query_stock_completa, "Stock_Tipos_Datos", filtros_texto)
                    ).pack(side="left", padx=3)
                else:
                    ctk.CTkLabel(frame_stock_pastel, text="Sin datos disponibles",
                                font=("Arial", 11), text_color="#9CA3AF").pack(pady=50)

            except Exception as e:
                import traceback
                print(f"Error en gráfico stock pastel: {e}")
                traceback.print_exc()
                ctk.CTkLabel(frame_stock_pastel, text=f"Error: {str(e)}",
                            font=("Arial", 10), text_color="red").pack(pady=20)

        # ===================== GRÁFICO 6: STOCK BARRAS =====================
        # Filtros: año emisión (Anio_Emis, todos), estado (default PENDIENTE), supervisor (multi), auditor (multi)
        def actualizar_grafico_stock_barras():
            """Gráfico de barras - Stock por tipo y mes de emisión"""
            anios_emis_sel = estado_filtros['stock_barras']['anio_emis']
            estado_sel = estado_filtros['stock_barras']['estado']
            supervisores_sel = estado_filtros['stock_barras']['supervisores']
            auditores_sel = estado_filtros['stock_barras']['auditores']
            
            for widget in frame_stock_barras.winfo_children():
                widget.destroy()

            header_barras = ctk.CTkFrame(frame_stock_barras, fg_color="transparent")
            header_barras.pack(fill="x", padx=15, pady=(15, 5))

            ctk.CTkLabel(
                header_barras,
                text="📊 Stock por Tipo y Mes de Emisión",
                font=("Arial", 12, "bold"),
                text_color="#002e6d"
            ).pack(anchor="center")

            # Construir filtro de año
            if not anios_emis_sel or len(anios_emis_sel) == len(anios_emision):
                filtro_anio_query = ""
                anio_texto = "Todos"
            else:
                anios_str = ", ".join([str(int(a)) for a in anios_emis_sel])
                filtro_anio_query = f"AND Anio_Emis IN ({anios_str})"
                anio_texto = ", ".join([str(a) for a in anios_emis_sel[:2]])
                if len(anios_emis_sel) > 2:
                    anio_texto += f" +{len(anios_emis_sel)-2}"

            # Obtener estados disponibles
            try:
                query_estados = f"""
                    SELECT DISTINCT UPPER(Estado) as estado
                    FROM fiscalizaciones1
                    WHERE Estado IS NOT NULL
                    AND CAST(Stock_AUD_25 AS CHAR) IN ('1', '2', '3')
                    {filtro_anio_query}
                    AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
                    ORDER BY estado
                """
                df_estados = pd.read_sql(query_estados, DB_ENGINE)
                estados_disponibles = df_estados['estado'].tolist()
            except:
                estados_disponibles = ["PENDIENTE", "TERMINADO"]

            # Obtener supervisores y auditores disponibles
            try:
                query_sup = f"""
                    SELECT DISTINCT NOMBRE_SUPERVISOR
                    FROM fiscalizaciones1
                    WHERE NOMBRE_SUPERVISOR IS NOT NULL
                    AND CAST(Stock_AUD_25 AS CHAR) IN ('1', '2', '3')
                    {filtro_anio_query}
                    AND UPPER(Estado) = '{estado_sel.upper()}'
                    AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
                    ORDER BY NOMBRE_SUPERVISOR
                """
                df_sup_anio = pd.read_sql(query_sup, DB_ENGINE)
                supervisores_anio = df_sup_anio['NOMBRE_SUPERVISOR'].tolist()

                query_aud = f"""
                    SELECT DISTINCT NOMBRE_AUDITOR
                    FROM fiscalizaciones1
                    WHERE NOMBRE_AUDITOR IS NOT NULL
                    AND CAST(Stock_AUD_25 AS CHAR) IN ('1', '2', '3')
                    {filtro_anio_query}
                    AND UPPER(Estado) = '{estado_sel.upper()}'
                    AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
                    ORDER BY NOMBRE_AUDITOR
                """
                df_aud_anio = pd.read_sql(query_aud, DB_ENGINE)
                auditores_anio = df_aud_anio['NOMBRE_AUDITOR'].tolist()
            except:
                supervisores_anio = []
                auditores_anio = []

            controles_barras = ctk.CTkFrame(frame_stock_barras, fg_color="transparent")
            controles_barras.pack(pady=8)

            # Fila 1: Año y Estado
            fila1 = ctk.CTkFrame(controles_barras, fg_color="transparent")
            fila1.pack(pady=3)

            ctk.CTkLabel(fila1, text="📅 Año Emisión:", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))

            def on_anio_barras_change():
                nuevos_anios = multi_anio_barras.get_selected()
                # Solo resetear otros filtros si los años realmente cambiaron
                if set(nuevos_anios) != set(estado_filtros['stock_barras']['anio_emis']):
                    estado_filtros['stock_barras']['anio_emis'] = nuevos_anios
                    estado_filtros['stock_barras']['supervisores'] = []
                    estado_filtros['stock_barras']['auditores'] = []
                actualizar_grafico_stock_barras()

            multi_anio_barras = MultiSelectCombobox(
                fila1,
                anios_emision,
                default_text="Seleccionar...",
                width=150,
                callback=on_anio_barras_change
            )
            if not anios_emis_sel or len(anios_emis_sel) == len(anios_emision):
                multi_anio_barras.selected_values = set()
            else:
                multi_anio_barras.selected_values = set([str(a) for a in anios_emis_sel if str(a) in anios_emision])
            multi_anio_barras.update_button_text()
            multi_anio_barras.pack(side="left", padx=(0, 15))

            ctk.CTkLabel(fila1, text="📊 Estado:", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))

            def on_estado_barras_change():
                estado_nuevo = multi_estado_barras.get_selected()[0] if multi_estado_barras.get_selected() else estado_sel
                # Solo resetear otros filtros si el estado realmente cambió
                if estado_nuevo.upper() != estado_filtros['stock_barras']['estado']:
                    estado_filtros['stock_barras']['estado'] = estado_nuevo.upper()
                    estado_filtros['stock_barras']['supervisores'] = []
                    estado_filtros['stock_barras']['auditores'] = []
                actualizar_grafico_stock_barras()

            multi_estado_barras = MultiSelectCombobox(
                fila1,
                estados_disponibles,
                default_text="Seleccionar...",
                width=150,
                callback=on_estado_barras_change
            )
            multi_estado_barras.selected_values = {estado_sel.upper()}
            multi_estado_barras.update_button_text()
            multi_estado_barras.pack(side="left")

            # Fila 2: Supervisor y Auditor
            fila2 = ctk.CTkFrame(controles_barras, fg_color="transparent")
            fila2.pack(pady=3)

            ctk.CTkLabel(fila2, text="👤 Supervisor:", font=("Arial", 10)).pack(side="left", padx=(0, 5))

            def on_supervisor_barras_change():
                estado_filtros['stock_barras']['supervisores'] = multi_supervisor_barras.get_selected()
                actualizar_grafico_stock_barras()

            multi_supervisor_barras = MultiSelectCombobox(
                fila2,
                supervisores_anio,
                default_text="Seleccionar...",
                width=180,
                callback=on_supervisor_barras_change
            )
            if supervisores_sel:
                multi_supervisor_barras.selected_values = set([s for s in supervisores_sel if s in supervisores_anio])
                multi_supervisor_barras.update_button_text()
            multi_supervisor_barras.pack(side="left", padx=(0, 10))

            ctk.CTkLabel(fila2, text="👨‍💼 Auditor:", font=("Arial", 10)).pack(side="left", padx=(0, 5))

            def on_auditor_barras_change():
                estado_filtros['stock_barras']['auditores'] = multi_auditor_barras.get_selected()
                actualizar_grafico_stock_barras()

            multi_auditor_barras = MultiSelectCombobox(
                fila2,
                auditores_anio,
                default_text="Seleccionar...",
                width=180,
                callback=on_auditor_barras_change
            )
            if auditores_sel:
                multi_auditor_barras.selected_values = set([a for a in auditores_sel if a in auditores_anio])
                multi_auditor_barras.update_button_text()
            multi_auditor_barras.pack(side="left")

            # Fila 3: Botón tabla
            fila3 = ctk.CTkFrame(controles_barras, fg_color="transparent")
            fila3.pack(pady=3)

            ctk.CTkButton(
                fila3,
                text="📋 Ver Tabla Stock Completa",
                width=200,
                height=30,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                font=("Arial", 9, "bold"),
                command=lambda: ir_a_tabla_stock({'anio_emis': anios_emis_sel, 'estado': estado_sel})
            ).pack()

            # Query y gráfico
            try:
                where_clauses = [
                    "CAST(Stock_AUD_25 AS CHAR) IN ('1', '2', '3')",
                    f"UPPER(Estado) = '{estado_sel.upper()}'",
                    "LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'"
                ]

                if anios_emis_sel and len(anios_emis_sel) < len(anios_emision):
                    anios_str = ", ".join([str(int(a)) for a in anios_emis_sel])
                    where_clauses.append(f"Anio_Emis IN ({anios_str})")

                if supervisores_sel and len(supervisores_sel) > 0:
                    supervisores_escaped = [s.replace("'", "''") for s in supervisores_sel]
                    supervisores_str = "', '".join(supervisores_escaped)
                    where_clauses.append(f"NOMBRE_SUPERVISOR IN ('{supervisores_str}')")

                if auditores_sel and len(auditores_sel) > 0:
                    auditores_escaped = [a.replace("'", "''") for a in auditores_sel]
                    auditores_str = "', '".join(auditores_escaped)
                    where_clauses.append(f"NOMBRE_AUDITOR IN ('{auditores_str}')")

                where_str = " AND ".join(where_clauses)

                query_barras = f"""
                    SELECT CAST(Stock_AUD_25 AS CHAR) as tipo, Mes_Emis, COUNT(*) as cantidad
                    FROM fiscalizaciones1
                    WHERE {where_str} AND Mes_Emis IS NOT NULL
                    GROUP BY CAST(Stock_AUD_25 AS CHAR), Mes_Emis
                    ORDER BY tipo, Mes_Emis
                """

                query_completa = f"SELECT * FROM fiscalizaciones1 WHERE {where_str}"

                df_barras = pd.read_sql(query_barras, DB_ENGINE)

                if not df_barras.empty:
                    meses = list(range(1, 13))
                    meses_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

                    datos_tipos = {}
                    for tipo in ['1', '2', '3']:
                        df_tipo = df_barras[df_barras['tipo'] == tipo]
                        valores = []
                        for mes in meses:
                            if mes in df_tipo['Mes_Emis'].values:
                                valores.append(int(df_tipo[df_tipo['Mes_Emis'] == mes]['cantidad'].iloc[0]))
                            else:
                                valores.append(0)
                        datos_tipos[tipo] = valores

                    fig_barras, ax_barras = plt.subplots(figsize=(5, 3.5), facecolor='white')

                    x = np.arange(len(meses))
                    width = 0.25

                    colores = {'1': '#EC4899', '2': '#3B82F6', '3': '#8B5CF6'}

                    for i, (tipo, valores) in enumerate(datos_tipos.items()):
                        offset = width * (i - 1)
                        ax_barras.bar(x + offset, valores, width, label=f'Tipo {tipo}',
                                    color=colores[tipo], alpha=0.85, edgecolor='white', linewidth=1.5)

                    ax_barras.set_xlabel('Mes de Emisión', fontsize=9, fontweight='bold')
                    ax_barras.set_ylabel('Cantidad', fontsize=9, fontweight='bold')
                    ax_barras.set_xticks(x)
                    ax_barras.set_xticklabels(meses_labels, fontsize=8)
                    ax_barras.legend(fontsize=8, loc='upper left', framealpha=0.9)
                    ax_barras.grid(True, alpha=0.2, linestyle='--', linewidth=0.5, axis='y')
                    ax_barras.set_facecolor('#F9FAFB')

                    ax_barras.spines['top'].set_visible(False)
                    ax_barras.spines['right'].set_visible(False)

                    plt.tight_layout()

                    canvas_barras = FigureCanvasTkAgg(fig_barras, master=frame_stock_barras)
                    canvas_barras.draw()
                    canvas_barras.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

                    # Botones exportación
                    export_frame = ctk.CTkFrame(frame_stock_barras, fg_color="transparent")
                    export_frame.pack(pady=(0, 10))

                    filtros_texto = f"Año Emisión: {anio_texto} | Estado: {estado_sel}"
                    if supervisores_sel and len(supervisores_sel) > 0:
                        filtros_texto += f" | Supervisores: {len(supervisores_sel)}"
                    if auditores_sel and len(auditores_sel) > 0:
                        filtros_texto += f" | Auditores: {len(auditores_sel)}"

                    ctk.CTkButton(
                        export_frame,
                        text="💾 PNG",
                        width=90,
                        height=28,
                        fg_color="#10B981",
                        hover_color="#059669",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_grafico_imagen(fig_barras, "Stock_Mensual", filtros_texto)
                    ).pack(side="left", padx=3)

                    ctk.CTkButton(
                        export_frame,
                        text="📥 Excel",
                        width=90,
                        height=28,
                        fg_color="#F59E0B",
                        hover_color="#D97706",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_datos_excel(query_completa, "Stock_Mensual_Datos", filtros_texto)
                    ).pack(side="left", padx=3)
                else:
                    ctk.CTkLabel(frame_stock_barras, text="Sin datos disponibles",
                                font=("Arial", 10), text_color="#9CA3AF").pack(pady=50)

            except Exception as e:
                import traceback
                print(f"Error en stock barras: {e}")
                traceback.print_exc()
                ctk.CTkLabel(frame_stock_barras, text=f"Error: {str(e)}",
                            font=("Arial", 9), text_color="red").pack(pady=20)

        # ===================== GRÁFICO 7: RENDIMIENTO MENSUAL =====================
        # Filtros: años (Anio_Termino, default [2025]), supervisor (multi), auditor (multi), COD_TIPACT (multi)
        def actualizar_grafico_rendimiento():
            """Gráfico de rendimiento mensual - OF Terminadas"""
            anios_sel = estado_filtros['rendimiento']['anios']
            cod_tipact_sel = estado_filtros['rendimiento']['cod']
            supervisores_sel = estado_filtros['rendimiento']['supervisores']
            auditores_sel = estado_filtros['rendimiento']['auditores']

            # Si no hay años seleccionados, usar 2025 por defecto
            if not anios_sel or len(anios_sel) == 0:
                anios_sel = ['2025']
                estado_filtros['rendimiento']['anios'] = ['2025']

            for widget in frame_rendimiento.winfo_children():
                widget.destroy()

            header_rend = ctk.CTkFrame(frame_rendimiento, fg_color="transparent")
            header_rend.pack(fill="x", padx=15, pady=(15, 5))

            ctk.CTkLabel(
                header_rend,
                text="📊 Rendimiento Mensual - OFs Terminadas",
                font=("Arial", 12, "bold"),
                text_color="#002e6d"
            ).pack(anchor="center")

            # Obtener códigos disponibles
            try:
                anios_str = ", ".join([str(int(a)) for a in anios_sel])

                query_cod = f"""
                    SELECT DISTINCT COD_TIPACT
                    FROM fiscalizaciones1
                    WHERE COD_TIPACT IS NOT NULL
                    AND Anio_Termino IN ({anios_str})
                    AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
                    ORDER BY COD_TIPACT
                """
                df_cod_anio = pd.read_sql(query_cod, DB_ENGINE)
                codigos_anio = df_cod_anio['COD_TIPACT'].astype(str).str.strip().tolist()
            except:
                codigos_anio = []

            # Construir filtro de códigos para supervisores/auditores
            filtro_cod_query = ""
            if cod_tipact_sel and len(cod_tipact_sel) > 0:
                codigos_str = "', '".join([str(c).strip() for c in cod_tipact_sel])
                filtro_cod_query = f"AND COD_TIPACT IN ('{codigos_str}')"

            # Obtener supervisores y auditores
            try:
                query_sup = f"""
                    SELECT DISTINCT NOMBRE_SUPERVISOR
                    FROM fiscalizaciones1
                    WHERE NOMBRE_SUPERVISOR IS NOT NULL
                    AND Anio_Termino IN ({anios_str})
                    AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
                    {filtro_cod_query}
                    ORDER BY NOMBRE_SUPERVISOR
                """
                df_sup_anio = pd.read_sql(query_sup, DB_ENGINE)
                supervisores_anio = df_sup_anio['NOMBRE_SUPERVISOR'].tolist()

                query_aud = f"""
                    SELECT DISTINCT NOMBRE_AUDITOR
                    FROM fiscalizaciones1
                    WHERE NOMBRE_AUDITOR IS NOT NULL
                    AND Anio_Termino IN ({anios_str})
                    AND LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'
                    {filtro_cod_query}
                    ORDER BY NOMBRE_AUDITOR
                """
                df_aud_anio = pd.read_sql(query_aud, DB_ENGINE)
                auditores_anio = df_aud_anio['NOMBRE_AUDITOR'].tolist()

            except:
                supervisores_anio = []
                auditores_anio = []

            controles_rend = ctk.CTkFrame(frame_rendimiento, fg_color="transparent")
            controles_rend.pack(pady=8)

            # Fila 1: Años y Código
            fila1_rend = ctk.CTkFrame(controles_rend, fg_color="transparent")
            fila1_rend.pack(pady=3)

            ctk.CTkLabel(fila1_rend, text="📅 Años:", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))

            def on_anio_rend_change():
                anios_nuevos = multi_anio_rend.get_selected()
                # Solo resetear otros filtros si los años realmente cambiaron
                if set(anios_nuevos) != set(estado_filtros['rendimiento']['anios']):
                    if anios_nuevos and len(anios_nuevos) > 0:
                        estado_filtros['rendimiento']['anios'] = anios_nuevos
                    else:
                        estado_filtros['rendimiento']['anios'] = ['2025']
                    estado_filtros['rendimiento']['supervisores'] = []
                    estado_filtros['rendimiento']['auditores'] = []
                actualizar_grafico_rendimiento()

            multi_anio_rend = MultiSelectCombobox(
                fila1_rend,
                anios_termino,
                default_text="Seleccionar años...",
                width=150,
                callback=on_anio_rend_change
            )
            multi_anio_rend.selected_values = set(anios_sel)
            multi_anio_rend.update_button_text()
            multi_anio_rend.pack(side="left", padx=(0, 15))

            ctk.CTkLabel(fila1_rend, text="🔢 COD:", font=("Arial", 10, "bold")).pack(side="left", padx=(0, 5))

            def on_cod_rend_change():
                nuevos_cod = multi_cod_rend.get_selected()
                # Solo resetear otros filtros si los códigos realmente cambiaron
                if set(nuevos_cod) != set(estado_filtros['rendimiento']['cod']):
                    estado_filtros['rendimiento']['cod'] = nuevos_cod
                    estado_filtros['rendimiento']['supervisores'] = []
                    estado_filtros['rendimiento']['auditores'] = []
                actualizar_grafico_rendimiento()

            multi_cod_rend = MultiSelectCombobox(
                fila1_rend,
                codigos_anio,
                default_text="Seleccionar...",
                width=150,
                callback=on_cod_rend_change
            )
            if cod_tipact_sel:
                multi_cod_rend.selected_values = set([str(c) for c in cod_tipact_sel if str(c) in codigos_anio])
                multi_cod_rend.update_button_text()
            multi_cod_rend.pack(side="left")

            # Fila 2: Supervisor y Auditor
            fila2_rend = ctk.CTkFrame(controles_rend, fg_color="transparent")
            fila2_rend.pack(pady=3)

            ctk.CTkLabel(fila2_rend, text="👤 Supervisor:", font=("Arial", 10)).pack(side="left", padx=(0, 5))

            def on_supervisor_rend_change():
                estado_filtros['rendimiento']['supervisores'] = multi_supervisor_rend.get_selected()
                actualizar_grafico_rendimiento()

            multi_supervisor_rend = MultiSelectCombobox(
                fila2_rend,
                supervisores_anio,
                default_text="Seleccionar...",
                width=180,
                callback=on_supervisor_rend_change
            )
            if supervisores_sel:
                multi_supervisor_rend.selected_values = set([s for s in supervisores_sel if s in supervisores_anio])
                multi_supervisor_rend.update_button_text()
            multi_supervisor_rend.pack(side="left", padx=(0, 10))

            ctk.CTkLabel(fila2_rend, text="👨‍💼 Auditor:", font=("Arial", 10)).pack(side="left", padx=(0, 5))

            def on_auditor_rend_change():
                estado_filtros['rendimiento']['auditores'] = multi_auditor_rend.get_selected()
                actualizar_grafico_rendimiento()

            multi_auditor_rend = MultiSelectCombobox(
                fila2_rend,
                auditores_anio,
                default_text="Seleccionar...",
                width=180,
                callback=on_auditor_rend_change
            )
            if auditores_sel:
                multi_auditor_rend.selected_values = set([a for a in auditores_sel if a in auditores_anio])
                multi_auditor_rend.update_button_text()
            multi_auditor_rend.pack(side="left")

            # Fila 3: Botón tabla
            fila3_rend = ctk.CTkFrame(controles_rend, fg_color="transparent")
            fila3_rend.pack(pady=3)

            ctk.CTkButton(
                fila3_rend,
                text="📋 Ver Tabla Rendimiento Completa",
                width=230,
                height=30,
                fg_color="#3B82F6",
                hover_color="#2563EB",
                font=("Arial", 9, "bold"),
                command=lambda: ir_a_tabla_rendimiento_terminadas({'anio': anios_sel[0] if anios_sel else 2025})
            ).pack()

            # Query y gráfico
            try:
                anios_str = ", ".join([str(int(a)) for a in anios_sel])
                anio_texto = ", ".join(anios_sel[:3])
                if len(anios_sel) > 3:
                    anio_texto += f" +{len(anios_sel)-3}"

                where_clauses = [
                    "LOWER(IFNULL(des_cod,'')) NOT LIKE '%%devol%%'",
                    f"Anio_Termino IN ({anios_str})"
                ]

                if cod_tipact_sel and len(cod_tipact_sel) > 0:
                    codigos_str = "', '".join([str(c).strip() for c in cod_tipact_sel])
                    where_clauses.append(f"COD_TIPACT IN ('{codigos_str}')")

                if supervisores_sel and len(supervisores_sel) > 0:
                    supervisores_escaped = [s.replace("'", "''") for s in supervisores_sel]
                    supervisores_str = "', '".join(supervisores_escaped)
                    where_clauses.append(f"NOMBRE_SUPERVISOR IN ('{supervisores_str}')")

                if auditores_sel and len(auditores_sel) > 0:
                    auditores_escaped = [a.replace("'", "''") for a in auditores_sel]
                    auditores_str = "', '".join(auditores_escaped)
                    where_clauses.append(f"NOMBRE_AUDITOR IN ('{auditores_str}')")

                where_str = " AND ".join(where_clauses)

                query_rendimiento = f"""
                    SELECT
                        Mes_Emis,
                        SUM(COALESCE(MTO_PAG_IN, 0)) as pago_inducido,
                        SUM(COALESCE(MTO_PAG_RE, 0)) as rectificatoria,
                        SUM(COALESCE(MTO_VAL_DE, 0)) as valores
                    FROM fiscalizaciones1
                    WHERE {where_str} AND Mes_Emis IS NOT NULL
                    GROUP BY Mes_Emis
                    ORDER BY Mes_Emis
                """

                query_completa = f"SELECT * FROM fiscalizaciones1 WHERE {where_str}"

                df_rend = pd.read_sql(query_rendimiento, DB_ENGINE)

                if not df_rend.empty:
                    meses = list(range(1, 13))
                    meses_labels = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun',
                                'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic']

                    pago_inducido_vals = []
                    rectificatoria_vals = []
                    valores_vals = []

                    for mes in meses:
                        if mes in df_rend['Mes_Emis'].values:
                            row = df_rend[df_rend['Mes_Emis'] == mes].iloc[0]
                            pago_inducido_vals.append(float(row['pago_inducido']))
                            rectificatoria_vals.append(float(row['rectificatoria']))
                            valores_vals.append(float(row['valores']))
                        else:
                            pago_inducido_vals.append(0)
                            rectificatoria_vals.append(0)
                            valores_vals.append(0)

                    fig_rend, ax_rend = plt.subplots(figsize=(10, 4), facecolor='white')

                    x = np.arange(len(meses))
                    width = 0.25

                    color_pago = '#EC4899'
                    color_rect = '#3B82F6'
                    color_val = '#10B981'

                    ax_rend.bar(x - width, pago_inducido_vals, width, label='Pago Inducido',
                              color=color_pago, alpha=0.85, edgecolor='white', linewidth=1.5)
                    ax_rend.bar(x, rectificatoria_vals, width, label='Rectificatoria',
                              color=color_rect, alpha=0.85, edgecolor='white', linewidth=1.5)
                    ax_rend.bar(x + width, valores_vals, width, label='Valores',
                              color=color_val, alpha=0.85, edgecolor='white', linewidth=1.5)

                    ax_rend.set_xlabel('Mes de Emisión', fontsize=10, fontweight='bold')
                    ax_rend.set_ylabel('Monto (S/)', fontsize=10, fontweight='bold')
                    ax_rend.set_xticks(x)
                    ax_rend.set_xticklabels(meses_labels, fontsize=9)
                    ax_rend.legend(fontsize=9, loc='upper left', framealpha=0.9)
                    ax_rend.grid(True, alpha=0.2, linestyle='--', linewidth=0.5, axis='y')
                    ax_rend.set_facecolor('#F9FAFB')

                    ax_rend.spines['top'].set_visible(False)
                    ax_rend.spines['right'].set_visible(False)

                    ax_rend.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x):,}'))

                    plt.tight_layout()

                    canvas_rend = FigureCanvasTkAgg(fig_rend, master=frame_rendimiento)
                    canvas_rend.draw()
                    canvas_rend.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

                    # Botones exportación
                    export_frame_rend = ctk.CTkFrame(frame_rendimiento, fg_color="transparent")
                    export_frame_rend.pack(pady=(0, 10))

                    filtros_texto = f"Años: {anio_texto}"
                    if cod_tipact_sel and len(cod_tipact_sel) > 0:
                        filtros_texto += f" | COD: {', '.join([str(c) for c in cod_tipact_sel[:3]])}"
                        if len(cod_tipact_sel) > 3:
                            filtros_texto += f" +{len(cod_tipact_sel)-3}"
                    if supervisores_sel and len(supervisores_sel) > 0:
                        filtros_texto += f" | Supervisores: {len(supervisores_sel)}"
                    if auditores_sel and len(auditores_sel) > 0:
                        filtros_texto += f" | Auditores: {len(auditores_sel)}"

                    ctk.CTkButton(
                        export_frame_rend,
                        text="💾 PNG",
                        width=90,
                        height=28,
                        fg_color="#10B981",
                        hover_color="#059669",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_grafico_imagen(fig_rend, "Rendimiento_Mensual", filtros_texto)
                    ).pack(side="left", padx=3)

                    ctk.CTkButton(
                        export_frame_rend,
                        text="📥 Excel",
                        width=90,
                        height=28,
                        fg_color="#F59E0B",
                        hover_color="#D97706",
                        font=("Arial", 9, "bold"),
                        command=lambda: exportar_datos_excel(query_completa, "Rendimiento_Mensual_Datos", filtros_texto)
                    ).pack(side="left", padx=3)
                else:
                    ctk.CTkLabel(frame_rendimiento, text="Sin datos disponibles",
                                font=("Arial", 10), text_color="#9CA3AF").pack(pady=50)

            except Exception as e:
                import traceback
                print(f"Error en rendimiento: {e}")
                traceback.print_exc()
                ctk.CTkLabel(frame_rendimiento, text=f"Error: {str(e)}",
                            font=("Arial", 9), text_color="red").pack(pady=20)

        # ===================== CARGA PROGRESIVA DE GRÁFICOS =====================
        # Usar after() para cargar gráficos de forma asíncrona
        def cargar_graficos_progresivamente():
            """Carga los gráficos uno por uno de forma progresiva"""
            # Gráfico 1
            actualizar_grafico_determinativas()
            scroll_container.update()
            
            # Gráfico 2
            scroll_container.after(50, lambda: [
                actualizar_progreso_determinativas(),
                scroll_container.update()
            ])
            
            # Gráfico 3
            scroll_container.after(100, lambda: [
                actualizar_grafico_no_determinativas(),
                scroll_container.update()
            ])
            
            # Gráfico 4
            scroll_container.after(150, lambda: [
                actualizar_progreso_no_determinativas(),
                scroll_container.update()
            ])
            
            # Gráfico 5
            scroll_container.after(200, lambda: [
                actualizar_grafico_stock_pastel(),
                scroll_container.update()
            ])
            
            # Gráfico 6
            scroll_container.after(250, lambda: [
                actualizar_grafico_stock_barras(),
                scroll_container.update()
            ])
            
            # Gráfico 7
            scroll_container.after(300, lambda: [
                actualizar_grafico_rendimiento(),
                scroll_container.update()
            ])

        # Iniciar carga progresiva
        scroll_container.after(100, cargar_graficos_progresivamente)

        # ===== BOTÓN VOLVER =====
        footer = ctk.CTkFrame(scroll_container, fg_color="transparent", height=50)
        footer.pack(fill="x", pady=(15, 0))
        
        def volver_inicio():
            """Volver al menú principal"""
            try:
                header.pack(fill="x")
            except:
                pass
            
            dashboard_frame.pack_forget()
            preview_frame.pack(fill="both", expand=True, padx=10, pady=(5,10))
        
        ctk.CTkButton(
            footer,
            text="← Volver",
            width=120,
            height=40,
            fg_color=COLOR_DANGER,
            hover_color="#DC2626",
            font=("Arial", 12, "bold"),
            command=volver_inicio
        ).pack(pady=10)

    # Cargar automáticamente el contenido OF
    cargar_contenido_of()
# ============================================================================
# CONTROL SALDO DETRACCIONES
# ============================================================================
# Función auxiliar para ejecutar queries SQL (debe estar definida en tu código)
# def ejecutar_read_sql(query, conexion):
#     return pd.read_sql(query, conexion)
# Función auxiliar para ejecutar queries SQL (debe estar definida en tu código)
# def ejecutar_read_sql(query, conexion):
#     return pd.read_sql(query, conexion)

def ajustar_altura_treeview(tree, total_filas, max_filas=25):
    """
    Ajusta dinámicamente la altura del Treeview según el número de filas.
    Si total_filas <= max_filas, se muestra todo sin scroll.
    Si total_filas > max_filas, se fija en max_filas y se usa el scrollbar.
    """
    if total_filas <= max_filas:
        tree.configure(height=total_filas)
    else:
        tree.configure(height=max_filas)


def generar_tabla_control_saldo_detracciones(parent_frame, filtros_des_cod=None, filtros_anio=None):
    """
    Genera tabla de control de saldo cuenta detracciones con drill-down al hacer clic
    INCLUYE COLUMNA DE PADRÓN MYPE
    """
    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=12)

    # Título
    ctk.CTkLabel(tabla_frame,
                 text="💰 CONTROL SALDO CUENTA DETRACCIONES - OF",
                 font=("Segoe UI", 14, "bold"),
                 text_color="#a51c30").pack(anchor="w", padx=12, pady=6)

    # Construir condiciones WHERE dinámicas
    condiciones_extra = []
    if filtros_des_cod and len(filtros_des_cod) > 0:
        placeholders = ', '.join([f"'{val}'" for val in filtros_des_cod])
        condiciones_extra.append(f"f1.des_cod IN ({placeholders})")
    
    if filtros_anio and len(filtros_anio) > 0:
        placeholders = ', '.join([f"'{val}'" for val in filtros_anio])
        condiciones_extra.append(f"f1.Anio_Emis IN ({placeholders})")
    
    where_adicional = ""
    if condiciones_extra:
        where_adicional = " AND " + " AND ".join(condiciones_extra)

    # Query principal con JOIN y filtros - INCLUYE CRUCE CON MYPES
    query = f"""
        SELECT 
            f1.NUM_ORD_FI,
            f1.NUM_DOCSEL,
            f1.DDP_NOMBRE,
            f4.mto_saldo,
            CASE 
                WHEN m.ruc IS NOT NULL THEN 'SI'
                ELSE 'NO'
            END as PADRON_MYPE
        FROM fiscalizaciones1 f1
        INNER JOIN fiscalizaciones4 f4 
            ON TRIM(f1.NUM_DOCSEL) = TRIM(f4.num_ruc)
        LEFT JOIN mypes m
            ON TRIM(f1.NUM_DOCSEL) = TRIM(m.ruc)
        WHERE LOWER(TRIM(IFNULL(f1.Estado, ''))) = 'pendiente'
        {where_adicional}
        ORDER BY f1.NUM_ORD_FI;
    """

    try:
        conn_temp = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql(query, DB_ENGINE)
        conn_temp.close()
    except Exception as e:
        ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
        return

    if df.empty:
        ctk.CTkLabel(tabla_frame, text="⚠ No hay datos disponibles con los filtros seleccionados", text_color="red").pack(pady=15)
        return

    # Contenedor con scroll
    container = ctk.CTkFrame(tabla_frame, fg_color="white")
    container.pack(fill="both", expand=True, padx=5, pady=5)

    # Columnas de la tabla resumen - INCLUYE PADRON_MYPE
    cols_resumen = ["NUM_ORD_FI", "NUM_DOCSEL", "DDP_NOMBRE", "mto_saldo", "PADRON_MYPE"]
    tree_local = ttk.Treeview(container, columns=cols_resumen, show="headings")

    vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
    hsb = ttk.Scrollbar(container, orient="horizontal", command=tree_local.xview)
    tree_local.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree_local.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    # Configurar columnas - INCLUYE PADRON_MYPE
    encabezados = {
        "NUM_ORD_FI": ("N° OF", 120),
        "NUM_DOCSEL": ("RUC", 120),
        "DDP_NOMBRE": ("Razón Social", 250),
        "mto_saldo": ("Saldo S/", 120),
        "PADRON_MYPE": ("Padrón MYPE", 120)
    }

    for col in cols_resumen:
        texto, ancho = encabezados[col]
        tree_local.heading(col, text=texto)
        tree_local.column(col, width=ancho, anchor="center" if col != "DDP_NOMBRE" else "w")

    # Insertar datos y calcular total
    total_saldo = 0
    for idx, row in df.iterrows():
        valores = [
            row["NUM_ORD_FI"],
            row["NUM_DOCSEL"],
            row["DDP_NOMBRE"],
            f"{float(row['mto_saldo']):,.2f}" if pd.notna(row['mto_saldo']) else "0.00",
            row["PADRON_MYPE"]
        ]
        tag = "mype" if row["PADRON_MYPE"] == "SI" else "normal"
        tree_local.insert("", "end", values=valores, tags=(tag,))
        total_saldo += float(row['mto_saldo']) if pd.notna(row['mto_saldo']) else 0

    # Fila de totales
    total_vals = ["", "", "TOTAL GENERAL", f"{total_saldo:,.2f}", ""]
    tree_local.insert("", "end", values=total_vals, tags=("total",))

    # Ajustar altura
    total_filas = len(df) + 1
    ajustar_altura_treeview(tree_local, total_filas)

    # Estilos
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background="#ffffff",
                    foreground="#4a4a4a",
                    rowheight=28,
                    fieldbackground="#ffffff",
                    font=("Segoe UI", 10))
    style.configure("Treeview.Heading",
                    background="#002e6d",
                    foreground="white",
                    font=("Segoe UI", 10, "bold"))
    style.map("Treeview",
              background=[("selected", "#a51c30")],
              foreground=[("selected", "white")])

    tree_local.tag_configure("normal", background="white", font=("Segoe UI", 10))
    tree_local.tag_configure("mype", background="#f5f5f5", font=("Segoe UI", 10, "bold"))
    tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

    # Función para mostrar detalles en popup - ACTUALIZADA CON PADRON_MYPE
    def mostrar_detalles(event):
        seleccion = tree_local.selection()
        if not seleccion:
            return
        
        item = tree_local.item(seleccion[0])
        valores = item['values']
        
        if item['tags'] and 'total' in item['tags']:
            return
        
        num_ord_fi = valores[0]
        
        popup = ctk.CTkToplevel(parent_frame)
        popup.title(f"Detalle - OF N° {num_ord_fi}")
        popup.geometry("900x600")
        popup.transient(parent_frame)
        popup.grab_set()
        
        main_frame = ctk.CTkFrame(popup, corner_radius=15, fg_color="#f5f6fa")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(main_frame,
                     text=f"📋 Detalle Completo - OF N° {num_ord_fi}",
                     font=("Segoe UI", 16, "bold"),
                     text_color="#002e6d").pack(pady=10)
        
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="white", corner_radius=10)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Query con PADRON_MYPE
        query_detalle = f"""
            SELECT f1.*, 
                   f4.num_cargos, f4.mto_cargos, 
                   f4.num_abonos, f4.mto_abonos, 
                   f4.ind_signo, f4.mto_saldo,
                   CASE 
                       WHEN m.ruc IS NOT NULL THEN 'SI'
                       ELSE 'NO'
                   END as PADRON_MYPE
            FROM fiscalizaciones1 f1
            INNER JOIN fiscalizaciones4 f4 
                ON TRIM(f1.NUM_DOCSEL) = TRIM(f4.num_ruc)
            LEFT JOIN mypes m
                ON TRIM(f1.NUM_DOCSEL) = TRIM(m.ruc)
            WHERE f1.NUM_ORD_FI = '{num_ord_fi}'
            LIMIT 1;
        """
        
        try:
            conn_popup = mysql.connector.connect(**DB_CONFIG)
            df_completo = pd.read_sql(query_detalle, DB_ENGINE)
            conn_popup.close()
            if not df_completo.empty:
                fila_completa = df_completo.iloc[0]
                
                # Sección: Datos de fiscalizaciones1
                seccion_frame = ctk.CTkFrame(scroll_frame, fg_color="#e8f4f8", corner_radius=8)
                seccion_frame.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkLabel(seccion_frame,
                             text="🔍 Datos de Fiscalización",
                             font=("Segoe UI", 13, "bold"),
                             text_color="#002e6d").pack(anchor="w", padx=10, pady=5)
                
                for col in df_completo.columns:
                    if col not in ['num_cargos', 'mto_cargos', 'num_abonos', 'mto_abonos', 'ind_signo', 'mto_saldo', 'PADRON_MYPE']:
                        valor = fila_completa[col]
                        if pd.isna(valor):
                            valor = "N/A"
                        
                        campo_frame = ctk.CTkFrame(seccion_frame, fg_color="white", corner_radius=5)
                        campo_frame.pack(fill="x", padx=10, pady=2)
                        
                        ctk.CTkLabel(campo_frame,
                                     text=f"{col}:",
                                     font=("Segoe UI", 10, "bold"),
                                     text_color="#4a4a4a",
                                     width=200,
                                     anchor="w").pack(side="left", padx=5, pady=3)
                        
                        ctk.CTkLabel(campo_frame,
                                     text=str(valor),
                                     font=("Segoe UI", 10),
                                     text_color="#2d3436",
                                     anchor="w").pack(side="left", padx=5, pady=3, fill="x", expand=True)
                
                # Sección: Datos de cuenta detracciones
                seccion_frame2 = ctk.CTkFrame(scroll_frame, fg_color="#fff3e0", corner_radius=8)
                seccion_frame2.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkLabel(seccion_frame2,
                             text="💳 Datos de Cuenta Detracciones",
                             font=("Segoe UI", 13, "bold"),
                             text_color="#e67e22").pack(anchor="w", padx=10, pady=5)
                
                campos_f4 = {
                    'num_cargos': 'Número de Cargos',
                    'mto_cargos': 'Monto Cargos (S/)',
                    'num_abonos': 'Número de Abonos',
                    'mto_abonos': 'Monto Abonos (S/)',
                    'ind_signo': 'Indicador Signo',
                    'mto_saldo': 'Saldo (S/)',
                    'PADRON_MYPE': '🏢 Padrón MYPE'
                }
                
                for col, etiqueta in campos_f4.items():
                    valor = fila_completa[col]
                    if pd.isna(valor):
                        valor = "N/A"
                    elif col in ['mto_cargos', 'mto_abonos', 'mto_saldo']:
                        try:
                            valor = f"{float(valor):,.2f}"
                        except:
                            valor = str(valor)
                    
                    # Color especial para PADRON_MYPE
                    bg_color = "#d4edda" if col == 'PADRON_MYPE' and valor == 'SI' else "white"
                    
                    campo_frame = ctk.CTkFrame(seccion_frame2, fg_color=bg_color, corner_radius=5)
                    campo_frame.pack(fill="x", padx=10, pady=2)
                    
                    ctk.CTkLabel(campo_frame,
                                 text=f"{etiqueta}:",
                                 font=("Segoe UI", 10, "bold"),
                                 text_color="#4a4a4a",
                                 width=200,
                                 anchor="w").pack(side="left", padx=5, pady=3)
                    
                    ctk.CTkLabel(campo_frame,
                                 text=str(valor),
                                 font=("Segoe UI", 10, "bold" if col == 'PADRON_MYPE' else "normal"),
                                 text_color="#155724" if col == 'PADRON_MYPE' and valor == 'SI' else "#2d3436",
                                 anchor="w").pack(side="left", padx=5, pady=3, fill="x", expand=True)
        
        except Exception as e:
            ctk.CTkLabel(scroll_frame,
                         text=f"⚠ Error al cargar detalles: {e}",
                         text_color="red").pack(pady=20)
        
        ctk.CTkButton(main_frame,
                      text="Cerrar",
                      command=popup.destroy,
                      fg_color="#a51c30",
                      hover_color="#8b1629",
                      font=("Segoe UI", 11, "bold"),
                      width=120).pack(pady=10)
        
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

    tree_local.bind("<Double-1>", mostrar_detalles)
    
    info_frame = ctk.CTkFrame(tabla_frame, fg_color="transparent")
    info_frame.pack(pady=5, fill="x", padx=12)
    
    ctk.CTkLabel(info_frame,
                 text="💡 Haz doble clic en cualquier fila para ver los detalles completos",
                 font=("Segoe UI", 9, "italic"),
                 text_color="#636e72").pack(side="left")
    
    # Botón para ver todos los datos - ACTUALIZADO CON PADRON_MYPE
    def ver_todos_datos():
        ventana_tabla = ctk.CTkToplevel(parent_frame)
        ventana_tabla.title("Control Saldo Detracciones - Vista Completa")
        ventana_tabla.geometry("1400x700")
        ventana_tabla.transient(parent_frame)
        
        main_frame = ctk.CTkFrame(ventana_tabla, corner_radius=15, fg_color="#f5f6fa")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        ctk.CTkLabel(header_frame,
                     text="📊 Control Saldo Cuenta Detracciones - Vista Completa",
                     font=("Segoe UI", 16, "bold"),
                     text_color="#002e6d").pack(side="left")
        
        ctk.CTkLabel(header_frame,
                     text=f"Total registros: {len(df)}",
                     font=("Segoe UI", 11),
                     text_color="#6B7280").pack(side="right")
        
        tabla_completa_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=10)
        tabla_completa_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        where_completo = ""
        if condiciones_extra:
            where_completo = " AND " + " AND ".join(condiciones_extra)
        
        # Query completa con PADRON_MYPE
        query_completa = f"""
            SELECT 
                f1.NUM_ORD_FI,
                f1.NUM_DOCSEL,
                f1.DDP_NOMBRE,
                f1.COD_PROGFI,
                f1.COD_TIPACT,
                f1.COD_GRP_TR,
                f1.COD_METODO,
                f1.FEC_EMISIO,
                f1.FEC_NOTIFI,
                f1.FEC_TERMIN,
                f1.MTO_PAG_IN,
                f1.MTO_PAG_RE,
                f1.MTO_VAL_DE,
                f1.MTO_VAL_CR,
                f1.Rendimiento_dia,
                f1.COD_REG_ES,
                f1.NUM_CARGA,
                f1.Des_eta_of,
                f1.des_est_of,
                f1.dias_asignados,
                f1.dias_empleados,
                f1.Exceso,
                f1.Resultado_dias,
                f1.REG_AUDITOR,
                f1.NOMBRE_AUDITOR,
                f1.Categoria_Auditor,
                f1.REG_SUPERVISOR,
                f1.NOMBRE_SUPERVISOR,
                f1.des_cod,
                f1.Tipo_Fiscalizacion,
                f1.SISCOR,
                f1.REQUERIMIENTO_INICIAL,
                f1.FEC_VENC,
                f1.Ult_requerimiento,
                f1.Fec_ini_ult_req,
                f1.Dias_ult_req,
                f1.Estado,
                f1.Anio_Emis,
                f1.Mes_Emis,
                f1.Anio_Termino,
                f1.Mes_termino,
                f1.Periodos_Revisados,
                f1.Denuncia,
                f1.Centralizada,
                f1.Cant_AF_ESSALUD,
                f1.MTG,
                f1.Exp_Electronico,
                f1.SIP_05,
                f1.MTO_SIP_05,
                f1.Monto_Comp2_SIP05,
                f1.Porc_Rend_Incons_SIP05,
                f1.Porc_PARTIC_MTO_RIESGO,
                f1.Stock_AUD_25,
                f1.Componente_PNC_R12_2024,
                f1.Monto_PNC_R12_2024,
                f1.Stock_AUD_25_Tot,
                f1.Rendimiento_OF,
                f4.mto_saldo,
                CASE 
                    WHEN m.ruc IS NOT NULL THEN 'SI'
                    ELSE 'NO'
                END as PADRON_MYPE
            FROM fiscalizaciones1 f1
            INNER JOIN fiscalizaciones4 f4 
                ON TRIM(f1.NUM_DOCSEL) = TRIM(f4.num_ruc)
            LEFT JOIN mypes m
                ON TRIM(f1.NUM_DOCSEL) = TRIM(m.ruc)
            WHERE LOWER(TRIM(IFNULL(f1.Estado, ''))) = 'pendiente'
            {where_completo}
            ORDER BY f1.NUM_ORD_FI;
        """
        
        try:
            conn_temp = mysql.connector.connect(**DB_CONFIG)
            df_completo = pd.read_sql(query_completa, DB_ENGINE)
            conn_temp.close()
            
            if df_completo.empty:
                ctk.CTkLabel(tabla_completa_frame, 
                           text="⚠ No hay datos disponibles",
                           text_color="red").pack(pady=50)
                return
            
            container_completo = ctk.CTkFrame(tabla_completa_frame, fg_color="white")
            container_completo.pack(fill="both", expand=True, padx=10, pady=10)
            
            columnas = df_completo.columns.tolist()
            tree_completo = ttk.Treeview(container_completo, columns=columnas, show="headings", height=25)
            
            vsb_completo = ttk.Scrollbar(container_completo, orient="vertical", command=tree_completo.yview)
            hsb_completo = ttk.Scrollbar(container_completo, orient="horizontal", command=tree_completo.xview)
            tree_completo.configure(yscrollcommand=vsb_completo.set, xscrollcommand=hsb_completo.set)
            
            tree_completo.grid(row=0, column=0, sticky="nsew")
            vsb_completo.grid(row=0, column=1, sticky="ns")
            hsb_completo.grid(row=1, column=0, sticky="ew")
            
            container_completo.grid_rowconfigure(0, weight=1)
            container_completo.grid_columnconfigure(0, weight=1)
            
            anchos_personalizados = {
                'NUM_ORD_FI': 100,
                'NUM_DOCSEL': 100,
                'DDP_NOMBRE': 250,
                'COD_PROGFI': 90,
                'COD_TIPACT': 90,
                'FEC_EMISIO': 100,
                'FEC_NOTIFI': 100,
                'Estado': 100,
                'NOMBRE_SUPERVISOR': 180,
                'NOMBRE_AUDITOR': 180,
                'Anio_Emis': 80,
                'Mes_Emis': 80,
                'des_cod': 150,
                'mto_saldo': 120,
                'PADRON_MYPE': 120
            }
            
            for col in columnas:
                ancho = anchos_personalizados.get(col, 100)
                tree_completo.heading(col, text=col)
                tree_completo.column(col, width=ancho, anchor="center")
            
            for idx, row in df_completo.iterrows():
                valores = []
                for col in columnas:
                    valor = row[col]
                    if pd.isna(valor):
                        valores.append("N/A")
                    elif col == 'mto_saldo':
                        try:
                            valores.append(f"{float(valor):,.2f}")
                        except:
                            valores.append(str(valor))
                    else:
                        valores.append(str(valor))
                
                tag = "mype" if row['PADRON_MYPE'] == 'SI' else ("par" if idx % 2 == 0 else "impar")
                tree_completo.insert("", "end", values=valores, tags=(tag,))
            
            style_completo = ttk.Style()
            style_completo.theme_use("clam")
            style_completo.configure("Treeview",
                                    background="#ffffff",
                                    foreground="#4a4a4a",
                                    rowheight=26,
                                    fieldbackground="#ffffff",
                                    font=("Segoe UI", 9))
            style_completo.configure("Treeview.Heading",
                                    background="#002e6d",
                                    foreground="white",
                                    font=("Segoe UI", 9, "bold"))
            style_completo.map("Treeview",
                              background=[("selected", "#a51c30")],
                              foreground=[("selected", "white")])
            
            tree_completo.tag_configure("par", background="#f9fafb")
            tree_completo.tag_configure("impar", background="white")
            tree_completo.tag_configure("mype", background="#f5f5f5", font=("Segoe UI", 9, "bold"))
            
            botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            botones_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            def exportar_excel():
                try:
                    from tkinter import filedialog
                    from datetime import datetime
                    archivo = filedialog.asksaveasfilename(
                        defaultextension=".xlsx",
                        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                        initialfile=f"Control_Detracciones_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    )
                    if archivo:
                        df_completo.to_excel(archivo, index=False, sheet_name="Control Detracciones")
                        messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{archivo}")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar:\n{e}")
            
            ctk.CTkButton(botones_frame,
                         text="📥 Exportar a Excel",
                         command=exportar_excel,
                         fg_color="#10B981",
                         hover_color="#059669",
                         font=("Segoe UI", 10, "bold"),
                         width=150,
                         height=35).pack(side="left", padx=5)
            
            ctk.CTkButton(botones_frame,
                         text="🔄 Actualizar",
                         command=lambda: [ventana_tabla.destroy(), ver_todos_datos()],
                         fg_color="#3B82F6",
                         hover_color="#2563EB",
                         font=("Segoe UI", 10, "bold"),
                         width=130,
                         height=35).pack(side="left", padx=5)
            
            ctk.CTkButton(botones_frame,
                         text="Cerrar",
                         command=ventana_tabla.destroy,
                         fg_color="#6B7280",
                         hover_color="#4B5563",
                         font=("Segoe UI", 10, "bold"),
                         width=100,
                         height=35).pack(side="right", padx=5)
            
            ctk.CTkLabel(botones_frame,
                        text=f"💡 Mostrando {len(df_completo)} registros | 🏢 MYPES resaltadas en verde",
                        font=("Segoe UI", 9, "italic"),
                        text_color="#6B7280").pack(side="left", padx=20)
            
        except Exception as e:
            ctk.CTkLabel(tabla_completa_frame,
                        text=f"⚠ Error al cargar datos completos: {e}",
                        text_color="red").pack(pady=50)
        
        ventana_tabla.update_idletasks()
        x = (ventana_tabla.winfo_screenwidth() // 2) - (ventana_tabla.winfo_width() // 2)
        y = (ventana_tabla.winfo_screenheight() // 2) - (ventana_tabla.winfo_height() // 2)
        ventana_tabla.geometry(f"+{x}+{y}")
    
    ctk.CTkButton(info_frame,
                 text="📊 Ver Todos los Datos",
                 command=ver_todos_datos,
                 fg_color="#3B82F6",
                 hover_color="#2563EB",
                 font=("Segoe UI", 10, "bold"),
                 width=160,
                 height=32).pack(side="right")

#---------------------------------------------------------------
#TABLA AI
def generar_tabla_control_saldo_detracciones_ai(parent_frame, filtros_supervisor=None, filtros_tipo_ai=None, filtros_anio=None):
    """
    Genera tabla de control de saldo cuenta detracciones AI con drill-down al hacer clic
    INCLUYE COLUMNA DE PADRÓN MYPE
    """
    tabla_frame = ctk.CTkFrame(parent_frame, corner_radius=15, fg_color="white")
    tabla_frame.pack(fill="both", expand=True, padx=15, pady=12)

    # Título
    ctk.CTkLabel(tabla_frame,
                 text="💰 CONTROL SALDO CUENTA DETRACCIONES - AI",
                 font=("Segoe UI", 14, "bold"),
                 text_color="#a51c30").pack(anchor="w", padx=12, pady=6)

    # Construir condiciones WHERE dinámicas
    condiciones_extra = []
    if filtros_supervisor and len(filtros_supervisor) > 0:
        placeholders = ', '.join([f"'{val}'" for val in filtros_supervisor])
        condiciones_extra.append(f"f3.DES_NOMB_SUP IN ({placeholders})")
    
    if filtros_tipo_ai and len(filtros_tipo_ai) > 0:
        placeholders = ', '.join([f"'{val}'" for val in filtros_tipo_ai])
        condiciones_extra.append(f"f3.des_tipo_ai IN ({placeholders})")
    
    if filtros_anio and len(filtros_anio) > 0:
        placeholders = ', '.join([f"'{val}'" for val in filtros_anio])
        condiciones_extra.append(f"f3.Anio_Emis IN ({placeholders})")
    
    where_adicional = ""
    if condiciones_extra:
        where_adicional = " AND " + " AND ".join(condiciones_extra)

    # Query principal con JOIN y filtros - INCLUYE CRUCE CON MYPES
    query = f"""
        SELECT 
            f3.NUM_ACC_IN,
            f3.NUM_DOCSEL,
            f4.nom_ruc,
            f4.mto_saldo,
            CASE 
                WHEN m.ruc IS NOT NULL THEN 'SI'
                ELSE 'NO'
            END as PADRON_MYPE
        FROM fiscalizaciones3 f3
        INNER JOIN fiscalizaciones4 f4 
            ON TRIM(f3.NUM_DOCSEL) = TRIM(f4.num_ruc)
        LEFT JOIN mypes m
            ON TRIM(f3.NUM_DOCSEL) = TRIM(m.ruc)
        WHERE LOWER(TRIM(IFNULL(f3.Estado, ''))) = 'pendiente'
        {where_adicional}
        ORDER BY f3.NUM_ACC_IN;
    """

    try:
        conn_temp = mysql.connector.connect(**DB_CONFIG)
        df = pd.read_sql(query, DB_ENGINE)
        conn_temp.close()
    except Exception as e:
        ctk.CTkLabel(tabla_frame, text=f"⚠ Error al consultar BD: {e}", text_color="red").pack(pady=15)
        return

    if df.empty:
        ctk.CTkLabel(tabla_frame, text="⚠ No hay datos disponibles con los filtros seleccionados", text_color="red").pack(pady=15)
        return

    # Contenedor con scroll
    container = ctk.CTkFrame(tabla_frame, fg_color="white")
    container.pack(fill="both", expand=True, padx=5, pady=5)

    # Columnas de la tabla resumen - INCLUYE PADRON_MYPE
    cols_resumen = ["NUM_ACC_IN", "NUM_DOCSEL", "nom_ruc", "mto_saldo", "PADRON_MYPE"]
    tree_local = ttk.Treeview(container, columns=cols_resumen, show="headings")

    vsb = ttk.Scrollbar(container, orient="vertical", command=tree_local.yview)
    hsb = ttk.Scrollbar(container, orient="horizontal", command=tree_local.xview)
    tree_local.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

    tree_local.grid(row=0, column=0, sticky="nsew")
    vsb.grid(row=0, column=1, sticky="ns")
    hsb.grid(row=1, column=0, sticky="ew")

    container.grid_rowconfigure(0, weight=1)
    container.grid_columnconfigure(0, weight=1)

    # Configurar columnas - INCLUYE PADRON_MYPE
    encabezados = {
        "NUM_ACC_IN": ("N° AI", 120),
        "NUM_DOCSEL": ("RUC", 120),
        "nom_ruc": ("Razón Social", 250),
        "mto_saldo": ("Saldo S/", 120),
        "PADRON_MYPE": ("Padrón MYPE", 120)
    }

    for col in cols_resumen:
        texto, ancho = encabezados[col]
        tree_local.heading(col, text=texto)
        tree_local.column(col, width=ancho, anchor="center" if col != "nom_ruc" else "w")

    # Insertar datos y calcular total
    total_saldo = 0
    for idx, row in df.iterrows():
        valores = [
            row["NUM_ACC_IN"],
            row["NUM_DOCSEL"],
            row["nom_ruc"],
            f"{float(row['mto_saldo']):,.2f}" if pd.notna(row['mto_saldo']) else "0.00",
            row["PADRON_MYPE"]
        ]
        tag = "mype" if row["PADRON_MYPE"] == "SI" else "normal"
        tree_local.insert("", "end", values=valores, tags=(tag,))
        total_saldo += float(row['mto_saldo']) if pd.notna(row['mto_saldo']) else 0

    # Fila de totales
    total_vals = ["", "", "TOTAL GENERAL", f"{total_saldo:,.2f}", ""]
    tree_local.insert("", "end", values=total_vals, tags=("total",))

    # Ajustar altura
    total_filas = len(df) + 1
    ajustar_altura_treeview(tree_local, total_filas)

    # Estilos
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Treeview",
                    background="#ffffff",
                    foreground="#4a4a4a",
                    rowheight=28,
                    fieldbackground="#ffffff",
                    font=("Segoe UI", 10))
    style.configure("Treeview.Heading",
                    background="#002e6d",
                    foreground="white",
                    font=("Segoe UI", 10, "bold"))
    style.map("Treeview",
              background=[("selected", "#a51c30")],
              foreground=[("selected", "white")])

    tree_local.tag_configure("normal", background="white", font=("Segoe UI", 10))
    tree_local.tag_configure("mype", background="#f5f5f5", font=("Segoe UI", 10, "bold"))
    tree_local.tag_configure("total", background="#dfe6e9", foreground="black", font=("Segoe UI", 11, "bold"))

    # Función para mostrar detalles en popup - ACTUALIZADA CON PADRON_MYPE
    def mostrar_detalles(event):
        seleccion = tree_local.selection()
        if not seleccion:
            return
        
        item = tree_local.item(seleccion[0])
        valores = item['values']
        
        if item['tags'] and 'total' in item['tags']:
            return
        
        num_acc_in = valores[0]
        
        popup = ctk.CTkToplevel(parent_frame)
        popup.title(f"Detalle - AI N° {num_acc_in}")
        popup.geometry("900x600")
        popup.transient(parent_frame)
        popup.grab_set()
        
        main_frame = ctk.CTkFrame(popup, corner_radius=15, fg_color="#f5f6fa")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        ctk.CTkLabel(main_frame,
                     text=f"📋 Detalle Completo - AI N° {num_acc_in}",
                     font=("Segoe UI", 16, "bold"),
                     text_color="#002e6d").pack(pady=10)
        
        scroll_frame = ctk.CTkScrollableFrame(main_frame, fg_color="white", corner_radius=10)
        scroll_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Query con PADRON_MYPE
        query_detalle = f"""
            SELECT f3.*, 
                   f4.num_cargos, f4.mto_cargos, 
                   f4.num_abonos, f4.mto_abonos, 
                   f4.ind_signo, f4.mto_saldo, f4.nom_ruc,
                   CASE 
                       WHEN m.ruc IS NOT NULL THEN 'SI'
                       ELSE 'NO'
                   END as PADRON_MYPE
            FROM fiscalizaciones3 f3
            INNER JOIN fiscalizaciones4 f4 
                ON TRIM(f3.NUM_DOCSEL) = TRIM(f4.num_ruc)
            LEFT JOIN mypes m
                ON TRIM(f3.NUM_DOCSEL) = TRIM(m.ruc)
            WHERE f3.NUM_ACC_IN = '{num_acc_in}'
            LIMIT 1;
        """
        
        try:
            conn_popup = mysql.connector.connect(**DB_CONFIG)
            df_completo = pd.read_sql(query_detalle, DB_ENGINE)
            conn_popup.close()
            if not df_completo.empty:
                fila_completa = df_completo.iloc[0]
                
                # Sección: Datos de fiscalizaciones3
                seccion_frame = ctk.CTkFrame(scroll_frame, fg_color="#e8f4f8", corner_radius=8)
                seccion_frame.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkLabel(seccion_frame,
                             text="🔍 Datos de Acción Inductiva",
                             font=("Segoe UI", 13, "bold"),
                             text_color="#002e6d").pack(anchor="w", padx=10, pady=5)
                
                for col in df_completo.columns:
                    if col not in ['num_cargos', 'mto_cargos', 'num_abonos', 'mto_abonos', 'ind_signo', 'mto_saldo', 'nom_ruc', 'PADRON_MYPE']:
                        valor = fila_completa[col]
                        if pd.isna(valor):
                            valor = "N/A"
                        
                        campo_frame = ctk.CTkFrame(seccion_frame, fg_color="white", corner_radius=5)
                        campo_frame.pack(fill="x", padx=10, pady=2)
                        
                        ctk.CTkLabel(campo_frame,
                                     text=f"{col}:",
                                     font=("Segoe UI", 10, "bold"),
                                     text_color="#4a4a4a",
                                     width=200,
                                     anchor="w").pack(side="left", padx=5, pady=3)
                        
                        ctk.CTkLabel(campo_frame,
                                     text=str(valor),
                                     font=("Segoe UI", 10),
                                     text_color="#2d3436",
                                     anchor="w").pack(side="left", padx=5, pady=3, fill="x", expand=True)
                
                # Sección: Datos de cuenta detracciones
                seccion_frame2 = ctk.CTkFrame(scroll_frame, fg_color="#fff3e0", corner_radius=8)
                seccion_frame2.pack(fill="x", padx=10, pady=5)
                
                ctk.CTkLabel(seccion_frame2,
                             text="💳 Datos de Cuenta Detracciones",
                             font=("Segoe UI", 13, "bold"),
                             text_color="#e67e22").pack(anchor="w", padx=10, pady=5)
                
                campos_f4 = {
                    'nom_ruc': 'Razón Social',
                    'num_cargos': 'Número de Cargos',
                    'mto_cargos': 'Monto Cargos (S/)',
                    'num_abonos': 'Número de Abonos',
                    'mto_abonos': 'Monto Abonos (S/)',
                    'ind_signo': 'Indicador Signo',
                    'mto_saldo': 'Saldo (S/)',
                    'PADRON_MYPE': '🏢 Padrón MYPE'
                }
                
                for col, etiqueta in campos_f4.items():
                    valor = fila_completa[col]
                    if pd.isna(valor):
                        valor = "N/A"
                    elif col in ['mto_cargos', 'mto_abonos', 'mto_saldo']:
                        try:
                            valor = f"{float(valor):,.2f}"
                        except:
                            valor = str(valor)
                    
                    # Color especial para PADRON_MYPE
                    bg_color = "#d4edda" if col == 'PADRON_MYPE' and valor == 'SI' else "white"
                    
                    campo_frame = ctk.CTkFrame(seccion_frame2, fg_color=bg_color, corner_radius=5)
                    campo_frame.pack(fill="x", padx=10, pady=2)
                    
                    ctk.CTkLabel(campo_frame,
                                 text=f"{etiqueta}:",
                                 font=("Segoe UI", 10, "bold"),
                                 text_color="#4a4a4a",
                                 width=200,
                                 anchor="w").pack(side="left", padx=5, pady=3)
                    
                    ctk.CTkLabel(campo_frame,
                                 text=str(valor),
                                 font=("Segoe UI", 10, "bold" if col == 'PADRON_MYPE' else "normal"),
                                 text_color="#155724" if col == 'PADRON_MYPE' and valor == 'SI' else "#2d3436",
                                 anchor="w").pack(side="left", padx=5, pady=3, fill="x", expand=True)
        
        except Exception as e:
            ctk.CTkLabel(scroll_frame,
                         text=f"⚠ Error al cargar detalles: {e}",
                         text_color="red").pack(pady=20)
        
        ctk.CTkButton(main_frame,
                      text="Cerrar",
                      command=popup.destroy,
                      fg_color="#a51c30",
                      hover_color="#8b1629",
                      font=("Segoe UI", 11, "bold"),
                      width=120).pack(pady=10)
        
        popup.update_idletasks()
        x = (popup.winfo_screenwidth() // 2) - (popup.winfo_width() // 2)
        y = (popup.winfo_screenheight() // 2) - (popup.winfo_height() // 2)
        popup.geometry(f"+{x}+{y}")

    tree_local.bind("<Double-1>", mostrar_detalles)
    
    info_frame = ctk.CTkFrame(tabla_frame, fg_color="transparent")
    info_frame.pack(pady=5, fill="x", padx=12)
    
    ctk.CTkLabel(info_frame,
                 text="💡 Haz doble clic en cualquier fila para ver los detalles completos",
                 font=("Segoe UI", 9, "italic"),
                 text_color="#636e72").pack(side="left")
    
    # Botón para ver todos los datos - ACTUALIZADO CON PADRON_MYPE
    def ver_todos_datos():
        ventana_tabla = ctk.CTkToplevel(parent_frame)
        ventana_tabla.title("Control Saldo Detracciones AI - Vista Completa")
        ventana_tabla.geometry("1400x700")
        ventana_tabla.transient(parent_frame)
        
        main_frame = ctk.CTkFrame(ventana_tabla, corner_radius=15, fg_color="#f5f6fa")
        main_frame.pack(fill="both", expand=True, padx=15, pady=15)
        
        header_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        header_frame.pack(fill="x", padx=15, pady=(10, 15))
        
        ctk.CTkLabel(header_frame,
                     text="📊 Control Saldo Cuenta Detracciones AI - Vista Completa",
                     font=("Segoe UI", 16, "bold"),
                     text_color="#002e6d").pack(side="left")
        
        ctk.CTkLabel(header_frame,
                     text=f"Total registros: {len(df)}",
                     font=("Segoe UI", 11),
                     text_color="#6B7280").pack(side="right")
        
        tabla_completa_frame = ctk.CTkFrame(main_frame, fg_color="white", corner_radius=10)
        tabla_completa_frame.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        where_completo = ""
        if condiciones_extra:
            where_completo = " AND " + " AND ".join(condiciones_extra)
        
        # Query completa con PADRON_MYPE
        query_completa = f"""
            SELECT 
                f3.COD_ACC_IN,
                f3.COD_PROGFI,
                f3.COD_GRP_TR,
                f3.IND_EST_AC,
                f3.NUM_ACC_IN,
                f3.NUM_DOCSEL,
                f3.FEC_TER,
                f3.FEC_NOT,
                f3.IND_EST_RE,
                f3.COD_METODO,
                f3.NUM_CARGA,
                f3.FEC_GEN,
                f3.COD_VER,
                f3.COD_SUP,
                f3.COD_REG_ES,
                f3.FLG_PASE_F,
                f3.MES,
                f3.DES_NOMB_VER,
                f3.DES_NOMB_SUP,
                f3.DES_NOMB_PROG,
                f3.DES_TIPO_AI,
                f3.Estado,
                f3.Anio_Emis,
                f3.Mes_Emis,
                f3.Anio_Termino,
                f3.Mes_termino,
                f3.Periodos_Revisados,
                f3.Pago_AI,
                f3.Rect_AI,
                f3.Total,
                f3.Dias,
                f3.Fec_limite,
                f3.FCJMMS,
                f3.ESSALUD,
                f3.SIP_05,
                f3.MTO_SIP_05,
                f3.Monto_Comp3_SIP05,
                f3.Porc_Rend_Incons_SIP05,
                f4.mto_saldo,
                CASE 
                    WHEN m.ruc IS NOT NULL THEN 'SI'
                    ELSE 'NO'
                END as PADRON_MYPE
            FROM fiscalizaciones3 f3
            INNER JOIN fiscalizaciones4 f4 
                ON TRIM(f3.NUM_DOCSEL) = TRIM(f4.num_ruc)
            LEFT JOIN mypes m
                ON TRIM(f3.NUM_DOCSEL) = TRIM(m.ruc)
            WHERE LOWER(TRIM(IFNULL(f3.Estado, ''))) = 'pendiente'
            {where_completo}
            ORDER BY f3.NUM_ACC_IN;
        """
        
        try:
            conn_temp = mysql.connector.connect(**DB_CONFIG)
            df_completo = pd.read_sql(query_completa, DB_ENGINE)
            conn_temp.close()
            
            if df_completo.empty:
                ctk.CTkLabel(tabla_completa_frame, 
                           text="⚠ No hay datos disponibles",
                           text_color="red").pack(pady=50)
                return
            
            container_completo = ctk.CTkFrame(tabla_completa_frame, fg_color="white")
            container_completo.pack(fill="both", expand=True, padx=10, pady=10)
            
            columnas = df_completo.columns.tolist()
            tree_completo = ttk.Treeview(container_completo, columns=columnas, show="headings", height=25)
            
            vsb_completo = ttk.Scrollbar(container_completo, orient="vertical", command=tree_completo.yview)
            hsb_completo = ttk.Scrollbar(container_completo, orient="horizontal", command=tree_completo.xview)
            tree_completo.configure(yscrollcommand=vsb_completo.set, xscrollcommand=hsb_completo.set)
            
            tree_completo.grid(row=0, column=0, sticky="nsew")
            vsb_completo.grid(row=0, column=1, sticky="ns")
            hsb_completo.grid(row=1, column=0, sticky="ew")
            
            container_completo.grid_rowconfigure(0, weight=1)
            container_completo.grid_columnconfigure(0, weight=1)
            
            anchos_personalizados = {
                'NUM_ACC_IN': 100,
                'NUM_DOCSEL': 100,
                'DES_NOMB_SUP': 180,
                'DES_TIPO_AI': 150,
                'Anio_Emis': 80,
                'Estado': 100,
                'FEC_TER': 100,
                'FEC_NOT': 100,
                'mto_saldo': 120,
                'PADRON_MYPE': 120
            }
            
            for col in columnas:
                ancho = anchos_personalizados.get(col, 100)
                tree_completo.heading(col, text=col)
                tree_completo.column(col, width=ancho, anchor="center")
            
            for idx, row in df_completo.iterrows():
                valores = []
                for col in columnas:
                    valor = row[col]
                    if pd.isna(valor):
                        valores.append("N/A")
                    elif col == 'mto_saldo':
                        try:
                            valores.append(f"{float(valor):,.2f}")
                        except:
                            valores.append(str(valor))
                    else:
                        valores.append(str(valor))
                
                tag = "mype" if row['PADRON_MYPE'] == 'SI' else ("par" if idx % 2 == 0 else "impar")
                tree_completo.insert("", "end", values=valores, tags=(tag,))
            
            style_completo = ttk.Style()
            style_completo.theme_use("clam")
            style_completo.configure("Treeview",
                                    background="#ffffff",
                                    foreground="#4a4a4a",
                                    rowheight=26,
                                    fieldbackground="#ffffff",
                                    font=("Segoe UI", 9))
            style_completo.configure("Treeview.Heading",
                                    background="#002e6d",
                                    foreground="white",
                                    font=("Segoe UI", 9, "bold"))
            style_completo.map("Treeview",
                              background=[("selected", "#a51c30")],
                              foreground=[("selected", "white")])
            
            tree_completo.tag_configure("par", background="#f9fafb")
            tree_completo.tag_configure("impar", background="white")
            tree_completo.tag_configure("mype", background="#f5f5f5", font=("Segoe UI", 9, "bold"))
            
            botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
            botones_frame.pack(fill="x", padx=15, pady=(0, 10))
            
            def exportar_excel():
                try:
                    from tkinter import filedialog
                    from datetime import datetime
                    archivo = filedialog.asksaveasfilename(
                        defaultextension=".xlsx",
                        filetypes=[("Excel files", "*.xlsx"), ("All files", "*.*")],
                        initialfile=f"Control_Detracciones_AI_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                    )
                    if archivo:
                        df_completo.to_excel(archivo, index=False, sheet_name="Control Detracciones AI")
                        messagebox.showinfo("Éxito", f"Datos exportados correctamente a:\n{archivo}")
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo exportar:\n{e}")
            
            ctk.CTkButton(botones_frame,
                         text="📥 Exportar a Excel",
                         command=exportar_excel,
                         fg_color="#10B981",
                         hover_color="#059669",
                         font=("Segoe UI", 10, "bold"),
                         width=150,
                         height=35).pack(side="left", padx=5)
            
            ctk.CTkButton(botones_frame,
                         text="🔄 Actualizar",
                         command=lambda: [ventana_tabla.destroy(), ver_todos_datos()],
                         fg_color="#3B82F6",
                         hover_color="#2563EB",
                         font=("Segoe UI", 10, "bold"),
                         width=130,
                         height=35).pack(side="left", padx=5)
            
            ctk.CTkButton(botones_frame,
                         text="Cerrar",
                         command=ventana_tabla.destroy,
                         fg_color="#6B7280",
                         hover_color="#4B5563",
                         font=("Segoe UI", 10, "bold"),
                         width=100,
                         height=35).pack(side="right", padx=5)
            
            ctk.CTkLabel(botones_frame,
                        text=f"💡 Mostrando {len(df_completo)} registros | 🏢 MYPES resaltadas en verde",
                        font=("Segoe UI", 9, "italic"),
                        text_color="#6B7280").pack(side="left", padx=20)
            
        except Exception as e:
            ctk.CTkLabel(tabla_completa_frame,
                        text=f"⚠ Error al cargar datos completos: {e}",
                        text_color="red").pack(pady=50)
        
        ventana_tabla.update_idletasks()
        x = (ventana_tabla.winfo_screenwidth() // 2) - (ventana_tabla.winfo_width() // 2)
        y = (ventana_tabla.winfo_screenheight() // 2) - (ventana_tabla.winfo_height() // 2)
        ventana_tabla.geometry(f"+{x}+{y}")
    
    ctk.CTkButton(info_frame,
                 text="📊 Ver Todos los Datos",
                 command=ver_todos_datos,
                 fg_color="#3B82F6",
                 hover_color="#2563EB",
                 font=("Segoe UI", 10, "bold"),
                 width=160,
                 height=32).pack(side="right")
# ============================================================
# DASHBOARD PRINCIPAL - CONTROL SALDO DETRACCIONES
# ============================================================

def dashboard_control_detracciones():
    """
    Dashboard para mostrar las tablas de Control Saldo Cuenta Detracciones.
    Incluye pestañas para OF (fiscalizaciones1) y AI (fiscalizaciones3).
    """
    
    # Definir colores
    COLOR_WHITE = "#ffffff"
    
    # Ocultar menú
    ocultar_menu()

    # Ocultar preview frame
    try:
        preview_frame.pack_forget()
    except Exception:
        pass
    
    # Mostrar dashboard frame
    dashboard_frame.pack(fill="both", expand=True, padx=10, pady=10)

    # Limpiar dashboard
    for widget in dashboard_frame.winfo_children():
        widget.destroy()

    # Mostrar banner si existe
    if "banner_detracciones_path" in config:
        mostrar_banner_supervisores(config["banner_detracciones_path"])

    # ====================
    # CONTENEDOR CON SCROLL
    # ====================
    scroll_container = ctk.CTkFrame(dashboard_frame, fg_color=COLOR_WHITE)
    scroll_container.pack(fill="both", expand=True, padx=10, pady=5)

    canvas = tk.Canvas(scroll_container, bg=COLOR_WHITE, highlightthickness=0)
    vscroll = ttk.Scrollbar(scroll_container, orient="vertical", command=canvas.yview)

    # Scrollbar estilo pastel
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Vertical.TScrollbar",
                    background="#cce7f0",
                    troughcolor="#eaf6fb",
                    arrowcolor="#4a4a4a",
                    gripcount=0,
                    relief="flat")

    canvas.configure(yscrollcommand=vscroll.set)

    vscroll.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    # Frame interior
    inner_frame = tk.Frame(canvas, bg=COLOR_WHITE)
    canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    def _on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
        try:
            canvas.itemconfig(canvas_window, width=event.width)
        except Exception:
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())
        canvas.update_idletasks()

    inner_frame.bind("<Configure>", _on_frame_configure)

    # Scroll con rueda del mouse
    def _on_mousewheel(event):
        if event.delta:  # Windows / MacOS
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        else:  # Linux
            if event.num == 5:
                canvas.yview_scroll(1, "units")
            elif event.num == 4:
                canvas.yview_scroll(-1, "units")

    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    canvas.bind_all("<Button-4>", _on_mousewheel)
    canvas.bind_all("<Button-5>", _on_mousewheel)

    # ====================
    # PESTAÑAS (TABS) - OF y AI
    # ====================
    tabs_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
    tabs_frame.pack(fill="x", padx=15, pady=(10, 0))

    # Variable para rastrear la pestaña activa
    active_tab = {"current": "OF"}

    # Función para cambiar de pestaña
    def cambiar_tab(tab_name):
        active_tab["current"] = tab_name
        
        # Actualizar colores de botones
        if tab_name == "OF":
            btn_tab_of.configure(fg_color="#a51c30", hover_color="#8b1629")
            btn_tab_ai.configure(fg_color="#6B7280", hover_color="#4B5563")
            
            # Mostrar contenido OF, ocultar AI
            contenido_of_frame.pack(fill="both", expand=True, pady=(0, 10))
            contenido_ai_frame.pack_forget()
        else:  # AI
            btn_tab_ai.configure(fg_color="#a51c30", hover_color="#8b1629")
            btn_tab_of.configure(fg_color="#6B7280", hover_color="#4B5563")
            
            # Mostrar contenido AI, ocultar OF
            contenido_ai_frame.pack(fill="both", expand=True, pady=(0, 10))
            contenido_of_frame.pack_forget()

    # Botones de pestañas
    btn_tab_of = ctk.CTkButton(
        tabs_frame,
        text="📋 ÓRDENES DE FISCALIZACIÓN (OF)",
        command=lambda: cambiar_tab("OF"),
        fg_color="#a51c30",
        hover_color="#8b1629",
        font=("Segoe UI", 13, "bold"),
        width=300,
        height=40
    )
    btn_tab_of.pack(side="left", padx=5)

    btn_tab_ai = ctk.CTkButton(
        tabs_frame,
        text="🎯 ACCIONES INDUCTIVAS (AI)",
        command=lambda: cambiar_tab("AI"),
        fg_color="#6B7280",
        hover_color="#4B5563",
        font=("Segoe UI", 13, "bold"),
        width=300,
        height=40
    )
    btn_tab_ai.pack(side="left", padx=5)

    # ====================
    # CONTENIDO PARA OF
    # ====================
    contenido_of_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")
    
    # ===== OBTENER VALORES ÚNICOS PARA FILTROS OF =====
    try:
        conn_filtros = mysql.connector.connect(**DB_CONFIG)
        
        query_des_cod = """
            SELECT DISTINCT des_cod 
            FROM fiscalizaciones1 
            WHERE des_cod IS NOT NULL AND des_cod != ''
            ORDER BY des_cod;
        """
        df_des_cod = pd.read_sql(query_des_cod, DB_ENGINE)
        available_des_cod = df_des_cod['des_cod'].tolist()
        
        query_anio = """
            SELECT DISTINCT Anio_Emis 
            FROM fiscalizaciones1 
            WHERE Anio_Emis IS NOT NULL AND Anio_Emis != ''
            ORDER BY Anio_Emis DESC;
        """
        df_anio = pd.read_sql(query_anio, DB_ENGINE)
        available_anios = df_anio['Anio_Emis'].tolist()
        
        conn_filtros.close()
    except Exception as e:
        available_des_cod = []
        available_anios = []

    # ===== MÉTRICAS OF =====
    metrics_of_container = ctk.CTkFrame(contenido_of_frame, fg_color=COLOR_WHITE)
    metrics_of_container.pack(pady=(4, 3), padx=15, fill="x")

    def crear_card(parent, icono, texto, valor, color_fondo, color_hover):
        frame = ctk.CTkFrame(parent, corner_radius=15, fg_color=color_fondo)
        frame.pack(side="left", padx=12, pady=10, ipadx=16, ipady=10)

        def on_enter(e): frame.configure(fg_color=color_hover)
        def on_leave(e): frame.configure(fg_color=color_fondo)
        frame.bind("<Enter>", on_enter)
        frame.bind("<Leave>", on_leave)

        ctk.CTkLabel(frame, text=icono, font=("Segoe UI Emoji", 26)).grid(row=0, column=0, rowspan=2, padx=8)
        ctk.CTkLabel(frame, text=texto, font=("Segoe UI", 11, "bold")).grid(row=0, column=1, sticky="w", pady=(6,0))
        ctk.CTkLabel(frame, text=str(valor), font=("Segoe UI", 16, "bold")).grid(row=1, column=1, sticky="w")
        return frame

    def recalcular_metricas_of(filtros_des=None, filtros_anio=None):
        for widget in metrics_of_container.winfo_children():
            widget.destroy()

        condiciones_metricas = []
        if filtros_des and len(filtros_des) > 0:
            placeholders = ', '.join([f"'{val}'" for val in filtros_des])
            condiciones_metricas.append(f"f1.des_cod IN ({placeholders})")
        if filtros_anio and len(filtros_anio) > 0:
            placeholders = ', '.join([f"'{val}'" for val in filtros_anio])
            condiciones_metricas.append(f"f1.Anio_Emis IN ({placeholders})")

        where_metricas = ""
        if condiciones_metricas:
            where_metricas = " AND " + " AND ".join(condiciones_metricas)

        try:
            query_metricas = f"""
                SELECT 
                    COUNT(*) as total_of,
                    SUM(f4.mto_saldo) as total_saldo,
                    COUNT(DISTINCT f1.NUM_DOCSEL) as total_contribuyentes
                FROM fiscalizaciones1 f1
                INNER JOIN fiscalizaciones4 f4 
                    ON TRIM(f1.NUM_DOCSEL) = TRIM(f4.num_ruc)
                WHERE LOWER(TRIM(IFNULL(f1.Estado, ''))) = 'pendiente'
                {where_metricas};
            """
            conn_metricas = mysql.connector.connect(**DB_CONFIG)
            df_metricas = pd.read_sql(query_metricas, DB_ENGINE)
            conn_metricas.close()

            if not df_metricas.empty:
                total_of = int(df_metricas.iloc[0]['total_of'])
                total_saldo = float(df_metricas.iloc[0]['total_saldo']) if pd.notna(df_metricas.iloc[0]['total_saldo']) else 0
                total_contribuyentes = int(df_metricas.iloc[0]['total_contribuyentes'])
                saldo_formateado = f"S/ {total_saldo:,.2f}"
            else:
                total_of = 0
                saldo_formateado = "S/ 0.00"
                total_contribuyentes = 0
        except Exception:
            total_of = 0
            saldo_formateado = "S/ 0.00"
            total_contribuyentes = 0

        crear_card(metrics_of_container, "📊", "Total OF Pendientes", total_of, "#c2e9fb", "#90cdf4")
        crear_card(metrics_of_container, "💰", "Saldo Total", saldo_formateado, "#ffd6a5", "#ffb347")
        crear_card(metrics_of_container, "👥", "Contribuyentes", total_contribuyentes, "#d4a5f9", "#b784f2")

    recalcular_metricas_of()

    # ===== FRAME DE TABLA OF =====
    frame_tabla_of = ctk.CTkFrame(contenido_of_frame, fg_color="white", corner_radius=12)

    # ===== FILTROS OF =====
    filtro_of_frame = ctk.CTkFrame(contenido_of_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_of_frame.pack(fill="x", padx=12, pady=(5, 5))

    def aplicar_filtros_of_auto():
        selected_descod = [k for k, v in check_descod_vars.items() if v.get() == 1 and k != "(Todos)"]
        filtros_des = selected_descod if len(selected_descod) > 0 else None

        selected_anio = [k for k, v in check_anio_vars.items() if v.get() == 1 and k != "(Todos)"]
        filtros_anio = selected_anio if len(selected_anio) > 0 else None

        for widget in frame_tabla_of.winfo_children():
            widget.destroy()

        generar_tabla_control_saldo_detracciones(frame_tabla_of, 
                                                  filtros_des_cod=filtros_des,
                                                  filtros_anio=filtros_anio)
        recalcular_metricas_of(filtros_des, filtros_anio)

    # Descripción (des_cod)
    ctk.CTkLabel(filtro_of_frame, text="🔎 Descripción:", font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=(6, 4))

    descod_button_text = tk.StringVar(value="(Todos)")
    btn_descod = ctk.CTkButton(filtro_of_frame, textvariable=descod_button_text, width=180,
                               command=lambda: toggle_dropdown_descod())
    btn_descod.pack(side="left", padx=(0, 12))

    dropdown_descod_win = {"win": None}
    check_descod_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in available_des_cod:
        check_descod_vars[val] = tk.IntVar(value=0)

    def toggle_dropdown_descod():
        if dropdown_descod_win["win"] is not None:
            try:
                dropdown_descod_win["win"].destroy()
            except:
                pass
            dropdown_descod_win["win"] = None
            return

        top = tk.Toplevel(filtro_of_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_descod_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_descod(selected_val):
            if selected_val == "(Todos)":
                if check_descod_vars["(Todos)"].get() == 1:
                    for k in check_descod_vars:
                        if k != "(Todos)":
                            check_descod_vars[k].set(0)
            else:
                check_descod_vars["(Todos)"].set(0)

            selected = [k for k, v in check_descod_vars.items() if v.get() == 1 and k != "(Todos)"]
            if check_descod_vars["(Todos)"].get() == 1 or len(selected) == 0:
                descod_button_text.set("(Todos)")
            elif len(selected) == 1:
                descod_button_text.set(selected[0])
            else:
                descod_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_of_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", variable=check_descod_vars["(Todos)"],
                                   command=lambda: on_check_change_descod("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in available_des_cod:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), variable=check_descod_vars[val],
                                command=lambda v=val: on_check_change_descod(v), font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_descod.winfo_rootx()
        y = btn_descod.winfo_rooty() + btn_descod.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown_descod(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_descod_win["win"] = None

        top.bind("<FocusOut>", close_dropdown_descod)
        top.bind("<Escape>", close_dropdown_descod)

    # Año de Emisión
    ctk.CTkLabel(filtro_of_frame, text="📅 Año Emisión:", font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=(6, 4))

    anio_button_text = tk.StringVar(value="(Todos)")
    btn_anio = ctk.CTkButton(filtro_of_frame, textvariable=anio_button_text, width=180,
                             command=lambda: toggle_dropdown_anio())
    btn_anio.pack(side="left", padx=(0, 12))

    dropdown_anio_win = {"win": None}
    check_anio_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in available_anios:
        check_anio_vars[val] = tk.IntVar(value=0)

    def toggle_dropdown_anio():
        if dropdown_anio_win["win"] is not None:
            try:
                dropdown_anio_win["win"].destroy()
            except:
                pass
            dropdown_anio_win["win"] = None
            return

        top = tk.Toplevel(filtro_of_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_anio_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_anio(selected_val):
            if selected_val == "(Todos)":
                if check_anio_vars["(Todos)"].get() == 1:
                    for k in check_anio_vars:
                        if k != "(Todos)":
                            check_anio_vars[k].set(0)
            else:
                check_anio_vars["(Todos)"].set(0)

            selected = [k for k, v in check_anio_vars.items() if v.get() == 1 and k != "(Todos)"]
            if check_anio_vars["(Todos)"].get() == 1 or len(selected) == 0:
                anio_button_text.set("(Todos)")
            elif len(selected) == 1:
                anio_button_text.set(str(selected[0]))
            else:
                anio_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_of_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", variable=check_anio_vars["(Todos)"],
                                   command=lambda: on_check_change_anio("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in available_anios:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), variable=check_anio_vars[val],
                                command=lambda v=val: on_check_change_anio(v), font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_anio.winfo_rootx()
        y = btn_anio.winfo_rooty() + btn_anio.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown_anio(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_anio_win["win"] = None

        top.bind("<FocusOut>", close_dropdown_anio)
        top.bind("<Escape>", close_dropdown_anio)

    def limpiar_filtros_of():
        check_descod_vars["(Todos)"].set(1)
        for k in check_descod_vars:
            if k != "(Todos)":
                check_descod_vars[k].set(0)
        descod_button_text.set("(Todos)")

        check_anio_vars["(Todos)"].set(1)
        for k in check_anio_vars:
            if k != "(Todos)":
                check_anio_vars[k].set(0)
        anio_button_text.set("(Todos)")
        aplicar_filtros_of_auto()

    ctk.CTkButton(filtro_of_frame, text="🔄 Limpiar", command=limpiar_filtros_of,
                  fg_color="#F59E0B", hover_color="#D97706", font=("Segoe UI", 11, "bold"),
                  width=120, height=32).pack(side="left", padx=5)

    # Generar tabla OF inicial
    frame_tabla_of.pack(pady=(5, 10), anchor="center", fill="both", expand=True)
    try:
        generar_tabla_control_saldo_detracciones(frame_tabla_of)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla OF:\n{e}")

    # ====================
    # CONTENIDO PARA AI
    # ====================
    contenido_ai_frame = ctk.CTkFrame(inner_frame, fg_color="transparent")

    # ===== OBTENER VALORES ÚNICOS PARA FILTROS AI =====
    try:
        conn_filtros_ai = mysql.connector.connect(**DB_CONFIG)
        
        query_supervisor = """
            SELECT DISTINCT DES_NOMB_SUP 
            FROM fiscalizaciones3 
            WHERE DES_NOMB_SUP IS NOT NULL AND DES_NOMB_SUP != ''
            ORDER BY DES_NOMB_SUP;
        """
        df_supervisor = pd.read_sql(query_supervisor, DB_ENGINE)
        available_supervisores = df_supervisor['DES_NOMB_SUP'].tolist()
        
        query_tipo_ai = """
            SELECT DISTINCT des_tipo_ai 
            FROM fiscalizaciones3 
            WHERE des_tipo_ai IS NOT NULL AND des_tipo_ai != ''
            ORDER BY des_tipo_ai;
        """
        df_tipo_ai = pd.read_sql(query_tipo_ai, DB_ENGINE)
        available_tipos_ai = df_tipo_ai['des_tipo_ai'].tolist()
        
        query_anio_ai = """
            SELECT DISTINCT Anio_Emis 
            FROM fiscalizaciones3 
            WHERE Anio_Emis IS NOT NULL AND Anio_Emis != ''
            ORDER BY Anio_Emis DESC;
        """
        df_anio_ai = pd.read_sql(query_anio_ai, DB_ENGINE)
        available_anios_ai = df_anio_ai['Año_Emis'].tolist()
        
        conn_filtros_ai.close()
    except Exception as e:
        available_supervisores = []
        available_tipos_ai = []
        available_anios_ai = []

    # ===== MÉTRICAS AI =====
    metrics_ai_container = ctk.CTkFrame(contenido_ai_frame, fg_color=COLOR_WHITE)
    metrics_ai_container.pack(pady=(4, 3), padx=15, fill="x")

    def recalcular_metricas_ai(filtros_sup=None, filtros_tipo=None, filtros_anio=None):
        for widget in metrics_ai_container.winfo_children():
            widget.destroy()

        condiciones_metricas = []
        if filtros_sup and len(filtros_sup) > 0:
            placeholders = ', '.join([f"'{val}'" for val in filtros_sup])
            condiciones_metricas.append(f"f3.DES_NOMB_SUP IN ({placeholders})")
        if filtros_tipo and len(filtros_tipo) > 0:
            placeholders = ', '.join([f"'{val}'" for val in filtros_tipo])
            condiciones_metricas.append(f"f3.des_tipo_ai IN ({placeholders})")
        if filtros_anio and len(filtros_anio) > 0:
            placeholders = ', '.join([f"'{val}'" for val in filtros_anio])
            condiciones_metricas.append(f"f3.Anio_Emis IN ({placeholders})")

        where_metricas = ""
        if condiciones_metricas:
            where_metricas = " AND " + " AND ".join(condiciones_metricas)

        try:
            query_metricas = f"""
                SELECT 
                    COUNT(*) as total_ai,
                    SUM(f4.mto_saldo) as total_saldo,
                    COUNT(DISTINCT f3.NUM_DOCSEL) as total_contribuyentes
                FROM fiscalizaciones3 f3
                INNER JOIN fiscalizaciones4 f4 
                    ON TRIM(f3.NUM_DOCSEL) = TRIM(f4.num_ruc)
                WHERE LOWER(TRIM(IFNULL(f3.Estado, ''))) = 'pendiente'
                {where_metricas};
            """
            conn_metricas = mysql.connector.connect(**DB_CONFIG)
            df_metricas = pd.read_sql(query_metricas, DB_ENGINE)
            conn_metricas.close()

            if not df_metricas.empty:
                total_ai = int(df_metricas.iloc[0]['total_ai'])
                total_saldo = float(df_metricas.iloc[0]['total_saldo']) if pd.notna(df_metricas.iloc[0]['total_saldo']) else 0
                total_contribuyentes = int(df_metricas.iloc[0]['total_contribuyentes'])
                saldo_formateado = f"S/ {total_saldo:,.2f}"
            else:
                total_ai = 0
                saldo_formateado = "S/ 0.00"
                total_contribuyentes = 0
        except Exception:
            total_ai = 0
            saldo_formateado = "S/ 0.00"
            total_contribuyentes = 0

        crear_card(metrics_ai_container, "🎯", "Total AI Pendientes", total_ai, "#c2e9fb", "#90cdf4")
        crear_card(metrics_ai_container, "💰", "Saldo Total", saldo_formateado, "#ffd6a5", "#ffb347")
        crear_card(metrics_ai_container, "👥", "Contribuyentes", total_contribuyentes, "#d4a5f9", "#b784f2")

    recalcular_metricas_ai()

    # ===== FRAME DE TABLA AI =====
    frame_tabla_ai = ctk.CTkFrame(contenido_ai_frame, fg_color="white", corner_radius=12)

    # ===== FILTROS AI =====
    filtro_ai_frame = ctk.CTkFrame(contenido_ai_frame, corner_radius=12, fg_color="#f5f6fa")
    filtro_ai_frame.pack(fill="x", padx=12, pady=(5, 5))

    def aplicar_filtros_ai_auto():
        selected_sup = [k for k, v in check_supervisor_vars.items() if v.get() == 1 and k != "(Todos)"]
        filtros_sup = selected_sup if len(selected_sup) > 0 else None

        selected_tipo = [k for k, v in check_tipo_ai_vars.items() if v.get() == 1 and k != "(Todos)"]
        filtros_tipo = selected_tipo if len(selected_tipo) > 0 else None

        selected_anio_ai = [k for k, v in check_anio_ai_vars.items() if v.get() == 1 and k != "(Todos)"]
        filtros_anio = selected_anio_ai if len(selected_anio_ai) > 0 else None

        for widget in frame_tabla_ai.winfo_children():
            widget.destroy()

        generar_tabla_control_saldo_detracciones_ai(frame_tabla_ai,
                                                     filtros_supervisor=filtros_sup,
                                                     filtros_tipo_ai=filtros_tipo,
                                                     filtros_anio=filtros_anio)
        recalcular_metricas_ai(filtros_sup, filtros_tipo, filtros_anio)

    # Supervisor
    ctk.CTkLabel(filtro_ai_frame, text="👤 Supervisor:", font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=(6, 4))

    supervisor_button_text = tk.StringVar(value="(Todos)")
    btn_supervisor = ctk.CTkButton(filtro_ai_frame, textvariable=supervisor_button_text, width=180,
                                   command=lambda: toggle_dropdown_supervisor())
    btn_supervisor.pack(side="left", padx=(0, 12))

    dropdown_supervisor_win = {"win": None}
    check_supervisor_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in available_supervisores:
        check_supervisor_vars[val] = tk.IntVar(value=0)

    def toggle_dropdown_supervisor():
        if dropdown_supervisor_win["win"] is not None:
            try:
                dropdown_supervisor_win["win"].destroy()
            except:
                pass
            dropdown_supervisor_win["win"] = None
            return

        top = tk.Toplevel(filtro_ai_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_supervisor_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_supervisor(selected_val):
            if selected_val == "(Todos)":
                if check_supervisor_vars["(Todos)"].get() == 1:
                    for k in check_supervisor_vars:
                        if k != "(Todos)":
                            check_supervisor_vars[k].set(0)
            else:
                check_supervisor_vars["(Todos)"].set(0)

            selected = [k for k, v in check_supervisor_vars.items() if v.get() == 1 and k != "(Todos)"]
            if check_supervisor_vars["(Todos)"].get() == 1 or len(selected) == 0:
                supervisor_button_text.set("(Todos)")
            elif len(selected) == 1:
                supervisor_button_text.set(selected[0])
            else:
                supervisor_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_ai_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", variable=check_supervisor_vars["(Todos)"],
                                   command=lambda: on_check_change_supervisor("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in available_supervisores:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), variable=check_supervisor_vars[val],
                                command=lambda v=val: on_check_change_supervisor(v), font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_supervisor.winfo_rootx()
        y = btn_supervisor.winfo_rooty() + btn_supervisor.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown_supervisor(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_supervisor_win["win"] = None

        top.bind("<FocusOut>", close_dropdown_supervisor)
        top.bind("<Escape>", close_dropdown_supervisor)

    # Tipo AI
    ctk.CTkLabel(filtro_ai_frame, text="📋 Tipo AI:", font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=(6, 4))

    tipo_ai_button_text = tk.StringVar(value="(Todos)")
    btn_tipo_ai = ctk.CTkButton(filtro_ai_frame, textvariable=tipo_ai_button_text, width=180,
                                command=lambda: toggle_dropdown_tipo_ai())
    btn_tipo_ai.pack(side="left", padx=(0, 12))

    dropdown_tipo_ai_win = {"win": None}
    check_tipo_ai_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in available_tipos_ai:
        check_tipo_ai_vars[val] = tk.IntVar(value=0)

    def toggle_dropdown_tipo_ai():
        if dropdown_tipo_ai_win["win"] is not None:
            try:
                dropdown_tipo_ai_win["win"].destroy()
            except:
                pass
            dropdown_tipo_ai_win["win"] = None
            return

        top = tk.Toplevel(filtro_ai_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_tipo_ai_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_tipo_ai(selected_val):
            if selected_val == "(Todos)":
                if check_tipo_ai_vars["(Todos)"].get() == 1:
                    for k in check_tipo_ai_vars:
                        if k != "(Todos)":
                            check_tipo_ai_vars[k].set(0)
            else:
                check_tipo_ai_vars["(Todos)"].set(0)

            selected = [k for k, v in check_tipo_ai_vars.items() if v.get() == 1 and k != "(Todos)"]
            if check_tipo_ai_vars["(Todos)"].get() == 1 or len(selected) == 0:
                tipo_ai_button_text.set("(Todos)")
            elif len(selected) == 1:
                tipo_ai_button_text.set(selected[0])
            else:
                tipo_ai_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_ai_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", variable=check_tipo_ai_vars["(Todos)"],
                                   command=lambda: on_check_change_tipo_ai("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in available_tipos_ai:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), variable=check_tipo_ai_vars[val],
                                command=lambda v=val: on_check_change_tipo_ai(v), font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_tipo_ai.winfo_rootx()
        y = btn_tipo_ai.winfo_rooty() + btn_tipo_ai.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown_tipo_ai(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_tipo_ai_win["win"] = None

        top.bind("<FocusOut>", close_dropdown_tipo_ai)
        top.bind("<Escape>", close_dropdown_tipo_ai)

    # Año de Emisión AI
    ctk.CTkLabel(filtro_ai_frame, text="📅 Año Emisión:", font=("Segoe UI", 13, "bold"),
                 text_color="#002e6d").pack(side="left", padx=(6, 4))

    anio_ai_button_text = tk.StringVar(value="(Todos)")
    btn_anio_ai = ctk.CTkButton(filtro_ai_frame, textvariable=anio_ai_button_text, width=180,
                                command=lambda: toggle_dropdown_anio_ai())
    btn_anio_ai.pack(side="left", padx=(0, 12))

    dropdown_anio_ai_win = {"win": None}
    check_anio_ai_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in available_anios_ai:
        check_anio_ai_vars[val] = tk.IntVar(value=0)

    def toggle_dropdown_anio_ai():
        if dropdown_anio_ai_win["win"] is not None:
            try:
                dropdown_anio_ai_win["win"].destroy()
            except:
                pass
            dropdown_anio_ai_win["win"] = None
            return

        top = tk.Toplevel(filtro_ai_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_anio_ai_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_anio_ai(selected_val):
            if selected_val == "(Todos)":
                if check_anio_ai_vars["(Todos)"].get() == 1:
                    for k in check_anio_ai_vars:
                        if k != "(Todos)":
                            check_anio_ai_vars[k].set(0)
            else:
                check_anio_ai_vars["(Todos)"].set(0)

            selected = [k for k, v in check_anio_ai_vars.items() if v.get() == 1 and k != "(Todos)"]
            if check_anio_ai_vars["(Todos)"].get() == 1 or len(selected) == 0:
                anio_ai_button_text.set("(Todos)")
            elif len(selected) == 1:
                anio_ai_button_text.set(str(selected[0]))
            else:
                anio_ai_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_ai_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", variable=check_anio_ai_vars["(Todos)"],
                                   command=lambda: on_check_change_anio_ai("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in available_anios_ai:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), variable=check_anio_ai_vars[val],
                                command=lambda v=val: on_check_change_anio_ai(v), font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_anio_ai.winfo_rootx()
        y = btn_anio_ai.winfo_rooty() + btn_anio_ai.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown_anio_ai(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_anio_ai_win["win"] = None

        top.bind("<FocusOut>", close_dropdown_anio_ai)
        top.bind("<Escape>", close_dropdown_anio_ai)

    def limpiar_filtros_ai():
        check_supervisor_vars["(Todos)"].set(1)
        for k in check_supervisor_vars:
            if k != "(Todos)":
                check_supervisor_vars[k].set(0)
        supervisor_button_text.set("(Todos)")

        check_tipo_ai_vars["(Todos)"].set(1)
        for k in check_tipo_ai_vars:
            if k != "(Todos)":
                check_tipo_ai_vars[k].set(0)
        tipo_ai_button_text.set("(Todos)")

        check_anio_ai_vars["(Todos)"].set(1)
        for k in check_anio_ai_vars:
            if k != "(Todos)":
                check_anio_ai_vars[k].set(0)
        anio_ai_button_text.set("(Todos)")
        
        aplicar_filtros_ai_auto()

    ctk.CTkButton(filtro_ai_frame, text="🔄 Limpiar", command=limpiar_filtros_ai,
                  fg_color="#F59E0B", hover_color="#D97706", font=("Segoe UI", 11, "bold"),
                  width=120, height=32).pack(side="left", padx=5)

    # Generar tabla AI inicial
    frame_tabla_ai.pack(pady=(5, 10), anchor="center", fill="both", expand=True)
    try:
        generar_tabla_control_saldo_detracciones_ai(frame_tabla_ai)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo generar la tabla AI:\n{e}")

    # ====================
    # MOSTRAR CONTENIDO INICIAL (OF)
    # ====================
    contenido_of_frame.pack(fill="both", expand=True, pady=(0, 10))

    # ====================
    # Forzar redraw
    # ====================
    def _force_redraw():
        try:
            # Verificar que los widgets todavía existen antes de actualizarlos
            if canvas.winfo_exists() and inner_frame.winfo_exists():
                inner_frame.update_idletasks()
                canvas.itemconfig(canvas_window, width=canvas.winfo_width())
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.update()
                canvas.yview_moveto(0)
        except Exception:
            pass

    # Programar callbacks con verificación de existencia del widget
    try:
        if canvas.winfo_exists():
            canvas.after(50, _force_redraw)
            canvas.after(200, _force_redraw)
            canvas.after(500, _force_redraw)
            _force_redraw()
    except Exception:
        pass
#----------------------------------------------------------------------
#--------------------------------------------------------------------
#--------------------------------------------------------------------
# ==========================
# FUNCIONES PARA DASHBOARD DE METAS - RECAUDACIÓN AUDITORIA
# ==========================
# ==========================
# FUNCIONES PARA DASHBOARD DE METAS - RECAUDACIÓN AUDITORIA
# VERSIÓN CORREGIDA CON MEJOR VISUALIZACIÓN
# ==========================
def generar_tabla_of_recaudacion_auditoria(parent_frame, df_filtrado):
    """
    Genera tabla OF - Recaudación Auditoria
    Tabla dinámica con auditores en filas y meses en columnas
    """
    for widget in parent_frame.winfo_children():
        widget.destroy()

    if df_filtrado.empty:
        lbl_no_data = ctk.CTkLabel(parent_frame, text="No hay datos para mostrar",
                                   font=("Segoe UI", 14), text_color=COLOR_TEXT)
        lbl_no_data.pack(pady=20)
        return

    # Mapeo de meses
    meses_map = {
        1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 5: "MAY", 6: "JUN",
        7: "JUL", 8: "AGO", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"
    }

    # Crear pivot table: des_func x MES -> suma de MTO_PAG
    df_pivot = df_filtrado.pivot_table(
        index='des_func',
        columns='MES',
        values='MTO_PAG',
        aggfunc='sum',
        fill_value=0
    )

    # Asegurar que todos los meses estén presentes
    for mes in range(1, 13):
        if mes not in df_pivot.columns:
            df_pivot[mes] = 0

    # Ordenar columnas por mes
    df_pivot = df_pivot[[i for i in range(1, 13) if i in df_pivot.columns]]

    # Calcular totales
    df_pivot['TOTAL'] = df_pivot.sum(axis=1)
    
    # Agregar fila de totales
    totales_fila = df_pivot.sum(axis=0)
    df_pivot.loc['TOTAL'] = totales_fila

    # Crear contenedor principal con más altura
    container_frame = ctk.CTkFrame(parent_frame, fg_color=COLOR_WHITE, height=420)
    container_frame.pack(fill="both", expand=False, padx=5, pady=5)
    container_frame.pack_propagate(False)  # Mantener altura fija
    
    canvas = tk.Canvas(container_frame, bg=COLOR_WHITE, highlightthickness=0)
    scrollbar_y = ctk.CTkScrollbar(container_frame, orientation="vertical", command=canvas.yview)
    
    tabla_frame = ctk.CTkFrame(canvas, fg_color=COLOR_WHITE)
    
    canvas_window = canvas.create_window((0, 0), window=tabla_frame, anchor="n")
    canvas.configure(yscrollcommand=scrollbar_y.set)

    # ENCABEZADOS
    header_frame = ctk.CTkFrame(tabla_frame, fg_color=COLOR_PRIMARY, corner_radius=5, 
                                border_width=1, border_color="#002e6d")
    header_frame.grid(row=0, column=0, columnspan=14, sticky="ew", padx=1, pady=1)

    # Configurar pesos de columnas para expansión uniforme
    for i in range(14):
        header_frame.grid_columnconfigure(i, weight=1, minsize=70)

    # Encabezado "Auditores"
    lbl_header_auditor = ctk.CTkLabel(header_frame, text="AUDITORES", 
                                       font=("Segoe UI", 9, "bold"),
                                       text_color="white", width=180, anchor="w")
    lbl_header_auditor.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # Encabezados de meses
    for idx, mes_num in enumerate(sorted([c for c in df_pivot.columns if c != 'TOTAL']), start=1):
        mes_nombre = meses_map.get(mes_num, str(mes_num))
        lbl_mes = ctk.CTkLabel(header_frame, text=mes_nombre, 
                               font=("Segoe UI", 9, "bold"),
                               text_color="white", width=70, anchor="center")
        lbl_mes.grid(row=0, column=idx, padx=1, pady=5, sticky="ew")

    # Encabezado TOTAL
    lbl_total_header = ctk.CTkLabel(header_frame, text="TOTAL", 
                                     font=("Segoe UI", 9, "bold"),
                                     text_color="white", width=85, anchor="center")
    lbl_total_header.grid(row=0, column=13, padx=1, pady=5, sticky="ew")

    # FILAS DE DATOS
    for row_idx, (auditor, row_data) in enumerate(df_pivot.iterrows(), start=1):
        # Alternar colores de fila
        if row_idx % 2 == 0:
            bg_color = "#F9FAFB"
        else:
            bg_color = COLOR_WHITE

        # Fila especial para TOTAL
        if auditor == 'TOTAL':
            bg_color = "#FEE2E2"  # Rojo claro para totales
            font_style = ("Segoe UI", 9, "bold")
        else:
            font_style = ("Segoe UI", 8)

        row_frame = ctk.CTkFrame(tabla_frame, fg_color=bg_color, corner_radius=3,
                                border_width=1, border_color="#E5E7EB")
        row_frame.grid(row=row_idx, column=0, columnspan=14, sticky="ew", padx=1, pady=1)

        # Configurar pesos de columnas
        for i in range(14):
            row_frame.grid_columnconfigure(i, weight=1, minsize=70)

        # Nombre del auditor
        lbl_auditor = ctk.CTkLabel(row_frame, text=str(auditor), 
                                   font=font_style,
                                   text_color=COLOR_TEXT, width=180, anchor="w")
        lbl_auditor.grid(row=0, column=0, padx=5, pady=3, sticky="ew")

        # Valores de cada mes
        for col_idx, mes_num in enumerate(sorted([c for c in df_pivot.columns if c != 'TOTAL']), start=1):
            valor = row_data[mes_num]
            texto_valor = f"S/ {valor:,.2f}" if valor != 0 else "S/ 0.00"
            
            lbl_valor = ctk.CTkLabel(row_frame, text=texto_valor, 
                                    font=font_style,
                                    text_color=COLOR_TEXT, width=70, anchor="center")
            lbl_valor.grid(row=0, column=col_idx, padx=1, pady=3, sticky="ew")

        # Valor TOTAL
        total_valor = row_data['TOTAL']
        texto_total = f"S/ {total_valor:,.2f}"
        lbl_total = ctk.CTkLabel(row_frame, text=texto_total, 
                                font=("Segoe UI", 9, "bold") if auditor == 'TOTAL' else ("Segoe UI", 8, "bold"),
                                text_color="#DC2626", width=85, anchor="center")
        lbl_total.grid(row=0, column=13, padx=1, pady=3, sticky="ew")

    # Configurar scroll
    def _configure_scroll(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Centrar la tabla horizontalmente
        tabla_width = tabla_frame.winfo_reqwidth()
        canvas_width = canvas.winfo_width()
        if tabla_width < canvas_width:
            x_offset = (canvas_width - tabla_width) // 2
            canvas.coords(canvas_window, x_offset, 0)
        else:
            canvas.coords(canvas_window, 0, 0)

    tabla_frame.bind("<Configure>", _configure_scroll)
    canvas.bind("<Configure>", _configure_scroll)
    tabla_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    # Empaquetar scrollbar vertical solamente
    scrollbar_y.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

def generar_tabla_ai_recaudacion_auditoria(parent_frame, df_filtrado):
    """
    Genera tabla AI - Recaudación Auditoria
    Tabla dinámica con auditores en filas y meses en columnas
    """
    for widget in parent_frame.winfo_children():
        widget.destroy()

    if df_filtrado.empty:
        lbl_no_data = ctk.CTkLabel(parent_frame, text="No hay datos para mostrar",
                                   font=("Segoe UI", 14), text_color=COLOR_TEXT)
        lbl_no_data.pack(pady=20)
        return

    # Mapeo de meses
    meses_map = {
        1: "ENE", 2: "FEB", 3: "MAR", 4: "ABR", 5: "MAY", 6: "JUN",
        7: "JUL", 8: "AGO", 9: "SEP", 10: "OCT", 11: "NOV", 12: "DIC"
    }

    # Crear pivot table: nomb_ver x MES -> suma de MTO_PAG_IN
    df_pivot = df_filtrado.pivot_table(
        index='nomb_ver',
        columns='MES',
        values='MTO_PAG_IN',
        aggfunc='sum',
        fill_value=0
    )

    # Asegurar que todos los meses estén presentes
    for mes in range(1, 13):
        if mes not in df_pivot.columns:
            df_pivot[mes] = 0

    # Ordenar columnas por mes
    df_pivot = df_pivot[[i for i in range(1, 13) if i in df_pivot.columns]]

    # Calcular totales
    df_pivot['TOTAL'] = df_pivot.sum(axis=1)
    
    # Agregar fila de totales
    totales_fila = df_pivot.sum(axis=0)
    df_pivot.loc['TOTAL'] = totales_fila

    # Crear contenedor principal con más altura
    container_frame = ctk.CTkFrame(parent_frame, fg_color=COLOR_WHITE, height=420)
    container_frame.pack(fill="both", expand=False, padx=5, pady=5)
    container_frame.pack_propagate(False)  # Mantener altura fija
    
    canvas = tk.Canvas(container_frame, bg=COLOR_WHITE, highlightthickness=0)
    scrollbar_y = ctk.CTkScrollbar(container_frame, orientation="vertical", command=canvas.yview)
    
    tabla_frame = ctk.CTkFrame(canvas, fg_color=COLOR_WHITE)
    
    canvas_window = canvas.create_window((0, 0), window=tabla_frame, anchor="n")
    canvas.configure(yscrollcommand=scrollbar_y.set)

    # ENCABEZADOS
    header_frame = ctk.CTkFrame(tabla_frame, fg_color=COLOR_PRIMARY, corner_radius=5,
                                border_width=1, border_color="#002e6d")
    header_frame.grid(row=0, column=0, columnspan=14, sticky="ew", padx=1, pady=1)

    # Configurar pesos de columnas para expansión uniforme
    for i in range(14):
        header_frame.grid_columnconfigure(i, weight=1, minsize=70)

    # Encabezado "Auditores"
    lbl_header_auditor = ctk.CTkLabel(header_frame, text="AUDITORES", 
                                       font=("Segoe UI", 9, "bold"),
                                       text_color="white", width=180, anchor="w")
    lbl_header_auditor.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

    # Encabezados de meses
    for idx, mes_num in enumerate(sorted([c for c in df_pivot.columns if c != 'TOTAL']), start=1):
        mes_nombre = meses_map.get(mes_num, str(mes_num))
        lbl_mes = ctk.CTkLabel(header_frame, text=mes_nombre, 
                               font=("Segoe UI", 9, "bold"),
                               text_color="white", width=70, anchor="center")
        lbl_mes.grid(row=0, column=idx, padx=1, pady=5, sticky="ew")

    # Encabezado TOTAL
    lbl_total_header = ctk.CTkLabel(header_frame, text="TOTAL", 
                                     font=("Segoe UI", 9, "bold"),
                                     text_color="white", width=85, anchor="center")
    lbl_total_header.grid(row=0, column=13, padx=1, pady=5, sticky="ew")

    # FILAS DE DATOS
    for row_idx, (auditor, row_data) in enumerate(df_pivot.iterrows(), start=1):
        # Alternar colores de fila
        if row_idx % 2 == 0:
            bg_color = "#F9FAFB"
        else:
            bg_color = COLOR_WHITE

        # Fila especial para TOTAL
        if auditor == 'TOTAL':
            bg_color = "#FEE2E2"  # Rojo claro para totales
            font_style = ("Segoe UI", 9, "bold")
        else:
            font_style = ("Segoe UI", 8)

        row_frame = ctk.CTkFrame(tabla_frame, fg_color=bg_color, corner_radius=3,
                                border_width=1, border_color="#E5E7EB")
        row_frame.grid(row=row_idx, column=0, columnspan=14, sticky="ew", padx=1, pady=1)

        # Configurar pesos de columnas
        for i in range(14):
            row_frame.grid_columnconfigure(i, weight=1, minsize=70)

        # Nombre del auditor
        lbl_auditor = ctk.CTkLabel(row_frame, text=str(auditor), 
                                   font=font_style,
                                   text_color=COLOR_TEXT, width=180, anchor="w")
        lbl_auditor.grid(row=0, column=0, padx=5, pady=3, sticky="ew")

        # Valores de cada mes
        for col_idx, mes_num in enumerate(sorted([c for c in df_pivot.columns if c != 'TOTAL']), start=1):
            valor = row_data[mes_num]
            texto_valor = f"S/ {valor:,.2f}" if valor != 0 else "S/ 0.00"
            
            lbl_valor = ctk.CTkLabel(row_frame, text=texto_valor, 
                                    font=font_style,
                                    text_color=COLOR_TEXT, width=70, anchor="center")
            lbl_valor.grid(row=0, column=col_idx, padx=1, pady=3, sticky="ew")

        # Valor TOTAL
        total_valor = row_data['TOTAL']
        texto_total = f"S/ {total_valor:,.2f}"
        lbl_total = ctk.CTkLabel(row_frame, text=texto_total, 
                                font=("Segoe UI", 9, "bold") if auditor == 'TOTAL' else ("Segoe UI", 8, "bold"),
                                text_color="#DC2626", width=85, anchor="center")
        lbl_total.grid(row=0, column=13, padx=1, pady=3, sticky="ew")

    # Configurar scroll
    def _configure_scroll(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        # Centrar la tabla horizontalmente
        tabla_width = tabla_frame.winfo_reqwidth()
        canvas_width = canvas.winfo_width()
        if tabla_width < canvas_width:
            x_offset = (canvas_width - tabla_width) // 2
            canvas.coords(canvas_window, x_offset, 0)
        else:
            canvas.coords(canvas_window, 0, 0)

    tabla_frame.bind("<Configure>", _configure_scroll)
    canvas.bind("<Configure>", _configure_scroll)
    tabla_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

    # Empaquetar scrollbar vertical solamente
    scrollbar_y.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

# ==========================
# DASHBOARD AVANCE DE METAS OF
# ==========================
def dashboard_avance_metas_of():
    """
    Dashboard para mostrar el avance de metas OF con:
    - Selector de año (automático desde tabla distribucion)
    - Filtros: Supervisor y Auditor
    - Gráfico de barras horizontal con avance de metas
    - Tabla de avance mensual y anual
    """
    try:
        preview_frame.pack_forget()
    except Exception:
        pass

    dashboard_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    for widget in dashboard_frame.winfo_children():
        widget.destroy()

    # Canvas principal con scroll - RESPONSIVO
    canvas_main = tk.Canvas(dashboard_frame, bg=COLOR_WHITE, highlightthickness=0)
    scrollbar_main = ctk.CTkScrollbar(dashboard_frame, orientation="vertical", command=canvas_main.yview)
    canvas_main.configure(yscrollcommand=scrollbar_main.set)

    inner_frame = ctk.CTkFrame(canvas_main, fg_color=COLOR_WHITE)
    canvas_window = canvas_main.create_window((0, 0), window=inner_frame, anchor="nw")

    def _on_frame_configure(event=None):
        """Configurar scroll y responsividad del canvas"""
        canvas_main.configure(scrollregion=canvas_main.bbox("all"))
        # Hacer que el inner_frame se expanda con la ventana
        if canvas_main.winfo_width() > 1:
            canvas_main.itemconfig(canvas_window, width=canvas_main.winfo_width())

    def _on_canvas_configure(event=None):
        """Ajustar tamaño del inner_frame cuando cambia el canvas"""
        if event and event.width > 1:
            canvas_main.itemconfig(canvas_window, width=event.width)

    inner_frame.bind("<Configure>", _on_frame_configure)
    canvas_main.bind("<Configure>", _on_canvas_configure)

    # Scroll con rueda del mouse
    def _on_mousewheel(event):
        if event.delta:
            canvas_main.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            if event.num == 5:
                canvas_main.yview_scroll(1, "units")
            elif event.num == 4:
                canvas_main.yview_scroll(-1, "units")

    canvas_main.bind_all("<MouseWheel>", _on_mousewheel)
    canvas_main.bind_all("<Button-4>", _on_mousewheel)
    canvas_main.bind_all("<Button-5>", _on_mousewheel)

    canvas_main.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar_main.pack(side="right", fill="y")

    # ====================
    # TÍTULO Y BOTÓN VOLVER
    # ====================
    titulo_frame = ctk.CTkFrame(inner_frame, fg_color=COLOR_PRIMARY, corner_radius=10)
    titulo_frame.pack(fill="x", padx=10, pady=(10, 5))

    titulo_container = ctk.CTkFrame(titulo_frame, fg_color="transparent")
    titulo_container.pack(fill="x", padx=15, pady=12)

    ctk.CTkLabel(titulo_container, text="📊 AVANCE DE METAS - OF",
                 font=("Segoe UI", 18, "bold"), text_color="white").pack(side="left", expand=True)

    # Botón Volver
    ctk.CTkButton(titulo_container, text="← Volver", command=mostrar_dashboard_metas,
                  fg_color="#4B5563", hover_color="#374151", font=("Segoe UI", 11, "bold"),
                  width=100, height=32).pack(side="right", padx=5)

    # Variables para almacenar objetos del gráfico (para exportar)
    grafico_fig = {"fig": None}
    datos_exportar = {"grafico": [], "tabla": [], "tabla_auditores": [], "filtros": {}}

    # Funciones de exportación
    def exportar_grafico_imagen():
        """Exporta el gráfico como imagen PNG"""
        try:
            if grafico_fig["fig"] is None:
                messagebox.showwarning("Sin gráfico", "No hay gráfico para exportar")
                return

            from tkinter import filedialog
            archivo = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Todos los archivos", "*.*")],
                title="Guardar gráfico como imagen"
            )
            if archivo:
                grafico_fig["fig"].savefig(archivo, dpi=150, bbox_inches='tight', facecolor='white')
                messagebox.showinfo("Éxito", "Gráfico exportado exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{e}")

    def exportar_tabla_auditores():
        """Exporta tabla de auditores a Excel"""
        try:
            if not datos_exportar["tabla_auditores"]:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")
                return

            from tkinter import filedialog
            import openpyxl
            from openpyxl.styles import Font, PatternFill

            archivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                title="Exportar Avance por Auditor"
            )
            if not archivo:
                return

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Avance por Auditor"

            # Encabezados
            headers = ["Auditor", "Meta Acumulada", "Recaudado", "Cumplimiento (%)"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(1, col, header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

            # Datos
            for row, dato in enumerate(datos_exportar["tabla_auditores"], 2):
                ws.cell(row, 1, dato['auditor'])
                ws.cell(row, 2, dato['meta_acumulada'])
                ws.cell(row, 3, dato['recaudado'])
                cumplimiento = (dato['recaudado'] / dato['meta_acumulada'] * 100) if dato['meta_acumulada'] > 0 else 0
                ws.cell(row, 4, cumplimiento)

            wb.save(archivo)
            messagebox.showinfo("Éxito", "Datos exportados exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{e}")

    def exportar_tabla_mensual():
        """Exporta tabla mensual a Excel"""
        try:
            if not datos_exportar["tabla"]:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")
                return

            from tkinter import filedialog
            import openpyxl
            from openpyxl.styles import Font, PatternFill

            archivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                title="Exportar Avance Mensual"
            )
            if not archivo:
                return

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Avance Mensual y Anual"

            # Encabezados
            headers = ["Mes", "Ejecutado", "Meta", "Cumplimiento Mes (%)", "Avance Anual (%)"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(1, col, header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

            # Datos
            meses_nombres = ["", "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
                            "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
            for row, dato in enumerate(datos_exportar["tabla"], 2):
                ws.cell(row, 1, meses_nombres[dato['mes']])
                ws.cell(row, 2, dato['ejecutado'])
                ws.cell(row, 3, dato['meta'])
                ws.cell(row, 4, dato['cumplimiento'])
                ws.cell(row, 5, dato['avance_anual'])

            wb.save(archivo)
            messagebox.showinfo("Éxito", "Datos exportados exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{e}")

    # Obtener año más reciente de tabla distribucion
    try:
        query_anio = """
            SELECT DISTINCT YEAR(fecha) as anio
            FROM distribucion
            WHERE tipo = 'OF'
            ORDER BY fecha DESC
            LIMIT 1
        """
        df_anio = pd.read_sql(query_anio, DB_ENGINE)
        if not df_anio.empty:
            anio_actual = df_anio['anio'].iloc[0]
        else:
            anio_actual = datetime.now().year
    except Exception:
        anio_actual = datetime.now().year

    # Variable para el año seleccionado
    anio_seleccionado = tk.IntVar(value=anio_actual)

    # ====================
    # SELECTOR DE AÑO Y FILTROS (TODO EN UNA FILA)
    # ====================
    filtros_frame = ctk.CTkFrame(inner_frame, fg_color=COLOR_BOX, corner_radius=10)
    filtros_frame.pack(fill="x", padx=10, pady=(10, 5))

    # Una sola fila con todos los filtros
    filtros_fila1 = ctk.CTkFrame(filtros_frame, fg_color="transparent")
    filtros_fila1.pack(fill="x", padx=15, pady=15)

    # Selector de Año
    ctk.CTkLabel(filtros_fila1, text="📅 Año:", font=("Segoe UI", 11, "bold"),
                 text_color=COLOR_TEXT).pack(side="left", padx=(0, 8))

    try:
        query_anios = """
            SELECT DISTINCT YEAR(fecha) as anio
            FROM distribucion
            WHERE tipo = 'OF'
            ORDER BY anio DESC
        """
        df_anios = pd.read_sql(query_anios, DB_ENGINE)
        lista_anios = df_anios['anio'].tolist() if not df_anios.empty else [anio_actual]
    except Exception:
        lista_anios = [anio_actual]

    combo_anio = ctk.CTkComboBox(filtros_fila1, values=[str(a) for a in lista_anios],
                                  width=100, height=32,
                                  font=("Segoe UI", 11), state="readonly")
    combo_anio.pack(side="left", padx=(0, 15))
    combo_anio.set(str(anio_actual))

    # Filtro de Mes con checkboxes
    ctk.CTkLabel(filtros_fila1, text="📆 Mes:", font=("Segoe UI", 11, "bold"),
                 text_color=COLOR_TEXT).pack(side="left", padx=(0, 8))

    # Variables para checkboxes de meses
    meses_nombres = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    check_mes_vars = {}
    for i in range(1, 13):
        check_mes_vars[i] = tk.IntVar(value=1)  # Todos seleccionados por defecto

    mes_button_text = tk.StringVar(value="(Todos)")
    dropdown_mes_win = {"win": None}

    btn_mes = ctk.CTkButton(filtros_fila1, textvariable=mes_button_text,
                            fg_color="#ffffff", text_color=COLOR_TEXT, border_width=2,
                            border_color=COLOR_PRIMARY, hover_color=COLOR_PANEL,
                            font=("Segoe UI", 10), width=130, height=32, anchor="w",
                            command=lambda: toggle_dropdown_mes())
    btn_mes.pack(side="left", padx=(0, 15))

    def toggle_dropdown_mes():
        """Abre/cierra dropdown de selección múltiple de meses"""
        if dropdown_mes_win["win"] is not None:
            try:
                dropdown_mes_win["win"].destroy()
            except:
                pass
            dropdown_mes_win["win"] = None
            return

        top = tk.Toplevel(filtros_fila1)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_mes_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=300, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_mes():
            """Actualiza el texto del botón según selección"""
            selected = [m for m, v in check_mes_vars.items() if v.get() == 1]

            if len(selected) == 0:
                mes_button_text.set("(Ninguno)")
            elif len(selected) == 12:
                mes_button_text.set("(Todos)")
            elif len(selected) == 1:
                mes_button_text.set(meses_nombres[selected[0] - 1])
            else:
                mes_button_text.set(f"({len(selected)} meses)")

            cargar_datos_y_actualizar()

        # Botón "Todos"
        def select_all_mes():
            for var in check_mes_vars.values():
                var.set(1)
            on_check_change_mes()

        btn_todos = ctk.CTkButton(frame_inner, text="✓ Seleccionar Todos",
                                  command=select_all_mes,
                                  fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
                                  font=("Segoe UI", 10, "bold"), height=28)
        btn_todos.pack(fill="x", padx=8, pady=(5, 2))

        # Botón "Ninguno"
        def deselect_all_mes():
            for var in check_mes_vars.values():
                var.set(0)
            on_check_change_mes()

        btn_ninguno = ctk.CTkButton(frame_inner, text="✗ Deseleccionar Todos",
                                    command=deselect_all_mes,
                                    fg_color="#6B7280", hover_color="#4B5563",
                                    font=("Segoe UI", 10, "bold"), height=28)
        btn_ninguno.pack(fill="x", padx=8, pady=(2, 5))

        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=5)

        # Checkboxes para cada mes
        for i in range(1, 13):
            cb = ctk.CTkCheckBox(frame_inner, text=meses_nombres[i-1],
                                variable=check_mes_vars[i],
                                command=on_check_change_mes,
                                font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_mes.winfo_rootx()
        y = btn_mes.winfo_rooty() + btn_mes.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_mes_win["win"] = None

        top.bind("<FocusOut>", close_dropdown)
        top.bind("<Escape>", close_dropdown)

    # Variables de filtros
    supervisor_seleccionado = tk.StringVar(value="(Todos)")
    auditor_seleccionado = tk.StringVar(value="(Todos)")

    # Filtro Supervisor (en la misma fila)
    ctk.CTkLabel(filtros_fila1, text="👤 Supervisor:", font=("Segoe UI", 11, "bold"),
                 text_color=COLOR_TEXT).pack(side="left", padx=(0, 8))

    combo_supervisor = ctk.CTkComboBox(filtros_fila1, values=["(Todos)"],
                                        variable=supervisor_seleccionado,
                                        width=160, height=32,
                                        font=("Segoe UI", 10), state="readonly")
    combo_supervisor.pack(side="left", padx=(0, 15))

    # Filtro Auditor (en la misma fila)
    ctk.CTkLabel(filtros_fila1, text="👨‍💼 Auditor:", font=("Segoe UI", 11, "bold"),
                 text_color=COLOR_TEXT).pack(side="left", padx=(0, 8))

    combo_auditor = ctk.CTkComboBox(filtros_fila1, values=["(Todos)"],
                                     variable=auditor_seleccionado,
                                     width=180, height=32,
                                     font=("Segoe UI", 10), state="readonly")
    combo_auditor.pack(side="left", padx=(0, 10))

    # Frame para gráfico
    grafico_frame = ctk.CTkFrame(inner_frame, fg_color=COLOR_WHITE, corner_radius=10)
    grafico_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))

    # Frame para tabla
    tabla_frame = ctk.CTkFrame(inner_frame, fg_color=COLOR_WHITE, corner_radius=10)
    tabla_frame.pack(fill="x", padx=10, pady=(5, 10))

    def cargar_supervisores_auditores():
        """Carga opciones de supervisores y auditores para los filtros - OPTIMIZADO"""
        try:
            anio = int(combo_anio.get())
        except:
            anio = anio_actual

        try:
            # Obtener supervisores desde fiscalizaciones1 (query optimizada)
            query_supervisores = """
                SELECT DISTINCT NOMBRE_SUPERVISOR
                FROM fiscalizaciones1
                WHERE Anio_Emis = (SELECT MAX(Anio_Emis) FROM fiscalizaciones1)
                  AND Mes_Emis = (
                      SELECT MAX(Mes_Emis)
                      FROM fiscalizaciones1
                      WHERE Anio_Emis = (SELECT MAX(Anio_Emis) FROM fiscalizaciones1)
                  )
                  AND NOMBRE_SUPERVISOR IS NOT NULL
                ORDER BY NOMBRE_SUPERVISOR
                LIMIT 100
            """
            df_supervisores = pd.read_sql(query_supervisores, DB_ENGINE)
            lista_supervisores = ["(Todos)"] + df_supervisores['NOMBRE_SUPERVISOR'].tolist()
            combo_supervisor.configure(values=lista_supervisores)

            # Obtener auditores desde tabla distribucion (query optimizada)
            query_auditores = """
                SELECT DISTINCT nombre_auditor
                FROM distribucion
                WHERE tipo = 'OF' AND YEAR(fecha) = %s
                ORDER BY nombre_auditor
                LIMIT 100
            """
            df_auditores = pd.read_sql(query_auditores, DB_ENGINE, params=(anio,))
            lista_auditores = ["(Todos)"] + df_auditores['nombre_auditor'].tolist()
            combo_auditor.configure(values=lista_auditores)

        except Exception as e:
            print(f"Error cargando filtros: {e}")

    def cargar_datos_y_actualizar():
        """Carga datos y actualiza gráfico y tabla según filtros"""
        try:
            anio = int(combo_anio.get())
        except:
            anio = anio_actual

        supervisor_filtro = supervisor_seleccionado.get()
        auditor_filtro = auditor_seleccionado.get()

        # Obtener meses seleccionados del filtro
        meses_seleccionados = [m for m, v in check_mes_vars.items() if v.get() == 1]
        if not meses_seleccionados:
            messagebox.showwarning("Sin filtro", "Debe seleccionar al menos un mes")
            return

        # Mes más alto seleccionado (para calcular meta acumulada)
        mes_maximo = max(meses_seleccionados)

        try:
            # 1. Obtener mapeo supervisor → auditor desde fiscalizaciones1 y fiscalizaciones2
            query_max_fecha = """
                SELECT MAX(Anio_Emis) as max_anio, MAX(Mes_Emis) as max_mes
                FROM fiscalizaciones1
                WHERE Anio_Emis = (SELECT MAX(Anio_Emis) FROM fiscalizaciones1)
            """
            df_max = pd.read_sql(query_max_fecha, DB_ENGINE)
            max_anio = df_max['max_anio'].iloc[0] if not df_max.empty else anio
            max_mes = df_max['max_mes'].iloc[0] if not df_max.empty else 12

            # Obtener relación supervisor → REG_AUDITOR desde fiscalizaciones1
            query_sup_aud = """
                SELECT DISTINCT f1.NOMBRE_SUPERVISOR, f1.REG_AUDITOR, f2.des_func
                FROM fiscalizaciones1 f1
                LEFT JOIN fiscalizaciones2 f2 ON f1.REG_AUDITOR = f2.COD_REG_AC
                WHERE f1.Anio_Emis = %s AND f1.Mes_Emis = %s
                  AND f1.NOMBRE_SUPERVISOR IS NOT NULL
                  AND f2.des_func IS NOT NULL
            """
            df_sup_aud = pd.read_sql(query_sup_aud, DB_ENGINE, params=(max_anio, max_mes))

            # 2. Obtener metas de la tabla distribucion (usar monto_asignado)
            query_metas = """
                SELECT nombre_auditor, monto_asignado
                FROM distribucion
                WHERE tipo = 'OF' AND YEAR(fecha) = %s
            """
            df_metas = pd.read_sql(query_metas, DB_ENGINE, params=(anio,))

            if df_metas.empty:
                messagebox.showwarning("Sin datos", f"No hay metas registradas para el año {anio}")
                return

            # 3. Aplicar filtro de supervisor
            if supervisor_filtro != "(Todos)":
                # Obtener auditores del supervisor seleccionado
                auditores_filtrados = df_sup_aud[
                    df_sup_aud['NOMBRE_SUPERVISOR'] == supervisor_filtro
                ]['des_func'].unique().tolist()
                df_metas = df_metas[df_metas['nombre_auditor'].isin(auditores_filtrados)]

            # 4. Aplicar filtro de auditor
            if auditor_filtro != "(Todos)":
                df_metas = df_metas[df_metas['nombre_auditor'] == auditor_filtro]

            if df_metas.empty:
                messagebox.showwarning("Sin datos", "No hay datos para los filtros seleccionados")
                actualizar_grafico([], grafico_frame, mes_maximo)
                actualizar_tabla([], tabla_frame)
                return

            # 5. Obtener datos de recaudación (tabla OF) - PRIMERO SIN FILTRO para encontrar último mes con datos
            lista_auditores_filtrados = df_metas['nombre_auditor'].tolist()

            if len(lista_auditores_filtrados) == 0:
                df_of_completo = pd.DataFrame()
                mes_real_con_datos = 1
            else:
                # Query SIN filtro de meses para encontrar el último mes con datos
                placeholders_auditores = ','.join(['%s'] * len(lista_auditores_filtrados))
                query_of_completo = f"""
                    SELECT des_func, MES, SUM(MTO_PAG) as monto
                    FROM fiscalizaciones2
                    WHERE des_func IN ({placeholders_auditores})
                      AND MES BETWEEN 1 AND 12
                    GROUP BY des_func, MES
                """
                df_of_completo = pd.read_sql(query_of_completo, DB_ENGINE, params=tuple(lista_auditores_filtrados))

                # Buscar el último mes que tenga al menos un valor diferente a 0
                # ESTA ES LA CONDICIÓN PRIORITARIA para determinar la meta
                if df_of_completo.empty:
                    mes_real_con_datos = 1
                else:
                    pivot_of_completo = df_of_completo.pivot_table(index='des_func', columns='MES', values='monto',
                                                                     aggfunc='sum', fill_value=0)

                    # Buscar última columna (mes) con algún valor != 0
                    mes_real_con_datos = 1
                    for mes in range(12, 0, -1):
                        if mes in pivot_of_completo.columns and pivot_of_completo[mes].sum() > 0:
                            mes_real_con_datos = mes
                            break

            # 6. Ahora obtener datos filtrados por meses seleccionados (solo para visualización)
            if len(lista_auditores_filtrados) == 0:
                df_of = pd.DataFrame()
            else:
                # Query con filtro de meses seleccionados para visualización
                placeholders_auditores = ','.join(['%s'] * len(lista_auditores_filtrados))
                placeholders_meses = ','.join(['%s'] * len(meses_seleccionados))
                query_of = f"""
                    SELECT des_func, MES, SUM(MTO_PAG) as monto
                    FROM fiscalizaciones2
                    WHERE des_func IN ({placeholders_auditores})
                      AND MES IN ({placeholders_meses})
                    GROUP BY des_func, MES
                """
                params = tuple(lista_auditores_filtrados) + tuple(meses_seleccionados)
                df_of = pd.read_sql(query_of, DB_ENGINE, params=params)

            # 7. Crear pivot con datos filtrados para visualización
            if df_of.empty:
                pivot_of = pd.DataFrame()
            else:
                pivot_of = df_of.pivot_table(index='des_func', columns='MES', values='monto',
                                              aggfunc='sum', fill_value=0)

            # 8. Calcular avance por auditor usando monto_asignado
            datos_grafico = []

            for idx, row in df_metas.iterrows():
                auditor = row['nombre_auditor']
                monto_asignado = row['monto_asignado']

                # Meta mensual: monto_asignado / 12
                meta_mensual = monto_asignado / 12

                # Meta acumulada hasta el MES REAL CON DATOS (no el filtro)
                # Esta es la meta calculada según el último mes con valores != 0 en la tabla OF
                meta_acumulada = meta_mensual * mes_real_con_datos

                # Obtener recaudado de los meses seleccionados (para visualización)
                if not pivot_of.empty and auditor in pivot_of.index:
                    recaudado = 0
                    for m in meses_seleccionados:
                        if m in pivot_of.columns:
                            recaudado += pivot_of.loc[auditor, m]
                else:
                    recaudado = 0

                datos_grafico.append({
                    'auditor': auditor,
                    'recaudado': recaudado,
                    'meta_acumulada': meta_acumulada,
                    'meta_mensual': meta_mensual
                })

            # 9. Generar tabla mensual hasta el mes con datos reales
            # La tabla muestra TODOS los meses desde enero hasta mes_real_con_datos
            # (independiente del filtro de mes, que solo afecta al gráfico)
            # LÓGICA:
            # - Meta: meta_global_anual / 12 (igual para cada mes)
            # - Ejecutado: suma de columna del mes en tabla OF
            # - Cumplimiento Mes: ejecutado_mes / meta_mes * 100
            # - Avance Anual: ejecutado_acumulado / meta_anual * 100

            datos_tabla = []
            meta_global_anual = df_metas['monto_asignado'].sum()
            meta_mensual_global = meta_global_anual / 12  # Meta por mes (sin acumular)

            ejecutado_acumulado_total = 0  # Para calcular avance anual

            # Iterar desde enero hasta el mes con datos reales (no usar filtro de mes)
            for mes in range(1, mes_real_con_datos + 1):
                # Ejecutado del mes: suma de la columna del mes en la tabla OF
                ejecutado_mes = 0

                if not pivot_of_completo.empty:
                    # Usar pivot_of_completo (sin filtro de meses) para obtener datos reales
                    if mes in pivot_of_completo.columns:
                        ejecutado_mes = pivot_of_completo[mes].sum()

                # Acumular para avance anual
                ejecutado_acumulado_total += ejecutado_mes

                # Cumplimiento del mes: ejecutado_mes vs meta_mensual
                cumplimiento_mes = (ejecutado_mes / meta_mensual_global * 100) if meta_mensual_global > 0 else 0

                # Avance anual: ejecutado acumulado vs meta anual
                avance_anual = (ejecutado_acumulado_total / meta_global_anual * 100) if meta_global_anual > 0 else 0

                datos_tabla.append({
                    'mes': mes,
                    'ejecutado': ejecutado_mes,  # Solo del mes, no acumulado
                    'meta': meta_mensual_global,  # Meta mensual (no acumulada)
                    'cumplimiento': cumplimiento_mes,
                    'avance_anual': avance_anual
                })

            # Guardar información de filtros para exportación
            datos_exportar["filtros"] = {
                "Año": anio,
                "Supervisor": supervisor_filtro,
                "Auditor": auditor_filtro,
                "Meses seleccionados": mes_button_text.get(),
                "Mes con datos reales": meses_nombres[mes_real_con_datos - 1] if mes_real_con_datos <= 12 else "DIC"
            }

            # Guardar datos de tabla para exportación
            datos_exportar["tabla"] = datos_tabla

            # Actualizar gráfico pasando el MES REAL CON DATOS para el título dinámico
            actualizar_grafico(datos_grafico, grafico_frame, mes_real_con_datos)

            # Actualizar tabla
            actualizar_tabla(datos_tabla, tabla_frame)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos:\n{e}")

    def actualizar_grafico(datos, parent, mes_hasta=12):
        """Genera gráfico de barras horizontal con cifras visibles"""
        for widget in parent.winfo_children():
            widget.destroy()

        if not datos:
            ctk.CTkLabel(parent, text="No hay datos para mostrar",
                        font=("Segoe UI", 14), text_color=COLOR_TEXT).pack(pady=20)
            return

        # Crear contenedor con dos columnas
        main_container = ctk.CTkFrame(parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Columna izquierda: Gráfico
        grafico_container = ctk.CTkFrame(main_container, fg_color=COLOR_WHITE)
        grafico_container.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Header del gráfico con botón de exportación
        grafico_header = ctk.CTkFrame(grafico_container, fg_color="transparent")
        grafico_header.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(grafico_header, text="", font=("Segoe UI", 10)).pack(side="left", expand=True)

        # Botón pequeño y sutil para exportar gráfico
        btn_export_graf = ctk.CTkButton(grafico_header, text="📷",
                                        command=exportar_grafico_imagen,
                                        fg_color="#059669", hover_color="#047857",
                                        width=30, height=24, corner_radius=5,
                                        font=("Segoe UI", 12))
        btn_export_graf.pack(side="right")

        # Columna derecha: Tabla de auditores
        tabla_auditores_container = ctk.CTkFrame(main_container, fg_color=COLOR_WHITE, width=450)
        tabla_auditores_container.pack(side="right", fill="y", padx=(10, 0))
        tabla_auditores_container.pack_propagate(False)

        # === GRÁFICO ===
        fig, ax = plt.subplots(figsize=(8, max(4, len(datos) * 0.5)), dpi=80)

        auditores = [d['auditor'] for d in datos]
        recaudado = [d['recaudado'] for d in datos]
        meta = [d['meta_acumulada'] for d in datos]

        y_pos = range(len(auditores))

        # Calcular colores según cumplimiento
        colores_barras = []
        for i in range(len(auditores)):
            cumplimiento = (recaudado[i] / meta[i] * 100) if meta[i] > 0 else 0
            if cumplimiento >= 100:
                colores_barras.append('#10B981')  # Verde - Cumplió o superó
            elif cumplimiento >= 50:
                colores_barras.append('#F59E0B')  # Amarillo - Cerca
            else:
                colores_barras.append('#EF4444')  # Rojo - Muy por debajo

        # Barras horizontales con colores condicionales
        bars_meta = ax.barh(y_pos, meta, color='#E5E7EB', label='Meta Acumulada', height=0.4, alpha=0.7)
        bars_recaudado = ax.barh(y_pos, recaudado, color=colores_barras, height=0.4)

        # Añadir cifras en las barras con fondo
        for i, (bar_meta, bar_rec) in enumerate(zip(bars_meta, bars_recaudado)):
            cumplimiento = (recaudado[i] / meta[i] * 100) if meta[i] > 0 else 0

            # Cifra de meta (al final de la barra gris) con fondo blanco
            if meta[i] > 0:
                # Calcular posición para la etiqueta de meta
                pos_x_meta = min(meta[i], max(meta) * 1.05)  # Limitar posición
                ax.text(pos_x_meta, bar_meta.get_y() + bar_meta.get_height()/2,
                       f' S/ {meta[i]:,.0f} ',
                       ha='left', va='center', fontsize=7, color='#374151', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#D1D5DB', linewidth=1))

            # Cifra de recaudado con color según cumplimiento
            if recaudado[i] > 0:
                # Determinar colores del texto según cumplimiento
                if cumplimiento >= 100:
                    color_texto = '#065F46'  # Verde oscuro
                    color_fondo = '#D1FAE5'  # Verde claro
                    color_borde = '#10B981'  # Verde
                elif cumplimiento >= 50:
                    color_texto = '#92400E'  # Amarillo oscuro
                    color_fondo = '#FEF3C7'  # Amarillo claro
                    color_borde = '#F59E0B'  # Amarillo
                else:
                    color_texto = '#991B1B'  # Rojo oscuro
                    color_fondo = '#FEE2E2'  # Rojo claro
                    color_borde = '#EF4444'  # Rojo

                texto_recaudado = f' S/ {recaudado[i]:,.0f} ({cumplimiento:.1f}%) '
                # Calcular posición para evitar que se salga
                pos_x_rec = min(recaudado[i], max(meta) * 1.05)
                ax.text(pos_x_rec, bar_rec.get_y() + bar_rec.get_height()/2,
                       texto_recaudado,
                       ha='left', va='center', fontsize=7, color=color_texto, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=color_fondo, edgecolor=color_borde, linewidth=1.5))

        ax.set_yticks(y_pos)
        ax.set_yticklabels(auditores, fontsize=9, fontweight='normal')  # Aumentado tamaño de fuente
        ax.set_xlabel('Monto (S/)', fontsize=9, fontweight='bold')

        # Título dinámico con el mes
        mes_nombre = meses_nombres[mes_hasta - 1] if mes_hasta <= 12 else "DIC"
        ax.set_title(f'Avance de Metas por Auditor (hasta {mes_nombre})', fontsize=11, fontweight='bold')

        # Limitar el eje X para que no se extienda demasiado
        max_meta = max(meta) if meta else 1
        max_recaudado = max(recaudado) if recaudado else 1
        # Limitar a máximo 110% de la meta más alta para evitar que se salga
        limite_x = max(max_meta * 1.10, min(max_recaudado * 1.05, max_meta * 1.15))
        ax.set_xlim(0, limite_x)

        # Leyenda personalizada con los colores
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#E5E7EB', label='Meta Acumulada'),
            Patch(facecolor='#10B981', label='≥100% (Cumplió)'),
            Patch(facecolor='#F59E0B', label='50-99% (Cerca)'),
            Patch(facecolor='#EF4444', label='<50% (Por debajo)')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=7)
        ax.grid(axis='x', alpha=0.3, linewidth=0.5)

        plt.tight_layout(pad=0.5)

        # Mostrar gráfico en tkinter
        canvas_grafico = FigureCanvasTkAgg(fig, grafico_container)
        canvas_grafico.draw()
        canvas_grafico.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # Tooltip con Toplevel de tkinter que se superpone a todo
        tooltip_window = None

        def mostrar_tooltip(event):
            nonlocal tooltip_window

            if event.inaxes == ax:
                for i, (bar_r, bar_m) in enumerate(zip(bars_recaudado, bars_meta)):
                    cont_r, _ = bar_r.contains(event)
                    cont_m, _ = bar_m.contains(event)

                    if cont_r or cont_m:
                        cumplimiento = (recaudado[i] / meta[i] * 100) if meta[i] > 0 else 0
                        texto = f"{auditores[i]}\n\n"
                        texto += f"Meta: S/ {meta[i]:,.2f}\n"
                        texto += f"Recaudado: S/ {recaudado[i]:,.2f}\n"
                        texto += f"Cumplimiento: {cumplimiento:.1f}%"

                        # Obtener coordenadas del mouse en pantalla
                        try:
                            x_root = event.guiEvent.x_root
                            y_root = event.guiEvent.y_root
                        except:
                            x_root = canvas_grafico.get_tk_widget().winfo_pointerx()
                            y_root = canvas_grafico.get_tk_widget().winfo_pointery()

                        # Destruir tooltip anterior si existe
                        if tooltip_window is not None:
                            tooltip_window.destroy()

                        # Crear tooltip nuevo
                        tooltip_window = tk.Toplevel()
                        tooltip_window.wm_overrideredirect(True)
                        tooltip_window.attributes('-topmost', True)

                        # Contenedor principal
                        main_container = tk.Frame(tooltip_window, bg="transparent")
                        main_container.pack()

                        # Determinar posición del auditor
                        total_auditores = len(auditores)
                        posicion_relativa = i / total_auditores if total_auditores > 0 else 0

                        # Flecha ARRIBA (si tooltip está abajo - primeros auditores)
                        if posicion_relativa < 0.3:
                            arrow_canvas = tk.Canvas(main_container, width=20, height=10,
                                                    bg="transparent", highlightthickness=0)
                            arrow_canvas.pack()
                            # Triángulo apuntando arriba: pico arriba, base abajo
                            arrow_canvas.create_polygon(10, 0, 0, 10, 20, 10,
                                                       fill="#1E40AF", outline="#1E40AF")

                        # Frame del tooltip
                        tooltip_frame = tk.Frame(main_container, bg="transparent")
                        tooltip_frame.pack()

                        # Frame exterior con borde
                        outer_frame = tk.Frame(tooltip_frame, bg="#1E40AF", bd=0)
                        outer_frame.pack(padx=2, pady=2)

                        # Frame interior
                        inner_frame = tk.Frame(outer_frame, bg="#1E3A8A", bd=0)
                        inner_frame.pack(padx=2, pady=2)

                        # Label con texto
                        label = tk.Label(inner_frame, text=texto, bg="#1E3A8A", fg="white",
                                       font=("Segoe UI", 10, "bold"), justify="left",
                                       padx=16, pady=12, relief="flat")
                        label.pack()

                        # Flecha ABAJO (si tooltip está arriba - centro y últimos auditores)
                        if posicion_relativa >= 0.3:
                            arrow_canvas = tk.Canvas(main_container, width=20, height=10,
                                                    bg="transparent", highlightthickness=0)
                            arrow_canvas.pack()
                            # Triángulo apuntando abajo: base arriba, pico abajo
                            arrow_canvas.create_polygon(0, 0, 20, 0, 10, 10,
                                                       fill="#1E40AF", outline="#1E40AF")

                        # Posicionar tooltip
                        if posicion_relativa < 0.3:
                            y_offset = 15
                        elif posicion_relativa > 0.7:
                            y_offset = -100
                        else:
                            y_offset = -50

                        tooltip_window.wm_geometry(f"+{x_root + 15}+{y_root + y_offset}")
                        return

            # Ocultar tooltip si no está sobre ninguna barra
            ocultar_tooltip()

        def ocultar_tooltip(event=None):
            nonlocal tooltip_window
            if tooltip_window is not None:
                tooltip_window.destroy()
                tooltip_window = None

        fig.canvas.mpl_connect("motion_notify_event", mostrar_tooltip)
        fig.canvas.mpl_connect("axes_leave_event", ocultar_tooltip)

        # CRÍTICO: Ocultar tooltip al cambiar de aplicación o perder foco
        canvas_widget = canvas_grafico.get_tk_widget()
        canvas_widget.bind("<Leave>", ocultar_tooltip)
        canvas_widget.bind("<FocusOut>", ocultar_tooltip)

        # Ocultar cuando la ventana principal pierde el foco
        root_window = canvas_widget.winfo_toplevel()
        root_window.bind("<FocusOut>", ocultar_tooltip, add="+")
        root_window.bind("<Unmap>", ocultar_tooltip, add="+")

        # Guardar figura para exportación (NO cerrarla)
        grafico_fig["fig"] = fig
        datos_exportar["grafico"] = datos
        datos_exportar["tabla_auditores"] = datos  # Guardar también para exportar tabla

        # === TABLA DE AUDITORES ===
        # Header con título y botón de exportación
        tabla_aud_header = ctk.CTkFrame(tabla_auditores_container, fg_color="transparent")
        tabla_aud_header.pack(fill="x", padx=10, pady=(10, 5))

        # Título dinámico con el mes
        mes_nombre = meses_nombres[mes_hasta - 1] if mes_hasta <= 12 else "DIC"
        titulo_tabla = f"📊 AVANCE POR AUDITOR\n(hasta {mes_nombre})"
        ctk.CTkLabel(tabla_aud_header, text=titulo_tabla,
                    font=("Segoe UI", 11, "bold"), text_color=COLOR_PRIMARY,
                    justify="center").pack(side="top", expand=True)

        # Botón pequeño para exportar tabla de auditores
        btn_export_aud = ctk.CTkButton(tabla_aud_header, text="📊",
                                       command=exportar_tabla_auditores,
                                       fg_color="#10B981", hover_color="#059669",
                                       width=30, height=24, corner_radius=5,
                                       font=("Segoe UI", 12))
        btn_export_aud.pack(side="top", pady=(5, 0))

        # Canvas con scroll para la tabla
        canvas_tabla = tk.Canvas(tabla_auditores_container, bg=COLOR_WHITE, highlightthickness=0)
        scrollbar_tabla = ctk.CTkScrollbar(tabla_auditores_container, orientation="vertical",
                                           command=canvas_tabla.yview)
        canvas_tabla.configure(yscrollcommand=scrollbar_tabla.set)

        tabla_frame = ctk.CTkFrame(canvas_tabla, fg_color=COLOR_WHITE)
        canvas_window_tabla = canvas_tabla.create_window((0, 0), window=tabla_frame, anchor="nw")

        def _on_tabla_configure(event=None):
            canvas_tabla.configure(scrollregion=canvas_tabla.bbox("all"))
            if canvas_tabla.winfo_width() > 1:
                canvas_tabla.itemconfig(canvas_window_tabla, width=canvas_tabla.winfo_width())

        tabla_frame.bind("<Configure>", _on_tabla_configure)

        # Encabezados de tabla
        headers = ["Auditor", "Meta", "Recaudado", "Cumplimiento"]
        header_frame = ctk.CTkFrame(tabla_frame, fg_color=COLOR_PRIMARY, corner_radius=5)
        header_frame.pack(fill="x", padx=2, pady=2)

        widths = [180, 80, 80, 80]
        for i, (header, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(header_frame, text=header, font=("Segoe UI", 9, "bold"),
                        text_color="white", width=width).grid(row=0, column=i, padx=1, pady=5)

        # Filas de datos
        for idx, dato in enumerate(datos):
            bg = "#F9FAFB" if idx % 2 == 0 else COLOR_WHITE
            row_frame = ctk.CTkFrame(tabla_frame, fg_color=bg, corner_radius=3)
            row_frame.pack(fill="x", padx=2, pady=1)

            cumplimiento = (dato['recaudado'] / dato['meta_acumulada'] * 100) if dato['meta_acumulada'] > 0 else 0

            # Color del cumplimiento
            if cumplimiento >= 100:
                color_cumplimiento = "#059669"  # Verde
            elif cumplimiento >= 75:
                color_cumplimiento = "#F59E0B"  # Amarillo
            else:
                color_cumplimiento = "#DC2626"  # Rojo

            valores = [
                dato['auditor'][:25] + "..." if len(dato['auditor']) > 25 else dato['auditor'],
                f"S/ {dato['meta_acumulada']:,.0f}",
                f"S/ {dato['recaudado']:,.0f}",
                f"{cumplimiento:.1f}%"
            ]

            for i, (valor, width) in enumerate(zip(valores, widths)):
                color_texto = color_cumplimiento if i == 3 else COLOR_TEXT
                ctk.CTkLabel(row_frame, text=valor, font=("Segoe UI", 8),
                            text_color=color_texto, width=width,
                            anchor="w" if i == 0 else "center").grid(row=0, column=i, padx=1, pady=3)

        scrollbar_tabla.pack(side="right", fill="y")
        canvas_tabla.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def actualizar_tabla(datos, parent):
        """Genera tabla de avance mensual y anual"""
        for widget in parent.winfo_children():
            widget.destroy()

        if not datos:
            return

        # Header con título y botón de exportación
        tabla_mens_header = ctk.CTkFrame(parent, fg_color="transparent")
        tabla_mens_header.pack(fill="x", padx=10, pady=(10, 0))

        # Título
        ctk.CTkLabel(tabla_mens_header, text="📈 AVANCE MENSUAL Y ANUAL",
                    font=("Segoe UI", 14, "bold"), text_color=COLOR_PRIMARY).pack(side="left")

        # Botón pequeño para exportar tabla mensual
        btn_export_mens = ctk.CTkButton(tabla_mens_header, text="📊",
                                       command=exportar_tabla_mensual,
                                       fg_color="#10B981", hover_color="#059669",
                                       width=30, height=24, corner_radius=5,
                                       font=("Segoe UI", 12))
        btn_export_mens.pack(side="right")

        # Contenedor centrado para la tabla
        tabla_outer = ctk.CTkFrame(parent, fg_color="transparent")
        tabla_outer.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Crear tabla centrada con ancho máximo
        tabla_container = ctk.CTkFrame(tabla_outer, fg_color=COLOR_WHITE)
        tabla_container.pack(anchor="center", padx=10, pady=(0, 10))

        # Encabezados
        headers = ["Mes", "Ejecutado", "Meta", "Cumplimiento Mes", "Avance Anual"]
        header_frame = ctk.CTkFrame(tabla_container, fg_color=COLOR_PRIMARY, corner_radius=5)
        header_frame.pack(fill="x", padx=2, pady=2)

        for i, header in enumerate(headers):
            ctk.CTkLabel(header_frame, text=header, font=("Segoe UI", 10, "bold"),
                        text_color="white", width=150).grid(row=0, column=i, padx=2, pady=5)

        meses_nombres = ["", "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
                        "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]

        # Filas de datos
        for idx, dato in enumerate(datos):
            bg = "#F9FAFB" if idx % 2 == 0 else COLOR_WHITE
            row_frame = ctk.CTkFrame(tabla_container, fg_color=bg, corner_radius=3)
            row_frame.pack(fill="x", padx=2, pady=1)

            valores = [
                meses_nombres[dato['mes']],
                f"S/ {dato['ejecutado']:,.2f}",
                f"S/ {dato['meta']:,.2f}",
                f"{dato['cumplimiento']:.1f}%",
                f"{dato['avance_anual']:.1f}%"
            ]

            for i, valor in enumerate(valores):
                ctk.CTkLabel(row_frame, text=valor, font=("Segoe UI", 9),
                            text_color=COLOR_TEXT, width=150).grid(row=0, column=i, padx=2, pady=3)

    # Cargar datos iniciales inmediatamente (sin esperar filtros)
    cargar_datos_y_actualizar()

    # Cargar filtros de forma asíncrona después de 100ms (lazy loading)
    dashboard_frame.after(100, cargar_supervisores_auditores)

    # Vincular cambios de filtros
    combo_anio.configure(command=lambda x: (cargar_supervisores_auditores(), cargar_datos_y_actualizar()))
    combo_supervisor.configure(command=lambda x: cargar_datos_y_actualizar())
    combo_auditor.configure(command=lambda x: cargar_datos_y_actualizar())

# ==========================
# DASHBOARD AVANCE DE METAS AI
# ==========================

# ==========================
# DASHBOARD AVANCE DE METAS AI
# ==========================
def dashboard_avance_metas_ai():
    """
    Dashboard para mostrar el avance de metas AI con:
    - Selector de año (automático desde tabla distribucion)
    - Filtros: Supervisor y Auditor
    - Gráfico de barras horizontal con avance de metas
    - Tabla de avance mensual y anual
    """
    try:
        preview_frame.pack_forget()
    except Exception:
        pass

    dashboard_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))

    for widget in dashboard_frame.winfo_children():
        widget.destroy()

    # Canvas principal con scroll - RESPONSIVO
    canvas_main = tk.Canvas(dashboard_frame, bg=COLOR_WHITE, highlightthickness=0)
    scrollbar_main = ctk.CTkScrollbar(dashboard_frame, orientation="vertical", command=canvas_main.yview)
    canvas_main.configure(yscrollcommand=scrollbar_main.set)

    inner_frame = ctk.CTkFrame(canvas_main, fg_color=COLOR_WHITE)
    canvas_window = canvas_main.create_window((0, 0), window=inner_frame, anchor="nw")

    def _on_frame_configure(event=None):
        """Configurar scroll y responsividad del canvas"""
        canvas_main.configure(scrollregion=canvas_main.bbox("all"))
        # Hacer que el inner_frame se expanda con la ventana
        if canvas_main.winfo_width() > 1:
            canvas_main.itemconfig(canvas_window, width=canvas_main.winfo_width())

    def _on_canvas_configure(event=None):
        """Ajustar tamaño del inner_frame cuando cambia el canvas"""
        if event and event.width > 1:
            canvas_main.itemconfig(canvas_window, width=event.width)

    inner_frame.bind("<Configure>", _on_frame_configure)
    canvas_main.bind("<Configure>", _on_canvas_configure)

    # Scroll con rueda del mouse
    def _on_mousewheel(event):
        if event.delta:
            canvas_main.yview_scroll(int(-1*(event.delta/120)), "units")
        else:
            if event.num == 5:
                canvas_main.yview_scroll(1, "units")
            elif event.num == 4:
                canvas_main.yview_scroll(-1, "units")

    canvas_main.bind_all("<MouseWheel>", _on_mousewheel)
    canvas_main.bind_all("<Button-4>", _on_mousewheel)
    canvas_main.bind_all("<Button-5>", _on_mousewheel)

    canvas_main.pack(side="left", fill="both", expand=True, padx=10, pady=10)
    scrollbar_main.pack(side="right", fill="y")

    # ====================
    # TÍTULO Y BOTÓN VOLVER
    # ====================
    titulo_frame = ctk.CTkFrame(inner_frame, fg_color=COLOR_PRIMARY, corner_radius=10)
    titulo_frame.pack(fill="x", padx=10, pady=(10, 5))

    titulo_container = ctk.CTkFrame(titulo_frame, fg_color="transparent")
    titulo_container.pack(fill="x", padx=15, pady=12)

    ctk.CTkLabel(titulo_container, text="📊 AVANCE DE METAS - AI",
                 font=("Segoe UI", 18, "bold"), text_color="white").pack(side="left", expand=True)

    # Botón Volver
    ctk.CTkButton(titulo_container, text="← Volver", command=mostrar_dashboard_metas,
                  fg_color="#4B5563", hover_color="#374151", font=("Segoe UI", 11, "bold"),
                  width=100, height=32).pack(side="right", padx=5)

    # Variables para almacenar objetos del gráfico (para exportar)
    grafico_fig = {"fig": None}
    datos_exportar = {"grafico": [], "tabla": [], "tabla_auditores": [], "filtros": {}}

    # Funciones de exportación
    def exportar_grafico_imagen():
        """Exporta el gráfico como imagen PNG"""
        try:
            if grafico_fig["fig"] is None:
                messagebox.showwarning("Sin gráfico", "No hay gráfico para exportar")
                return

            from tkinter import filedialog
            archivo = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg"), ("Todos los archivos", "*.*")],
                title="Guardar gráfico como imagen"
            )
            if archivo:
                grafico_fig["fig"].savefig(archivo, dpi=150, bbox_inches='tight', facecolor='white')
                messagebox.showinfo("Éxito", "Gráfico exportado exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{e}")

    def exportar_tabla_auditores():
        """Exporta tabla de auditores a Excel"""
        try:
            if not datos_exportar["tabla_auditores"]:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")
                return

            from tkinter import filedialog
            import openpyxl
            from openpyxl.styles import Font, PatternFill

            archivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                title="Exportar Avance por Auditor"
            )
            if not archivo:
                return

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Avance por Auditor"

            # Encabezados
            headers = ["Auditor", "Meta Acumulada", "Recaudado", "Cumplimiento (%)"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(1, col, header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

            # Datos
            for row, dato in enumerate(datos_exportar["tabla_auditores"], 2):
                ws.cell(row, 1, dato['auditor'])
                ws.cell(row, 2, dato['meta_acumulada'])
                ws.cell(row, 3, dato['recaudado'])
                cumplimiento = (dato['recaudado'] / dato['meta_acumulada'] * 100) if dato['meta_acumulada'] > 0 else 0
                ws.cell(row, 4, cumplimiento)

            wb.save(archivo)
            messagebox.showinfo("Éxito", "Datos exportados exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{e}")

    def exportar_tabla_mensual():
        """Exporta tabla mensual a Excel"""
        try:
            if not datos_exportar["tabla"]:
                messagebox.showwarning("Sin datos", "No hay datos para exportar")
                return

            from tkinter import filedialog
            import openpyxl
            from openpyxl.styles import Font, PatternFill

            archivo = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx"), ("Todos los archivos", "*.*")],
                title="Exportar Avance Mensual"
            )
            if not archivo:
                return

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Avance Mensual y Anual"

            # Encabezados
            headers = ["Mes", "Ejecutado", "Meta", "Cumplimiento Mes (%)", "Avance Anual (%)"]
            for col, header in enumerate(headers, 1):
                cell = ws.cell(1, col, header)
                cell.font = Font(bold=True, color="FFFFFF")
                cell.fill = PatternFill(start_color="4472C4", end_color="4472C4", fill_type="solid")

            # Datos
            meses_nombres = ["", "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
                            "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
            for row, dato in enumerate(datos_exportar["tabla"], 2):
                ws.cell(row, 1, meses_nombres[dato['mes']])
                ws.cell(row, 2, dato['ejecutado'])
                ws.cell(row, 3, dato['meta'])
                ws.cell(row, 4, dato['cumplimiento'])
                ws.cell(row, 5, dato['avance_anual'])

            wb.save(archivo)
            messagebox.showinfo("Éxito", "Datos exportados exitosamente")
        except Exception as e:
            messagebox.showerror("Error", f"Error al exportar:\n{e}")

    # Obtener año más reciente de tabla distribucion
    try:
        query_anio = """
            SELECT DISTINCT YEAR(fecha) as anio
            FROM distribucion
            WHERE tipo = 'AI'
            ORDER BY fecha DESC
            LIMIT 1
        """
        df_anio = pd.read_sql(query_anio, DB_ENGINE)
        if not df_anio.empty:
            anio_actual = df_anio['anio'].iloc[0]
        else:
            anio_actual = datetime.now().year
    except Exception:
        anio_actual = datetime.now().year

    # Variable para el año seleccionado
    anio_seleccionado = tk.IntVar(value=anio_actual)

    # ====================
    # SELECTOR DE AÑO Y FILTROS (TODO EN UNA FILA)
    # ====================
    filtros_frame = ctk.CTkFrame(inner_frame, fg_color=COLOR_BOX, corner_radius=10)
    filtros_frame.pack(fill="x", padx=10, pady=(10, 5))

    # Una sola fila con todos los filtros
    filtros_fila1 = ctk.CTkFrame(filtros_frame, fg_color="transparent")
    filtros_fila1.pack(fill="x", padx=15, pady=15)

    # Selector de Año
    ctk.CTkLabel(filtros_fila1, text="📅 Año:", font=("Segoe UI", 11, "bold"),
                 text_color=COLOR_TEXT).pack(side="left", padx=(0, 8))

    try:
        query_anios = """
            SELECT DISTINCT YEAR(fecha) as anio
            FROM distribucion
            WHERE tipo = 'AI'
            ORDER BY anio DESC
        """
        df_anios = pd.read_sql(query_anios, DB_ENGINE)
        lista_anios = df_anios['anio'].tolist() if not df_anios.empty else [anio_actual]
    except Exception:
        lista_anios = [anio_actual]

    combo_anio = ctk.CTkComboBox(filtros_fila1, values=[str(a) for a in lista_anios],
                                  width=100, height=32,
                                  font=("Segoe UI", 11), state="readonly")
    combo_anio.pack(side="left", padx=(0, 15))
    combo_anio.set(str(anio_actual))

    # Filtro de Mes con checkboxes
    ctk.CTkLabel(filtros_fila1, text="📆 Mes:", font=("Segoe UI", 11, "bold"),
                 text_color=COLOR_TEXT).pack(side="left", padx=(0, 8))

    # Variables para checkboxes de meses
    meses_nombres = ["ENE", "FEB", "MAR", "ABR", "MAY", "JUN", "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]
    check_mes_vars = {}
    for i in range(1, 13):
        check_mes_vars[i] = tk.IntVar(value=1)  # Todos seleccionados por defecto

    mes_button_text = tk.StringVar(value="(Todos)")
    dropdown_mes_win = {"win": None}

    btn_mes = ctk.CTkButton(filtros_fila1, textvariable=mes_button_text,
                            fg_color="#ffffff", text_color=COLOR_TEXT, border_width=2,
                            border_color=COLOR_PRIMARY, hover_color=COLOR_PANEL,
                            font=("Segoe UI", 10), width=130, height=32, anchor="w",
                            command=lambda: toggle_dropdown_mes())
    btn_mes.pack(side="left", padx=(0, 15))

    def toggle_dropdown_mes():
        """Abre/cierra dropdown de selección múltiple de meses"""
        if dropdown_mes_win["win"] is not None:
            try:
                dropdown_mes_win["win"].destroy()
            except:
                pass
            dropdown_mes_win["win"] = None
            return

        top = tk.Toplevel(filtros_fila1)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_mes_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=300, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_mes():
            """Actualiza el texto del botón según selección"""
            selected = [m for m, v in check_mes_vars.items() if v.get() == 1]

            if len(selected) == 0:
                mes_button_text.set("(Ninguno)")
            elif len(selected) == 12:
                mes_button_text.set("(Todos)")
            elif len(selected) == 1:
                mes_button_text.set(meses_nombres[selected[0] - 1])
            else:
                mes_button_text.set(f"({len(selected)} meses)")

            cargar_datos_y_actualizar()

        # Botón "Todos"
        def select_all_mes():
            for var in check_mes_vars.values():
                var.set(1)
            on_check_change_mes()

        btn_todos = ctk.CTkButton(frame_inner, text="✓ Seleccionar Todos",
                                  command=select_all_mes,
                                  fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
                                  font=("Segoe UI", 10, "bold"), height=28)
        btn_todos.pack(fill="x", padx=8, pady=(5, 2))

        # Botón "Ninguno"
        def deselect_all_mes():
            for var in check_mes_vars.values():
                var.set(0)
            on_check_change_mes()

        btn_ninguno = ctk.CTkButton(frame_inner, text="✗ Deseleccionar Todos",
                                    command=deselect_all_mes,
                                    fg_color="#6B7280", hover_color="#4B5563",
                                    font=("Segoe UI", 10, "bold"), height=28)
        btn_ninguno.pack(fill="x", padx=8, pady=(2, 5))

        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=5)

        # Checkboxes para cada mes
        for i in range(1, 13):
            cb = ctk.CTkCheckBox(frame_inner, text=meses_nombres[i-1],
                                variable=check_mes_vars[i],
                                command=on_check_change_mes,
                                font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_mes.winfo_rootx()
        y = btn_mes.winfo_rooty() + btn_mes.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_mes_win["win"] = None

        top.bind("<FocusOut>", close_dropdown)
        top.bind("<Escape>", close_dropdown)

    # Variables de filtros
    supervisor_seleccionado = tk.StringVar(value="(Todos)")
    auditor_seleccionado = tk.StringVar(value="(Todos)")

    # Filtro Supervisor (en la misma fila)
    ctk.CTkLabel(filtros_fila1, text="👤 Supervisor:", font=("Segoe UI", 11, "bold"),
                 text_color=COLOR_TEXT).pack(side="left", padx=(0, 8))

    combo_supervisor = ctk.CTkComboBox(filtros_fila1, values=["(Todos)"],
                                        variable=supervisor_seleccionado,
                                        width=160, height=32,
                                        font=("Segoe UI", 10), state="readonly")
    combo_supervisor.pack(side="left", padx=(0, 15))

    # Filtro Auditor (en la misma fila)
    ctk.CTkLabel(filtros_fila1, text="👨‍💼 Auditor:", font=("Segoe UI", 11, "bold"),
                 text_color=COLOR_TEXT).pack(side="left", padx=(0, 8))

    combo_auditor = ctk.CTkComboBox(filtros_fila1, values=["(Todos)"],
                                     variable=auditor_seleccionado,
                                     width=180, height=32,
                                     font=("Segoe UI", 10), state="readonly")
    combo_auditor.pack(side="left", padx=(0, 10))

    # Frame para gráfico
    grafico_frame = ctk.CTkFrame(inner_frame, fg_color=COLOR_WHITE, corner_radius=10)
    grafico_frame.pack(fill="both", expand=True, padx=10, pady=(10, 5))

    # Frame para tabla
    tabla_frame = ctk.CTkFrame(inner_frame, fg_color=COLOR_WHITE, corner_radius=10)
    tabla_frame.pack(fill="x", padx=10, pady=(5, 10))

    def cargar_supervisores_auditores():
        """Carga opciones de supervisores y auditores para los filtros - OPTIMIZADO"""
        try:
            anio = int(combo_anio.get())
        except:
            anio = anio_actual

        try:
            # Obtener supervisores desde fiscalizaciones1 (query optimizada)
            query_supervisores = """
                SELECT DISTINCT NOMBRE_SUPERVISOR
                FROM fiscalizaciones1
                WHERE Anio_Emis = (SELECT MAX(Anio_Emis) FROM fiscalizaciones1)
                  AND Mes_Emis = (
                      SELECT MAX(Mes_Emis)
                      FROM fiscalizaciones1
                      WHERE Anio_Emis = (SELECT MAX(Anio_Emis) FROM fiscalizaciones1)
                  )
                  AND NOMBRE_SUPERVISOR IS NOT NULL
                ORDER BY NOMBRE_SUPERVISOR
                LIMIT 100
            """
            df_supervisores = pd.read_sql(query_supervisores, DB_ENGINE)
            lista_supervisores = ["(Todos)"] + df_supervisores['NOMBRE_SUPERVISOR'].tolist()
            combo_supervisor.configure(values=lista_supervisores)

            # Obtener auditores desde tabla distribucion (query optimizada)
            query_auditores = """
                SELECT DISTINCT nombre_auditor
                FROM distribucion
                WHERE tipo = 'AI' AND YEAR(fecha) = %s
                ORDER BY nombre_auditor
                LIMIT 100
            """
            df_auditores = pd.read_sql(query_auditores, DB_ENGINE, params=(anio,))
            lista_auditores = ["(Todos)"] + df_auditores['nombre_auditor'].tolist()
            combo_auditor.configure(values=lista_auditores)

        except Exception as e:
            print(f"Error cargando filtros: {e}")

    def cargar_datos_y_actualizar():
        """Carga datos y actualiza gráfico y tabla según filtros"""
        try:
            anio = int(combo_anio.get())
        except:
            anio = anio_actual

        supervisor_filtro = supervisor_seleccionado.get()
        auditor_filtro = auditor_seleccionado.get()

        # Obtener meses seleccionados del filtro
        meses_seleccionados = [m for m, v in check_mes_vars.items() if v.get() == 1]
        if not meses_seleccionados:
            messagebox.showwarning("Sin filtro", "Debe seleccionar al menos un mes")
            return

        # Mes más alto seleccionado (para calcular meta acumulada)
        mes_maximo = max(meses_seleccionados)

        try:
            # 1. Obtener mapeo supervisor → auditor desde fiscalizaciones1 y fiscalizaciones5
            query_max_fecha = """
                SELECT MAX(Anio_Emis) as max_anio, MAX(Mes_Emis) as max_mes
                FROM fiscalizaciones1
                WHERE Anio_Emis = (SELECT MAX(Anio_Emis) FROM fiscalizaciones1)
            """
            df_max = pd.read_sql(query_max_fecha, DB_ENGINE)
            max_anio = df_max['max_anio'].iloc[0] if not df_max.empty else anio
            max_mes = df_max['max_mes'].iloc[0] if not df_max.empty else 12

            # Obtener relación supervisor → REG_AUDITOR desde fiscalizaciones1
            query_sup_aud = """
                SELECT DISTINCT f1.NOMBRE_SUPERVISOR, f1.REG_AUDITOR, f5.nomb_ver
                FROM fiscalizaciones1 f1
                LEFT JOIN fiscalizaciones5 f5 ON f1.REG_AUDITOR = f5.COD_REG_VE
                WHERE f1.Anio_Emis = %s AND f1.Mes_Emis = %s
                  AND f1.NOMBRE_SUPERVISOR IS NOT NULL
                  AND f5.nomb_ver IS NOT NULL
            """
            df_sup_aud = pd.read_sql(query_sup_aud, DB_ENGINE, params=(max_anio, max_mes))

            # 2. Obtener metas de la tabla distribucion (usar monto_asignado)
            query_metas = """
                SELECT nombre_auditor, monto_asignado
                FROM distribucion
                WHERE tipo = 'AI' AND YEAR(fecha) = %s
            """
            df_metas = pd.read_sql(query_metas, DB_ENGINE, params=(anio,))

            if df_metas.empty:
                messagebox.showwarning("Sin datos", f"No hay metas registradas para el año {anio}")
                return

            # 3. Aplicar filtro de supervisor
            if supervisor_filtro != "(Todos)":
                # Obtener auditores del supervisor seleccionado
                auditores_filtrados = df_sup_aud[
                    df_sup_aud['NOMBRE_SUPERVISOR'] == supervisor_filtro
                ]['nomb_ver'].unique().tolist()
                df_metas = df_metas[df_metas['nombre_auditor'].isin(auditores_filtrados)]

            # 4. Aplicar filtro de auditor
            if auditor_filtro != "(Todos)":
                df_metas = df_metas[df_metas['nombre_auditor'] == auditor_filtro]

            if df_metas.empty:
                messagebox.showwarning("Sin datos", "No hay datos para los filtros seleccionados")
                actualizar_grafico([], grafico_frame, mes_maximo)
                actualizar_tabla([], tabla_frame)
                return

            # 5. Obtener datos de recaudación (tabla AI) - PRIMERO SIN FILTRO para encontrar último mes con datos
            lista_auditores_filtrados = df_metas['nombre_auditor'].tolist()

            if len(lista_auditores_filtrados) == 0:
                df_ai_completo = pd.DataFrame()
                mes_real_con_datos = 1
            else:
                # Query SIN filtro de meses para encontrar el último mes con datos
                placeholders_auditores = ','.join(['%s'] * len(lista_auditores_filtrados))
                query_ai_completo = f"""
                    SELECT nomb_ver, MES, SUM(MTO_PAG_IN) as monto
                    FROM fiscalizaciones5
                    WHERE nomb_ver IN ({placeholders_auditores})
                      AND MES BETWEEN 1 AND 12
                    GROUP BY nomb_ver, MES
                """
                df_ai_completo = pd.read_sql(query_ai_completo, DB_ENGINE, params=tuple(lista_auditores_filtrados))

                # Buscar el último mes que tenga al menos un valor diferente a 0
                # ESTA ES LA CONDICIÓN PRIORITARIA para determinar la meta
                if df_ai_completo.empty:
                    mes_real_con_datos = 1
                else:
                    pivot_ai_completo = df_ai_completo.pivot_table(index='nomb_ver', columns='MES', values='monto',
                                                                     aggfunc='sum', fill_value=0)

                    # Buscar última columna (mes) con algún valor != 0
                    mes_real_con_datos = 1
                    for mes in range(12, 0, -1):
                        if mes in pivot_ai_completo.columns and pivot_ai_completo[mes].sum() > 0:
                            mes_real_con_datos = mes
                            break

            # 6. Ahora obtener datos filtrados por meses seleccionados (solo para visualización)
            if len(lista_auditores_filtrados) == 0:
                df_ai = pd.DataFrame()
            else:
                # Query con filtro de meses seleccionados para visualización
                placeholders_auditores = ','.join(['%s'] * len(lista_auditores_filtrados))
                placeholders_meses = ','.join(['%s'] * len(meses_seleccionados))
                query_ai = f"""
                    SELECT nomb_ver, MES, SUM(MTO_PAG_IN) as monto
                    FROM fiscalizaciones5
                    WHERE nomb_ver IN ({placeholders_auditores})
                      AND MES IN ({placeholders_meses})
                    GROUP BY nomb_ver, MES
                """
                params = tuple(lista_auditores_filtrados) + tuple(meses_seleccionados)
                df_ai = pd.read_sql(query_ai, DB_ENGINE, params=params)

            # 7. Crear pivot con datos filtrados para visualización
            if df_ai.empty:
                pivot_ai = pd.DataFrame()
            else:
                pivot_ai = df_ai.pivot_table(index='nomb_ver', columns='MES', values='monto',
                                              aggfunc='sum', fill_value=0)

            # 8. Calcular avance por auditor usando monto_asignado
            datos_grafico = []

            for idx, row in df_metas.iterrows():
                auditor = row['nombre_auditor']
                monto_asignado = row['monto_asignado']

                # Meta mensual: monto_asignado / 12
                meta_mensual = monto_asignado / 12

                # Meta acumulada hasta el MES REAL CON DATOS (no el filtro)
                # Esta es la meta calculada según el último mes con valores != 0 en la tabla AI
                meta_acumulada = meta_mensual * mes_real_con_datos

                # Obtener recaudado de los meses seleccionados (para visualización)
                if not pivot_ai.empty and auditor in pivot_ai.index:
                    recaudado = 0
                    for m in meses_seleccionados:
                        if m in pivot_ai.columns:
                            recaudado += pivot_ai.loc[auditor, m]
                else:
                    recaudado = 0

                datos_grafico.append({
                    'auditor': auditor,
                    'recaudado': recaudado,
                    'meta_acumulada': meta_acumulada,
                    'meta_mensual': meta_mensual
                })

            # 9. Generar tabla mensual hasta el mes con datos reales
            # La tabla muestra TODOS los meses desde enero hasta mes_real_con_datos
            # (independiente del filtro de mes, que solo afecta al gráfico)
            # LÓGICA:
            # - Meta: meta_global_anual / 12 (igual para cada mes)
            # - Ejecutado: suma de columna del mes en tabla AI
            # - Cumplimiento Mes: ejecutado_mes / meta_mes * 100
            # - Avance Anual: ejecutado_acumulado / meta_anual * 100

            datos_tabla = []
            meta_global_anual = df_metas['monto_asignado'].sum()
            meta_mensual_global = meta_global_anual / 12  # Meta por mes (sin acumular)

            ejecutado_acumulado_total = 0  # Para calcular avance anual

            # Iterar desde enero hasta el mes con datos reales (no usar filtro de mes)
            for mes in range(1, mes_real_con_datos + 1):
                # Ejecutado del mes: suma de la columna del mes en la tabla AI
                ejecutado_mes = 0

                if not pivot_ai_completo.empty:
                    # Usar pivot_ai_completo (sin filtro de meses) para obtener datos reales
                    if mes in pivot_ai_completo.columns:
                        ejecutado_mes = pivot_ai_completo[mes].sum()

                # Acumular para avance anual
                ejecutado_acumulado_total += ejecutado_mes

                # Cumplimiento del mes: ejecutado_mes vs meta_mensual
                cumplimiento_mes = (ejecutado_mes / meta_mensual_global * 100) if meta_mensual_global > 0 else 0

                # Avance anual: ejecutado acumulado vs meta anual
                avance_anual = (ejecutado_acumulado_total / meta_global_anual * 100) if meta_global_anual > 0 else 0

                datos_tabla.append({
                    'mes': mes,
                    'ejecutado': ejecutado_mes,  # Solo del mes, no acumulado
                    'meta': meta_mensual_global,  # Meta mensual (no acumulada)
                    'cumplimiento': cumplimiento_mes,
                    'avance_anual': avance_anual
                })

            # Guardar información de filtros para exportación
            datos_exportar["filtros"] = {
                "Año": anio,
                "Supervisor": supervisor_filtro,
                "Auditor": auditor_filtro,
                "Meses seleccionados": mes_button_text.get(),
                "Mes con datos reales": meses_nombres[mes_real_con_datos - 1] if mes_real_con_datos <= 12 else "DIC"
            }

            # Guardar datos de tabla para exportación
            datos_exportar["tabla"] = datos_tabla

            # Actualizar gráfico pasando el MES REAL CON DATOS para el título dinámico
            actualizar_grafico(datos_grafico, grafico_frame, mes_real_con_datos)

            # Actualizar tabla
            actualizar_tabla(datos_tabla, tabla_frame)

        except Exception as e:
            messagebox.showerror("Error", f"Error al cargar datos:\n{e}")

    def actualizar_grafico(datos, parent, mes_hasta=12):
        """Genera gráfico de barras horizontal con cifras visibles"""
        for widget in parent.winfo_children():
            widget.destroy()

        if not datos:
            ctk.CTkLabel(parent, text="No hay datos para mostrar",
                        font=("Segoe UI", 14), text_color=COLOR_TEXT).pack(pady=20)
            return

        # Crear contenedor con dos columnas
        main_container = ctk.CTkFrame(parent, fg_color="transparent")
        main_container.pack(fill="both", expand=True, padx=10, pady=10)

        # Columna izquierda: Gráfico
        grafico_container = ctk.CTkFrame(main_container, fg_color=COLOR_WHITE)
        grafico_container.pack(side="left", fill="both", expand=True, padx=(0, 10))

        # Header del gráfico con botón de exportación
        grafico_header = ctk.CTkFrame(grafico_container, fg_color="transparent")
        grafico_header.pack(fill="x", padx=10, pady=(10, 0))

        ctk.CTkLabel(grafico_header, text="", font=("Segoe UI", 10)).pack(side="left", expand=True)

        # Botón pequeño y sutil para exportar gráfico
        btn_export_graf = ctk.CTkButton(grafico_header, text="📷",
                                        command=exportar_grafico_imagen,
                                        fg_color="#059669", hover_color="#047857",
                                        width=30, height=24, corner_radius=5,
                                        font=("Segoe UI", 12))
        btn_export_graf.pack(side="right")

        # Columna derecha: Tabla de auditores
        tabla_auditores_container = ctk.CTkFrame(main_container, fg_color=COLOR_WHITE, width=450)
        tabla_auditores_container.pack(side="right", fill="y", padx=(10, 0))
        tabla_auditores_container.pack_propagate(False)

        # === GRÁFICO ===
        fig, ax = plt.subplots(figsize=(8, max(4, len(datos) * 0.5)), dpi=80)

        auditores = [d['auditor'] for d in datos]
        recaudado = [d['recaudado'] for d in datos]
        meta = [d['meta_acumulada'] for d in datos]

        y_pos = range(len(auditores))

        # Calcular colores según cumplimiento
        colores_barras = []
        for i in range(len(auditores)):
            cumplimiento = (recaudado[i] / meta[i] * 100) if meta[i] > 0 else 0
            if cumplimiento >= 100:
                colores_barras.append('#10B981')  # Verde - Cumplió o superó
            elif cumplimiento >= 50:
                colores_barras.append('#F59E0B')  # Amarillo - Cerca
            else:
                colores_barras.append('#EF4444')  # Rojo - Muy por debajo

        # Barras horizontales con colores condicionales
        bars_meta = ax.barh(y_pos, meta, color='#E5E7EB', label='Meta Acumulada', height=0.4, alpha=0.7)
        bars_recaudado = ax.barh(y_pos, recaudado, color=colores_barras, height=0.4)

        # Añadir cifras en las barras con fondo
        for i, (bar_meta, bar_rec) in enumerate(zip(bars_meta, bars_recaudado)):
            cumplimiento = (recaudado[i] / meta[i] * 100) if meta[i] > 0 else 0

            # Cifra de meta (al final de la barra gris) con fondo blanco
            if meta[i] > 0:
                # Calcular posición para la etiqueta de meta
                pos_x_meta = min(meta[i], max(meta) * 1.05)  # Limitar posición
                ax.text(pos_x_meta, bar_meta.get_y() + bar_meta.get_height()/2,
                       f' S/ {meta[i]:,.0f} ',
                       ha='left', va='center', fontsize=7, color='#374151', fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#D1D5DB', linewidth=1))

            # Cifra de recaudado con color según cumplimiento
            if recaudado[i] > 0:
                # Determinar colores del texto según cumplimiento
                if cumplimiento >= 100:
                    color_texto = '#065F46'  # Verde oscuro
                    color_fondo = '#D1FAE5'  # Verde claro
                    color_borde = '#10B981'  # Verde
                elif cumplimiento >= 50:
                    color_texto = '#92400E'  # Amarillo oscuro
                    color_fondo = '#FEF3C7'  # Amarillo claro
                    color_borde = '#F59E0B'  # Amarillo
                else:
                    color_texto = '#991B1B'  # Rojo oscuro
                    color_fondo = '#FEE2E2'  # Rojo claro
                    color_borde = '#EF4444'  # Rojo

                texto_recaudado = f' S/ {recaudado[i]:,.0f} ({cumplimiento:.1f}%) '
                # Calcular posición para evitar que se salga
                pos_x_rec = min(recaudado[i], max(meta) * 1.05)
                ax.text(pos_x_rec, bar_rec.get_y() + bar_rec.get_height()/2,
                       texto_recaudado,
                       ha='left', va='center', fontsize=7, color=color_texto, fontweight='bold',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=color_fondo, edgecolor=color_borde, linewidth=1.5))

        ax.set_yticks(y_pos)
        ax.set_yticklabels(auditores, fontsize=9, fontweight='normal')  # Aumentado tamaño de fuente
        ax.set_xlabel('Monto (S/)', fontsize=9, fontweight='bold')

        # Título dinámico con el mes
        mes_nombre = meses_nombres[mes_hasta - 1] if mes_hasta <= 12 else "DIC"
        ax.set_title(f'Avance de Metas por Auditor (hasta {mes_nombre})', fontsize=11, fontweight='bold')

        # Limitar el eje X para que no se extienda demasiado
        max_meta = max(meta) if meta else 1
        max_recaudado = max(recaudado) if recaudado else 1
        # Limitar a máximo 110% de la meta más alta para evitar que se salga
        limite_x = max(max_meta * 1.10, min(max_recaudado * 1.05, max_meta * 1.15))
        ax.set_xlim(0, limite_x)

        # Leyenda personalizada con los colores
        from matplotlib.patches import Patch
        legend_elements = [
            Patch(facecolor='#E5E7EB', label='Meta Acumulada'),
            Patch(facecolor='#10B981', label='≥100% (Cumplió)'),
            Patch(facecolor='#F59E0B', label='50-99% (Cerca)'),
            Patch(facecolor='#EF4444', label='<50% (Por debajo)')
        ]
        ax.legend(handles=legend_elements, loc='lower right', fontsize=7)
        ax.grid(axis='x', alpha=0.3, linewidth=0.5)

        plt.tight_layout(pad=0.5)

        # Mostrar gráfico en tkinter
        canvas_grafico = FigureCanvasTkAgg(fig, grafico_container)
        canvas_grafico.draw()
        canvas_grafico.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)

        # Tooltip con Toplevel de tkinter que se superpone a todo
        tooltip_window = None

        def mostrar_tooltip(event):
            nonlocal tooltip_window

            if event.inaxes == ax:
                for i, (bar_r, bar_m) in enumerate(zip(bars_recaudado, bars_meta)):
                    cont_r, _ = bar_r.contains(event)
                    cont_m, _ = bar_m.contains(event)

                    if cont_r or cont_m:
                        cumplimiento = (recaudado[i] / meta[i] * 100) if meta[i] > 0 else 0
                        texto = f"{auditores[i]}\n\n"
                        texto += f"Meta: S/ {meta[i]:,.2f}\n"
                        texto += f"Recaudado: S/ {recaudado[i]:,.2f}\n"
                        texto += f"Cumplimiento: {cumplimiento:.1f}%"

                        # Obtener coordenadas del mouse en pantalla
                        try:
                            x_root = event.guiEvent.x_root
                            y_root = event.guiEvent.y_root
                        except:
                            x_root = canvas_grafico.get_tk_widget().winfo_pointerx()
                            y_root = canvas_grafico.get_tk_widget().winfo_pointery()

                        # Destruir tooltip anterior si existe
                        if tooltip_window is not None:
                            tooltip_window.destroy()

                        # Crear tooltip nuevo
                        tooltip_window = tk.Toplevel()
                        tooltip_window.wm_overrideredirect(True)
                        tooltip_window.attributes('-topmost', True)

                        # Contenedor principal
                        main_container = tk.Frame(tooltip_window, bg="transparent")
                        main_container.pack()

                        # Determinar posición del auditor
                        total_auditores = len(auditores)
                        posicion_relativa = i / total_auditores if total_auditores > 0 else 0

                        # Flecha ARRIBA (si tooltip está abajo - primeros auditores)
                        if posicion_relativa < 0.3:
                            arrow_canvas = tk.Canvas(main_container, width=20, height=10,
                                                    bg="transparent", highlightthickness=0)
                            arrow_canvas.pack()
                            # Triángulo apuntando arriba: pico arriba, base abajo
                            arrow_canvas.create_polygon(10, 0, 0, 10, 20, 10,
                                                       fill="#1E40AF", outline="#1E40AF")

                        # Frame del tooltip
                        tooltip_frame = tk.Frame(main_container, bg="transparent")
                        tooltip_frame.pack()

                        # Frame exterior con borde
                        outer_frame = tk.Frame(tooltip_frame, bg="#1E40AF", bd=0)
                        outer_frame.pack(padx=2, pady=2)

                        # Frame interior
                        inner_frame = tk.Frame(outer_frame, bg="#1E3A8A", bd=0)
                        inner_frame.pack(padx=2, pady=2)

                        # Label con texto
                        label = tk.Label(inner_frame, text=texto, bg="#1E3A8A", fg="white",
                                       font=("Segoe UI", 10, "bold"), justify="left",
                                       padx=16, pady=12, relief="flat")
                        label.pack()

                        # Flecha ABAJO (si tooltip está arriba - centro y últimos auditores)
                        if posicion_relativa >= 0.3:
                            arrow_canvas = tk.Canvas(main_container, width=20, height=10,
                                                    bg="transparent", highlightthickness=0)
                            arrow_canvas.pack()
                            # Triángulo apuntando abajo: base arriba, pico abajo
                            arrow_canvas.create_polygon(0, 0, 20, 0, 10, 10,
                                                       fill="#1E40AF", outline="#1E40AF")

                        # Posicionar tooltip
                        if posicion_relativa < 0.3:
                            y_offset = 15
                        elif posicion_relativa > 0.7:
                            y_offset = -100
                        else:
                            y_offset = -50

                        tooltip_window.wm_geometry(f"+{x_root + 15}+{y_root + y_offset}")
                        return

            # Ocultar tooltip si no está sobre ninguna barra
            ocultar_tooltip()

        def ocultar_tooltip(event=None):
            nonlocal tooltip_window
            if tooltip_window is not None:
                tooltip_window.destroy()
                tooltip_window = None

        fig.canvas.mpl_connect("motion_notify_event", mostrar_tooltip)
        fig.canvas.mpl_connect("axes_leave_event", ocultar_tooltip)

        # CRÍTICO: Ocultar tooltip al cambiar de aplicación o perder foco
        canvas_widget = canvas_grafico.get_tk_widget()
        canvas_widget.bind("<Leave>", ocultar_tooltip)
        canvas_widget.bind("<FocusOut>", ocultar_tooltip)

        # Ocultar cuando la ventana principal pierde el foco
        root_window = canvas_widget.winfo_toplevel()
        root_window.bind("<FocusOut>", ocultar_tooltip, add="+")
        root_window.bind("<Unmap>", ocultar_tooltip, add="+")

        # Guardar figura para exportación (NO cerrarla)
        grafico_fig["fig"] = fig
        datos_exportar["grafico"] = datos
        datos_exportar["tabla_auditores"] = datos  # Guardar también para exportar tabla

        # === TABLA DE AUDITORES ===
        # Header con título y botón de exportación
        tabla_aud_header = ctk.CTkFrame(tabla_auditores_container, fg_color="transparent")
        tabla_aud_header.pack(fill="x", padx=10, pady=(10, 5))

        # Título dinámico con el mes
        mes_nombre = meses_nombres[mes_hasta - 1] if mes_hasta <= 12 else "DIC"
        titulo_tabla = f"📊 AVANCE POR AUDITOR\n(hasta {mes_nombre})"
        ctk.CTkLabel(tabla_aud_header, text=titulo_tabla,
                    font=("Segoe UI", 11, "bold"), text_color=COLOR_PRIMARY,
                    justify="center").pack(side="top", expand=True)

        # Botón pequeño para exportar tabla de auditores
        btn_export_aud = ctk.CTkButton(tabla_aud_header, text="📊",
                                       command=exportar_tabla_auditores,
                                       fg_color="#10B981", hover_color="#059669",
                                       width=30, height=24, corner_radius=5,
                                       font=("Segoe UI", 12))
        btn_export_aud.pack(side="top", pady=(5, 0))

        # Canvas con scroll para la tabla
        canvas_tabla = tk.Canvas(tabla_auditores_container, bg=COLOR_WHITE, highlightthickness=0)
        scrollbar_tabla = ctk.CTkScrollbar(tabla_auditores_container, orientation="vertical",
                                           command=canvas_tabla.yview)
        canvas_tabla.configure(yscrollcommand=scrollbar_tabla.set)

        tabla_frame = ctk.CTkFrame(canvas_tabla, fg_color=COLOR_WHITE)
        canvas_window_tabla = canvas_tabla.create_window((0, 0), window=tabla_frame, anchor="nw")

        def _on_tabla_configure(event=None):
            canvas_tabla.configure(scrollregion=canvas_tabla.bbox("all"))
            if canvas_tabla.winfo_width() > 1:
                canvas_tabla.itemconfig(canvas_window_tabla, width=canvas_tabla.winfo_width())

        tabla_frame.bind("<Configure>", _on_tabla_configure)

        # Encabezados de tabla
        headers = ["Auditor", "Meta", "Recaudado", "Cumplimiento"]
        header_frame = ctk.CTkFrame(tabla_frame, fg_color=COLOR_PRIMARY, corner_radius=5)
        header_frame.pack(fill="x", padx=2, pady=2)

        widths = [180, 80, 80, 80]
        for i, (header, width) in enumerate(zip(headers, widths)):
            ctk.CTkLabel(header_frame, text=header, font=("Segoe UI", 9, "bold"),
                        text_color="white", width=width).grid(row=0, column=i, padx=1, pady=5)

        # Filas de datos
        for idx, dato in enumerate(datos):
            bg = "#F9FAFB" if idx % 2 == 0 else COLOR_WHITE
            row_frame = ctk.CTkFrame(tabla_frame, fg_color=bg, corner_radius=3)
            row_frame.pack(fill="x", padx=2, pady=1)

            cumplimiento = (dato['recaudado'] / dato['meta_acumulada'] * 100) if dato['meta_acumulada'] > 0 else 0

            # Color del cumplimiento
            if cumplimiento >= 100:
                color_cumplimiento = "#059669"  # Verde
            elif cumplimiento >= 75:
                color_cumplimiento = "#F59E0B"  # Amarillo
            else:
                color_cumplimiento = "#DC2626"  # Rojo

            valores = [
                dato['auditor'][:25] + "..." if len(dato['auditor']) > 25 else dato['auditor'],
                f"S/ {dato['meta_acumulada']:,.0f}",
                f"S/ {dato['recaudado']:,.0f}",
                f"{cumplimiento:.1f}%"
            ]

            for i, (valor, width) in enumerate(zip(valores, widths)):
                color_texto = color_cumplimiento if i == 3 else COLOR_TEXT
                ctk.CTkLabel(row_frame, text=valor, font=("Segoe UI", 8),
                            text_color=color_texto, width=width,
                            anchor="w" if i == 0 else "center").grid(row=0, column=i, padx=1, pady=3)

        scrollbar_tabla.pack(side="right", fill="y")
        canvas_tabla.pack(side="left", fill="both", expand=True, padx=5, pady=5)

    def actualizar_tabla(datos, parent):
        """Genera tabla de avance mensual y anual"""
        for widget in parent.winfo_children():
            widget.destroy()

        if not datos:
            return

        # Header con título y botón de exportación
        tabla_mens_header = ctk.CTkFrame(parent, fg_color="transparent")
        tabla_mens_header.pack(fill="x", padx=10, pady=(10, 0))

        # Título
        ctk.CTkLabel(tabla_mens_header, text="📈 AVANCE MENSUAL Y ANUAL",
                    font=("Segoe UI", 14, "bold"), text_color=COLOR_PRIMARY).pack(side="left")

        # Botón pequeño para exportar tabla mensual
        btn_export_mens = ctk.CTkButton(tabla_mens_header, text="📊",
                                       command=exportar_tabla_mensual,
                                       fg_color="#10B981", hover_color="#059669",
                                       width=30, height=24, corner_radius=5,
                                       font=("Segoe UI", 12))
        btn_export_mens.pack(side="right")

        # Contenedor centrado para la tabla
        tabla_outer = ctk.CTkFrame(parent, fg_color="transparent")
        tabla_outer.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Crear tabla centrada con ancho máximo
        tabla_container = ctk.CTkFrame(tabla_outer, fg_color=COLOR_WHITE)
        tabla_container.pack(anchor="center", padx=10, pady=(0, 10))

        # Encabezados
        headers = ["Mes", "Ejecutado", "Meta", "Cumplimiento Mes", "Avance Anual"]
        header_frame = ctk.CTkFrame(tabla_container, fg_color=COLOR_PRIMARY, corner_radius=5)
        header_frame.pack(fill="x", padx=2, pady=2)

        for i, header in enumerate(headers):
            ctk.CTkLabel(header_frame, text=header, font=("Segoe UI", 10, "bold"),
                        text_color="white", width=150).grid(row=0, column=i, padx=2, pady=5)

        meses_nombres = ["", "ENE", "FEB", "MAR", "ABR", "MAY", "JUN",
                        "JUL", "AGO", "SEP", "OCT", "NOV", "DIC"]

        # Filas de datos
        for idx, dato in enumerate(datos):
            bg = "#F9FAFB" if idx % 2 == 0 else COLOR_WHITE
            row_frame = ctk.CTkFrame(tabla_container, fg_color=bg, corner_radius=3)
            row_frame.pack(fill="x", padx=2, pady=1)

            valores = [
                meses_nombres[dato['mes']],
                f"S/ {dato['ejecutado']:,.2f}",
                f"S/ {dato['meta']:,.2f}",
                f"{dato['cumplimiento']:.1f}%",
                f"{dato['avance_anual']:.1f}%"
            ]

            for i, valor in enumerate(valores):
                ctk.CTkLabel(row_frame, text=valor, font=("Segoe UI", 9),
                            text_color=COLOR_TEXT, width=150).grid(row=0, column=i, padx=2, pady=3)

    # Cargar datos iniciales inmediatamente (sin esperar filtros)
    cargar_datos_y_actualizar()

    # Cargar filtros de forma asíncrona después de 100ms (lazy loading)
    dashboard_frame.after(100, cargar_supervisores_auditores)

    # Vincular cambios de filtros
    combo_anio.configure(command=lambda x: (cargar_supervisores_auditores(), cargar_datos_y_actualizar()))
    combo_supervisor.configure(command=lambda x: cargar_datos_y_actualizar())
    combo_auditor.configure(command=lambda x: cargar_datos_y_actualizar())

def mostrar_dashboard_metas():
    """
    Dashboard principal para mostrar las tablas de recaudación auditoria
    Con pestañas para OF y AI, y filtros independientes para cada una
    """
    try:
        preview_frame.pack_forget()
    except Exception:
        pass
    
    dashboard_frame.pack(fill="both", expand=True, padx=10, pady=(5, 10))
    
    for widget in dashboard_frame.winfo_children():
        widget.destroy()

    # Canvas principal con scroll
    canvas = tk.Canvas(dashboard_frame, bg=COLOR_WHITE, highlightthickness=0)
    scrollbar = ctk.CTkScrollbar(dashboard_frame, orientation="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=scrollbar.set)

    inner_frame = ctk.CTkFrame(canvas, fg_color=COLOR_WHITE)
    canvas_window = canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    def _on_frame_configure(event=None):
        canvas.configure(scrollregion=canvas.bbox("all"))
        if canvas.winfo_width() > 1:
            canvas.itemconfig(canvas_window, width=canvas.winfo_width())

    inner_frame.bind("<Configure>", _on_frame_configure)
    canvas.bind("<Configure>", _on_frame_configure)

    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    # ====================
    # TÍTULO PRINCIPAL
    # ====================
    titulo_frame = ctk.CTkFrame(inner_frame, fg_color=COLOR_BOX, corner_radius=10)
    titulo_frame.pack(fill="x", padx=10, pady=(10, 5))

    ctk.CTkLabel(titulo_frame, text="📊 DASHBOARD DE METAS - RECAUDACIÓN AUDITORIA",
                 font=("Segoe UI", 18, "bold"), text_color=COLOR_PRIMARY).pack(pady=12)

    # ====================
    # PESTAÑAS (TABVIEW)
    # ====================
    tabview = ctk.CTkTabview(inner_frame, fg_color=COLOR_WHITE, 
                             segmented_button_fg_color=COLOR_PRIMARY,
                             segmented_button_selected_color=COLOR_SECONDARY,
                             segmented_button_selected_hover_color=COLOR_PRIMARY,
                             height=600)
    tabview.pack(fill="both", expand=True, padx=10, pady=10)

    tab_of = tabview.add("OF - Recaudación Auditoria")
    tab_ai = tabview.add("AI - Recaudación Auditoria")

    # ====================
    # TAB 1: OF - RECAUDACIÓN AUDITORIA
    # ====================
    
    # Cargar datos iniciales OF
    try:
        query_of = "SELECT MTO_PAG, MES, des_func, reimputado, des_ai, corriente FROM fiscalizaciones2"
        df_of_completo = pd.read_sql(query_of, DB_ENGINE)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar datos de OF:\n{e}")
        return

    # Frame de filtros OF
    filtro_of_frame = ctk.CTkFrame(tab_of, fg_color=COLOR_BOX, corner_radius=10)
    filtro_of_frame.pack(fill="x", padx=10, pady=(10, 5))

    ctk.CTkLabel(filtro_of_frame, text="Filtros:", font=("Segoe UI", 13, "bold"),
                 text_color=COLOR_TEXT).pack(side="left", padx=(10, 15), pady=10)

    # Obtener valores únicos para filtros OF
    valores_reimputado_of = sorted(df_of_completo['reimputado'].dropna().unique().tolist())
    valores_des_ai_of = sorted(df_of_completo['des_ai'].dropna().unique().tolist())
    valores_corriente_of = sorted(df_of_completo['corriente'].dropna().unique().tolist())
    valores_des_func_of = sorted(df_of_completo['des_func'].dropna().unique().tolist())

    # Variables de filtros OF
    check_reimputado_of_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in valores_reimputado_of:
        check_reimputado_of_vars[val] = tk.IntVar(value=0)

    check_des_ai_of_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in valores_des_ai_of:
        check_des_ai_of_vars[val] = tk.IntVar(value=0)

    check_corriente_of_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in valores_corriente_of:
        check_corriente_of_vars[val] = tk.IntVar(value=0)

    check_des_func_of_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in valores_des_func_of:
        check_des_func_of_vars[val] = tk.IntVar(value=0)

    # Frame para tabla OF
    frame_tabla_of = ctk.CTkFrame(tab_of, fg_color=COLOR_WHITE, corner_radius=10, height=450)
    frame_tabla_of.pack(fill="both", expand=True, pady=(5, 10), padx=10)

    # Función para aplicar filtros OF
    def aplicar_filtros_of_auto():
        df_filtrado = df_of_completo.copy()

        # Filtro reimputado
        if check_reimputado_of_vars["(Todos)"].get() == 0:
            seleccionados = [k for k, v in check_reimputado_of_vars.items() 
                           if v.get() == 1 and k != "(Todos)"]
            if seleccionados:
                df_filtrado = df_filtrado[df_filtrado['reimputado'].isin(seleccionados)]

        # Filtro des_ai
        if check_des_ai_of_vars["(Todos)"].get() == 0:
            seleccionados = [k for k, v in check_des_ai_of_vars.items() 
                           if v.get() == 1 and k != "(Todos)"]
            if seleccionados:
                df_filtrado = df_filtrado[df_filtrado['des_ai'].isin(seleccionados)]

        # Filtro corriente
        if check_corriente_of_vars["(Todos)"].get() == 0:
            seleccionados = [k for k, v in check_corriente_of_vars.items() 
                           if v.get() == 1 and k != "(Todos)"]
            if seleccionados:
                df_filtrado = df_filtrado[df_filtrado['corriente'].isin(seleccionados)]

        # Filtro des_func
        if check_des_func_of_vars["(Todos)"].get() == 0:
            seleccionados = [k for k, v in check_des_func_of_vars.items() 
                           if v.get() == 1 and k != "(Todos)"]
            if seleccionados:
                df_filtrado = df_filtrado[df_filtrado['des_func'].isin(seleccionados)]

        generar_tabla_of_recaudacion_auditoria(frame_tabla_of, df_filtrado)

    # FILTRO 1: REIMPUTADO
    filtro_1_container = ctk.CTkFrame(filtro_of_frame, fg_color="transparent")
    filtro_1_container.pack(side="left", padx=(0, 12))
    
    ctk.CTkLabel(filtro_1_container, text="Reimputado:", 
                 font=("Segoe UI", 10), text_color=COLOR_TEXT).pack(anchor="w")
    
    reimputado_of_button_text = tk.StringVar(value="(Todos)")
    dropdown_reimputado_of_win = {"win": None}

    btn_reimputado_of = ctk.CTkButton(filtro_1_container, textvariable=reimputado_of_button_text,
                                      fg_color="#ffffff", text_color=COLOR_TEXT, border_width=2,
                                      border_color=COLOR_PRIMARY, hover_color=COLOR_PANEL,
                                      font=("Segoe UI", 11), width=150, height=32, anchor="w",
                                      command=lambda: toggle_dropdown_reimputado_of())
    btn_reimputado_of.pack()

    def toggle_dropdown_reimputado_of():
        if dropdown_reimputado_of_win["win"] is not None:
            try:
                dropdown_reimputado_of_win["win"].destroy()
            except:
                pass
            dropdown_reimputado_of_win["win"] = None
            return

        top = tk.Toplevel(filtro_of_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_reimputado_of_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_reimputado_of(selected_val):
            if selected_val == "(Todos)":
                if check_reimputado_of_vars["(Todos)"].get() == 1:
                    for k in check_reimputado_of_vars:
                        if k != "(Todos)":
                            check_reimputado_of_vars[k].set(0)
            else:
                check_reimputado_of_vars["(Todos)"].set(0)

            selected = [k for k, v in check_reimputado_of_vars.items() 
                       if v.get() == 1 and k != "(Todos)"]
            if check_reimputado_of_vars["(Todos)"].get() == 1 or len(selected) == 0:
                reimputado_of_button_text.set("(Todos)")
            elif len(selected) == 1:
                reimputado_of_button_text.set(str(selected[0]))
            else:
                reimputado_of_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_of_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", 
                                   variable=check_reimputado_of_vars["(Todos)"],
                                   command=lambda: on_check_change_reimputado_of("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in valores_reimputado_of:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), 
                                variable=check_reimputado_of_vars[val],
                                command=lambda v=val: on_check_change_reimputado_of(v), 
                                font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_reimputado_of.winfo_rootx()
        y = btn_reimputado_of.winfo_rooty() + btn_reimputado_of.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_reimputado_of_win["win"] = None

        top.bind("<FocusOut>", close_dropdown)
        top.bind("<Escape>", close_dropdown)

    # FILTRO 2: ÁREA DE INFLUENCIA
    filtro_2_container = ctk.CTkFrame(filtro_of_frame, fg_color="transparent")
    filtro_2_container.pack(side="left", padx=(0, 12))
    
    ctk.CTkLabel(filtro_2_container, text="Área de Influencia:", 
                 font=("Segoe UI", 10), text_color=COLOR_TEXT).pack(anchor="w")
    
    des_ai_of_button_text = tk.StringVar(value="(Todos)")
    dropdown_des_ai_of_win = {"win": None}

    btn_des_ai_of = ctk.CTkButton(filtro_2_container, textvariable=des_ai_of_button_text,
                                  fg_color="#ffffff", text_color=COLOR_TEXT, border_width=2,
                                  border_color=COLOR_PRIMARY, hover_color=COLOR_PANEL,
                                  font=("Segoe UI", 11), width=150, height=32, anchor="w",
                                  command=lambda: toggle_dropdown_des_ai_of())
    btn_des_ai_of.pack()

    def toggle_dropdown_des_ai_of():
        if dropdown_des_ai_of_win["win"] is not None:
            try:
                dropdown_des_ai_of_win["win"].destroy()
            except:
                pass
            dropdown_des_ai_of_win["win"] = None
            return

        top = tk.Toplevel(filtro_of_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_des_ai_of_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_des_ai_of(selected_val):
            if selected_val == "(Todos)":
                if check_des_ai_of_vars["(Todos)"].get() == 1:
                    for k in check_des_ai_of_vars:
                        if k != "(Todos)":
                            check_des_ai_of_vars[k].set(0)
            else:
                check_des_ai_of_vars["(Todos)"].set(0)

            selected = [k for k, v in check_des_ai_of_vars.items() 
                       if v.get() == 1 and k != "(Todos)"]
            if check_des_ai_of_vars["(Todos)"].get() == 1 or len(selected) == 0:
                des_ai_of_button_text.set("(Todos)")
            elif len(selected) == 1:
                des_ai_of_button_text.set(str(selected[0]))
            else:
                des_ai_of_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_of_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", 
                                   variable=check_des_ai_of_vars["(Todos)"],
                                   command=lambda: on_check_change_des_ai_of("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in valores_des_ai_of:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), 
                                variable=check_des_ai_of_vars[val],
                                command=lambda v=val: on_check_change_des_ai_of(v), 
                                font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_des_ai_of.winfo_rootx()
        y = btn_des_ai_of.winfo_rooty() + btn_des_ai_of.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_des_ai_of_win["win"] = None

        top.bind("<FocusOut>", close_dropdown)
        top.bind("<Escape>", close_dropdown)

    # FILTRO 3: CORRIENTE
    filtro_3_container = ctk.CTkFrame(filtro_of_frame, fg_color="transparent")
    filtro_3_container.pack(side="left", padx=(0, 12))
    
    ctk.CTkLabel(filtro_3_container, text="Corriente:", 
                 font=("Segoe UI", 10), text_color=COLOR_TEXT).pack(anchor="w")
    
    corriente_of_button_text = tk.StringVar(value="(Todos)")
    dropdown_corriente_of_win = {"win": None}

    btn_corriente_of = ctk.CTkButton(filtro_3_container, textvariable=corriente_of_button_text,
                                     fg_color="#ffffff", text_color=COLOR_TEXT, border_width=2,
                                     border_color=COLOR_PRIMARY, hover_color=COLOR_PANEL,
                                     font=("Segoe UI", 11), width=150, height=32, anchor="w",
                                     command=lambda: toggle_dropdown_corriente_of())
    btn_corriente_of.pack()

    def toggle_dropdown_corriente_of():
        if dropdown_corriente_of_win["win"] is not None:
            try:
                dropdown_corriente_of_win["win"].destroy()
            except:
                pass
            dropdown_corriente_of_win["win"] = None
            return

        top = tk.Toplevel(filtro_of_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_corriente_of_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_corriente_of(selected_val):
            if selected_val == "(Todos)":
                if check_corriente_of_vars["(Todos)"].get() == 1:
                    for k in check_corriente_of_vars:
                        if k != "(Todos)":
                            check_corriente_of_vars[k].set(0)
            else:
                check_corriente_of_vars["(Todos)"].set(0)

            selected = [k for k, v in check_corriente_of_vars.items() 
                       if v.get() == 1 and k != "(Todos)"]
            if check_corriente_of_vars["(Todos)"].get() == 1 or len(selected) == 0:
                corriente_of_button_text.set("(Todos)")
            elif len(selected) == 1:
                corriente_of_button_text.set(str(selected[0]))
            else:
                corriente_of_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_of_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", 
                                   variable=check_corriente_of_vars["(Todos)"],
                                   command=lambda: on_check_change_corriente_of("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in valores_corriente_of:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), 
                                variable=check_corriente_of_vars[val],
                                command=lambda v=val: on_check_change_corriente_of(v), 
                                font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_corriente_of.winfo_rootx()
        y = btn_corriente_of.winfo_rooty() + btn_corriente_of.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_corriente_of_win["win"] = None

        top.bind("<FocusOut>", close_dropdown)
        top.bind("<Escape>", close_dropdown)

    # FILTRO 4: FUNCIONARIO
    filtro_4_container = ctk.CTkFrame(filtro_of_frame, fg_color="transparent")
    filtro_4_container.pack(side="left", padx=(0, 12))
    
    ctk.CTkLabel(filtro_4_container, text="Funcionario:", 
                 font=("Segoe UI", 10), text_color=COLOR_TEXT).pack(anchor="w")
    
    des_func_of_button_text = tk.StringVar(value="(Todos)")
    dropdown_des_func_of_win = {"win": None}

    btn_des_func_of = ctk.CTkButton(filtro_4_container, textvariable=des_func_of_button_text,
                                    fg_color="#ffffff", text_color=COLOR_TEXT, border_width=2,
                                    border_color=COLOR_PRIMARY, hover_color=COLOR_PANEL,
                                    font=("Segoe UI", 11), width=150, height=32, anchor="w",
                                    command=lambda: toggle_dropdown_des_func_of())
    btn_des_func_of.pack()

    def toggle_dropdown_des_func_of():
        if dropdown_des_func_of_win["win"] is not None:
            try:
                dropdown_des_func_of_win["win"].destroy()
            except:
                pass
            dropdown_des_func_of_win["win"] = None
            return

        top = tk.Toplevel(filtro_of_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_des_func_of_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_des_func_of(selected_val):
            if selected_val == "(Todos)":
                if check_des_func_of_vars["(Todos)"].get() == 1:
                    for k in check_des_func_of_vars:
                        if k != "(Todos)":
                            check_des_func_of_vars[k].set(0)
            else:
                check_des_func_of_vars["(Todos)"].set(0)

            selected = [k for k, v in check_des_func_of_vars.items() 
                       if v.get() == 1 and k != "(Todos)"]
            if check_des_func_of_vars["(Todos)"].get() == 1 or len(selected) == 0:
                des_func_of_button_text.set("(Todos)")
            elif len(selected) == 1:
                des_func_of_button_text.set(str(selected[0]))
            else:
                des_func_of_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_of_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", 
                                   variable=check_des_func_of_vars["(Todos)"],
                                   command=lambda: on_check_change_des_func_of("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in valores_des_func_of:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), 
                                variable=check_des_func_of_vars[val],
                                command=lambda v=val: on_check_change_des_func_of(v), 
                                font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_des_func_of.winfo_rootx()
        y = btn_des_func_of.winfo_rooty() + btn_des_func_of.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_des_func_of_win["win"] = None

        top.bind("<FocusOut>", close_dropdown)
        top.bind("<Escape>", close_dropdown)

    # BOTONES DE ACCIÓN
    botones_container = ctk.CTkFrame(filtro_of_frame, fg_color="transparent")
    botones_container.pack(side="left", padx=(20, 5))

    # Botón LIMPIAR FILTROS OF
    def limpiar_filtros_of():
        check_reimputado_of_vars["(Todos)"].set(1)
        for k in check_reimputado_of_vars:
            if k != "(Todos)":
                check_reimputado_of_vars[k].set(0)
        reimputado_of_button_text.set("(Todos)")

        check_des_ai_of_vars["(Todos)"].set(1)
        for k in check_des_ai_of_vars:
            if k != "(Todos)":
                check_des_ai_of_vars[k].set(0)
        des_ai_of_button_text.set("(Todos)")

        check_corriente_of_vars["(Todos)"].set(1)
        for k in check_corriente_of_vars:
            if k != "(Todos)":
                check_corriente_of_vars[k].set(0)
        corriente_of_button_text.set("(Todos)")

        check_des_func_of_vars["(Todos)"].set(1)
        for k in check_des_func_of_vars:
            if k != "(Todos)":
                check_des_func_of_vars[k].set(0)
        des_func_of_button_text.set("(Todos)")
        
        aplicar_filtros_of_auto()

    ctk.CTkButton(botones_container, text="🔄 Limpiar", command=limpiar_filtros_of,
                  fg_color="#F59E0B", hover_color="#D97706", font=("Segoe UI", 11, "bold"),
                  width=120, height=32).pack(side="left", padx=5)

    # Botón METAS OF
    def mostrar_metas_of():
        """
        Muestra la gestión de metas OF dentro del dashboard principal
        """
        # Limpiar el dashboard
        for widget in dashboard_frame.winfo_children():
            widget.destroy()
        
        # Variables globales de la ventana
        auditores_data = {}  # {nombre_auditor: {'entry': widget, 'var': StringVar}}
        meta_anual_var = tk.StringVar(value="0.00")
        suma_total_var = tk.StringVar(value="0.00")
        modo_edicion = tk.BooleanVar(value=False)
        fecha_guardado_var = tk.StringVar(value="")
        anio_actual = datetime.now().year
        
        # Canvas principal con scroll
        canvas = tk.Canvas(dashboard_frame, bg=COLOR_WHITE, highlightthickness=0)
        scrollbar = ctk.CTkScrollbar(dashboard_frame, orientation="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)

        main_frame = ctk.CTkFrame(canvas, fg_color=COLOR_WHITE)
        canvas_window = canvas.create_window((0, 0), window=main_frame, anchor="nw")

        def _on_frame_configure(event=None):
            canvas.configure(scrollregion=canvas.bbox("all"))
            if canvas.winfo_width() > 1:
                canvas.itemconfig(canvas_window, width=canvas.winfo_width())

        main_frame.bind("<Configure>", _on_frame_configure)
        canvas.bind("<Configure>", _on_frame_configure)

        canvas.pack(side="left", fill="both", expand=True, padx=10, pady=10)
        scrollbar.pack(side="right", fill="y")
        
        # ====================
        # ENCABEZADO CON BOTÓN VOLVER
        # ====================
        header_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_PRIMARY, corner_radius=10)
        header_frame.pack(fill="x", padx=10, pady=(10, 5))
        
        header_inner = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_inner.pack(fill="x", padx=15, pady=12)
        
        # Botón volver
        def volver_dashboard():
            canvas.pack_forget()
            scrollbar.pack_forget()
            mostrar_dashboard_metas()
        
        ctk.CTkButton(header_inner, text="← Volver", command=volver_dashboard,
                    fg_color="transparent", hover_color=COLOR_SECONDARY,
                    font=("Segoe UI", 11, "bold"), width=100, height=32,
                    border_width=2, border_color="white").pack(side="left")
        
        ctk.CTkLabel(header_inner, text="🎯 GESTIÓN DE METAS ANUALES - OF", 
                    font=("Segoe UI", 16, "bold"), text_color="white").pack(side="left", padx=20, expand=True)
        
        # ====================
        # SECCIÓN META ANUAL
        # ====================
        meta_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_BOX, corner_radius=10)
        meta_frame.pack(fill="x", padx=10, pady=(10, 10))
        
        meta_inner = ctk.CTkFrame(meta_frame, fg_color="transparent")
        meta_inner.pack(fill="x", padx=15, pady=15)
        
        ctk.CTkLabel(meta_inner, text="💰 Meta Anual Total:", 
                    font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT).pack(side="left", padx=(0, 10))
        
        entry_meta_anual = ctk.CTkEntry(meta_inner, textvariable=meta_anual_var, 
                                        font=("Segoe UI", 13), width=200, height=35,
                                        border_color=COLOR_PRIMARY, border_width=2)
        entry_meta_anual.pack(side="left", padx=(0, 15))
        
        def distribuir_equitativamente():
            """Divide la meta anual equitativamente entre todos los auditores"""
            try:
                meta = float(meta_anual_var.get().replace(",", ""))
                total_auditores = len(auditores_data)
                
                if total_auditores == 0:
                    messagebox.showwarning("Advertencia", "No hay auditores para distribuir")
                    return
                
                monto_por_auditor = meta / total_auditores
                
                for nombre, data in auditores_data.items():
                    data['var'].set(f"{monto_por_auditor:,.2f}")
                
                calcular_suma_total()
            except ValueError:
                messagebox.showerror("Error", "Ingrese un monto válido")
        
        ctk.CTkButton(meta_inner, text="⚖️ Distribuir Equitativamente", 
                    command=distribuir_equitativamente,
                    fg_color=COLOR_SECONDARY, hover_color=COLOR_PRIMARY,
                    font=("Segoe UI", 11, "bold"), width=200, height=35).pack(side="left")
        
        # ====================
        # SECCIÓN RESUMEN
        # ====================
        resumen_frame = ctk.CTkFrame(main_frame, fg_color="#F0F9FF", corner_radius=10, border_width=2, border_color="#3B82F6")
        resumen_frame.pack(fill="x", padx=10, pady=(0, 10))
        
        resumen_inner = ctk.CTkFrame(resumen_frame, fg_color="transparent")
        resumen_inner.pack(fill="x", padx=15, pady=12)
        
        ctk.CTkLabel(resumen_inner, text="📊 Suma Total Asignada:", 
                    font=("Segoe UI", 12, "bold"), text_color="#1E40AF").pack(side="left", padx=(0, 10))
        
        label_suma = ctk.CTkLabel(resumen_inner, textvariable=suma_total_var, 
                                font=("Segoe UI", 14, "bold"), text_color="#059669")
        label_suma.pack(side="left", padx=(0, 20))
        
        diferencia_label = ctk.CTkLabel(resumen_inner, text="", 
                                        font=("Segoe UI", 11), text_color="#DC2626")
        diferencia_label.pack(side="left")
        
        fecha_label = ctk.CTkLabel(resumen_inner, textvariable=fecha_guardado_var,
                                font=("Segoe UI", 10, "italic"), text_color="#6B7280")
        fecha_label.pack(side="right")
        
        def calcular_suma_total():
            """Calcula la suma de todos los montos asignados y muestra diferencias"""
            try:
                suma = 0.0
                for nombre, data in auditores_data.items():
                    valor = data['var'].get().replace(",", "")
                    if valor and valor != "":
                        suma += float(valor)
                
                suma_total_var.set(f"S/ {suma:,.2f}")
                
                # Calcular diferencia con meta anual
                try:
                    meta = float(meta_anual_var.get().replace(",", ""))
                    diferencia = suma - meta
                    
                    if abs(diferencia) < 0.01:  # Igual (tolerancia de centavos)
                        diferencia_label.configure(text="✅ Distribución correcta", text_color="#059669")
                        label_suma.configure(text_color="#059669")
                    elif diferencia > 0:
                        diferencia_label.configure(text=f"⚠️ Excede en S/ {diferencia:,.2f}", text_color="#DC2626")
                        label_suma.configure(text_color="#DC2626")
                    else:
                        diferencia_label.configure(text=f"⚠️ Falta asignar S/ {abs(diferencia):,.2f}", text_color="#F59E0B")
                        label_suma.configure(text_color="#F59E0B")
                except:
                    diferencia_label.configure(text="")
            except:
                suma_total_var.set("S/ 0.00")
        
        # ====================
        # SECCIÓN AUDITORES (CON SCROLL)
        # ====================
        auditores_container_frame = ctk.CTkFrame(main_frame, fg_color=COLOR_BOX, corner_radius=10)
        auditores_container_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        ctk.CTkLabel(auditores_container_frame, text="👥 Distribución por Auditor", 
                    font=("Segoe UI", 13, "bold"), text_color=COLOR_TEXT, anchor="w").pack(fill="x", padx=15, pady=(15, 10))
        
        # Canvas con scrollbar para auditores
        canvas_auditores = tk.Canvas(auditores_container_frame, bg=COLOR_WHITE, highlightthickness=0, height=300)
        scrollbar_auditores = ctk.CTkScrollbar(auditores_container_frame, orientation="vertical", command=canvas_auditores.yview)
        canvas_auditores.configure(yscrollcommand=scrollbar_auditores.set)
        
        frame_auditores = ctk.CTkFrame(canvas_auditores, fg_color=COLOR_WHITE)
        canvas_window_aud = canvas_auditores.create_window((0, 0), window=frame_auditores, anchor="nw")
        
        def on_frame_configure_aud(event=None):
            canvas_auditores.configure(scrollregion=canvas_auditores.bbox("all"))
            if canvas_auditores.winfo_width() > 1:
                canvas_auditores.itemconfig(canvas_window_aud, width=canvas_auditores.winfo_width())
        
        frame_auditores.bind("<Configure>", on_frame_configure_aud)
        canvas_auditores.bind("<Configure>", on_frame_configure_aud)
        
        canvas_auditores.pack(side="left", fill="both", expand=True, padx=(15, 5), pady=(0, 15))
        scrollbar_auditores.pack(side="right", fill="y", padx=(0, 15), pady=(0, 15))
        
        # ====================
        # CARGAR AUDITORES Y DATOS
        # ====================
        def cargar_auditores():
            """Carga auditores únicos de fiscalizaciones2 y verifica si hay datos guardados"""
            try:
                # Obtener auditores únicos de fiscalizaciones2
                query_auditores = """
                    SELECT DISTINCT des_func 
                    FROM fiscalizaciones2 
                    WHERE des_func IS NOT NULL AND des_func != ''
                    ORDER BY des_func
                """
                df_auditores = pd.read_sql(query_auditores, DB_ENGINE)
                
                if df_auditores.empty:
                    messagebox.showwarning("Advertencia", "No se encontraron auditores en la base de datos")
                    volver_dashboard()
                    return
                
                # Verificar si ya existen datos guardados para este año
                query_guardados = """
                    SELECT nombre_auditor, monto_asignado, monto_anual, fecha
                    FROM distribucion
                    WHERE tipo = 'OF' AND anio = %s
                """
                df_guardados = pd.read_sql(query_guardados, DB_ENGINE, params=(anio_actual,))
                
                if not df_guardados.empty:
                    # MODO EDICIÓN - Cargar datos existentes
                    modo_edicion.set(True)
                    meta_anual_var.set(f"{df_guardados['monto_anual'].iloc[0]:,.2f}")
                    fecha_guardado_var.set(f"📅 Última actualización: {df_guardados['fecha'].iloc[0].strftime('%d/%m/%Y %H:%M')}")
                    
                    # Crear diccionario de montos guardados
                    montos_guardados = {}
                    for idx, row in df_guardados.iterrows():
                        montos_guardados[row['nombre_auditor']] = row['monto_asignado']
                else:
                    # MODO NUEVO
                    modo_edicion.set(False)
                    montos_guardados = {}
                
                # Crear campos para cada auditor
                for idx, row in df_auditores.iterrows():
                    nombre_auditor = row['des_func']
                    
                    # Frame para cada auditor
                    auditor_frame = ctk.CTkFrame(frame_auditores, fg_color=COLOR_BOX, corner_radius=8)
                    auditor_frame.pack(fill="x", padx=5, pady=3)
                    
                    inner_frame = ctk.CTkFrame(auditor_frame, fg_color="transparent")
                    inner_frame.pack(fill="x", padx=10, pady=8)
                    
                    # Nombre del auditor
                    ctk.CTkLabel(inner_frame, text=f"👤 {nombre_auditor}", 
                                font=("Segoe UI", 11), text_color=COLOR_TEXT, 
                                width=300, anchor="w").pack(side="left", padx=(0, 10))
                    
                    # Entry para monto
                    monto_var = tk.StringVar(value="0.00")
                    
                    # Si hay datos guardados, cargar el monto
                    if nombre_auditor in montos_guardados:
                        monto_var.set(f"{montos_guardados[nombre_auditor]:,.2f}")
                    
                    def on_monto_change(*args, var=monto_var):
                        calcular_suma_total()
                    
                    monto_var.trace_add("write", on_monto_change)
                    
                    entry_monto = ctk.CTkEntry(inner_frame, textvariable=monto_var,
                                            font=("Segoe UI", 11), width=180, height=32,
                                            border_color="#D1D5DB", border_width=1,
                                            placeholder_text="0.00")
                    entry_monto.pack(side="left", padx=(0, 5))
                    
                    ctk.CTkLabel(inner_frame, text="S/", 
                                font=("Segoe UI", 11, "bold"), text_color=COLOR_SECONDARY).pack(side="left")
                    
                    # Guardar referencia
                    auditores_data[nombre_auditor] = {
                        'entry': entry_monto,
                        'var': monto_var
                    }
                
                # Calcular suma inicial
                calcular_suma_total()
                
            except Exception as e:
                messagebox.showerror("Error", f"Error al cargar auditores:\n{e}")
                volver_dashboard()
        
        # ====================
        # BOTONES DE ACCIÓN
        # ====================
        botones_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        botones_frame.pack(fill="x", padx=10, pady=(10, 15))
        
        def guardar_metas():
            """Guarda o actualiza las metas en la base de datos"""
            try:
                # Validar meta anual
                try:
                    meta_anual = float(meta_anual_var.get().replace(",", ""))
                except:
                    messagebox.showerror("Error", "Ingrese una meta anual válida")
                    return
                
                if meta_anual <= 0:
                    messagebox.showerror("Error", "La meta anual debe ser mayor a 0")
                    return
                
                # Validar que todos los montos sean válidos
                suma_total = 0.0
                datos_a_guardar = []
                
                for nombre in auditores_data.keys():
                    data = auditores_data[nombre]
                    try:
                        monto_str = data['var'].get().replace(",", "").strip()
                        if not monto_str or monto_str == "":
                            monto_str = "0"
                        monto = float(monto_str)
                        suma_total += monto
                        datos_a_guardar.append(tuple([nombre, monto, meta_anual, anio_actual]))
                    except ValueError as ve:
                        messagebox.showerror("Error", f"Monto inválido para {nombre}: {data['var'].get()}")
                        return
                    except Exception as ex:
                        messagebox.showerror("Error", f"Error procesando {nombre}: {str(ex)}")
                        return
                
                # Advertir si hay diferencia
                diferencia = abs(suma_total - meta_anual)
                if diferencia > 0.01:
                    respuesta = messagebox.askyesno(
                        "Advertencia",
                        f"La suma total (S/ {suma_total:,.2f}) difiere de la meta anual (S/ {meta_anual:,.2f})\n"
                        f"Diferencia: S/ {diferencia:,.2f}\n\n"
                        "¿Desea guardar de todos modos?"
                    )
                    if not respuesta:
                        return
                
                # Guardar en base de datos
                connection = DB_ENGINE.raw_connection()
                cursor = connection.cursor()
                
                try:
                    # Eliminar registros existentes del año y tipo OF
                    cursor.execute("""
                        DELETE FROM distribucion 
                        WHERE tipo = 'OF' AND anio = %s
                    """, (anio_actual,))
                    
                    # Insertar nuevos registros
                    cursor.executemany("""
                        INSERT INTO distribucion 
                        (nombre_auditor, monto_asignado, monto_anual, anio, tipo, fecha)
                        VALUES (%s, %s, %s, %s, 'OF', NOW())
                    """, datos_a_guardar)
                    
                    connection.commit()
                    
                    messagebox.showinfo("Éxito", f"✅ Metas guardadas correctamente\n\n"
                                                f"Total de auditores: {len(datos_a_guardar)}\n"
                                                f"Meta anual: S/ {meta_anual:,.2f}\n"
                                                f"Suma asignada: S/ {suma_total:,.2f}")
                    
                    # Actualizar fecha de guardado
                    fecha_guardado_var.set(f"📅 Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
                    modo_edicion.set(True)
                    
                except Exception as e:
                    connection.rollback()
                    raise e
                finally:
                    cursor.close()
                    connection.close()
                    
            except Exception as e:
                messagebox.showerror("Error", f"Error al guardar metas:\n{e}")
        
        # Botón Guardar
        ctk.CTkButton(botones_frame, text="💾 Guardar Metas", command=guardar_metas,
                    fg_color="#10B981", hover_color="#059669", 
                    font=("Segoe UI", 12, "bold"), width=180, height=40).pack(side="left", padx=5)
        
        # Botón Volver
        ctk.CTkButton(botones_frame, text="← Volver al Dashboard", command=volver_dashboard,
                    fg_color="#6B7280", hover_color="#4B5563", 
                    font=("Segoe UI", 12, "bold"), width=180, height=40).pack(side="right", padx=5)
        
        # Cargar datos iniciales
        dashboard_frame.after(100, cargar_auditores)
        
        # Forzar redraw
        def _force_redraw():
            try:
                if canvas.winfo_exists() and main_frame.winfo_exists():
                    main_frame.update_idletasks()
                    canvas.itemconfig(canvas_window, width=canvas.winfo_width())
                    canvas.configure(scrollregion=canvas.bbox("all"))
                    canvas.update()
                    canvas.yview_moveto(0)
            except Exception:
                pass
        
        dashboard_frame.after(50, _force_redraw)
        dashboard_frame.after(200, _force_redraw)
    
    ctk.CTkButton(botones_container, text="🎯 Metas", command=mostrar_metas_of,
                  fg_color="#10B981", hover_color="#059669", font=("Segoe UI", 11, "bold"),
                  width=120, height=32).pack(side="left", padx=5)

    # Botón AVANCE DE METAS OF
    def ir_a_avance_metas_of():
        """Función para ir al dashboard de avance de metas OF"""
        # Limpiar el dashboard actual
        for widget in dashboard_frame.winfo_children():
            widget.destroy()
        # Llamar al dashboard de avance de metas
        dashboard_avance_metas_of()

    ctk.CTkButton(botones_container, text="📊 Avance de Metas", command=ir_a_avance_metas_of,
                  fg_color="#6366F1", hover_color="#4F46E5", font=("Segoe UI", 11, "bold"),
                  width=150, height=32).pack(side="left", padx=5)

    # Generar tabla OF inicial
    aplicar_filtros_of_auto()

    # ====================
    # TAB 2: AI - RECAUDACIÓN AUDITORIA
    # ====================
    
    # Cargar datos iniciales AI
    try:
        query_ai = "SELECT MTO_PAG_IN, MES, nomb_ver, reimputado, corriente FROM fiscalizaciones5"
        df_ai_completo = pd.read_sql(query_ai, DB_ENGINE)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar datos de AI:\n{e}")
        return

    # Frame de filtros AI
    filtro_ai_frame = ctk.CTkFrame(tab_ai, fg_color=COLOR_BOX, corner_radius=10)
    filtro_ai_frame.pack(fill="x", padx=10, pady=(10, 5))

    ctk.CTkLabel(filtro_ai_frame, text="Filtros:", font=("Segoe UI", 13, "bold"),
                 text_color=COLOR_TEXT).pack(side="left", padx=(10, 15), pady=10)

    # Obtener valores únicos para filtros AI
    valores_reimputado_ai = sorted(df_ai_completo['reimputado'].dropna().unique().tolist())
    valores_corriente_ai = sorted(df_ai_completo['corriente'].dropna().unique().tolist())
    valores_nomb_ver_ai = sorted(df_ai_completo['nomb_ver'].dropna().unique().tolist())

    # Variables de filtros AI
    check_reimputado_ai_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in valores_reimputado_ai:
        check_reimputado_ai_vars[val] = tk.IntVar(value=0)

    check_corriente_ai_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in valores_corriente_ai:
        check_corriente_ai_vars[val] = tk.IntVar(value=0)

    check_nomb_ver_ai_vars = {"(Todos)": tk.IntVar(value=1)}
    for val in valores_nomb_ver_ai:
        check_nomb_ver_ai_vars[val] = tk.IntVar(value=0)

    # Frame para tabla AI
    frame_tabla_ai = ctk.CTkFrame(tab_ai, fg_color=COLOR_WHITE, corner_radius=10, height=450)
    frame_tabla_ai.pack(fill="both", expand=True, pady=(5, 10), padx=10)

    # Función para aplicar filtros
# Función para aplicar filtros AI
    def aplicar_filtros_ai_auto():
        df_filtrado = df_ai_completo.copy()

        # Filtro reimputado
        if check_reimputado_ai_vars["(Todos)"].get() == 0:
            seleccionados = [k for k, v in check_reimputado_ai_vars.items() 
                           if v.get() == 1 and k != "(Todos)"]
            if seleccionados:
                df_filtrado = df_filtrado[df_filtrado['reimputado'].isin(seleccionados)]

        # Filtro corriente
        if check_corriente_ai_vars["(Todos)"].get() == 0:
            seleccionados = [k for k, v in check_corriente_ai_vars.items() 
                           if v.get() == 1 and k != "(Todos)"]
            if seleccionados:
                df_filtrado = df_filtrado[df_filtrado['corriente'].isin(seleccionados)]

        # Filtro nomb_ver
        if check_nomb_ver_ai_vars["(Todos)"].get() == 0:
            seleccionados = [k for k, v in check_nomb_ver_ai_vars.items() 
                           if v.get() == 1 and k != "(Todos)"]
            if seleccionados:
                df_filtrado = df_filtrado[df_filtrado['nomb_ver'].isin(seleccionados)]

        generar_tabla_ai_recaudacion_auditoria(frame_tabla_ai, df_filtrado)

    # FILTRO 1: REIMPUTADO AI
    filtro_1_ai_container = ctk.CTkFrame(filtro_ai_frame, fg_color="transparent")
    filtro_1_ai_container.pack(side="left", padx=(0, 12))
    
    ctk.CTkLabel(filtro_1_ai_container, text="Reimputado:", 
                 font=("Segoe UI", 10), text_color=COLOR_TEXT).pack(anchor="w")
    
    reimputado_ai_button_text = tk.StringVar(value="(Todos)")
    dropdown_reimputado_ai_win = {"win": None}

    btn_reimputado_ai = ctk.CTkButton(filtro_1_ai_container, textvariable=reimputado_ai_button_text,
                                      fg_color="#ffffff", text_color=COLOR_TEXT, border_width=2,
                                      border_color=COLOR_PRIMARY, hover_color=COLOR_PANEL,
                                      font=("Segoe UI", 11), width=150, height=32, anchor="w",
                                      command=lambda: toggle_dropdown_reimputado_ai())
    btn_reimputado_ai.pack()

    def toggle_dropdown_reimputado_ai():
        if dropdown_reimputado_ai_win["win"] is not None:
            try:
                dropdown_reimputado_ai_win["win"].destroy()
            except:
                pass
            dropdown_reimputado_ai_win["win"] = None
            return

        top = tk.Toplevel(filtro_ai_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_reimputado_ai_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_reimputado_ai(selected_val):
            if selected_val == "(Todos)":
                if check_reimputado_ai_vars["(Todos)"].get() == 1:
                    for k in check_reimputado_ai_vars:
                        if k != "(Todos)":
                            check_reimputado_ai_vars[k].set(0)
            else:
                check_reimputado_ai_vars["(Todos)"].set(0)

            selected = [k for k, v in check_reimputado_ai_vars.items() 
                       if v.get() == 1 and k != "(Todos)"]
            if check_reimputado_ai_vars["(Todos)"].get() == 1 or len(selected) == 0:
                reimputado_ai_button_text.set("(Todos)")
            elif len(selected) == 1:
                reimputado_ai_button_text.set(str(selected[0]))
            else:
                reimputado_ai_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_ai_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", 
                                   variable=check_reimputado_ai_vars["(Todos)"],
                                   command=lambda: on_check_change_reimputado_ai("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in valores_reimputado_ai:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), 
                                variable=check_reimputado_ai_vars[val],
                                command=lambda v=val: on_check_change_reimputado_ai(v), 
                                font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_reimputado_ai.winfo_rootx()
        y = btn_reimputado_ai.winfo_rooty() + btn_reimputado_ai.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_reimputado_ai_win["win"] = None

        top.bind("<FocusOut>", close_dropdown)
        top.bind("<Escape>", close_dropdown)

    # FILTRO 2: CORRIENTE AI
    filtro_2_ai_container = ctk.CTkFrame(filtro_ai_frame, fg_color="transparent")
    filtro_2_ai_container.pack(side="left", padx=(0, 12))
    
    ctk.CTkLabel(filtro_2_ai_container, text="Corriente:", 
                 font=("Segoe UI", 10), text_color=COLOR_TEXT).pack(anchor="w")
    
    corriente_ai_button_text = tk.StringVar(value="(Todos)")
    dropdown_corriente_ai_win = {"win": None}

    btn_corriente_ai = ctk.CTkButton(filtro_2_ai_container, textvariable=corriente_ai_button_text,
                                     fg_color="#ffffff", text_color=COLOR_TEXT, border_width=2,
                                     border_color=COLOR_PRIMARY, hover_color=COLOR_PANEL,
                                     font=("Segoe UI", 11), width=150, height=32, anchor="w",
                                     command=lambda: toggle_dropdown_corriente_ai())
    btn_corriente_ai.pack()

    def toggle_dropdown_corriente_ai():
        if dropdown_corriente_ai_win["win"] is not None:
            try:
                dropdown_corriente_ai_win["win"].destroy()
            except:
                pass
            dropdown_corriente_ai_win["win"] = None
            return

        top = tk.Toplevel(filtro_ai_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_corriente_ai_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_corriente_ai(selected_val):
            if selected_val == "(Todos)":
                if check_corriente_ai_vars["(Todos)"].get() == 1:
                    for k in check_corriente_ai_vars:
                        if k != "(Todos)":
                            check_corriente_ai_vars[k].set(0)
            else:
                check_corriente_ai_vars["(Todos)"].set(0)

            selected = [k for k, v in check_corriente_ai_vars.items() 
                       if v.get() == 1 and k != "(Todos)"]
            if check_corriente_ai_vars["(Todos)"].get() == 1 or len(selected) == 0:
                corriente_ai_button_text.set("(Todos)")
            elif len(selected) == 1:
                corriente_ai_button_text.set(str(selected[0]))
            else:
                corriente_ai_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_ai_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", 
                                   variable=check_corriente_ai_vars["(Todos)"],
                                   command=lambda: on_check_change_corriente_ai("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in valores_corriente_ai:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), 
                                variable=check_corriente_ai_vars[val],
                                command=lambda v=val: on_check_change_corriente_ai(v), 
                                font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_corriente_ai.winfo_rootx()
        y = btn_corriente_ai.winfo_rooty() + btn_corriente_ai.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_corriente_ai_win["win"] = None

        top.bind("<FocusOut>", close_dropdown)
        top.bind("<Escape>", close_dropdown)

    # FILTRO 3: VERIFICADOR AI
    filtro_3_ai_container = ctk.CTkFrame(filtro_ai_frame, fg_color="transparent")
    filtro_3_ai_container.pack(side="left", padx=(0, 12))
    
    ctk.CTkLabel(filtro_3_ai_container, text="Verificador:", 
                 font=("Segoe UI", 10), text_color=COLOR_TEXT).pack(anchor="w")
    
    nomb_ver_ai_button_text = tk.StringVar(value="(Todos)")
    dropdown_nomb_ver_ai_win = {"win": None}

    btn_nomb_ver_ai = ctk.CTkButton(filtro_3_ai_container, textvariable=nomb_ver_ai_button_text,
                                    fg_color="#ffffff", text_color=COLOR_TEXT, border_width=2,
                                    border_color=COLOR_PRIMARY, hover_color=COLOR_PANEL,
                                    font=("Segoe UI", 11), width=150, height=32, anchor="w",
                                    command=lambda: toggle_dropdown_nomb_ver_ai())
    btn_nomb_ver_ai.pack()

    def toggle_dropdown_nomb_ver_ai():
        if dropdown_nomb_ver_ai_win["win"] is not None:
            try:
                dropdown_nomb_ver_ai_win["win"].destroy()
            except:
                pass
            dropdown_nomb_ver_ai_win["win"] = None
            return

        top = tk.Toplevel(filtro_ai_frame)
        top.withdraw()
        top.overrideredirect(True)
        top.configure(bg="#ffffff", relief="solid", borderwidth=1)
        dropdown_nomb_ver_ai_win["win"] = top

        frame_inner = ctk.CTkScrollableFrame(top, width=220, height=200, fg_color="#ffffff")
        frame_inner.pack(fill="both", expand=True, padx=2, pady=2)

        def on_check_change_nomb_ver_ai(selected_val):
            if selected_val == "(Todos)":
                if check_nomb_ver_ai_vars["(Todos)"].get() == 1:
                    for k in check_nomb_ver_ai_vars:
                        if k != "(Todos)":
                            check_nomb_ver_ai_vars[k].set(0)
            else:
                check_nomb_ver_ai_vars["(Todos)"].set(0)

            selected = [k for k, v in check_nomb_ver_ai_vars.items() 
                       if v.get() == 1 and k != "(Todos)"]
            if check_nomb_ver_ai_vars["(Todos)"].get() == 1 or len(selected) == 0:
                nomb_ver_ai_button_text.set("(Todos)")
            elif len(selected) == 1:
                nomb_ver_ai_button_text.set(str(selected[0]))
            else:
                nomb_ver_ai_button_text.set(f"({len(selected)} seleccionados)")
            
            aplicar_filtros_ai_auto()

        cb_todos = ctk.CTkCheckBox(frame_inner, text="(Todos)", 
                                   variable=check_nomb_ver_ai_vars["(Todos)"],
                                   command=lambda: on_check_change_nomb_ver_ai("(Todos)"),
                                   font=("Segoe UI", 10, "bold"), text_color="#002e6d")
        cb_todos.pack(anchor="w", padx=8, pady=2)
        ttk.Separator(frame_inner, orient="horizontal").pack(fill="x", padx=5, pady=3)

        for val in valores_nomb_ver_ai:
            cb = ctk.CTkCheckBox(frame_inner, text=str(val), 
                                variable=check_nomb_ver_ai_vars[val],
                                command=lambda v=val: on_check_change_nomb_ver_ai(v), 
                                font=("Segoe UI", 10))
            cb.pack(anchor="w", padx=8, pady=2)

        top.update_idletasks()
        x = btn_nomb_ver_ai.winfo_rootx()
        y = btn_nomb_ver_ai.winfo_rooty() + btn_nomb_ver_ai.winfo_height()
        top.geometry(f"+{x}+{y}")
        top.deiconify()

        def close_dropdown(event=None):
            try:
                top.destroy()
            except:
                pass
            dropdown_nomb_ver_ai_win["win"] = None

        top.bind("<FocusOut>", close_dropdown)
        top.bind("<Escape>", close_dropdown)

    # BOTONES DE ACCIÓN AI
    botones_ai_container = ctk.CTkFrame(filtro_ai_frame, fg_color="transparent")
    botones_ai_container.pack(side="left", padx=(20, 5))

    # Botón LIMPIAR FILTROS AI
    def limpiar_filtros_ai():
        check_reimputado_ai_vars["(Todos)"].set(1)
        for k in check_reimputado_ai_vars:
            if k != "(Todos)":
                check_reimputado_ai_vars[k].set(0)
        reimputado_ai_button_text.set("(Todos)")

        check_corriente_ai_vars["(Todos)"].set(1)
        for k in check_corriente_ai_vars:
            if k != "(Todos)":
                check_corriente_ai_vars[k].set(0)
        corriente_ai_button_text.set("(Todos)")

        check_nomb_ver_ai_vars["(Todos)"].set(1)
        for k in check_nomb_ver_ai_vars:
            if k != "(Todos)":
                check_nomb_ver_ai_vars[k].set(0)
        nomb_ver_ai_button_text.set("(Todos)")
        
        aplicar_filtros_ai_auto()

    ctk.CTkButton(botones_ai_container, text="🔄 Limpiar", command=limpiar_filtros_ai,
                  fg_color="#F59E0B", hover_color="#D97706", font=("Segoe UI", 11, "bold"),
                  width=120, height=32).pack(side="left", padx=5)

    # Botón METAS AI
    def mostrar_metas_ai():
        messagebox.showinfo("Metas AI", "Funcionalidad de Metas AI en desarrollo")

    ctk.CTkButton(botones_ai_container, text="🎯 Metas", command=mostrar_metas_ai,
                  fg_color="#10B981", hover_color="#059669", font=("Segoe UI", 11, "bold"),
                  width=120, height=32).pack(side="left", padx=5)

    # Botón AVANCE DE METAS AI
    def ir_a_avance_metas_ai():
        """Función para ir al dashboard de avance de metas AI"""
        # Limpiar el dashboard actual
        for widget in dashboard_frame.winfo_children():
            widget.destroy()
        # Llamar al dashboard de avance de metas
        dashboard_avance_metas_ai()

    ctk.CTkButton(botones_ai_container, text="📊 Avance de Metas", command=ir_a_avance_metas_ai,
                  fg_color="#6366F1", hover_color="#4F46E5", font=("Segoe UI", 11, "bold"),
                  width=150, height=32).pack(side="left", padx=5)

    # Generar tabla AI inicial
    aplicar_filtros_ai_auto()

    # Forzar redraw
    def _force_redraw():
        try:
            if canvas.winfo_exists() and inner_frame.winfo_exists():
                inner_frame.update_idletasks()
                canvas.itemconfig(canvas_window, width=canvas.winfo_width())
                canvas.configure(scrollregion=canvas.bbox("all"))
                canvas.update()
                canvas.yview_moveto(0)
        except Exception:
            pass

    try:
        if canvas.winfo_exists():
            canvas.after(50, _force_redraw)
            canvas.after(200, _force_redraw)
            canvas.after(500, _force_redraw)
            _force_redraw()
    except Exception:
        pass

#OTRA PARTE
# ==========================
# FUNCIONES PREVIEW y OTROS
# ==========================
def actualizar_barra():
    try:
        barra_label.configure(text=f"Última actualización: {ultima_actualizacion}")
    except Exception:
        pass

def mostrar_datos():
    try:
        try:
            dashboard_frame.pack_forget()
        except Exception:
            pass
        preview_frame.pack(fill="both", expand=True, padx=10, pady=(5,10))

        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("SELECT NUM_ORD_FI, DDP_NOMBRE, Anio_Emis, Estado FROM fiscalizaciones1 LIMIT 20")
        filas = cursor.fetchall()
        conn.close()

        for item in tree.get_children():
            tree.delete(item)

        for fila in filas:
            tree.insert("", "end", values=fila)
    except Exception as e:
        messagebox.showerror("Error", f"No se pudieron cargar los datos:\n{e}")

def toggle_menu():
    global menu_visible
    if menu_visible:
        menu_frame.pack_forget()
        toggle_button.configure(text=">")
        menu_visible = False
    else:
        menu_frame.pack(side="left", fill="y")
        toggle_button.configure(text="<")
        menu_visible = True

def ocultar_menu():
    global menu_visible
    if menu_visible:
        menu_frame.pack_forget()
        toggle_button.configure(text=">")
        menu_visible = False

def ir_a_modulo():
    frame_inicio.pack_forget()
    header.pack_forget()
    header_modulo.pack(fill="x")
    frame_modulo.pack(fill="both", expand=True)
    app.state("zoomed")
    try:
        dashboard_frame.pack_forget()
    except Exception:
        pass
    preview_frame.pack(fill="both", expand=True, padx=10, pady=(5,10))
    if "banner_modulo_path" in config:
        mostrar_banner_modulo(config["banner_modulo_path"])
    mostrar_datos()

ctk.CTkButton(
    frame_inicio,
    text="Órdenes de Fiscalización y Acciones Inductivas",
    command=ir_a_modulo,
    width=350,
    fg_color=COLOR_PRIMARY,
    hover_color=COLOR_SECONDARY
).pack(pady=20)

ctk.CTkButton(
    frame_inicio,
    text="Otros",
    width=350,
    fg_color=COLOR_DANGER,
    hover_color="#B91C1C"
).pack(pady=20)

# Cargar logo y banners desde config.json
if "logo_path" in config:
    mostrar_logo(config["logo_path"])
if "banner_path" in config:
    mostrar_banner(config["banner_path"])
if "banner_modulo_path" in config:
    mostrar_banner_modulo(config["banner_modulo_path"])
if "banner_supervisores_path" in config:
    mostrar_banner_supervisores(config["banner_supervisores_path"])

# Inicializar ventana pequeña
app.geometry("550x375")
app.mainloop()