import os
import json
import sys
from datetime import datetime
from functools import partial
from kivymd.app import MDApp
from kivymd.uix.screen import MDScreen
from kivymd.uix.button import MDRectangleFlatButton, MDRaisedButton, MDFillRoundFlatButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.dialog import MDDialog
from kivymd.uix.list import OneLineAvatarIconListItem, TwoLineAvatarIconListItem, IconLeftWidget
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.toolbar import MDTopAppBar
from kivy.lang import Builder
from kivy.properties import ObjectProperty, DictProperty, ListProperty, StringProperty, NumericProperty, BooleanProperty
from kivy.clock import Clock
from kivy.uix.screenmanager import ScreenManager
from kivy.metrics import dp, Metrics, sp
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Rectangle, Ellipse
from kivy.utils import get_color_from_hex, platform
from kivy.core.window import Window

# --- CONFIGURACIÓN DE PANTALLA ---
# Redimensionar la ventana cuando sale el teclado
Window.softinput_mode = 'resize'

# ¡IMPORTANTE! Hemos quitado "Metrics.density = 0.85".
# Ahora usamos la densidad nativa del móvil para que el texto se vea GRANDE y legible.
# Como tenemos ScrollView, no importa si ocupa más espacio vertical.

import fase1_logic
import fase2_drawing

