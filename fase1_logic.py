# fase1_logic.py
import json

def process_panel_data(project_data, hueco_data, raw_panels_data):
    """
    Procesa los datos y calcula coordenadas absolutas para el dibujo.
    """
    processed_data = {
        "project_data": project_data,
        "hueco_data": hueco_data,
        "panels": []
    }

    current_x_offset_base = 0.0
    
    base_panels = [p for p in raw_panels_data if p['tipo'] in ['fijo', 'puerta']]
    montante_panels = [p for p in raw_panels_data if p['tipo'] == 'montante']
    
    max_base_height = 0.0

    # --- Procesar Paneles Base ---
    for i, panel in enumerate(base_panels):
        panel_id = f"P{i+1}"
        panel_x = current_x_offset_base
        panel_y = 0.0 
        
        processed_panel = {
            "id": panel_id, "tipo": panel['tipo'], "material": panel['material'],
            "ancho": panel['ancho'], "alto": panel['alto'],
            "x_offset": panel_x, "y_offset": panel_y, "herrajes": []
        }
        
        for herraje in panel.get('herrajes', []):
            processed_herraje = process_single_herraje(herraje, panel['alto'], panel['ancho'], panel_x, panel_y)
            processed_panel["herrajes"].append(processed_herraje)
        
        processed_data["panels"].append(processed_panel)
        current_x_offset_base += panel['ancho']
        if panel['alto'] > max_base_height: max_base_height = panel['alto']

    # --- Procesar Montantes ---
    current_x_offset_montante = 0.0
    y_offset_montantes = max_base_height 

    for i, panel in enumerate(montante_panels):
        panel_id = f"M{i+1}"
        panel_x = current_x_offset_montante
        panel_y = y_offset_montantes
        
        processed_panel = {
            "id": panel_id, "tipo": panel['tipo'], "material": panel['material'],
            "ancho": panel['ancho'], "alto": panel['alto'],
            "x_offset": panel_x, "y_offset": panel_y, "herrajes": []
        }

        for herraje in panel.get('herrajes', []):
            processed_herraje = process_single_herraje(herraje, panel['alto'], panel['ancho'], panel_x, panel_y)
            processed_panel["herrajes"].append(processed_herraje)
        
        processed_data["panels"].append(processed_panel)
        current_x_offset_montante += panel['ancho']

    return processed_data


def process_single_herraje(herraje_raw, panel_alto, panel_ancho, panel_x_offset, panel_y_offset):
    """
    Calcula geometría exacta según las reglas de negocio.
    """
    processed_herraje = herraje_raw.copy()
    h_type = herraje_raw['tipo'].lower()

    # 1. PINZA Y BISAGRA
    if h_type in ["pinza", "bisagra"]:
        processed_herraje['ancho_real'] = 60.0
        processed_herraje['alto_real'] = 80.0
        processed_herraje['y_absolute_sup'] = panel_y_offset + panel_alto - herraje_raw['posiciones'][0]
        processed_herraje['y_absolute_inf'] = panel_y_offset + herraje_raw['posiciones'][1]
        if herraje_raw['lado'] == 'izquierda':
            processed_herraje['x_absolute'] = panel_x_offset
        else:
            processed_herraje['x_absolute'] = panel_x_offset + panel_ancho - 60.0

    elif h_type == "bisagra doble":
        processed_herraje['ancho_real'] = 120.0
        processed_herraje['alto_real'] = 80.0
        processed_herraje['y_absolute_sup'] = panel_y_offset + panel_alto - herraje_raw['posiciones'][0]
        processed_herraje['y_absolute_inf'] = panel_y_offset + herraje_raw['posiciones'][1]
        if herraje_raw['lado'] == 'izquierda':
            processed_herraje['x_absolute'] = panel_x_offset - 60.0
        else:
            processed_herraje['x_absolute'] = panel_x_offset + panel_ancho - 60.0

    elif h_type == "pomo":
        processed_herraje['diametro'] = 30.0
        processed_herraje['ancho_real'] = 30.0
        processed_herraje['alto_real'] = 30.0
        processed_herraje['y_absolute'] = herraje_raw['altura']
        dist = herraje_raw['distancia_borde']
        if herraje_raw['lado'] == 'izquierda':
            processed_herraje['x_absolute'] = panel_x_offset + dist
        else:
            processed_herraje['x_absolute'] = panel_x_offset + panel_ancho - dist

    elif h_type == "tirador":
        processed_herraje['ancho_real'] = 20.0  
        processed_herraje['alto_real'] = 250.0 
        processed_herraje['y_absolute'] = herraje_raw['altura'] 
        dist = herraje_raw['distancia_borde']
        if herraje_raw['lado'] == 'izquierda':
            processed_herraje['x_absolute'] = panel_x_offset + dist
        else:
            processed_herraje['x_absolute'] = panel_x_offset + panel_ancho - dist

    elif h_type == "toallero":
        processed_herraje['ancho_real'] = 450.0
        processed_herraje['alto_real'] = 25.0
        processed_herraje['y_absolute'] = 900.0
        processed_herraje['x_absolute'] = panel_x_offset + (panel_ancho - 450.0) / 2

    # 5. PERFILES (U, BURBUJA, VIERTE-AGUAS, PERFIL IMÁN 45º)
    elif h_type in ["u", "perfil burbuja", "perfil vierte-aguas", "perfil imán 45º"]:
        
        if h_type == "u": grosor = 20.0
        elif h_type == "perfil imán 45º": grosor = 20.0 
        else: grosor = 10.0
        
        lado = 'abajo' if h_type == "perfil vierte-aguas" else herraje_raw.get('lado', 'abajo')
        
        if lado in ['izquierda', 'derecha']:
            processed_herraje['ancho_real'] = grosor
            processed_herraje['alto_real'] = panel_alto
            processed_herraje['y_absolute'] = panel_y_offset
            
            if lado == 'izquierda':
                processed_herraje['x_absolute'] = panel_x_offset
            else: # Derecha
                processed_herraje['x_absolute'] = panel_x_offset + panel_ancho - grosor
        else: 
            processed_herraje['ancho_real'] = panel_ancho
            processed_herraje['alto_real'] = grosor
            processed_herraje['x_absolute'] = panel_x_offset
            if lado == 'abajo':
                 processed_herraje['y_absolute'] = panel_y_offset
            else: 
                 processed_herraje['y_absolute'] = panel_y_offset + panel_alto - grosor

    elif h_type == "taladro":
        dist_v = herraje_raw['pos_vertical_dist']
        if herraje_raw['pos_vertical_ref'] == 'alta':
             processed_herraje['y_absolute'] = panel_y_offset + panel_alto - dist_v
        else: 
             processed_herraje['y_absolute'] = panel_y_offset + dist_v
        dist_h = herraje_raw['pos_horizontal_dist']
        if herraje_raw['pos_horizontal_ref'] == 'izquierda':
             processed_herraje['x_absolute'] = panel_x_offset + dist_h
        else: 
             processed_herraje['x_absolute'] = panel_x_offset + panel_ancho - dist_h
        processed_herraje['diametro'] = herraje_raw['diametro']

    return processed_herraje