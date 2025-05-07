import os
import traceback
from . import config_logic, resumen_logic

def extraer_texto_pdf(curso, libro):
    """Extrae el texto del PDF especificado."""
    try:
        # Obtener el nombre del archivo PDF
        filename = config_logic.CURSOS.get(curso, {}).get(libro)
        if not filename:
            raise FileNotFoundError(f"No se encontró referencia para {curso} - {libro}")
        
        # Construir la ruta del archivo manteniendo la estructura original
        curso_folder_name = "".join(
            c if c.isalnum() else "_" for c in curso.lower()
        ).strip("_")
        
        # Ruta relativa al directorio assets
        pdf_path = os.path.join("assets", "pdfs", curso_folder_name, filename)
        print(f"Intentando acceder al PDF: {pdf_path}")
        
        # Usar la función existente de resumen_logic para extraer texto
        texto = resumen_logic.extraer_texto_pdf(curso, libro)
        if not texto:
            raise ValueError(f"No se pudo extraer texto del PDF para {curso} - {libro}")
        
        return texto
    
    except FileNotFoundError as e:
        print(f"Archivo PDF no encontrado: {e}")
        raise FileNotFoundError(f"PDF no encontrado: {pdf_path}")
    
    except Exception as e:
        traceback.print_exc()
        raise Exception(f"Error al extraer texto del PDF: {e}")