# --- DISEÑO KV INTEGRADO (Textos agrandados) ---
KV_DESIGN = '''
<ProjectDataScreen>:
    name: 'project_data_screen'
    MDBoxLayout:
        orientation: 'vertical'
        
        MDTopAppBar:
            title: app.current_screen_title
            elevation: 4
            left_action_items: [['arrow-left', lambda x: app.go_back()]] if app.can_go_back else []
            right_action_items: [['information-outline', lambda x: app.show_info_dialog()]]

        MDScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(20)
                spacing: dp(30)

                MDLabel:
                    text: "Datos del Proyecto"
                    halign: "center"
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding_y: dp(15)

                MDRaisedButton:
                    text: "Cargar Proyecto Guardado"
                    icon: "folder-open"
                    pos_hint: {'center_x': 0.5}
                    on_release: app.open_load_dialog()
                    md_bg_color: app.theme_cls.accent_color
                    font_size: "18sp"
                    padding: dp(20)

                MDBoxLayout:
                    size_hint_y: None
                    height: dp(20)

                MDTextField:
                    id: project_name_input
                    mode: "fill"
                    hint_text: "Nombre del Proyecto"
                    required: True
                    max_text_length: 50
                    font_size: "18sp"
                    on_text: app.project_data['proyecto'] = self.text
                    size_hint_y: None
                    height: dp(70)

                MDTextField:
                    id: client_input
                    mode: "fill"
                    hint_text: "Cliente"
                    max_text_length: 50
                    font_size: "18sp"
                    on_text: app.project_data['cliente'] = self.text
                    size_hint_y: None
                    height: dp(70)

                MDTextField:
                    id: author_input
                    mode: "fill"
                    hint_text: "Autor / Taller"
                    max_text_length: 50
                    font_size: "18sp"
                    on_text: app.project_data['autor'] = self.text
                    size_hint_y: None
                    height: dp(70)

                MDBoxLayout:
                    adaptive_height: True
                    spacing: dp(20)
                    padding: dp(10), dp(30), dp(10), dp(50)
                    MDRectangleFlatButton:
                        text: "Salir"
                        font_size: "16sp"
                        on_release: app.exit_app()
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    MDRectangleFlatButton:
                        text: "Continuar"
                        font_size: "16sp"
                        on_release: root.save_and_next()
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

<HoleDataScreen>:
    name: 'hole_data_screen'
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: app.current_screen_title
            elevation: 4
            left_action_items: [['arrow-left', lambda x: app.go_back()]] if app.can_go_back else []
            right_action_items: [['information-outline', lambda x: app.show_info_dialog()]]

        MDScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(20)
                spacing: dp(30)

                MDLabel:
                    text: "Medidas del Hueco"
                    halign: "center"
                    font_style: "H5"
                    size_hint_y: None
                    height: self.texture_size[1]
                    padding_y: dp(15)

                MDTextField:
                    id: ancho_hueco_input
                    mode: "fill"
                    hint_text: "Ancho total (mm)"
                    input_type: "number"
                    required: True
                    font_size: "18sp"
                    on_text: root.validate_and_set_float(self, 'ancho', app.hueco_data)
                    size_hint_y: None
                    height: dp(70)
                
                MDTextField:
                    id: alto_hueco_input
                    mode: "fill"
                    hint_text: "Alto total (mm)"
                    input_type: "number"
                    required: True
                    font_size: "18sp"
                    on_text: root.validate_and_set_float(self, 'alto', app.hueco_data)
                    size_hint_y: None
                    height: dp(70)

                MDTextField:
                    id: color_herrajes_input
                    mode: "fill"
                    hint_text: "Color de los herrajes"
                    text: app.hueco_data['color_herrajes']
                    font_size: "18sp"
                    on_text: app.hueco_data['color_herrajes'] = self.text
                    size_hint_y: None
                    height: dp(70)

                MDBoxLayout:
                    adaptive_height: True
                    spacing: dp(20)
                    padding: dp(10), dp(30), dp(10), dp(50)
                    MDRectangleFlatButton:
                        text: "Atrás"
                        font_size: "16sp"
                        on_release: app.show_screen('project_data_screen')
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    MDRectangleFlatButton:
                        text: "Aceptar"
                        font_size: "16sp"
                        on_release: root.save_and_next()
                        pos_hint: {'center_x': 0.5, 'center_y': 0.5}

<PanelDataScreen>:
    name: 'panel_data_screen'
    MDBoxLayout:
        orientation: 'vertical'

        MDTopAppBar:
            title: app.current_screen_title
            elevation: 4
            left_action_items: [['arrow-left', lambda x: app.go_back()]] if app.can_go_back else []
            right_action_items: [['information-outline', lambda x: app.show_info_dialog()]]

        MDScrollView:
            MDBoxLayout:
                orientation: 'vertical'
                size_hint_y: None
                height: self.minimum_height
                padding: dp(10)
                spacing: dp(15)

                MDCard:
                    orientation: 'vertical'
                    size_hint_y: None
                    height: dp(250)
                    elevation: 2
                    padding: dp(5)
                    radius: [10, 10, 10, 10]
                    md_bg_color: [0.9, 0.9, 0.9, 1]
                    
                    MDLabel:
                        text: "Vista Previa"
                        font_style: "Subtitle1"
                        halign: "center"
                        size_hint_y: None
                        height: dp(30)
                    
                    DrawingWidget:
                        id: preview_area
                        size_hint: (1, 1)

                MDCard:
                    orientation: 'vertical'
                    padding: dp(15)
                    spacing: dp(20)
                    size_hint_y: None
                    height: self.minimum_height
                    elevation: 2
                    radius: [10, 10, 10, 10]
                    md_bg_color: [0.98, 0.98, 0.98, 1]

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: dp(20)
                        pos_hint: {'center_x': 0.5}
                        
                        MDLabel:
                            text: "Tipo:"
                            font_style: "Body1"
                            size_hint_x: None
                            width: dp(50)
                            pos_hint: {'center_y': 0.5}
                        
                        MDBoxLayout:
                            adaptive_size: True
                            spacing: dp(5)
                            pos_hint: {'center_y': 0.5}
                            MDRaisedButton:
                                id: btn_fijo
                                text: "Fijo"
                                font_size: "16sp"
                                on_release: root.set_panel_type_from_toggle("Fijo")
                                disabled: True
                                elevation: 0
                            MDRaisedButton:
                                id: btn_puerta
                                text: "Puerta"
                                font_size: "16sp"
                                on_release: root.set_panel_type_from_toggle("Puerta")
                                disabled: True
                                elevation: 0
                            MDRaisedButton:
                                id: btn_montante
                                text: "Montante"
                                font_size: "16sp"
                                on_release: root.set_panel_type_from_toggle("Montante")
                                disabled: True
                                elevation: 0

                    MDTextField:
                        id: material_input
                        mode: "fill"
                        hint_text: "Material"
                        text: root.current_panel_material
                        font_size: "18sp"
                        on_text: root.current_panel_material = self.text
                        disabled: True
                        size_hint_y: None
                        height: dp(60)

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: dp(10)
                        MDTextField:
                            id: panel_alto_input
                            mode: "fill"
                            hint_text: "Alto (mm)"
                            input_type: "number"
                            required: True
                            font_size: "18sp"
                            on_text: root.validate_and_set_float_property(self, 'current_panel_alto')
                            disabled: True
                            size_hint_x: 0.5
                        MDTextField:
                            id: panel_ancho_input
                            mode: "fill"
                            hint_text: "Ancho (mm)"
                            input_type: "number"
                            required: True
                            font_size: "18sp"
                            on_text: root.validate_and_set_float_property(self, 'current_panel_ancho')
                            disabled: True
                            size_hint_x: 0.5

                    MDBoxLayout:
                        adaptive_height: True
                        spacing: dp(10)
                        padding: dp(5)
                        pos_hint: {'center_x': 0.5}
                        
                        MDRaisedButton:
                            id: btn_nuevo_vidrio
                            text: "Nuevo / Limpiar"
                            font_size: "16sp"
                            on_release: root.start_new_vidrio()
                            md_bg_color: app.theme_cls.primary_color
                        
                        MDRaisedButton:
                            id: btn_add_herraje
                            text: "+ Herraje"
                            font_size: "16sp"
                            on_release: root.open_herraje_dialog()
                            disabled: True

                        MDRaisedButton:
                            id: btn_aceptar_vidrio
                            text: "Aceptar Vidrio"
                            font_size: "16sp"
                            on_release: root.confirm_add_panel()
                            disabled: True
                            md_bg_color: app.theme_cls.accent_color

                MDCard:
                    orientation: 'vertical'
                    padding: dp(0)
                    spacing: dp(0)
                    size_hint_y: None
                    height: dp(300)
                    elevation: 1
                    radius: [10, 10, 10, 10]
                    md_bg_color: [0.95, 0.95, 0.95, 1]

                    MDBoxLayout:
                        adaptive_height: True
                        padding: dp(10)
                        md_bg_color: [0.9, 0.9, 0.9, 1]
                        radius: [10, 10, 0, 0]
                        MDLabel:
                            text: "Ficha Técnica Global (Click para editar)"
                            font_style: "H6"
                            halign: "center"
                            theme_text_color: "Primary"

                    MDScrollView:
                        MDList:
                            id: global_panel_list

                MDGridLayout:
                    cols: 2
                    spacing: dp(10)
                    padding: dp(0), dp(0), dp(0), dp(50)
                    size_hint_y: None
                    height: self.minimum_height
                    adaptive_height: True
                    
                    MDRectangleFlatButton:
                        text: "Guardar Proyecto"
                        on_release: app.open_save_dialog()
                        size_hint_x: 1
                        text_color: 0, 0.5, 0, 1
                        line_color: 0, 0.5, 0, 1

                    MDRectangleFlatButton:
                        text: "Nuevo Proyecto"
                        on_release: root.new_project_action()
                        size_hint_x: 1

                    MDRectangleFlatButton:
                        text: "Generar PDF"
                        on_release: app.open_save_pdf_dialog()
                        size_hint_x: 1
                        text_color: 0, 0, 1, 1
                        line_color: 0, 0, 1, 1
                    
                    MDRectangleFlatButton:
                        text: "Salir"
                        on_release: app.exit_app()
                        size_hint_x: 1

<HerrajesPopup>:
    orientation: 'vertical'
    spacing: dp(20)
    padding: dp(15)
    adaptive_height: True
    
    # 1. SELECCIÓN DE TIPO
    MDCard:
        orientation: 'vertical'
        padding: dp(0)
        size_hint_y: None
        height: dp(200)
        elevation: 2
        radius: [12, 12, 12, 12]
        
        MDBoxLayout:
            adaptive_height: True
            padding: dp(10)
            md_bg_color: app.theme_cls.primary_light
            radius: [12, 12, 0, 0]
            MDLabel:
                text: "1. Seleccione Tipo"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0,0,0,1
                halign: "center"
        
        MDScrollView:
            MDList:
                id: herraje_type_list

    # 2. CONFIGURACIÓN
    MDCard:
        orientation: 'vertical'
        padding: dp(0)
        adaptive_height: True
        elevation: 2
        radius: [12, 12, 12, 12]
        
        MDBoxLayout:
            adaptive_height: True
            padding: dp(10)
            md_bg_color: app.theme_cls.primary_light
            radius: [12, 12, 0, 0]
            MDLabel:
                text: "2. Configuración"
                font_style: "H6"
                theme_text_color: "Custom"
                text_color: 0,0,0,1
                halign: "center"

        MDBoxLayout:
            id: container_wrapper
            adaptive_height: True
            orientation: 'vertical'
            padding: dp(15)
            
            MDBoxLayout:
                id: herraje_details_container_layout
                orientation: 'vertical'
                adaptive_height: True
                padding: dp(5)
                spacing: dp(20)

    # 3. LISTA ACTUAL
    MDCard:
        orientation: 'vertical'
        padding: dp(0)
        size_hint_y: None
        height: dp(150)
        elevation: 1
        radius: [8, 8, 8, 8]
        md_bg_color: [0.95, 0.95, 0.95, 1]
        
        MDBoxLayout:
            adaptive_height: True
            padding: dp(5)
            md_bg_color: [0.9, 0.9, 0.9, 1]
            radius: [8, 8, 0, 0]
            MDLabel:
                text: "Herrajes del Panel Actual"
                font_style: "Subtitle1"
                halign: "center"
        
        MDScrollView:
            MDList:
                id: current_panel_list

    # 4. BOTONES DE ACCIÓN
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(15)
        adaptive_height: True
        padding: dp(0), dp(10), dp(0), dp(20)
        
        MDRaisedButton:
            text: "Añadir / Aceptar Complemento"
            font_size: "18sp"
            on_release: root.accept_herraje()
            size_hint_x: 1
            md_bg_color: app.theme_cls.primary_color
            elevation: 2
            padding: dp(15)
        
        MDRaisedButton:
            text: "Limpiar Formulario"
            font_size: "16sp"
            on_release: root.reset_herraje_form()
            size_hint_x: 1
            md_bg_color: app.theme_cls.accent_color
        
        MDRectangleFlatButton:
            text: "Cerrar Ventana"
            font_size: "16sp"
            on_release: root.close_dialog()
            size_hint_x: 1
'''

