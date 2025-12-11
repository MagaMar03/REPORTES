# EXTRACCIÓN COMPLETA DEL CÓDIGO DEL BOTÓN RESUMEN - COMMIT ef4e1b5

## INFORMACIÓN DEL COMMIT
- **Commit Hash**: ef4e1b5e684ff002686c5b7d36d5e22bec7a52be
- **Autor**: Claude <noreply@anthropic.com>
- **Fecha**: Fri Dec 5 15:51:33 2025 +0000
- **Mensaje**: Implementar tooltips interactivos con mplcursors en todos los gráficos

---

## IMPORTACIÓN NECESARIA

```python
import mplcursors
```

---

## GRÁFICOS DEL BOTÓN "OF" (RESUMEN)

### 1. GRÁFICO: OFs DETERMINATIVAS (Pie Chart)
**Ubicación**: Línea 8189 del archivo CODIGOweb.PY

```python
# Agregar tooltips interactivos
cursor = mplcursors.cursor(wedges, hover=True)
@cursor.connect("add")
def on_add(sel):
    i = sel.index
    supervisor = df_det.iloc[i]['NOMBRE_SUPERVISOR']
    total = df_det.iloc[i]['total']
    porcentaje = (total / df_det['total'].sum()) * 100
    sel.annotation.set_text(
        f"{supervisor}\n"
        f"OFs: {total:,}\n"
        f"Porcentaje: {porcentaje:.1f}%"
    )
    sel.annotation.get_bbox_patch().set(
        boxstyle='round,pad=0.5',
        facecolor='#1E3A8A',
        alpha=0.9,
        edgecolor='white',
        linewidth=2
    )
    sel.annotation.set_fontsize(9)
    sel.annotation.set_color('white')

canvas_det = FigureCanvasTkAgg(fig_det, master=frame_determinativas)
canvas_det.draw()
canvas_det.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
```

**Descripción**:
- Muestra distribución de OFs Determinativas por supervisor
- Tooltip muestra: supervisor, cantidad de OFs y porcentaje

---

### 2. GRÁFICO: PROGRESO DETERMINATIVAS (Área)
**Ubicación**: Línea 8472 del archivo CODIGOweb.PY

```python
# Agregar tooltips interactivos
cursor = mplcursors.cursor(ax_prog, hover=True)
meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
@cursor.connect("add")
def on_add(sel):
    x_val = int(round(sel.target[0]))
    y_val = int(round(sel.target[1]))
    if 1 <= x_val <= 12:
        mes_nombre = meses_nombres[x_val - 1]
        sel.annotation.set_text(
            f"{mes_nombre}\n"
            f"Casos Resueltos: {y_val:,}"
        )
        sel.annotation.get_bbox_patch().set(
            boxstyle='round,pad=0.5',
            facecolor='#1E3A8A',
            alpha=0.9,
            edgecolor='white',
            linewidth=2
        )
        sel.annotation.set_fontsize(9)
        sel.annotation.set_color('white')

canvas_prog = FigureCanvasTkAgg(fig_prog, master=frame_progreso_det)
canvas_prog.draw()
canvas_prog.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
```

**Descripción**:
- Muestra progreso mensual de casos determinativos resueltos
- Tooltip muestra: mes y cantidad de casos resueltos

---

### 3. GRÁFICO: OFs NO DETERMINATIVAS (Pie Chart)
**Ubicación**: Línea 8669 del archivo CODIGOweb.PY

```python
# Agregar tooltips interactivos
cursor = mplcursors.cursor(wedges, hover=True)
@cursor.connect("add")
def on_add(sel):
    i = sel.index
    supervisor = df_no_det.iloc[i]['NOMBRE_SUPERVISOR']
    total = df_no_det.iloc[i]['total']
    porcentaje = (total / df_no_det['total'].sum()) * 100
    sel.annotation.set_text(
        f"{supervisor}\n"
        f"OFs: {total:,}\n"
        f"Porcentaje: {porcentaje:.1f}%"
    )
    sel.annotation.get_bbox_patch().set(
        boxstyle='round,pad=0.5',
        facecolor='#1E3A8A',
        alpha=0.9,
        edgecolor='white',
        linewidth=2
    )
    sel.annotation.set_fontsize(9)
    sel.annotation.set_color('white')

canvas_no_det = FigureCanvasTkAgg(fig_no_det, master=frame_no_determinativas)
canvas_no_det.draw()
canvas_no_det.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
```

