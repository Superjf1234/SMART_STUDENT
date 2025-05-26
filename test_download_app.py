#!/usr/bin/env python
"""
Aplicación simplificada de prueba para verificar las correcciones
de descarga de cuestionario en formato HTML.

Este script crea una aplicación Reflex mínima con las correcciones implementadas.
"""
import reflex as rx
import datetime
import os
import re
from pathlib import Path
import traceback

# Funciones auxiliares para manejar variables reactivas de forma segura
def get_safe_var_value(var, default=None):
    """
    Obtiene de manera segura el valor de una variable reactiva de Reflex.
    """
    if var is None:
        return default
        
    try:
        # Intentar obtener _var_value directamente
        if hasattr(var, "_var_value"):
            return var._var_value
    except:
        pass
        
    try:
        # Intentar conversión con str()
        val = str(var)
        if "<reflex.Var>" in val:
            val = val.split("</reflex.Var>")[-1]
        return val
    except:
        pass
        
    return default


def get_safe_var_list(var_list, default=None):
    """
    Obtiene de manera segura los valores de una lista reactiva de Reflex.
    """
    if default is None:
        default = []
        
    if var_list is None:
        return default
        
    # Método 1: Acceder directamente a _var_value
    try:
        if hasattr(var_list, "_var_value"):
            val = var_list._var_value
            if isinstance(val, list):
                return val
    except:
        pass
        
    # Método 2: Intentar acceder a los elementos individuales
    try:
        first_item = var_list[0]  # Verificar si podemos acceder por índice
        items = []
        i = 0
        try:
            while True:
                item = var_list[i]
                if hasattr(item, "_var_value"):
                    items.append(item._var_value)
                else:
                    items.append(item)
                i += 1
        except IndexError:
            pass
        except:
            pass
            
        if items:
            return items
    except:
        pass
        
    # Método 3: Intentar convertir a lista explícitamente
    try:
        val = list(var_list)
        if isinstance(val, list) and val:
            return val
    except:
        pass
        
    # Método 4: Intentar obtener como dict
    try:
        if hasattr(var_list, "to_dict"):
            val = var_list.to_dict()
            if isinstance(val, list):
                return val
    except:
        pass
        
    # Si todo falla, devolver el valor por defecto
    return default