# --- Funciones auxiliares ---
def create_safe_dialog(title, text, buttons=None):
    content = MDLabel(text=text, theme_text_color="Primary", adaptive_height=True, font_style="Body1")
    return MDDialog(title=title, type="custom", content_cls=content, buttons=buttons if buttons else [])

def show_alert(title, text):
    dialog = create_safe_dialog(title, text, [MDRectangleFlatButton(text="OK", on_release=lambda x: dialog.dismiss())])
    dialog.open()

def show_snackbar(text, color=(0.2, 0.2, 0.2, 1)):
    try:
        sb = Snackbar(text=text, bg_color=color, duration=1.5, font_size="16sp")
        sb.open()
    except TypeError:
         show_alert("Aviso", text)

def get_storage_path():
    if platform == 'android':
        from android.storage import primary_external_storage_path
        dir_path = os.path.join(primary_external_storage_path(), 'Download') 
        if not os.path.exists(dir_path):
            dir_path = os.path.join(primary_external_storage_path(), 'Documents')
        return dir_path
    else:
        return os.path.expanduser("~/Documents")

# --- CLASE DRAWING WIDGET ---
class DrawingWidget(Widget):
    def redraw(self, processed_data):
        self.canvas.clear()
        hueco_w = processed_data['hueco_data']['ancho']
        hueco_h = processed_data['hueco_data']['alto']
        if hueco_w == 0 or hueco_h == 0: return

        margin = 10
        available_w = self.width - 2 * margin
        available_h = self.height - 2 * margin
        scale = min(available_w / hueco_w, available_h / hueco_h)
        
        draw_w = hueco_w * scale
        draw_h = hueco_h * scale
        start_x = self.x + (self.width - draw_w) / 2
        start_y = self.y + (self.height - draw_h) / 2

        with self.canvas:
            Color(0, 0, 0, 1)
            Line(rectangle=(start_x, start_y, draw_w, draw_h), width=1.5)
            
            for panel in processed_data['panels']:
                px = start_x + (panel['x_offset'] * scale)
                py = start_y + (panel['y_offset'] * scale)
                pw = panel['ancho'] * scale
                ph = panel['alto'] * scale
                
                Color(0.9, 0.95, 1, 0.5) 
                Rectangle(pos=(px, py), size=(pw, ph))
                Color(0, 0, 0, 1)
                Line(rectangle=(px, py, pw, ph), width=1)

                for h in panel['herrajes']:
                    h_type = h['tipo'].lower()
                    col_hex = '#FFFFFF'
                    if h_type in ['pomo', 'tirador', 'toallero']: col_hex = '#A35A00'
                    elif h_type == 'perfil vierte-aguas': col_hex = '#90EE90'
                    elif h_type == 'pinza': col_hex = '#ADD8E6'
                    elif h_type in ['bisagra', 'bisagra doble']: col_hex = '#6495ED'
                    elif h_type == 'u': col_hex = '#FFB6C1'
                    elif h_type == 'perfil burbuja': col_hex = '#FFDE21'
                    elif h_type == 'perfil imán 45º': col_hex = '#FF6600'
                    elif h_type == 'taladro': col_hex = '#D3D3D3'
                    
                    c_rgba = get_color_from_hex(col_hex)
                    Color(*c_rgba)

                    if h_type in ["pinza", "bisagra", "bisagra doble"]:
                        w_h = h['ancho_real'] * scale
                        h_h = h['alto_real'] * scale
                        xx = start_x + (h['x_absolute'] * scale)
                        yx_sup = start_y + (h['y_absolute_sup'] * scale) - h_h
                        Rectangle(pos=(xx, yx_sup), size=(w_h, h_h))
                        yx_inf = start_y + (h['y_absolute_inf'] * scale)
                        Rectangle(pos=(xx, yx_inf), size=(w_h, h_h))
                    elif h_type == "pomo":
                        cx = start_x + (h['x_absolute'] * scale)
                        cy = start_y + (h['y_absolute'] * scale)
                        r = (h['diametro'] / 2) * scale
                        Ellipse(pos=(cx-r, cy-r), size=(r*2, r*2))
                    elif h_type == "taladro":
                        cx = start_x + (h['x_absolute'] * scale)
                        cy = start_y + (h['y_absolute'] * scale)
                        r = (h['diametro'] / 2) * scale
                        Line(circle=(cx, cy, r), width=1)
                    else: 
                        bx = start_x + (h['x_absolute'] * scale)
                        by = start_y + (h['y_absolute'] * scale)
                        if h_type in ['tirador', 'toallero']: by = by - (h['alto_real'] * scale)/2
                        w_h = h['ancho_real'] * scale
                        h_h = h['alto_real'] * scale
                        Rectangle(pos=(bx, by), size=(w_h, h_h))

# --- Clases de Pantalla ---