**Descripción**:
- Muestra distribución de OFs No Determinativas por supervisor
- Tooltip muestra: supervisor, cantidad de OFs y porcentaje

---

### 4. GRÁFICO: PROGRESO NO DETERMINATIVAS (Área)
**Ubicación**: Línea 8951 del archivo CODIGOweb.PY

```python
# Agregar tooltips interactivos
cursor = mplcursors.cursor(ax_prog_no, hover=True)
meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
@cursor.connect("add")
def on_add(sel):
    x_val = int(round(sel.target[0]))
    y_val = int(round(sel.target[1]))
    if 1 <= x_val <= 12:
        mes_nombre = meses_nombres[x_val - 1]
        sel.annotation.set_text(
            f"{mes_nombre}\n"
            f"Casos Resueltos: {y_val:,}"
        )
        sel.annotation.get_bbox_patch().set(
            boxstyle='round,pad=0.5',
            facecolor='#1E3A8A',
            alpha=0.9,
            edgecolor='white',
            linewidth=2
        )
        sel.annotation.set_fontsize(9)
        sel.annotation.set_color('white')

canvas_prog_no = FigureCanvasTkAgg(fig_prog_no, master=frame_progreso_no_det)
canvas_prog_no.draw()
canvas_prog_no.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
```

**Descripción**:
- Muestra progreso mensual de casos no determinativos resueltos
- Tooltip muestra: mes y cantidad de casos resueltos

---

### 5. GRÁFICO: DISTRIBUCIÓN DE TIPOS STOCK (Pie Chart)
**Ubicación**: Línea 9151 del archivo CODIGOweb.PY

```python
# Agregar tooltips interactivos
cursor = mplcursors.cursor(wedges, hover=True)
@cursor.connect("add")
def on_add(sel):
    i = sel.index
    tipo = df_stock.iloc[i]['tipo']
    total = df_stock.iloc[i]['total']
    porcentaje = (total / df_stock['total'].sum()) * 100
    sel.annotation.set_text(
        f"Tipo {tipo}\n"
        f"Cantidad: {total:,}\n"
        f"Porcentaje: {porcentaje:.1f}%"
    )
    sel.annotation.get_bbox_patch().set(
        boxstyle='round,pad=0.5',
        facecolor='#1E3A8A',
        alpha=0.9,
        edgecolor='white',
        linewidth=2
    )
    sel.annotation.set_fontsize(9)
    sel.annotation.set_color('white')

canvas_stock = FigureCanvasTkAgg(fig_stock, master=frame_stock_pastel)
canvas_stock.draw()
canvas_stock.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
```

**Descripción**:
- Muestra distribución de stock por tipo
- Tooltip muestra: tipo, cantidad y porcentaje

---

### 6. GRÁFICO: STOCK POR TIPO Y MES (Barras Agrupadas)
**Ubicación**: Línea 9482 del archivo CODIGOweb.PY

```python
# Agregar tooltips interactivos
cursor = mplcursors.cursor(ax_barras, hover=True)
meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
@cursor.connect("add")
def on_add(sel):
    bar = sel.artist
    label = bar.get_label()
    height = sel.target[1]
    x_index = int(round(sel.target[0]))
    if 0 <= x_index < len(meses_nombres):
        mes_nombre = meses_nombres[x_index]
        sel.annotation.set_text(
            f"{label} - {mes_nombre}\n"
            f"Cantidad: {int(height):,}"
        )
        sel.annotation.get_bbox_patch().set(
            boxstyle='round,pad=0.5',
            facecolor='#1E3A8A',
            alpha=0.9,
            edgecolor='white',
            linewidth=2
        )
        sel.annotation.set_fontsize(9)
        sel.annotation.set_color('white')

canvas_barras = FigureCanvasTkAgg(fig_barras, master=frame_stock_barras)
canvas_barras.draw()
canvas_barras.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
```

