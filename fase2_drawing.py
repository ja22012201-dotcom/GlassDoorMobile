# fase2_drawing.py
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import black, white, HexColor

# Conjuntos globales para evitar cotas duplicadas
drawn_dimensions_y = set()
drawn_dimensions_x = set()

def get_herraje_color(h_type):
    """Devuelve el objeto Color de ReportLab según el tipo de herraje."""
    t = h_type.lower()
    
    # 1. Marrón / Bronce
    if t in ['pomo', 'tirador', 'toallero']:
        return HexColor('#A35A00') 

    # 2. Verde Claro
    elif t == 'perfil vierte-aguas':
        return HexColor('#90EE90') 
        
    # 3. Azul Claro
    elif t == 'pinza':
        return HexColor('#ADD8E6') 
        
    # 4. Azul un poco más oscuro
    elif t in ['bisagra', 'bisagra doble']:
        return HexColor('#6495ED') 
        
    # 5. Rojo Claro
    elif t == 'u':
        return HexColor('#FFB6C1') 
        
    # 6. Amarillo Intenso
    elif t == 'perfil burbuja':
        return HexColor('#FFDE21')

    # 7. NARANJA
    elif t == 'perfil imán 45º':
        return HexColor('#FF6600')
        
    # 8. Gris Claro
    elif t == 'taladro':
        return HexColor('#D3D3D3') 
        
    # Default
    return HexColor('#FFFFFF')

def draw_text_with_background(c, x, y, text, font="Helvetica", size=6):
    """Dibuja texto con un fondo blanco para no pisar líneas."""
    text_width = c.stringWidth(text, font, size)
    text_height = size 
    
    c.setFillColor(white)
    # Ajuste fino del rectángulo centrado
    rect_x = x - (text_width / 2) - 1
    rect_y = y - (text_height / 2) + 1 
    c.rect(rect_x, rect_y, text_width + 2, text_height + 1, fill=1, stroke=0)
    
    c.setFillColor(black)
    c.drawCentredString(x, y, text)

def draw_dimension_line(c, x1, y1, x2, y2, text, offset=10, orientation='vertical'):
    """Dibuja una línea de cota con fondo en el texto para legibilidad."""
    c.setLineWidth(0.5)
    c.setStrokeColor(black) 
    c.setFont("Helvetica", 6)
    
    # Clave única para evitar redibujar la misma cota
    dim_key = (round(x1), round(y1), round(x2), round(y2), round(offset))
    
    if orientation == 'vertical':
        if dim_key in drawn_dimensions_y: return
        drawn_dimensions_y.add(dim_key)
        
        dim_x = x1 + offset
        # Línea principal vertical
        c.line(dim_x, y1, dim_x, y2) 
        # Patas horizontales (extremos)
        c.line(x1, y1, dim_x + (2 if offset > 0 else -2), y1)
        c.line(x2, y2, dim_x + (2 if offset > 0 else -2), y2)
        
        c.saveState()
        text_offset_x = 4 if offset > 0 else -4
        c.translate(dim_x + text_offset_x, (y1 + y2) / 2)
        c.rotate(90)
        draw_text_with_background(c, 0, 0, text)
        c.restoreState()
        
    else: # Horizontal
        if dim_key in drawn_dimensions_x: return
        drawn_dimensions_x.add(dim_key)
        
        dim_y = y1 - offset
        # Línea principal horizontal
        c.line(x1, dim_y, x2, dim_y)
        # Patas verticales
        c.line(x1, y1, x1, dim_y + (2 if offset < 0 else -2))
        c.line(x2, y2, x2, dim_y + (2 if offset < 0 else -2))
        
        text_offset_y = -8 if offset > 0 else 4
        draw_text_with_background(c, (x1 + x2) / 2, dim_y + text_offset_y, text)