class BaseContentScreen(MDScreen):
    title = StringProperty("Título")
    def on_enter(self):
        app = MDApp.get_running_app()
        app.current_screen_title = self.title
        app.can_go_back = (self.name != 'project_data_screen')

    def validate_and_set_float(self, tf, prop, target):
        try:
            if not tf.text: return False
            val = float(tf.text)
            if val <= 0:
                tf.error = True
                return False
            tf.error = False
            target[prop] = val
            return True
        except ValueError:
            tf.error = True
            return False

    def validate_and_set_float_property(self, tf, prop):
        try:
            if not tf.text: return False
            val = float(tf.text)
            if val <= 0:
                tf.error = True
                return False
            tf.error = False
            setattr(self, prop, val)
            return True
        except ValueError:
            tf.error = True
            return False

class ProjectDataScreen(BaseContentScreen):
    title = "Datos del Proyecto"
    def on_enter(self):
        super().on_enter()
        app = MDApp.get_running_app()
        self.ids.project_name_input.text = app.project_data.get('proyecto', '')
        self.ids.client_input.text = app.project_data.get('cliente', '')
        self.ids.author_input.text = app.project_data.get('autor', '')

    def save_and_next(self):
        app = MDApp.get_running_app()
        app.project_data['proyecto'] = self.ids.project_name_input.text.strip()
        app.project_data['cliente'] = self.ids.client_input.text.strip()
        app.project_data['autor'] = self.ids.author_input.text.strip()
        if not app.project_data['proyecto']:
            show_alert("Error", "Nombre del proyecto obligatorio.")
            return
        app.show_screen('hole_data_screen')

class HoleDataScreen(BaseContentScreen):
    title = "Medidas del Hueco"
    def on_enter(self):
        super().on_enter()
        app = MDApp.get_running_app()
        self.ids.ancho_hueco_input.text = str(app.hueco_data['ancho']) if app.hueco_data['ancho'] > 0 else ""
        self.ids.alto_hueco_input.text = str(app.hueco_data['alto']) if app.hueco_data['alto'] > 0 else ""
        self.ids.color_herrajes_input.text = app.hueco_data['color_herrajes'] or "Cromo brillo"

    def save_and_next(self):
        app = MDApp.get_running_app()
        v1 = self.validate_and_set_float(self.ids.ancho_hueco_input, 'ancho', app.hueco_data)
        v2 = self.validate_and_set_float(self.ids.alto_hueco_input, 'alto', app.hueco_data)
        app.hueco_data['color_herrajes'] = self.ids.color_herrajes_input.text.strip()

        if not (v1 and v2):
            show_alert("Error", "Introduce medidas válidas.")
            return

        if app.panels_raw_data:
             dialog = create_safe_dialog("Aviso", "Cambiar hueco podría invalidar paneles.",
                [MDRectangleFlatButton(text="OK", on_release=lambda *a: (dialog.dismiss(), app.show_screen('panel_data_screen')))])
             dialog.open()
             return

        app.show_screen('panel_data_screen')