# Estado de la aplicación de prueba
class TestState(rx.State):
    """Estado simplificado para probar las correcciones."""
    
    # Variables simuladas similares a CuestionarioState
    cuestionario_tema: str = "Sistema Respiratorio"
    cuestionario_libro: str = "Biología General"
    cuestionario_curso: str = "2º Medio"
    cuestionario_pdf_url: str = ""
    
    # Lista de preguntas simulada
    cuestionario_preguntas: list = [
        {
            "tipo": "alternativas",
            "pregunta": "¿Qué ocurre durante la inspiración?",
            "alternativas": [
                {"letra": "a", "texto": "El diafragma se relaja y sube."},
                {"letra": "b", "texto": "Las costillas descienden."}, 
                {"letra": "c", "texto": "El diafragma se contrae y baja."}, 
                {"letra": "d", "texto": "Los pulmones se contraen."}
            ],
            "correcta": "c",
            "explicacion": "En la inspiración, el diafragma se contrae y desciende."
        },
        {
            "tipo": "verdadero_falso",
            "pregunta": "El intercambio gaseoso en los alveolos ocurre por transporte activo.",
            "alternativas": [
                {"letra": "a", "texto": "Verdadero"}, 
                {"letra": "b", "texto": "Falso"}
            ],
            "correcta": "b",
            "explicacion": "El intercambio gaseoso ocurre por difusión simple."
        },
        {
            "tipo": "seleccion_multiple",
            "pregunta": "¿Cuáles de las siguientes estructuras forman parte del sistema respiratorio?",
            "alternativas": [
                {"letra": "a", "texto": "Fosas nasales"}, 
                {"letra": "b", "texto": "Esófago"}, 
                {"letra": "c", "texto": "Alveolos"}, 
                {"letra": "d", "texto": "Estómago"}
            ],
            "correctas": ["a", "c"],
            "explicacion": "El aire ingresa por las fosas nasales y llega a los alveolos."
        }
    ]
    
    # Estado de la interfaz
    is_downloading: bool = False
    error_message: str = ""
    download_success: bool = False
    
    def clear_messages(self):
        """Limpia los mensajes de error y éxito."""
        self.error_message = ""
        self.download_success = False
    
    async def download_cuestionario(self):
        """Descarga el cuestionario actual en formato HTML."""
        print("DEBUG: Iniciando download_cuestionario...")
        
        self.is_downloading = True
        self.clear_messages()
        yield
        
        try:
            # Verificamos si hay preguntas
            preguntas_lista = get_safe_var_list(self.cuestionario_preguntas, [])
            tiene_preguntas = len(preguntas_lista) > 0
            print(f"DEBUG: Encontradas {len(preguntas_lista)} preguntas en el cuestionario")
            
            if not tiene_preguntas:
                self.error_message = "No hay preguntas en el cuestionario para descargar."
                self.is_downloading = False
                yield
                return
            
            # Preparar valores para el nombre del archivo
            tema_str = get_safe_var_value(self.cuestionario_tema, "tema")
            libro_str = get_safe_var_value(self.cuestionario_libro, "libro")
            curso_str = get_safe_var_value(self.cuestionario_curso, "curso")
            
            # Sanitizar los valores para el nombre del archivo
            s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_str)[:50]
            s_lib = re.sub(r'[\\/*?:"<>|]', "", libro_str)[:50]
            s_cur = re.sub(r'[\\/*?:"<>|]', "", curso_str)[:50]
            
            # Crear nombre base del archivo
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            fname_base = f"Test_Cuestionario_{s_cur}_{s_lib}_{s_tema}_{timestamp}".replace(" ", "_")
            print(f"DEBUG: Nombre base del archivo generado: {fname_base}")
            
            # Generar HTML con las preguntas
            preguntas_html = ""
            for i, pregunta in enumerate(preguntas_lista):
                # Extraer valores seguros
                pregunta_texto = str(pregunta.get("pregunta", f"Pregunta {i+1}"))
                explicacion = str(pregunta.get("explicacion", ""))
                
                # Manejar diferentes formatos de respuesta correcta
                if "correcta" in pregunta:
                    correcta = str(pregunta.get("correcta", ""))
                elif "correctas" in pregunta and isinstance(pregunta.get("correctas"), list):
                    correctas_lista = pregunta.get("correctas", [])
                    correcta = ", ".join([str(c) for c in correctas_lista]) if correctas_lista else ""
                else:
                    correcta = ""
                
                # Agregar la entrada HTML para esta pregunta
                preguntas_html += f"""
                <div class="pregunta">
                    <h3>{i+1}. {pregunta_texto}</h3>
                    <div class="respuesta">Respuesta: {correcta}</div>
                    {f'<div class="explicacion">Explicación: {explicacion}</div>' if explicacion else ''}
                </div>
                """
            
            # Fecha para el pie de página
            fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            
            # Generar contenido HTML completo
            html_content = f"""<!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Test - Cuestionario: {s_tema}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #2563eb; }}
                    h2 {{ color: #4b5563; margin-top: 30px; }}
                    .pregunta {{ background-color: #f3f4f6; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    .pregunta h3 {{ margin-top: 0; color: #1e40af; }}
                    .respuesta {{ margin-top: 10px; font-weight: bold; }}
                    .explicacion {{ margin-top: 10px; font-style: italic; color: #4b5563; }}
                </style>
            </head>
            <body>
                <h1>Test - Cuestionario: {s_tema}</h1>
                <h3>Curso: {s_cur} - Libro: {s_lib}</h3>
                <p>Contiene preguntas de prueba</p>
                <hr>
                {preguntas_html}
                <hr>
                <footer>
                    <p><i>Generado por Test App el {fecha_actual}</i></p>
                </footer>
            </body>
            </html>"""
            
            # Generar archivo HTML para descarga
            fname = f"{fname_base}.html"
            print(f"DEBUG: Descargando cuestionario como HTML: {fname}")
            self.download_success = True
            yield rx.download(data=html_content.encode("utf-8", errors='replace'), filename=fname)
            
        except Exception as e:
            self.error_message = f"Error al descargar cuestionario: {str(e)}"
            print(f"ERROR: {traceback.format_exc()}")
        finally:
            self.is_downloading = False
            yield