**Descripción**:
- Muestra stock distribuido por tipo y mes
- Tooltip muestra: tipo, mes y cantidad

---

### 7. GRÁFICO: RENDIMIENTO (Barras Agrupadas)
**Ubicación**: Línea 9839 del archivo CODIGOweb.PY

```python
# Agregar tooltips interactivos
cursor = mplcursors.cursor(ax_rend, hover=True)
meses_nombres = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
               'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
@cursor.connect("add")
def on_add(sel):
    bar = sel.artist
    label = bar.get_label()
    height = sel.target[1]
    x_index = int(round(sel.target[0]))
    if 0 <= x_index < len(meses_nombres):
        mes_nombre = meses_nombres[x_index]
        sel.annotation.set_text(
            f"{label} - {mes_nombre}\n"
            f"Monto: S/ {int(height):,}"
        )
        sel.annotation.get_bbox_patch().set(
            boxstyle='round,pad=0.5',
            facecolor='#1E3A8A',
            alpha=0.9,
            edgecolor='white',
            linewidth=2
        )
        sel.annotation.set_fontsize(9)
        sel.annotation.set_color('white')

canvas_rend = FigureCanvasTkAgg(fig_rend, master=frame_rendimiento)
canvas_rend.draw()
canvas_rend.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
```

**Descripción**:
- Muestra rendimiento mensual por categoría
- Tooltip muestra: categoría, mes y monto en soles

---

## GRÁFICOS DEL BOTÓN "AIS" (AUDITORÍAS INTERNAS)

### 8. GRÁFICO: AIs ASIGNADAS POR TIPO (Barras Verticales)
**Ubicación**: Línea 10289 del archivo CODIGOweb.PY

```python
# Agregar tooltips interactivos
cursor = mplcursors.cursor(bars, hover=True)
@cursor.connect("add")
def on_add(sel):
    i = sel.index
    tipo_ai = df.iloc[i]['DES_TIPO_AI']
    total = df.iloc[i]['total']
    sel.annotation.set_text(
        f"{tipo_ai}\n"
        f"Cantidad: {total:,} AIs"
    )
    sel.annotation.get_bbox_patch().set(
        boxstyle='round,pad=0.5',
        facecolor='#1E3A8A',
        alpha=0.9,
        edgecolor='white',
        linewidth=2
    )
    sel.annotation.set_fontsize(9)
    sel.annotation.set_color('white')

canvas = FigureCanvasTkAgg(fig, frame_ais_asignadas)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
```

**Descripción**:
- Muestra cantidad de AIs asignadas por tipo
- Tooltip muestra: tipo de AI y cantidad

---

### 9. GRÁFICO: AIs PENDIENTES POR SUPERVISOR (Barras Horizontales)
**Ubicación**: Línea 10519 del archivo CODIGOweb.PY

```python
# Agregar tooltips interactivos
cursor = mplcursors.cursor(bars, hover=True)
@cursor.connect("add")
def on_add(sel):
    i = sel.index
    supervisor = df.iloc[i]['DES_NOMB_SUP']
    total = df.iloc[i]['total']
    sel.annotation.set_text(
        f"{supervisor}\n"
        f"AIs Pendientes: {total:,}"
    )
    sel.annotation.get_bbox_patch().set(
        boxstyle='round,pad=0.5',
        facecolor='#1E3A8A',
        alpha=0.9,
        edgecolor='white',
        linewidth=2
    )
    sel.annotation.set_fontsize(9)
    sel.annotation.set_color('white')

canvas = FigureCanvasTkAgg(fig, frame_ais_pendientes)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
```