def generate_pdf_drawing(processed_data, file_path):
    global drawn_dimensions_y, drawn_dimensions_x
    drawn_dimensions_y = set()
    drawn_dimensions_x = set()
    
    c = canvas.Canvas(file_path, pagesize=landscape(A4))
    width, height = landscape(A4)

    # --- 1. CONFIGURACIÓN DEL ÁREA DE DIBUJO ---
    margin_x = 15 * mm
    margin_y = 15 * mm
    
    # Reservamos espacio a la derecha para la ficha técnica (35% del ancho total aprox)
    drawing_area_width = (width - 2 * margin_x) * 0.65 
    drawing_area_height = height - 2 * margin_y - 20 * mm # Margen extra abajo para cajetín

    hueco_ancho = processed_data['hueco_data']['ancho']
    hueco_alto = processed_data['hueco_data']['alto']
    
    # Calcular escala (0.85 para dejar aire para las cotas)
    scale = min(drawing_area_width / hueco_ancho, drawing_area_height / hueco_alto) * 0.85
    
    # Dimensiones reales del dibujo en el papel
    drawn_w = hueco_ancho * scale
    drawn_h = hueco_alto * scale
    
    # --- 2. CÁLCULO DEL CENTRADO (ORIGEN) ---
    # Centramos el rectángulo de dibujo en el área disponible
    origin_x = margin_x + 20 * mm + (drawing_area_width - drawn_w) / 2
    origin_y = margin_y + 30 * mm + (drawing_area_height - drawn_h) / 2
    
    # --- 3. DIBUJAR HUECO (Contorno General) ---
    c.setStrokeColor(black)
    c.setLineWidth(1.5)
    c.setFillColor(black) 
    c.rect(origin_x, origin_y, drawn_w, drawn_h, fill=0, stroke=1)
    
    # Cotas TOTALES del hueco (Capa más lejana: offsets grandes)
    # Total Ancho (Abajo, muy separado)
    draw_dimension_line(c, origin_x, origin_y, origin_x + drawn_w, origin_y, 
                        f"TOTAL: {hueco_ancho:.0f}", offset=40, orientation='horizontal')
    
    # Total Alto (Izquierda, muy separado para no chocar con paneles)
    draw_dimension_line(c, origin_x, origin_y, origin_x, origin_y + drawn_h, 
                        f"TOTAL: {hueco_alto:.0f}", offset=-50, orientation='vertical')

    # === PASADA 1: GEOMETRÍA Y COLORES ===
    panels = processed_data['panels']
    
    for panel in panels:
        px = origin_x + (panel['x_offset'] * scale)
        py = origin_y + (panel['y_offset'] * scale)
        pw = panel['ancho'] * scale
        ph = panel['alto'] * scale

        # Panel Vidrio
        c.setLineWidth(0.5)
        c.setStrokeColor(black)
        c.rect(px, py, pw, ph, fill=0, stroke=1)
        
        # Etiqueta Panel (Centrada)
        draw_text_with_background(c, px + pw/2, py + ph/2, f"{panel['id']}", size=8, font="Helvetica-Bold")

        # Dibujar Herrajes (Geometría)
        for h in panel['herrajes']:
            h_type = h['tipo'].lower()
            fill_col = get_herraje_color(h_type)
            c.setFillColor(fill_col)
            c.setStrokeColor(black) 
            c.setLineWidth(0.5)

            if h_type in ["pinza", "bisagra", "bisagra doble"]:
                w_h = h['ancho_real'] * scale
                h_h = h['alto_real'] * scale
                yx_sup = origin_y + (h['y_absolute_sup'] * scale) - h_h
                xx = origin_x + (h['x_absolute'] * scale)
                c.rect(xx, yx_sup, w_h, h_h, fill=1, stroke=1)
                yx_inf = origin_y + (h['y_absolute_inf'] * scale)
                c.rect(xx, yx_inf, w_h, h_h, fill=1, stroke=1)

            elif h_type == "pomo":
                cx = origin_x + (h['x_absolute'] * scale)
                cy = origin_y + (h['y_absolute'] * scale)
                r = (h['diametro'] / 2) * scale
                c.circle(cx, cy, r, fill=1, stroke=1)

            elif h_type == "tirador":
                w_h = h['ancho_real'] * scale
                h_h = h['alto_real'] * scale
                cx = origin_x + (h['x_absolute'] * scale)
                cy = origin_y + (h['y_absolute'] * scale)
                c.rect(cx - w_h/2, cy - h_h/2, w_h, h_h, fill=1, stroke=1)

            elif h_type == "toallero":
                bx = origin_x + (h['x_absolute'] * scale)
                cy = origin_y + (h['y_absolute'] * scale)
                w_h = h['ancho_real'] * scale
                h_h = h['alto_real'] * scale
                c.rect(bx, cy - h_h/2, w_h, h_h, fill=1, stroke=1)

            elif h_type in ["u", "perfil burbuja", "perfil vierte-aguas", "perfil imán 45º"]:
                bx = origin_x + (h['x_absolute'] * scale)
                by = origin_y + (h['y_absolute'] * scale)
                w_h = h['ancho_real'] * scale
                h_h = h['alto_real'] * scale
                c.rect(bx, by, w_h, h_h, fill=1, stroke=1)

            elif h_type == "taladro":
                cx = origin_x + (h['x_absolute'] * scale)
                cy = origin_y + (h['y_absolute'] * scale)
                r = (h['diametro'] / 2) * scale
                c.circle(cx, cy, r, fill=1, stroke=1)

    # === PASADA 2: COTAS ===
    # Estrategia de capas: Panel (cerca), Herraje (medio), Totales (lejos)
    
    for i, panel in enumerate(panels):
        px = origin_x + (panel['x_offset'] * scale)
        py = origin_y + (panel['y_offset'] * scale)
        pw = panel['ancho'] * scale
        ph = panel['alto'] * scale
        
        # 1. Cota Ancho Panel (Abajo, cerca)
        draw_dimension_line(c, px, py, px + pw, py, f"{panel['ancho']:.0f}", offset=15, orientation='horizontal')
        
        # 2. Cota Alto Panel (Izquierda o Derecha según convenga, cerca)
        # Si es el último panel, cota a la derecha. Si hay cambio de altura, dibujamos.
        draw_height = False
        if i == len(panels) - 1:
            draw_height = True
        else:
            next_panel = panels[i + 1]
            if abs(panel['alto'] - next_panel['alto']) > 1.0: 
                draw_height = True
                
        if draw_height:
            # Cota altura panel a la derecha (offset positivo)
            draw_dimension_line(c, px + pw, py, px + pw, py + ph, f"{panel['alto']:.0f}", offset=15, orientation='vertical')
        else:
            # Si no es el último y es igual al siguiente, a veces conviene ponerla a la izquierda
            # Para simplificar y evitar cruces con Totales (que están muy a la izq -50), 
            # ponemos la cota individual a la izquierda pero cerca (-15)
            if i == 0: # Solo para el primer panel si no cambia altura
                 draw_dimension_line(c, px, py, px, py + ph, f"{panel['alto']:.0f}", offset=-15, orientation='vertical')

        # 3. Cotas Herrajes
        for h in panel['herrajes']:
            h_type = h['tipo'].lower()
            
            if h_type in ["pinza", "bisagra", "bisagra doble"]:
                w_h = h['ancho_real'] * scale
                h_h = h['alto_real'] * scale
                yx_sup = origin_y + (h['y_absolute_sup'] * scale) - h_h
                yx_inf = origin_y + (h['y_absolute_inf'] * scale)
                xx = origin_x + (h['x_absolute'] * scale)
                
                lado = h.get('lado', 'izquierda')
                
                # Inteligencia de Offset para herrajes:
                # Si está a la izquierda, offset negativo (pero más allá de la cota de panel -15) -> -25
                # Si está a la derecha, offset positivo (más allá de la cota de panel 15) -> ancho + 25
                offset_cota = -28 if lado == 'izquierda' else (w_h + 28)

                draw_dimension_line(c, xx, py + ph, xx, yx_sup + h_h, 
                                    f"{panel['alto'] - (h['y_absolute_sup'] - panel['y_offset']):.0f}", 
                                    offset=offset_cota, orientation='vertical')
                draw_dimension_line(c, xx, py, xx, yx_inf, 
                                    f"{h['y_absolute_inf'] - panel['y_offset']:.0f}", 
                                    offset=offset_cota, orientation='vertical')

            elif h_type == "pomo":
                cx = origin_x + (h['x_absolute'] * scale)
                cy = origin_y + (h['y_absolute'] * scale)
                draw_dimension_line(c, cx, origin_y, cx, cy, f"{h['y_absolute']:.0f}", offset=20, orientation='vertical')

            elif h_type == "tirador":
                cx = origin_x + (h['x_absolute'] * scale)
                cy = origin_y + (h['y_absolute'] * scale)
                draw_dimension_line(c, cx, origin_y, cx, cy, f"{h['y_absolute']:.0f}", offset=20, orientation='vertical')

            elif h_type == "toallero":
                bx = origin_x + (h['x_absolute'] * scale)
                cy = origin_y + (h['y_absolute'] * scale)
                w_h = h['ancho_real'] * scale
                # Cota al centro del toallero desde el suelo
                draw_dimension_line(c, bx + w_h/2, origin_y, bx + w_h/2, cy, f"{h['y_absolute']:.0f}", offset=30, orientation='vertical')

            elif h_type == "taladro":
                cx = origin_x + (h['x_absolute'] * scale)
                cy = origin_y + (h['y_absolute'] * scale)
                pw = panel['ancho'] * scale
                ph = panel['alto'] * scale
                
                ref_h = h.get('pos_horizontal_ref', 'izquierda')
                target_x = px if ref_h == 'izquierda' else px + pw
                # Cotas horizontales internas (offset pequeño negativo o positivo según lado)
                off_h = -10 if ref_h=='izquierda' else 10
                draw_dimension_line(c, target_x, cy, cx, cy, 
                                    f"{h['pos_horizontal_dist']:.0f}", 
                                    offset=off_h, orientation='horizontal')

                ref_v = h.get('pos_vertical_ref', 'baja')
                target_y = py if ref_v == 'baja' else py + ph
                # Cotas verticales internas
                off_v = -10 if ref_v=='baja' else 10
                draw_dimension_line(c, cx, target_y, cx, cy, 
                                    f"{h['pos_vertical_dist']:.0f}", 
                                    offset=off_v, orientation='vertical')

    # --- FICHA TÉCNICA (Barra Lateral Derecha) ---
    # Posicionamos la ficha aprovechando el espacio reservado (35%)
    ficha_x = width - (width * 0.30) - margin_x 
    fy = height - margin_y
    
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 12)
    c.drawString(ficha_x, fy, "FICHA TÉCNICA")
    fy -= 8*mm
    
    c.setFont("Helvetica", 9)
    c.drawString(ficha_x, fy, f"Hueco: {hueco_ancho:.0f} x {hueco_alto:.0f} mm")
    fy -= 8*mm
    
    # Listado de Vidrios
    for p in processed_data['panels']:
        c.setFont("Helvetica-Bold", 9)
        c.drawString(ficha_x, fy, f"{p['id']}: {p['tipo'].capitalize()} ({p['ancho']:.0f}x{p['alto']:.0f})")
        fy -= 4*mm
        c.setFont("Helvetica", 8)
        c.drawString(ficha_x, fy, f"Mat: {p['material']}")
        fy -= 5*mm
        
    fy -= 5*mm
    c.setStrokeColor(black)
    c.line(ficha_x, fy, width-margin_x, fy)
    fy -= 5*mm
    
    c.setFont("Helvetica-Bold", 9)
    c.drawString(ficha_x, fy, "RESUMEN HERRAJES:")
    fy -= 6*mm
    
    # Color Herrajes
    color_h = processed_data['hueco_data'].get('color_herrajes', 'Sin definir')
    c.setFont("Helvetica-Bold", 8)
    c.drawString(ficha_x, fy, f"COLOR DE LOS HERRAJES: {color_h.upper()}")
    fy -= 5*mm

    # Conteo de Herrajes
    total_herrajes = {}
    for p in processed_data['panels']:
        for h in p['herrajes']:
            h_type_raw = h['tipo'].lower()
            name = h_type_raw.capitalize()
            
            if h_type_raw == 'taladro': name += f" Ø{h.get('diametro',0):.0f}"
            elif h_type_raw == 'bisagra doble': name += f" ({h.get('apertura', '180')}º)"
            
            # Conteo doble para juegos
            count_add = 2 if h_type_raw in ['pinza', 'bisagra', 'bisagra doble'] else 1
            
            key = (name, h_type_raw)
            if key not in total_herrajes:
                total_herrajes[key] = 0
            total_herrajes[key] += count_add

    c.setFont("Helvetica", 8)
    for (name, raw_type), count in total_herrajes.items():
        text_str = f"{count} ud. {name}"
        c.drawString(ficha_x, fy, text_str)
        
        # Tira de Color
        text_w = c.stringWidth(text_str, "Helvetica", 8)
        swatch_x = ficha_x + text_w + 5
        swatch_y = fy - 1
        swatch_w = 15
        swatch_h = 8
        
        color_fill = get_herraje_color(raw_type)
        c.setFillColor(color_fill)
        c.setStrokeColor(black)
        c.setLineWidth(0.5)
        c.rect(swatch_x, swatch_y, swatch_w, swatch_h, fill=1, stroke=1)
        
        c.setFillColor(black)
        fy -= 5*mm

    # --- CAJETÍN "DATOS DEL PROYECTO" (Abajo Derecha) ---
    cajetin_w = 80*mm
    cajetin_h = 25*mm
    cajetin_x = width - margin_x - cajetin_w
    cajetin_y = margin_y
    
    c.setStrokeColor(black)
    c.setLineWidth(1)
    c.rect(cajetin_x, cajetin_y, cajetin_w, cajetin_h, stroke=1, fill=0)
    
    c.setFont("Helvetica-Bold", 10)
    c.drawString(cajetin_x + 2*mm, cajetin_y + cajetin_h - 5*mm, "DATOS DEL PROYECTO")
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(cajetin_x + 2*mm, cajetin_y + 13*mm, "PROYECTO:")
    c.setFont("Helvetica", 8)
    c.drawString(cajetin_x + 25*mm, cajetin_y + 13*mm, processed_data['project_data']['proyecto'].upper())
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(cajetin_x + 2*mm, cajetin_y + 8*mm, "CLIENTE:")
    c.setFont("Helvetica", 8)
    c.drawString(cajetin_x + 25*mm, cajetin_y + 8*mm, processed_data['project_data']['cliente'].upper())
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(cajetin_x + 2*mm, cajetin_y + 3*mm, "AUTOR/TALLER:")
    c.setFont("Helvetica", 8)
    c.drawString(cajetin_x + 25*mm, cajetin_y + 3*mm, processed_data['project_data']['autor'].upper())

    c.save()