class PanelDataScreen(BaseContentScreen):
    title = "Vidrios"
    current_panel_ancho = NumericProperty(0.0)
    current_panel_alto = NumericProperty(0.0)
    current_panel_type = StringProperty("Fijo")
    current_panel_material = StringProperty("Templado 8mm Incoloro")
    current_panel_herrajes = ListProperty([])
    editing_panel_index = NumericProperty(-1)
    
    herraje_dialog = None

    def on_enter(self):
        super().on_enter()
        self.update_global_summary()
        MDApp.get_running_app().update_preview(self.ids.preview_area)
        if self.editing_panel_index == -1 and not self.current_panel_ancho: 
            self.reset_panel_form_state()

    def reset_panel_form_state(self):
        self.ids.btn_fijo.disabled = True
        self.ids.btn_puerta.disabled = True
        self.ids.btn_montante.disabled = True
        self.ids.material_input.disabled = True
        self.ids.panel_alto_input.disabled = True
        self.ids.panel_ancho_input.disabled = True
        self.ids.btn_nuevo_vidrio.disabled = False
        self.ids.btn_add_herraje.disabled = True
        self.ids.btn_aceptar_vidrio.disabled = True
        self.current_panel_type = "Fijo"
        self.update_toggle_buttons_state()
        self.current_panel_material = "Templado 8mm Incoloro"
        self.current_panel_ancho = 0.0
        self.current_panel_alto = 0.0
        self.ids.panel_alto_input.text = ""
        self.ids.panel_ancho_input.text = ""
        self.current_panel_herrajes = []
        self.editing_panel_index = -1 
    
    def update_toggle_buttons_state(self):
        app = MDApp.get_running_app()
        s_col = app.theme_cls.primary_color
        u_col = [0.9, 0.9, 0.9, 1] 
        def style(bid, sel):
            b = self.ids[bid]
            b.md_bg_color = s_col if sel else u_col
            b.text_color = [1,1,1,1] if sel else [0,0,0,1]
        style('btn_fijo', self.current_panel_type == "Fijo")
        style('btn_puerta', self.current_panel_type == "Puerta")
        style('btn_montante', self.current_panel_type == "Montante")

    def set_panel_type_from_toggle(self, t):
        self.current_panel_type = t
        self.update_toggle_buttons_state()

    def start_new_vidrio(self):
        self.editing_panel_index = -1 
        self._activate_form_fields()
        self.current_panel_herrajes = []
        self.current_panel_type = "Fijo"
        self.update_toggle_buttons_state()
        self.ids.panel_alto_input.text = ""
        self.ids.panel_ancho_input.text = ""
        self.current_panel_ancho = 0.0
        self.current_panel_alto = 0.0

    def _activate_form_fields(self):
        self.ids.btn_fijo.disabled = False
        self.ids.btn_puerta.disabled = False
        self.ids.btn_montante.disabled = False
        self.ids.material_input.disabled = False
        self.ids.panel_alto_input.disabled = False
        self.ids.panel_ancho_input.disabled = False
        self.ids.btn_nuevo_vidrio.disabled = False
        self.ids.btn_add_herraje.disabled = False
        self.ids.btn_aceptar_vidrio.disabled = False

    def validate_panel_dims(self):
        v1 = self.validate_and_set_float_property(self.ids.panel_alto_input, 'current_panel_alto')
        v2 = self.validate_and_set_float_property(self.ids.panel_ancho_input, 'current_panel_ancho')
        return v1 and v2

    def check_global_constraints(self):
        app = MDApp.get_running_app()
        hueco_ancho = app.hueco_data['ancho']
        hueco_alto = app.hueco_data['alto']
        existing = list(app.panels_raw_data)
        if self.editing_panel_index != -1 and self.editing_panel_index < len(existing): del existing[self.editing_panel_index]

        base_panels = [p for p in existing if p['tipo'] in ['fijo', 'puerta']]
        width_sum = sum(p['ancho'] for p in base_panels)
        available_width = hueco_ancho - width_sum
        
        if self.current_panel_type in ['Fijo', 'Puerta']:
            if self.current_panel_ancho > available_width:
                def fix_width(*args):
                    self.ids.panel_ancho_input.text = str(available_width)
                    self.current_panel_ancho = available_width
                    dialog.dismiss()
                if available_width <= 0: create_safe_dialog("Error Ancho", "No queda espacio disponible.").open()
                else:
                    dialog = create_safe_dialog("Error Ancho", f"Supera hueco disponible.\nMáximo: {available_width} mm",
                        [MDRectangleFlatButton(text="Cancelar", on_release=lambda x: dialog.dismiss()),
                         MDRectangleFlatButton(text="Ajustar", on_release=fix_width)])
                    dialog.open()
                return False
        else:
            montante_panels = [p for p in existing if p['tipo'] == 'montante']
            width_sum_montantes = sum(p['ancho'] for p in montante_panels)
            available_width_mont = hueco_ancho - width_sum_montantes
            if self.current_panel_ancho > available_width_mont:
                 create_safe_dialog("Error Ancho Montante", f"Supera ancho hueco. Disp: {available_width_mont}").open()
                 return False

        max_base_h = max([p['alto'] for p in base_panels], default=0)
        max_montante_h = max([p['alto'] for p in existing if p['tipo']=='montante'], default=0)
        
        if self.current_panel_type in ['Fijo', 'Puerta']: available_height = hueco_alto - max_montante_h
        else: available_height = hueco_alto - max_base_h
            
        if self.current_panel_alto > available_height:
             def fix_height(*args):
                self.ids.panel_alto_input.text = str(available_height)
                self.current_panel_alto = available_height
                dialog_h.dismiss()
             if available_height <= 0: create_safe_dialog("Error Alto", "No queda altura disponible.").open()
             else:
                 dialog_h = create_safe_dialog("Error Alto", f"Supera altura disp.\nMáximo: {available_height} mm",
                    [MDRectangleFlatButton(text="Cancelar", on_release=lambda x: dialog_h.dismiss()),
                     MDRectangleFlatButton(text="Ajustar", on_release=fix_height)])
                 dialog_h.open()
             return False
        return True

    def open_herraje_dialog(self):
        # AVISO DE SEGURIDAD
        if not self.validate_panel_dims(): 
            show_alert("Atención", "Debes introducir Ancho y Alto del vidrio antes de añadir herrajes.")
            return

        data = {
            "tipo": self.current_panel_type.lower(), "material": self.current_panel_material,
            "ancho": self.current_panel_ancho, "alto": self.current_panel_alto,
            "herrajes": self.current_panel_herrajes
        }
        self.herraje_dialog_content = HerrajesPopup(panel_data=data, parent_screen=self)
        
        # En PC y Android con diseño vertical, ya no necesitamos el ScrollView externo 
        # (porque el contenido tiene sus propios controles o cabe).
        
        self.herraje_dialog = MDDialog(
            title="Herrajes", 
            type="custom", 
            content_cls=self.herraje_dialog_content, 
            size_hint=(0.95, 0.95), 
            auto_dismiss=False
        )
        self.herraje_dialog.open()

    def confirm_add_panel(self):
        if not self.validate_panel_dims(): return
        if not self.check_global_constraints(): return
        accion = "Editar" if self.editing_panel_index != -1 else "Guardar"
        txt = f"{self.current_panel_type} {self.current_panel_ancho}x{self.current_panel_alto}mm\n{len(self.current_panel_herrajes)} herrajes"
        dialog = create_safe_dialog(f"Confirmar {accion}", txt, [
            MDRectangleFlatButton(text="Revisar", on_release=lambda x: dialog.dismiss()),
            MDRectangleFlatButton(text="Confirmar", on_release=lambda x: (dialog.dismiss(), self.save_panel_and_reset()))
        ])
        dialog.open()

    def save_panel_and_reset(self):
        app = MDApp.get_running_app()
        data = {
            "tipo": self.current_panel_type.lower(), "material": self.current_panel_material,
            "ancho": self.current_panel_ancho, "alto": self.current_panel_alto,
            "herrajes": self.current_panel_herrajes
        }
        if self.editing_panel_index != -1 and self.editing_panel_index < len(app.panels_raw_data):
            app.panels_raw_data[self.editing_panel_index] = data; msg = "Vidrio actualizado."
        else:
            app.panels_raw_data.append(data); msg = "Vidrio guardado."
        self.update_global_summary()
        MDApp.get_running_app().update_preview(self.ids.preview_area)
        self.reset_panel_form_state()
        show_snackbar(msg)

    def update_global_summary(self):
        list_view = self.ids.global_panel_list
        list_view.clear_widgets()
        panels = MDApp.get_running_app().panels_raw_data
        for i, p in enumerate(panels):
            p_type = p['tipo'].capitalize()
            detalles = f"{p['ancho']}x{p['alto']}mm - {len(p['herrajes'])} herrajes"
            icon = "window-closed" if p['tipo'] == "fijo" else "door" if p['tipo'] == "puerta" else "table-headers-eye"
            item = TwoLineAvatarIconListItem(text=f"P{i+1}: {p_type}", secondary_text=detalles, on_release=partial(self.on_panel_click, i))
            item.add_widget(IconLeftWidget(icon=icon))
            list_view.add_widget(item)

    def on_panel_click(self, index, item_widget):
        def do_delete(*args):
            del MDApp.get_running_app().panels_raw_data[index]
            self.update_global_summary()
            MDApp.get_running_app().update_preview(self.ids.preview_area)
            dialog.dismiss()
            show_snackbar("Vidrio eliminado.")
        def do_edit(*args):
            self.load_panel_for_editing(index)
            dialog.dismiss()
            show_snackbar(f"Editando Panel P{index+1}...")
        dialog = MDDialog(title=f"Opciones Panel P{index+1}", text="¿Qué desea hacer con este vidrio?",
            buttons=[MDRectangleFlatButton(text="Cancelar", on_release=lambda x: dialog.dismiss()),
                     MDRectangleFlatButton(text="Eliminar", on_release=do_delete, text_color=[1,0,0,1]),
                     MDRaisedButton(text="Editar", on_release=do_edit)], auto_dismiss=False)
        dialog.open()

    def load_panel_for_editing(self, index):
        p_data = MDApp.get_running_app().panels_raw_data[index]
        self.editing_panel_index = index 
        self._activate_form_fields()
        self.current_panel_type = p_data['tipo'].capitalize()
        self.update_toggle_buttons_state()
        self.current_panel_material = p_data['material']
        self.ids.panel_ancho_input.text = str(p_data['ancho'])
        self.ids.panel_alto_input.text = str(p_data['alto'])
        self.current_panel_ancho = p_data['ancho']
        self.current_panel_alto = p_data['alto']
        self.current_panel_herrajes = [dict(h) for h in p_data.get('herrajes', [])]

    def new_project_action(self): 
        d = create_safe_dialog("Nuevo", "¿Borrar actual?", [
            MDRectangleFlatButton(text="No", on_release=lambda x: d.dismiss()),
            MDRectangleFlatButton(text="Sí", on_release=lambda x: (d.dismiss(), MDApp.get_running_app().reset_app()))
        ])
        d.open()