**Descripción**:
- Muestra AIs pendientes por supervisor
- Tooltip muestra: supervisor y cantidad de AIs pendientes

---

### 10. GRÁFICO: AIs TERMINADAS POR TIPO (Pie Chart)
**Ubicación**: Línea 10719 del archivo CODIGOweb.PY

```python
# Agregar tooltips interactivos
cursor = mplcursors.cursor(wedges, hover=True)
@cursor.connect("add")
def on_add(sel):
    i = sel.index
    tipo_ai = df.iloc[i]['DES_TIPO_AI']
    total = df.iloc[i]['total']
    porcentaje = (total / df['total'].sum()) * 100
    sel.annotation.set_text(
        f"{tipo_ai}\n"
        f"Cantidad: {total:,}\n"
        f"Porcentaje: {porcentaje:.1f}%"
    )
    sel.annotation.get_bbox_patch().set(
        boxstyle='round,pad=0.5',
        facecolor='#1E3A8A',
        alpha=0.9,
        edgecolor='white',
        linewidth=2
    )
    sel.annotation.set_fontsize(9)
    sel.annotation.set_color('white')

canvas = FigureCanvasTkAgg(fig, frame_ais_terminadas)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
```

**Descripción**:
- Muestra distribución de AIs terminadas por tipo
- Tooltip muestra: tipo de AI, cantidad y porcentaje

---

### 11. GRÁFICO: RENDIMIENTO POR AUDITOR (Barras Horizontales)
**Ubicación**: Línea 10920 del archivo CODIGOweb.PY

```python
# Agregar tooltips interactivos
cursor = mplcursors.cursor(bars, hover=True)
@cursor.connect("add")
def on_add(sel):
    i = sel.index
    auditor = df.iloc[i]['DES_NOMB_VER']
    total = df.iloc[i]['total']
    sel.annotation.set_text(
        f"{auditor}\n"
        f"AIs Completadas: {total:,}"
    )
    sel.annotation.get_bbox_patch().set(
        boxstyle='round,pad=0.5',
        facecolor='#1E3A8A',
        alpha=0.9,
        edgecolor='white',
        linewidth=2
    )
    sel.annotation.set_fontsize(9)
    sel.annotation.set_color('white')

canvas = FigureCanvasTkAgg(fig, frame_ais_rendimiento)
canvas.draw()
canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=5)
```

**Descripción**:
- Muestra rendimiento de auditores por AIs completadas
- Tooltip muestra: nombre del auditor y cantidad de AIs completadas

---

## CARACTERÍSTICAS COMUNES DE LOS TOOLTIPS

Todos los tooltips implementados comparten estas características:

1. **Activación**: `hover=True` - Se activan al pasar el mouse
2. **Estilo del fondo**:
   - Color: `#1E3A8A` (azul oscuro)
   - Transparencia: `alpha=0.9`
   - Borde: blanco con grosor 2
   - Forma: redondeada con padding 0.5
3. **Texto**:
   - Color: blanco
   - Tamaño de fuente: 9
   - Formato de números con separadores de miles (`:,`)
4. **Información contextual**: Varía según el tipo de gráfico

---

## RESUMEN DE GRÁFICOS POR BOTÓN

### BOTÓN "OF" (RESUMEN) - 7 GRÁFICOS:
1. OFs Determinativas (Pie)
2. Progreso Determinativas (Área)
3. OFs No Determinativas (Pie)
4. Progreso No Determinativas (Área)
5. Distribución Tipos Stock (Pie)
6. Stock por Tipo y Mes (Barras)
7. Rendimiento (Barras)

### BOTÓN "AIS" - 4 GRÁFICOS:
1. AIs Asignadas por Tipo (Barras)
2. AIs Pendientes por Supervisor (Barras Horizontales)
3. AIs Terminadas por Tipo (Pie)
4. Rendimiento por Auditor (Barras Horizontales)

**TOTAL: 11 GRÁFICOS INTERACTIVOS CON TOOLTIPS**