def obtener_puntos_clave(texto_pdf, tema):
    """Consulta a una API para obtener los puntos clave del tema."""
    try:
        # Si no tenemos texto_pdf (porque no se encontró el archivo)
        # Usamos directamente el tema para consultar información general
        if not texto_pdf or len(texto_pdf.strip()) < 100:
            prompt = f"""
            Genera un mapa conceptual sobre el tema "{tema}".
            No necesito ningún texto introductorio, solo dame la estructura en formato JSON:
            {{
              "status": "EXITO",
              "nodos": [
                {{
                  "titulo": "Concepto 1",
                  "subnodos": ["Subconcepto 1.1", "Subconcepto 1.2"]
                }},
                {{
                  "titulo": "Concepto 2",
                  "subnodos": ["Subconcepto 2.1", "Subconcepto 2.2"]
                }}
              ]
            }}
            Incluye 5 conceptos principales y 3 subconceptos por concepto relacionados con {tema}.
            IMPORTANTE: Responde únicamente con el JSON, sin texto adicional ni marcadores de código.
            """
        else:
            # Original prompt cuando sí tenemos texto del PDF
            prompt = f"""
            Analiza el siguiente texto y extrae los puntos clave relacionados con el tema "{tema}".
            Estructura la respuesta en formato JSON con la siguiente estructura exacta:
            {{
              "status": "EXITO",
              "nodos": [
                {{
                  "titulo": "Concepto 1",
                  "subnodos": ["Subconcepto 1.1", "Subconcepto 1.2"]
                }},
                {{
                  "titulo": "Concepto 2",
                  "subnodos": ["Subconcepto 2.1", "Subconcepto 2.2"]
                }}
              ]
            }}
            Limita la respuesta a 5 conceptos principales y 3 subconceptos por concepto.
            IMPORTANTE: Responde únicamente con el JSON, sin texto adicional ni marcadores de código.
            
            Texto de análisis:
            {texto_pdf[:5000]}
            """
        
        # Llamar a la API
        respuesta = config_logic.llamar_api_gemini(prompt)
        
        # Parsear respuesta JSON
        import json
        import re
        
        # Limpiar cualquier texto antes o después del JSON
        json_match = re.search(r'\{.*\}', respuesta, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            resultado = json.loads(json_str)
            return resultado
        else:
            # Formato de fallback si no se puede parsear como JSON
            print(f"No se pudo parsear la respuesta como JSON: {respuesta}")
            return {
                "status": "EXITO",
                "nodos": [
                    {
                        "titulo": tema,
                        "subnodos": ["Información no disponible"]
                    }
                ]
            }
            
    except Exception as e:
        traceback.print_exc()
        print(f"Error al obtener puntos clave: {e}")
        return {
            "status": "ERROR",
            "mensaje": str(e)
        }

def obtener_puntos_clave_mapa(texto_pdf, tema):
    """Consulta a una API para obtener los puntos clave del tema."""
    try:
        # Si no tenemos texto_pdf (porque no se encontró el archivo)
        # Usamos directamente el tema para consultar información general
        if not texto_pdf or len(texto_pdf.strip()) < 100:
            prompt = f"""
            Genera un mapa conceptual sobre el tema "{tema}".
            No necesito ningún texto introductorio, solo dame la estructura en formato JSON:
            {{
              "status": "EXITO",
              "nodos": [
                {{
                  "titulo": "Concepto 1",
                  "subnodos": ["Subconcepto 1.1", "Subconcepto 1.2"]
                }},
                {{
                  "titulo": "Concepto 2",
                  "subnodos": ["Subconcepto 2.1", "Subconcepto 2.2"]
                }}
              ]
            }}
            Incluye 5 conceptos principales y 3 subconceptos por concepto relacionados con {tema}.
            IMPORTANTE: Responde únicamente con el JSON, sin texto adicional ni marcadores de código.
            """
        else:
            # Original prompt cuando sí tenemos texto del PDF
            prompt = f"""
            Analiza el siguiente texto y extrae los puntos clave relacionados con el tema "{tema}".
            Estructura la respuesta en formato JSON con la siguiente estructura exacta:
            {{
              "status": "EXITO",
              "nodos": [
                {{
                  "titulo": "Concepto 1",
                  "subnodos": ["Subconcepto 1.1", "Subconcepto 1.2"]
                }},
                {{
                  "titulo": "Concepto 2",
                  "subnodos": ["Subconcepto 2.1", "Subconcepto 2.2"]
                }}
              ]
            }}
            Limita la respuesta a 5 conceptos principales y 3 subconceptos por concepto.
            IMPORTANTE: Responde únicamente con el JSON, sin texto adicional ni marcadores de código.
            
            Texto de análisis:
            {texto_pdf[:5000]}
            """
        
        # Llamar a la API
        from backend import config_logic
        respuesta = config_logic.llamar_api_gemini(prompt)
        
        # Parsear respuesta JSON
        import json
        import re
        
        # Limpiar cualquier texto antes o después del JSON
        json_match = re.search(r'\{.*\}', respuesta, re.DOTALL)
        if json_match:
            json_str = json_match.group(0)
            resultado = json.loads(json_str)
            return resultado
        else:
            # Formato de fallback si no se puede parsear como JSON
            print(f"No se pudo parsear la respuesta como JSON: {respuesta}")
            return {
                "status": "EXITO",
                "nodos": [
                    {
                        "titulo": tema,
                        "subnodos": ["Información no disponible"]
                    }
                ]
            }
            
    except Exception as e:
        traceback.print_exc()
        print(f"Error al obtener puntos clave: {e}")
        return {
            "status": "ERROR",
            "mensaje": str(e)
        }

def mapa_tab_content() -> rx.Component:
    return rx.box(
        rx.vstack(
            # Encabezado principal más atractivo
            rx.heading(
                "🌟 ¡Explora tus Ideas con Mapas Mentales!\n 🧠",
                size="6",
                margin_bottom="1.5em",
                color_scheme=ACCENT_COLOR_SCHEME,
            ),
            
            # Texto introductorio divertido
            rx.text(
                "Transforma conceptos complejos en mapas visuales fáciles de entender.\n 🚀",
                font_weight="bold",
                margin_bottom="1em",
            ),
            
            # Segundo texto con más espacio y salto de línea
            rx.text(
                "Selecciona un curso, libro y tema para comenzar. 📚\n\n¡Es hora de dar vida a tus ideas! ✨",
                margin_bottom="2.5em",  # Espaciado adicional
                font_style="italic",
                color="var(--gray-9)",
            ),
            
            # Espacio adicional para separar las secciones
            rx.divider(margin_y="2em"),
            
            # Mostrar mensajes de error si existen
            rx.cond(
                AppState.error_message_ui != "",
                rx.callout(
                    AppState.error_message_ui,
                    icon="triangle_alert",
                    color_scheme="red",
                    role="alert",
                    width="100%",
                    margin_y="1em",
                    size="2",
                ),
            ),
            
            # Formulario para seleccionar curso, libro y tema
            rx.grid(
                rx.text("📘 Curso:", weight="medium", align_self="center"),
                rx.select(
                    AppState.cursos_list,
                    placeholder="Selecciona un curso...",
                    value=AppState.selected_curso,
                    on_change=AppState.handle_curso_change,
                    width="100%",
                    size="2",
                    name="mapa_curso_select",
                ),
                rx.text("📖 Libro/Materia:", weight="medium", align_self="center"),
                rx.select(
                    AppState.libros_para_curso,
                    placeholder="Selecciona un libro...",
                    value=AppState.selected_libro,
                    on_change=AppState.handle_libro_change,
                    width="100%",
                    size="2",
                    name="mapa_libro_select",
                    is_disabled=(AppState.selected_curso == ""),
                ),
                rx.text("📝 Tema:", weight="medium", align_self="center"),
                rx.input(
                    placeholder="Escribe el tema o concepto clave",
                    value=AppState.selected_tema,
                    on_change=AppState.set_selected_tema,
                    width="100%",
                    size="2",
                    name="mapa_tema_input",
                ),
                columns="1fr 3fr",
                spacing="3",
                width="100%",
                max_width="700px",
                align_items="center",
                margin_bottom="2.5em",  # Espaciado adicional
            ),
            
            # Botón para generar el mapa conceptual
            rx.button(
                rx.hstack(rx.icon("chart-network", size=18), rx.text("¡Cerebro en Acción!")),
                on_click=AppState.generate_map(
                    AppState.selected_curso, AppState.selected_libro, AppState.selected_tema
                ),
                is_loading=AppState.is_generating_mapa,
                is_disabled=(
                    (AppState.selected_tema == "")
                    | AppState.is_generating_mapa
                ),
                color_scheme=ACCENT_COLOR_SCHEME,
                size="3",
                margin_bottom="2em",
            ),
            
            # Mostrar el mapa generado y botón de descarga
            rx.cond(
                AppState.mapa_image_url != "",
                rx.vstack(
                    rx.divider(),
                    rx.center(
                        rx.image(
                            src=AppState.mapa_image_url,
                            alt="Mapa Conceptual",
                            width="75%",
                            max_width="800px",
                        ),
                        width="100%",
                        margin_top="2em",
                    ),
                    rx.hstack(
                        rx.button(
                            rx.hstack(
                                rx.icon("arrow-down-to-line", size=18), 
                                rx.text("Descargar Mapa Mental")
                            ),
                            as_="a",
                            href=AppState.mapa_image_url,
                            download=True,
                            color_scheme="green",
                            variant="soft",
                            size="3",
                            margin_top="1em",
                        ),
                    ),
                    # Agregar botones de navegación a otras funcionalidades
                    rx.hstack(
                        rx.button(
                            rx.hstack(
                                rx.icon("file-text", size=18),
                                rx.text("Crear Resumen")
                            ),
                            on_click=AppState.set_active_tab("resumen"),
                            variant="soft",
                            color_scheme="blue",
                            size="3",
                            margin_top="1em",
                        ),
                        rx.button(
                            rx.hstack(
                                rx.icon("clipboard-check", size=18),
                                rx.text("Crear Evaluación")
                            ),
                            on_click=AppState.set_active_tab("evaluacion"),
                            variant="soft",
                            color_scheme="purple",
                            size="3",
                            margin_top="1em",
                        ),
                        spacing="4",
                        width="100%",
                        justify="center",
                    ),
                    width="100%",
                    align_items="center",
                ),
            ),
            
            # Mostrar spinner mientras se genera el mapa
            rx.cond(
                AppState.is_generating_mapa,
                rx.center(rx.spinner(size="3"), padding_y="5em"),
            ),
            
            spacing="5",
            width="100%",
        ),
        padding="2em",  # Espaciado general alrededor del contenido
    )

html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Mapa Conceptual: {tema}</title>
    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
    <style>
        /* Estilos... */
    </style>
</head>
<body>
    <div class="mermaid">
        {self.mapa_mermaid_code}
    </div>
    <script>
        mermaid.initialize({{
            /* Configuración... */
        }});
        // Agregar script para descargar automáticamente
        document.addEventListener('DOMContentLoaded', function() {{
            // Crear enlace invisible
            var link = document.createElement('a');
            link.href = 'data:image/png;base64,' + window.btoa(document.querySelector('.mermaid svg').outerHTML);
            link.download = 'mapa_conceptual.png';
            link.click();
        }});
    </script>
</body>
</html>
"""