# --- Subventana Herrajes ---

class HerrajesPopup(MDBoxLayout):
    panel_data = DictProperty({})
    parent_screen = ObjectProperty()
    selected_herraje_type = StringProperty("")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.herraje_types = ["Pinza", "Bisagra", "Bisagra Doble", "Pomo", "Tirador", "Toallero", "U", "Perfil Burbuja", "Perfil Imán 45º", "Perfil Vierte-Aguas", "Taladro"]
        Clock.schedule_once(self.populate_herraje_types)
        Clock.schedule_once(lambda dt: self.update_current_panel_summary())

    def populate_herraje_types(self, dt):
        lv = self.ids.herraje_type_list
        for t in self.herraje_types:
            item = OneLineAvatarIconListItem(text=t, on_release=partial(self.on_herraje_type_select, t))
            item.add_widget(IconLeftWidget(icon="checkbox-blank-circle-outline"))
            lv.add_widget(item)
    
    def update_current_panel_summary(self):
        list_view = self.ids.current_panel_list
        list_view.clear_widgets()
        herrajes = self.panel_data.get('herrajes', [])
        for i, h in enumerate(herrajes):
            h_type = h['tipo'].capitalize()
            detalles = ""
            if h['tipo'] == 'taladro': detalles = f"Ø{h.get('diametro', 0)}mm"
            elif h['tipo'] == 'bisagra doble': detalles = f"{h.get('apertura', '180')}º"
            elif 'lado' in h: detalles = f"Lado: {h['lado'].capitalize()}"
            
            icon_map = {'taladro': 'circle-outline', 'pomo': 'checkbox-blank-circle', 'tirador': 'minus-box',
                        'toallero': 'minus', 'bisagra': 'door-hinge', 'bisagra doble': 'door-sliding',
                        'pinza': 'crop-square', 'perfil': 'ruler'}
            icon_name = 'cog'
            for key in icon_map:
                if key in h['tipo']: icon_name = icon_map[key]; break
            item = TwoLineAvatarIconListItem(text=h_type, secondary_text=detalles, on_release=partial(self.on_herraje_click, i))
            item.add_widget(IconLeftWidget(icon=icon_name))
            list_view.add_widget(item)

    def on_herraje_click(self, index, item_widget):
        def do_delete(*args):
            del self.panel_data['herrajes'][index]
            self.update_current_panel_summary()
            dialog.dismiss()
            show_snackbar("Herraje eliminado.")
        def do_edit(*args):
            h_data = self.panel_data['herrajes'][index]
            self.selected_herraje_type = h_data['tipo']
            
            def set_icon_safe(widget_item, icon_name):
                for child in widget_item.children:
                    if isinstance(child, IconLeftWidget): child.icon = icon_name; return
                    if hasattr(child, 'children'):
                        for subchild in child.children:
                            if isinstance(subchild, IconLeftWidget): subchild.icon = icon_name; return

            self.show_herraje_details_form(h_data['tipo'])
            Clock.schedule_once(lambda dt: self.fill_form_with_data(h_data), 0.1)
            del self.panel_data['herrajes'][index]
            self.update_current_panel_summary()
            dialog.dismiss()
            show_snackbar("Editando... (Modifique y pulse Aceptar)")

        dialog = MDDialog(title="Opciones de Herraje", text="¿Qué desea hacer?",
            buttons=[MDRectangleFlatButton(text="Cancelar", on_release=lambda x: dialog.dismiss()),
                     MDRectangleFlatButton(text="Eliminar", on_release=do_delete, text_color=[1,0,0,1]),
                     MDRaisedButton(text="Editar", on_release=do_edit)], auto_dismiss=False)
        dialog.open()

    def fill_form_with_data(self, h_data):
        if 'lado' in self.detail_widgets and 'lado' in h_data: self.detail_widgets['lado'].set_item(h_data['lado'].capitalize())
        if 'apertura' in self.detail_widgets and 'apertura' in h_data: self.detail_widgets['apertura'].set_item(str(h_data['apertura']))
        if 'ref_vert' in self.detail_widgets and 'pos_vertical_ref' in h_data: self.detail_widgets['ref_vert'].set_item(h_data['pos_vertical_ref'].capitalize())
        if 'ref_horiz' in self.detail_widgets and 'pos_horizontal_ref' in h_data: self.detail_widgets['ref_horiz'].set_item(h_data['pos_horizontal_ref'].capitalize())
        if 'pos_sup' in self.detail_widgets: self.detail_widgets['pos_sup'].text = str(h_data['posiciones'][0])
        if 'pos_inf' in self.detail_widgets: self.detail_widgets['pos_inf'].text = str(h_data['posiciones'][1])
        if 'dist_borde' in self.detail_widgets: self.detail_widgets['dist_borde'].text = str(h_data['distancia_borde'])
        if 'altura' in self.detail_widgets: self.detail_widgets['altura'].text = str(h_data['altura'])
        if 'diametro' in self.detail_widgets: self.detail_widgets['diametro'].text = str(h_data['diametro'])
        if 'dist_vert' in self.detail_widgets: self.detail_widgets['dist_vert'].text = str(h_data['pos_vertical_dist'])
        if 'dist_horiz' in self.detail_widgets: self.detail_widgets['dist_horiz'].text = str(h_data['pos_horizontal_dist'])

    def on_herraje_type_select(self, h_type, item_widget):
        self.selected_herraje_type = h_type
        def set_icon_safe(widget_item, icon_name):
            for child in widget_item.children:
                if isinstance(child, IconLeftWidget): child.icon = icon_name; return
                if hasattr(child, 'children'):
                    for subchild in child.children:
                        if isinstance(subchild, IconLeftWidget): subchild.icon = icon_name; return
        for c in self.ids.herraje_type_list.children:
            if isinstance(c, OneLineAvatarIconListItem): set_icon_safe(c, "checkbox-blank-circle-outline")
        set_icon_safe(item_widget, "checkbox-marked-circle-outline")
        self.show_herraje_details_form(h_type)

    def show_herraje_details_form(self, h_type):
        c = self.ids.herraje_details_container_layout
        c.clear_widgets()
        self.detail_widgets = {}
        ht = h_type.lower()
        if ht in ["pinza", "bisagra"]:
            self._add(c, "Lado:", MDDropdownMenu_Wrapper(["Izquierda", "Derecha"], "Izquierda"), 'lado')
            self._add(c, "Dist. Sup (mm):", MDTextField(text="160"), 'pos_sup')
            self._add(c, "Dist. Inf (mm):", MDTextField(text="160"), 'pos_inf')
        elif ht == "bisagra doble":
            self._add(c, "Lado:", MDDropdownMenu_Wrapper(["Izquierda", "Derecha"], "Izquierda"), 'lado')
            self._add(c, "Grados Apertura:", MDDropdownMenu_Wrapper(["180", "90"], "180"), 'apertura')
            self._add(c, "Dist. Sup (mm):", MDTextField(text="160"), 'pos_sup')
            self._add(c, "Dist. Inf (mm):", MDTextField(text="160"), 'pos_inf')
        elif ht in ["pomo", "tirador", "toallero"]:
             if ht != "toallero":
                 self._add(c, "Lado:", MDDropdownMenu_Wrapper(["Izquierda", "Derecha"], "Izquierda"), 'lado')
                 self._add(c, "Dist. Borde (mm):", MDTextField(text="70"), 'dist_borde')
             self._add(c, "Alt. Suelo (mm):", MDTextField(text="900"), 'altura')
        elif ht in ["u", "perfil burbuja"]:
            self._add(c, "Posición:", MDDropdownMenu_Wrapper(["Izquierda", "Derecha", "Arriba", "Abajo"], "Abajo"), 'lado')
        elif ht == "perfil imán 45º":
            self._add(c, "Posición:", MDDropdownMenu_Wrapper(["Izquierda", "Derecha"], "Izquierda"), 'lado')
        elif ht == "perfil vierte-aguas":
            self._add(c, "Posición:", MDLabel(text="Abajo (Fijo)"), 'lado_fixed')
        elif ht == "taladro":
             self._add(c, "Diámetro (mm):", MDTextField(), 'diametro')
             self._add(c, "Ref. Vertical:", MDDropdownMenu_Wrapper(["Alta", "Baja"], "Baja"), 'ref_vert')
             self._add(c, "Dist. Vert (mm):", MDTextField(), 'dist_vert')
             self._add(c, "Ref. Horiz:", MDDropdownMenu_Wrapper(["Izquierda", "Derecha"], "Izquierda"), 'ref_horiz')
             self._add(c, "Dist. Horiz (mm):", MDTextField(), 'dist_horiz')

    def _add(self, c, txt, w, k):
        b = MDBoxLayout(orientation='vertical', adaptive_height=True, spacing=dp(2))
        b.add_widget(MDLabel(text=txt, font_style="Caption", theme_text_color="Secondary"))
        b.add_widget(w); c.add_widget(b); self.detail_widgets[k] = w

    def get_float(self, k):
        try: return float(self.detail_widgets[k].text)
        except: return None

    def accept_herraje(self):
        if not self.selected_herraje_type: return
        ht = self.selected_herraje_type.lower()
        new = {"tipo": ht}
        try:
            if ht in ["pinza", "bisagra"]:
                new['lado'] = self.detail_widgets['lado'].current_item.lower()
                new['posiciones'] = [self.get_float('pos_sup'), self.get_float('pos_inf')]
                if None in new['posiciones']: raise ValueError
            elif ht == "bisagra doble":
                new['lado'] = self.detail_widgets['lado'].current_item.lower()
                new['apertura'] = self.detail_widgets['apertura'].current_item
                new['posiciones'] = [self.get_float('pos_sup'), self.get_float('pos_inf')]
                if None in new['posiciones']: raise ValueError
            elif ht in ["pomo", "tirador", "toallero"]:
                 if ht != "toallero":
                    new['lado'] = self.detail_widgets['lado'].current_item.lower()
                    new['distancia_borde'] = self.get_float('dist_borde')
                    if new['distancia_borde'] is None: raise ValueError
                 new['altura'] = self.get_float('altura')
                 if new['altura'] is None: raise ValueError
                 if ht == "tirador": new.update({'ancho': 20.0, 'alto': 250.0})
                 elif ht == "toallero": new.update({'ancho': 450.0, 'alto': 25.0})
            elif ht in ["u", "perfil burbuja", "perfil imán 45º"]:
                new['lado'] = self.detail_widgets['lado'].current_item.lower()
            elif ht == "taladro":
                new.update({'diametro': self.get_float('diametro'), 
                            'pos_vertical_ref': self.detail_widgets['ref_vert'].current_item.lower(),
                            'pos_vertical_dist': self.get_float('dist_vert'),
                            'pos_horizontal_ref': self.detail_widgets['ref_horiz'].current_item.lower(),
                            'pos_horizontal_dist': self.get_float('dist_horiz')})
                if None in new.values(): raise ValueError
            self.panel_data['herrajes'].append(new)
            self.update_current_panel_summary()
            show_snackbar("Herraje añadido.")
        except ValueError:
            show_alert("Error", "Datos inválidos.")

    def reset_herraje_form(self):
        self.selected_herraje_type = ""
        self.ids.herraje_details_container_layout.clear_widgets()
        self.detail_widgets = {}

    def close_dialog(self): self.parent_screen.herraje_dialog.dismiss()