# UI de la aplicación de prueba
def index():
    """Página principal de la aplicación de prueba."""
    return rx.container(
        rx.vstack(
            rx.heading("Test de Descarga de Cuestionario", size="xl"),
            rx.divider(),
            rx.hstack(
                rx.vstack(
                    rx.heading("Datos del Cuestionario", size="md"),
                    rx.form_control(
                        rx.form_label("Tema"),
                        rx.input(
                            value=TestState.cuestionario_tema,
                            placeholder="Ingresa el tema",
                            on_change=TestState.set_cuestionario_tema,
                        ),
                    ),
                    rx.form_control(
                        rx.form_label("Libro"),
                        rx.input(
                            value=TestState.cuestionario_libro,
                            placeholder="Ingresa el libro",
                            on_change=TestState.set_cuestionario_libro,
                        ),
                    ),
                    rx.form_control(
                        rx.form_label("Curso"),
                        rx.input(
                            value=TestState.cuestionario_curso,
                            placeholder="Ingresa el curso",
                            on_change=TestState.set_cuestionario_curso,
                        ),
                    ),
                    width="100%",
                    spacing="4",
                ),
                width="100%",
            ),
            rx.divider(),
            rx.vstack(
                rx.heading("Preguntas del Cuestionario", size="md"),
                rx.box(
                    rx.foreach(
                        TestState.cuestionario_preguntas,
                        lambda pregunta, i: rx.box(
                            rx.text(f"{i+1}. {pregunta['pregunta']}", font_weight="bold"),
                            rx.text(f"Respuesta: {pregunta.get('correcta', pregunta.get('correctas', []))}"),
                            rx.text(f"Explicación: {pregunta['explicacion']}"),
                            padding="3",
                            border_radius="md",
                            bg="gray.50",
                            mb="2",
                        ),
                    ),
                    width="100%",
                ),
                width="100%",
                spacing="4",
            ),
            rx.cond(
                TestState.error_message != "",
                rx.alert(
                    rx.alert_icon(),
                    rx.alert_title(TestState.error_message),
                    status="error",
                ),
                rx.fragment(),
            ),
            rx.cond(
                TestState.download_success,
                rx.alert(
                    rx.alert_icon(),
                    rx.alert_title("¡Descarga exitosa!"),
                    status="success",
                ),
                rx.fragment(),
            ),
            rx.button(
                "Descargar Cuestionario",
                on_click=TestState.download_cuestionario,
                is_loading=TestState.is_downloading,
                color_scheme="blue",
                size="lg",
                width="full",
                mt="4",
            ),
            width="100%",
            max_width="800px",
            padding="6",
            spacing="4",
        ),
        py="8",
    )


# Métodos de actualización para las variables
@TestState.mutation
def set_cuestionario_tema(self, value: str):
    self.cuestionario_tema = value

@TestState.mutation
def set_cuestionario_libro(self, value: str):
    self.cuestionario_libro = value

@TestState.mutation
def set_cuestionario_curso(self, value: str):
    self.cuestionario_curso = value


# Configuración de la aplicación
app = rx.App()
app.add_page(index)