class MDDropdownMenu_Wrapper(MDRectangleFlatButton):
    current_item = StringProperty("")
    def __init__(self, options, default, **kwargs):
        super().__init__(**kwargs)
        self.text = default
        self.current_item = default
        items = [{"viewclass": "OneLineListItem", "text": o, "on_release": lambda x=o: self.set_item(x)} for o in options]
        self.menu = MDDropdownMenu(caller=self, items=items, width_mult=4)
        self.on_release = self.menu.open
    def set_item(self, t):
        self.text = t
        self.current_item = t
        self.menu.dismiss()

class GlassDoorApp(MDApp):
    project_data = DictProperty({"proyecto": "", "cliente": "", "autor": ""})
    hueco_data = DictProperty({"ancho": 0.0, "alto": 0.0, "color_herrajes": "Cromo brillo"})
    panels_raw_data = ListProperty([])
    current_screen_title = StringProperty("Inicio")
    can_go_back = BooleanProperty(False)

    def on_start(self):
        # Permisos Android
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.WRITE_EXTERNAL_STORAGE, Permission.READ_EXTERNAL_STORAGE])

        # FECHA LÍMITE (SOLUCIÓN SEGURA HARDCODED)
        limit_date = datetime(2026, 2, 28)
        
        if datetime.now() > limit_date: self.show_expiration_dialog()

    def show_expiration_dialog(self):
        dialog = MDDialog(title="Licencia Caducada", text="El periodo de prueba ha finalizado.",
            buttons=[MDRectangleFlatButton(text="Salir", on_release=lambda x: sys.exit())], auto_dismiss=False)
        dialog.open()

    def build(self):
        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.accent_palette = "DeepOrange"
        self.theme_cls.theme_style = "Light"
        Builder.load_string(KV_DESIGN)
        self.sm = ScreenManager()
        for S in [ProjectDataScreen, HoleDataScreen, PanelDataScreen]: self.sm.add_widget(S())
        return self.sm

    def show_screen(self, n): self.sm.current = n
    def go_back(self): 
        if self.sm.current != 'project_data_screen': self.sm.current = self.sm.previous()
    def exit_app(self): self.stop()
    def reset_app(self):
        self.project_data = {"proyecto": "", "cliente": "", "autor": ""}
        self.hueco_data = {"ancho": 0.0, "alto": 0.0, "color_herrajes": ""}
        self.panels_raw_data = []
        self.show_screen('project_data_screen')
        
    def get_current_panel_data_display(self):
        return "\n".join([f"{i+1}. {p['tipo']} {p['ancho']}x{p['alto']}" for i,p in enumerate(self.panels_raw_data)]) or "Sin datos"
    
    def show_info_dialog(self): create_safe_dialog("Info", "App v1.0").open()
    
    def update_preview(self, widget):
        if not hasattr(widget, 'redraw'): return
        try:
            d = fase1_logic.process_panel_data(self.project_data, self.hueco_data, self.panels_raw_data)
            widget.redraw(d)
        except Exception: pass

    # --- DIALOGOS DE GUARDADO/CARGA MANUALES (SIN TKINTER) ---
    def open_save_dialog(self):
        # Preguntar nombre de archivo
        self.input_filename = MDTextField(hint_text="Nombre del archivo (sin .json)")
        self.save_dialog = MDDialog(
            title="Guardar Proyecto",
            type="custom",
            content_cls=self.input_filename,
            buttons=[
                MDRectangleFlatButton(text="Cancelar", on_release=lambda x: self.save_dialog.dismiss()),
                MDRaisedButton(text="Guardar", on_release=self.finish_save_project)
            ],
            auto_dismiss=False
        )
        self.save_dialog.open()

    def finish_save_project(self, *args):
        name = self.input_filename.text.strip()
        if not name:
            show_alert("Error", "Debes escribir un nombre.")
            return
        
        try:
            folder = get_storage_path()
            if not os.path.exists(folder): os.makedirs(folder)
            filepath = os.path.join(folder, f"{name}.json")
            
            save_data = {"project_data": dict(self.project_data), "hueco_data": dict(self.hueco_data), "panels_raw_data": list(self.panels_raw_data)}
            with open(filepath, 'w', encoding='utf-8') as f: json.dump(save_data, f, indent=4)
            
            self.save_dialog.dismiss()
            show_snackbar(f"Guardado en: {filepath}")
        except Exception as e:
            show_alert("Error al guardar", str(e))

    def open_save_pdf_dialog(self):
        self.input_pdfname = MDTextField(hint_text="Nombre del PDF (sin .pdf)")
        self.pdf_dialog = MDDialog(
            title="Generar PDF",
            type="custom",
            content_cls=self.input_pdfname,
            buttons=[
                MDRectangleFlatButton(text="Cancelar", on_release=lambda x: self.pdf_dialog.dismiss()),
                MDRaisedButton(text="Guardar PDF", on_release=self.finish_save_pdf)
            ],
            auto_dismiss=False
        )
        self.pdf_dialog.open()

    def finish_save_pdf(self, *args):
        name = self.input_pdfname.text.strip()
        if not name:
            show_alert("Error", "Debes escribir un nombre.")
            return
        
        try:
            folder = get_storage_path()
            if not os.path.exists(folder): os.makedirs(folder)
            filepath = os.path.join(folder, f"{name}.pdf")
            
            data = fase1_logic.process_panel_data(self.project_data, self.hueco_data, self.panels_raw_data)
            fase2_drawing.generate_pdf_drawing(data, filepath)
            
            self.pdf_dialog.dismiss()
            create_safe_dialog("Éxito", f"PDF guardado en:\n{filepath}").open()
        except Exception as e:
            show_alert("Error al guardar PDF", str(e))

    def open_load_dialog(self):
        # Listar archivos JSON en la carpeta de documentos
        folder = get_storage_path()
        if not os.path.exists(folder): os.makedirs(folder)
        
        files = [f for f in os.listdir(folder) if f.endswith('.json')]
        
        if not files:
            show_alert("Info", f"No hay proyectos guardados en:\n{folder}")
            return

        # Crear lista visual
        scroll = MDBoxLayout(orientation="vertical", adaptive_height=True, size_hint_y=None)
        
        for f in files:
            item = OneLineAvatarIconListItem(text=f, on_release=partial(self.finish_load_project, os.path.join(folder, f)))
            item.add_widget(IconLeftWidget(icon="file-document"))
            scroll.add_widget(item)

        # Usamos un ScrollView dentro del dialogo
        from kivy.uix.scrollview import ScrollView
        sv = ScrollView(size_hint_y=None, height=dp(300))
        sv.add_widget(scroll)

        self.load_dialog = MDDialog(
            title="Seleccionar Proyecto",
            type="custom",
            content_cls=sv,
            buttons=[MDRectangleFlatButton(text="Cancelar", on_release=lambda x: self.load_dialog.dismiss())],
            auto_dismiss=False
        )
        self.load_dialog.open()

    def finish_load_project(self, filepath, *args):
        try:
            with open(filepath, 'r', encoding='utf-8') as f: loaded = json.load(f)
            self.project_data = loaded.get('project_data', {})
            self.hueco_data = loaded.get('hueco_data', {})
            self.panels_raw_data = loaded.get('panels_raw_data', [])
            
            screen = self.sm.get_screen('project_data_screen')
            screen.ids.project_name_input.text = self.project_data.get('proyecto', '')
            screen.ids.client_input.text = self.project_data.get('cliente', '')
            screen.ids.author_input.text = self.project_data.get('autor', '')
            
            self.load_dialog.dismiss()
            show_snackbar("Proyecto cargado.")
            self.show_screen('hole_data_screen')
        except Exception as e:
            show_alert("Error al cargar", str(e))

if __name__ == '__main__': GlassDoorApp().run()
