# backend/map_logic.py
import os
import traceback
import sys
import random  # Puede que aún uses random para IDs si lo dejaste
import io
import base64
import re
from typing import Optional

# Intentar importar FPDF para la generación de PDFs
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    print("ERROR CRITICO (map_logic): Falta la librería 'fpdf'. Los PDF no se podrán generar.",
          file=sys.stderr)
    FPDF_AVAILABLE = False
    FPDF = None  # Para evitar errores si se intenta usar

# Asume que config.py está disponible
try:
    from .config_logic import CURSOS, extraer_texto_pdf, llamar_api_gemini
except ImportError:
    print(
        "ERROR CRITICO (map_logic): No se pudo importar desde config_logic.py",
        file=sys.stderr,
    )
    # Define Mocks si necesitas probar aisladamente
    CURSOS = {}

    def extraer_texto_pdf(c, a):
        return "Texto prueba mapa."

    def llamar_api_gemini(p):
        return "- Nodo Central: Tema Prueba\n  - Nodo Secundario: Subtema A"


def generar_mermaid_code(estructura_mapa_raw, orientation="LR"):
    # ... (Esta función se mantiene prácticamente igual que en tu versión Kivy)
    # ... (Asegúrate que no tenga dependencias de UI y devuelva el string Mermaid o None/error)
    if not estructura_mapa_raw:
        return None, "La API no devolvió una estructura."

    # Limpieza inicial de la respuesta API
    unwanted = ["```mermaid", "```", "graph TD", "graph LR"]
    estructura_mapa = estructura_mapa_raw.strip()
    for u in unwanted:
        estructura_mapa = estructura_mapa.replace(u, "")
    estructura_mapa = "\n".join(
        [line for line in estructura_mapa.split("\n") if line.strip()]
    )

    lineas = estructura_mapa.split("\n")
    if not lineas:
        return None, "La estructura procesada está vacía."

    mermaid_code = [f"graph {orientation}"]
    nodos_ids = {}
    contador_nodos = 0
    nodo_central_id = None
    ultimo_nodo_secundario_id = None

    def get_node_id(nodo_texto_limpio):
        nonlocal contador_nodos
        if nodo_texto_limpio not in nodos_ids:
            contador_nodos += 1
            new_id = f"N{contador_nodos}_{random.randint(100, 999)}"  # Añadir aleatorio para más unicidad
            nodos_ids[nodo_texto_limpio] = new_id
            texto_nodo_display = nodo_texto_limpio.replace('"', "#quot;")
            if len(texto_nodo_display) > 50:
                texto_nodo_display = texto_nodo_display[:47] + "..."
            mermaid_code.append(f'    {new_id}["{texto_nodo_display}"]')
            print(f"      Nuevo ID: {new_id} -> '{nodo_texto_limpio[:30]}...'")
            return new_id
        return nodos_ids[nodo_texto_limpio]

    print("\n--- Parseando estructura para Mermaid ---")
    for i, linea_original in enumerate(lineas):
        linea = linea_original.strip()
        indent = len(linea_original) - len(linea_original.lstrip(" "))
        if not linea:
            continue

        texto_bruto = linea
        prefijos = [
            "- Nodo Central:",
            "- Nodo Secundario:",
            "- Nodo Terciario:",
            "--",
            "- ",
            "* ",
        ]
        for pref in prefijos:
            if texto_bruto.startswith(pref):
                texto_bruto = texto_bruto[len(pref) :].strip()
                break
        nodo_texto_actual = texto_bruto.strip()
        if not nodo_texto_actual:
            continue

        current_node_id = None
        parent_node_id = None
        node_style = None

        if indent < 2 and not nodo_central_id:
            current_node_id = get_node_id(nodo_texto_actual)
            nodo_central_id = current_node_id
            node_style = "fill:#f9f,stroke:#333,stroke-width:2px"
            print(
                f"  -> Central: '{nodo_texto_actual[:30]}...' (ID: {current_node_id})"
            )
        elif indent >= 1 and indent < 4 and nodo_central_id:
            current_node_id = get_node_id(nodo_texto_actual)
            parent_node_id = nodo_central_id
            ultimo_nodo_secundario_id = current_node_id
            node_style = "fill:#ccf,stroke:#333,stroke-width:2px"
            print(
                f"    -> Secundario: '{nodo_texto_actual[:30]}...' (ID: {current_node_id})"
            )
        elif indent >= 4 and ultimo_nodo_secundario_id:
            current_node_id = get_node_id(nodo_texto_actual)
            parent_node_id = ultimo_nodo_secundario_id
            node_style = "fill:#9cf,stroke:#333,stroke-width:2px"
            print(
                f"      -> Terciario: '{nodo_texto_actual[:30]}...' (ID: {current_node_id})"
            )
        else:
            print(
                f"  WARN (Mermaid Parse): Indentación/Contexto no reconocido: '{linea_original}'"
            )
            continue

        if parent_node_id and current_node_id:
            link = f"    {parent_node_id} --> {current_node_id}"
            if link not in mermaid_code:
                mermaid_code.append(link)
            print(f"        -> Link: {parent_node_id} --> {current_node_id}")

        if node_style and current_node_id:
            style_line = f"    style {current_node_id} {node_style}"
            if style_line not in mermaid_code:
                mermaid_code.append(style_line)

    # Evitar duplicados de nodos (aunque get_node_id ya lo hace) y asegurar unicidad de estilos/links
    final_mermaid_code_lines = []
    seen_lines = set()
    for line in mermaid_code:
        line_strip = line.strip()
        if line_strip not in seen_lines:
            final_mermaid_code_lines.append(line)
            seen_lines.add(line_strip)

    final_mermaid_code = "\n".join(final_mermaid_code_lines)
    print(
        f"\n--- Código Mermaid Generado ({len(final_mermaid_code_lines)} líneas) ---\n```mermaid\n{final_mermaid_code}\n```\n--------------------\n"
    )

    if len(final_mermaid_code_lines) <= 1:
        return None, "No se generaron nodos o enlaces válidos para el mapa."

    return final_mermaid_code, None  # Éxito, devuelve código y None para error


# ELIMINADO: def renderizar_mapa_mermaid(...)


# --- MODIFICADA ---
def generar_mapa_logica(curso, libro, tema_usuario, selected_orientation="LR"):
    """
    Función principal de lógica para generar CÓDIGO MERMAID para un mapa mental.
    Retorna: {'status': 'EXITO'/'ERROR_...', 'mermaid_code': str|None, 'message': str|None}
    """
    print(
        f"INFO (map_logic): Iniciando generación CÓDIGO mapa para C={curso}, L={libro}, T={tema_usuario}, O={selected_orientation}"
    )
    resultado = {
        "status": "ERROR",
        "mermaid_code": None,  # Cambiado de png/pdf_path
        "message": "Error desconocido",
    }

    # ELIMINADO: Verificación de MERMAID_AVAILABLE

    if not curso or not libro or not tema_usuario:
        resultado["message"] = "Curso, libro y tema son requeridos."
        resultado["status"] = "ERROR_INPUT"
        return resultado

    try:
        # 1. Extraer Texto PDF
        print("INFO (map_logic): Extrayendo texto PDF...")
        # ... (Lógica de extracción igual, usa config_logic) ...
        archivo = CURSOS.get(curso, {}).get(libro)
        if not archivo:
            resultado["message"] = (
                f"Libro '{libro}' no encontrado para curso '{curso}'."
            )
            resultado["status"] = "ERROR_CONFIG"
            return resultado
        texto_pdf = extraer_texto_pdf(curso, archivo)  # Lanza excepción si falla

        # 2. Llamar API para obtener estructura
        print("INFO (map_logic): Llamando API para estructura de mapa...")
        # ... (Prompt y llamada a llamar_api_gemini igual) ...
        prompt_mapa = (
            f"Analiza texto. Identifica concepto ppal relacionado con '{tema_usuario}'.\n"
            f"Genera estructura jerárquica mapa mental centrado en concepto ppal (Nodo Central).\n"
            f"Formato EXACTO: lista anidada, guiones, prefijos claros:\n"
            f"- Nodo Central: [Concepto ppal]\n"
            f"  - Nodo Secundario: [Subtema 1]\n"
            f"    - Nodo Terciario: [Detalle 1.1]\n"
            f"(Max 5-6 sec, max 3-4 ter/sec. Conciso).\n"
            f"IMPORTANTE: SOLO la lista.\nTexto:\n{texto_pdf}"
        )  # Puedes ajustar el prompt
        estructura_raw = llamar_api_gemini(prompt_mapa)  # Devuelve texto o error string

        if isinstance(estructura_raw, str) and (
            "Error:" in estructura_raw
            or "Error " in estructura_raw
            or not estructura_raw.strip()
        ):
            print(
                f"WARN (map_logic): API retornó error o vacío: {estructura_raw[:200]}"
            )
            resultado["message"] = (
                f"La API no generó una estructura válida: {estructura_raw}"
            )
            resultado["status"] = "ERROR_API"
            return resultado
        print("INFO (map_logic): Estructura recibida de API.")

        # 3. Generar Código Mermaid
        print("INFO (map_logic): Generando código Mermaid...")
        mermaid_code, error_mermaid = generar_mermaid_code(
            estructura_raw, selected_orientation
        )
        if error_mermaid:
            resultado["message"] = f"Error al generar código Mermaid: {error_mermaid}"
            resultado["status"] = "ERROR_MERMAID_CODE"
            return resultado

        # Éxito
        resultado["status"] = "EXITO"
        resultado["mermaid_code"] = mermaid_code  # Guardar el código generado
        resultado["message"] = "Código Mermaid generado exitosamente."

    except FileNotFoundError as e_fnf:
        print(
            f"ERROR (map_logic): Archivo PDF no encontrado - {e_fnf}", file=sys.stderr
        )
        resultado["status"] = "ERROR_PDF_NOT_FOUND"
        resultado["message"] = f"No se encontró el archivo PDF: {e_fnf}"
    except IOError as e_io:
        print(f"ERROR (map_logic): Error de lectura PDF - {e_io}", file=sys.stderr)
        resultado["status"] = "ERROR_PDF_READ"
        resultado["message"] = f"Error al leer el PDF: {e_io}"
    except Exception as e:
        print(
            f"ERROR (map_logic): Excepción general en generar_mapa_logica: {e}",
            file=sys.stderr,
        )
        traceback.print_exc()
        resultado["status"] = "ERROR_INESPERADO"
        resultado["message"] = f"Ocurrió un error interno inesperado: {e}"

    print(f"INFO (map_logic): Finalizado. Status: {resultado['status']}")
    return resultado


# ELIMINADO: def limpiar_archivos_mapa(...)

def obtener_puntos_clave(texto_pdf, tema):
    """
    Obtiene los puntos clave relacionados con un tema específico.
    
    Args:
        texto_pdf (str): Texto extraído del PDF o texto vacío si no hay PDF
        tema (str): Tema sobre el cual obtener puntos clave
    
    Returns:
        dict: Diccionario con el status y los nodos para el mapa conceptual
    """
    import requests
    import json
    import os
    
    try:
        # Si usamos una API externa, configura la URL y la clave API
        api_key = os.environ.get("API_KEY", "")
        
        # Si no hay API configurada, usar un generador local basado en reglas
        if not api_key or texto_pdf == "":
            # Generador local basado en el tema proporcionado
            return generar_nodos_localmente(tema)
        
        # Configuración para API externa
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # Datos para enviar a la API
        data = {
            "tema": tema,
            "texto": texto_pdf[:5000]  # Limitar tamaño del texto
        }
        
        # URL de la API (reemplazar con la URL real)
        api_url = os.environ.get("API_URL", "https://api.example.com/concept-map")
        
        # Realizar solicitud a la API
        response = requests.post(api_url, headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            resultado = response.json()
            return {
                "status": "EXITO",
                "nodos": resultado.get("nodos", [])
            }
        else:
            # Si la API falla, usar el generador local
            return generar_nodos_localmente(tema)
            
    except Exception as e:
        print(f"Error al obtener puntos clave: {e}")
        # En caso de error, generar nodos localmente
        return generar_nodos_localmente(tema)

def generar_nodos_localmente(tema):
    """
    Genera nodos para un mapa conceptual basado en reglas predefinidas según el tema.
    
    Args:
        tema (str): Tema del mapa conceptual
    
    Returns:
        dict: Diccionario con status y nodos generados
    """
    tema_lower = tema.lower()
    
    # Mapas predefinidos para temas comunes
    mapas_predefinidos = {
        "sistema respiratorio": [
            {
                "titulo": "Estructura",
                "subnodos": ["Nariz", "Faringe", "Laringe", "Tráquea", "Bronquios", "Pulmones"]
            },
            {
                "titulo": "Función",
                "subnodos": ["Intercambio de gases", "Oxigenación de la sangre", "Eliminación de CO2"]
            },
            {
                "titulo": "Mecanismos",
                "subnodos": ["Inspiración", "Espiración", "Control nervioso"]
            },
            {
                "titulo": "Enfermedades",
                "subnodos": ["Asma", "Bronquitis", "Neumonía", "EPOC"]
            },
            {
                "titulo": "Factores de riesgo",
                "subnodos": ["Tabaquismo", "Contaminación", "Infecciones"]
            }
        ],
        "fotosíntesis": [
            {
                "titulo": "Fases",
                "subnodos": ["Fase luminosa", "Fase oscura", "Ciclo de Calvin"]
            },
            {
                "titulo": "Reactivos",
                "subnodos": ["Agua", "Dióxido de carbono", "Luz solar"]
            },
            {
                "titulo": "Productos",
                "subnodos": ["Glucosa", "Oxígeno", "ATP"]
            },
            {
                "titulo": "Estructuras",
                "subnodos": ["Cloroplastos", "Tilacoides", "Estroma"]
            },
            {
                "titulo": "Importancia",
                "subnodos": ["Producción de alimentos", "Ciclo del carbono", "Oxígeno atmosférico"]
            }
        ]
    }
    
    # Buscar coincidencias aproximadas
    for clave, nodos in mapas_predefinidos.items():
        if clave in tema_lower or tema_lower in clave:
            return {
                "status": "EXITO",
                "nodos": nodos
            }
    
    # Si no hay coincidencias, generar un mapa genérico
    return {
        "status": "EXITO",
        "nodos": [
            {
                "titulo": "Definición",
                "subnodos": ["Concepto básico", "Origen", "Importancia"]
            },
            {
                "titulo": "Características",
                "subnodos": ["Principal", "Secundaria", "Terciaria"]
            },
            {
                "titulo": "Componentes",
                "subnodos": ["Parte 1", "Parte 2", "Parte 3"]
            },
            {
                "titulo": "Aplicaciones",
                "subnodos": ["Área 1", "Área 2", "Área 3"]
            },
            {
                "titulo": "Relaciones",
                "subnodos": ["Conexión 1", "Conexión 2", "Conexión 3"]
            }
        ]
    }

def capturar_imagen_mapa(mermaid_code, tema=""):
    """
    Genera una imagen del mapa conceptual a partir del código Mermaid utilizando mermaid-cli.
    
    Args:
        mermaid_code (str): Código Mermaid del mapa conceptual
        tema (str): Tema del mapa conceptual
        
    Returns:
        str: Ruta a la imagen generada o None si hay error
    """
    try:
        if not mermaid_code:
            print("ERROR (map_logic): No hay código Mermaid para generar imagen")
            return None
        
        # Crear un directorio para mapas si no existe
        mapas_dir = os.path.join("assets", "mapas")
        if not os.path.exists(mapas_dir):
            os.makedirs(mapas_dir)
        
        # Generar un nombre de archivo único
        import datetime
        import random
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        random_suffix = random.randint(1000, 9999)
        mmd_filename = f"map_{timestamp}_{random_suffix}.mmd"
        img_filename = f"map_{timestamp}_{random_suffix}.png"
        mmd_path = os.path.join(mapas_dir, mmd_filename)
        img_path = os.path.join(mapas_dir, img_filename)
        
        # Mejorar el código Mermaid para mayor legibilidad
        mermaid_code_mejorado = mermaid_code
        
        # Aumentar tamaño de fuente en nodos para mejor legibilidad
        if "graph LR" in mermaid_code_mejorado or "graph TD" in mermaid_code_mejorado:
            # Añadir configuración de tamaño de fuente para todo el gráfico
            lineas = mermaid_code_mejorado.split('\n')
            if len(lineas) > 0:
                lineas[0] = lineas[0] + "\n    classDef default fontSize:14pt"
                mermaid_code_mejorado = '\n'.join(lineas)
        
        # Guardar el código Mermaid mejorado en un archivo temporal
        with open(mmd_path, "w", encoding="utf-8") as mmd_file:
            mmd_file.write(mermaid_code_mejorado)
        
        # Generar la imagen utilizando mermaid-cli con parámetros optimizados para alta calidad
        # Aumentar la escala a 3.0 para mayor resolución
        # Usar formato PNG con alta calidad
        command = f"mmdc -i {mmd_path} -o {img_path} --scale 3.0 --backgroundColor white --width 1600"
        result = os.system(command)
        
        if result != 0:
            print(f"ERROR (map_logic): Falló la generación de la imagen con mermaid-cli (código {result})")
            # Intento de fallback con parámetros más básicos
            fallback_command = f"mmdc -i {mmd_path} -o {img_path} --scale 2.5"
            fallback_result = os.system(fallback_command)
            if fallback_result != 0:
                return None
        
        # Optimizar la imagen PNG para mejor calidad y tamaño
        try:
            from PIL import Image, ImageEnhance
            
            # Abrir y mejorar la imagen
            img = Image.open(img_path)
            
            # Aumentar nitidez
            enhancer = ImageEnhance.Sharpness(img)
            img = enhancer.enhance(1.5)  # Factor de nitidez 1.5
            
            # Aumentar ligeramente el contraste
            enhancer = ImageEnhance.Contrast(img)
            img = enhancer.enhance(1.2)  # Factor de contraste 1.2
            
            # Guardar con alta calidad
            img.save(img_path, "PNG", quality=95, optimize=True)
            
            print(f"INFO (map_logic): Imagen optimizada guardada en {img_path}")
        except ImportError:
            print("INFO (map_logic): PIL no disponible para optimización de imagen")
        except Exception as img_error:
            print(f"WARN (map_logic): Error optimizando imagen: {img_error}")
            # Continuamos con la imagen original
        
        print(f"INFO (map_logic): Imagen mapa de alta calidad generada en {img_path}")
        return img_path
        
    except Exception as e:
        print(f"ERROR (map_logic): Error generando imagen del mapa - {e}")
        import traceback
        traceback.print_exc()
        return None

def generar_visualizacion_html(mermaid_code, tema=""):
    """
    Genera una URL data con HTML para visualizar un código Mermaid con estilos mejorados.
    
    Args:
        mermaid_code (str): Código Mermaid a visualizar
        tema (str): Tema del mapa conceptual (opcional)
    
    Returns:
        str: URL de data con HTML para visualizar, o cadena vacía si hay error
    """
    try:
        if not mermaid_code:
            print("ERROR (map_logic): No hay código Mermaid para visualizar")
            return ""
        
        # Formatear el tema con la primera letra de cada palabra en mayúscula
        tema_formateado = ' '.join(word.capitalize() for word in tema.split())
        
        # Sanitizar título ya formateado
        titulo_sanitizado = tema_formateado.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Sanitizar código Mermaid para inclusión en HTML
        mermaid_code_sanitizado = mermaid_code.replace('"', '&quot;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Modificar el código Mermaid para agregar estilos más llamativos
        # Cambiar colores de nodos y bordes para un aspecto más atractivo
        mermaid_code_mejorado = mermaid_code_sanitizado
        
        # Reemplazar estilos por defecto con estilos más coloridos y modernos
        mermaid_code_mejorado = mermaid_code_mejorado.replace(
            "fill:#f9f,stroke:#333,stroke-width:2px", 
            "fill:#6366F1,stroke:#4F46E5,stroke-width:3px,color:#fff,font-weight:bold"
        )
        mermaid_code_mejorado = mermaid_code_mejorado.replace(
            "fill:#ccf,stroke:#333,stroke-width:2px", 
            "fill:#A5B4FC,stroke:#818CF8,stroke-width:2px,color:#000,font-weight:bold"
        )
        mermaid_code_mejorado = mermaid_code_mejorado.replace(
            "fill:#9cf,stroke:#333,stroke-width:2px", 
            "fill:#DBEAFE,stroke:#93C5FD,stroke-width:2px,color:#1E3A8A"
        )
        
        # Crear HTML con el visualizador de Mermaid y estilos mejorados
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Mapa Conceptual: {titulo_sanitizado}</title>
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=Quicksand:wght@400;600;700&family=Comfortaa:wght@400;700&display=swap" rel="stylesheet">
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
            <style>
                body {{
                    font-family: 'Quicksand', sans-serif;
                    margin: 0;
                    padding: 20px;
                    background-color: #f8fafc;
                    color: #1e293b;
                }}
                .container {{
                    max-width: 1200px;
                    margin: 0 auto;
                    background-color: white;
                    padding: 30px;
                    border-radius: 16px;
                    box-shadow: 0 10px 25px rgba(0,0,0,0.08);
                }}
                .mermaid {{
                    background-color: white;
                    padding: 20px;
                    border-radius: 12px;
                    margin-top: 20px;
                }}
                h1 {{
                    font-family: 'Comfortaa', cursive;
                    color: #4338ca;
                    text-align: center;
                    margin-bottom: 30px;
                    font-size: 2.2rem;
                    font-weight: 700;
                    text-shadow: 0px 2px 3px rgba(0,0,0,0.1);
                }}
                .footer {{
                    text-align: center;
                    margin-top: 30px;
                    font-size: 0.9rem;
                    color: #94a3b8;
                }}
                /* Estilos adicionales para el gráfico Mermaid */
                .node rect, .node circle, .node ellipse, .node polygon, .node path {{
                    fill: #6366F1;
                    stroke: #4F46E5;
                    stroke-width: 2px;
                }}
                .edgePath .path {{
                    stroke: #818CF8 !important;
                    stroke-width: 2px !important;
                }}
                .arrowheadPath {{
                    fill: #818CF8 !important;
                }}
                .edgeLabel {{
                    background-color: #fff;
                    padding: 2px;
                }}
                .label {{
                    font-family: 'Quicksand', sans-serif !important;
                    font-weight: 500;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <h1>✨ Mapa Conceptual: {titulo_sanitizado} ✨</h1>
                <div class="mermaid">
                {mermaid_code_mejorado}
                </div>
                <div class="footer">
                    Creado con 💡 SMART_STUDENT
                </div>
            </div>
            <script>
                mermaid.initialize({{ 
                    startOnLoad: true, 
                    theme: 'default', 
                    securityLevel: 'loose',
                    fontFamily: 'Quicksand, sans-serif'
                }});
            </script>
        </body>
        </html>
        """
        
        # Codificar el HTML como URL de datos
        import base64
        encoded_html = base64.b64encode(html_content.encode('utf-8')).decode('utf-8')
        data_url = f"data:text/html;base64,{encoded_html}"
        
        print(f"INFO (map_logic): Visualización HTML mejorada generada ({len(html_content)} bytes)")
        return data_url
        
    except Exception as e:
        print(f"ERROR (map_logic): Error al generar visualización HTML: {e}")
        import traceback
        traceback.print_exc()
        return ""

def generar_mapa_pdf_bytes(mermaid_code=None, tema="", curso="", libro="", html_url=None):
    """
    Genera un PDF del mapa conceptual con la visualización gráfica estilizada y mejor contraste.
    Función de interfaz pública para exportar el mapa a PDF.
    
    Args:
        mermaid_code (str): Código Mermaid del mapa conceptual
        tema (str): Tema del mapa conceptual
        curso (str): Curso relacionado
        libro (str): Libro relacionado
        html_url (str): URL HTML del mapa para capturar (opcional)
    
    Returns:
        bytes: Bytes del PDF generado o None si hay error
    """
    print(f"INFO (map_logic): Generando PDF estilizado de mapa conceptual para '{tema}'")
    
    # Importar datetime aquí para asegurar que está disponible
    import datetime
    
    if not FPDF_AVAILABLE:
        print("ERROR (map_logic): FPDF no está disponible. No se puede generar PDF.", file=sys.stderr)
        return None
    
    try:
        # Asegurarse de que tenemos o el código mermaid o la URL HTML
        if not mermaid_code and not html_url:
            print("ERROR (map_logic): No hay código mermaid ni URL HTML para generar PDF del mapa")
            return None
            
        # Si tenemos HTML URL pero no código mermaid, intentar extraerlo
        if html_url and not mermaid_code:
            try:
                html_code = base64.b64decode(html_url.replace("data:text/html;base64,", "")).decode('utf-8')
                mermaid_match = re.search(r'<div class="mermaid">\s*(graph [^<]+)</div>', html_code, re.DOTALL)
                if mermaid_match:
                    mermaid_code = mermaid_match.group(1)
            except Exception as e:
                print(f"ERROR (map_logic): Error extrayendo mermaid code de HTML: {e}")
                # Continuamos incluso si falla, podríamos tener mermaid_code
        
        # Formatear el tema con la primera letra de cada palabra en mayúscula
        tema_formateado = ' '.join(word.capitalize() for word in tema.split())
        
        # Modificar el código Mermaid para hacer que sea más colorido y MEJORAR EL CONTRASTE
        mermaid_code_estilizado = mermaid_code
        if mermaid_code_estilizado:
            # Nodo central con TEXTO BLANCO para mejor contraste
            mermaid_code_estilizado = mermaid_code_estilizado.replace(
                "fill:#f9f,stroke:#333,stroke-width:2px", 
                "fill:#4F46E5,stroke:#3730A3,stroke-width:3px,color:#FFFFFF,font-weight:bold"
            )
            # Nodos secundarios con buen contraste
            mermaid_code_estilizado = mermaid_code_estilizado.replace(
                "fill:#ccf,stroke:#333,stroke-width:2px", 
                "fill:#818CF8,stroke:#4F46E5,stroke-width:2px,color:#1E1B4B,font-weight:bold"
            )
            # Nodos terciarios con buen contraste
            mermaid_code_estilizado = mermaid_code_estilizado.replace(
                "fill:#9cf,stroke:#333,stroke-width:2px", 
                "fill:#C7D2FE,stroke:#6366F1,stroke-width:2px,color:#1E293B,font-weight:bold"
            )
            
        # Intentar generar una imagen del mapa conceptual con el código estilizado
        img_path = capturar_imagen_mapa(mermaid_code_estilizado, tema_formateado)
        
        # Crear una subclase de FPDF para personalizar cabeceras y pies de página
        class PDF(FPDF):
            def __init__(self, tema, curso, libro, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.tema = tema  # Guardar el tema como atributo de la clase
                self.curso = curso
                self.libro = libro
                
            def header(self):
                # Reducir la altura del encabezado para ganar espacio
                self.set_fill_color(79, 70, 229)  # Color indigo-600 (más oscuro para mejor contraste)
                self.rect(0, 0, self.w, 20, style='F')  # Reducir altura a 20
                
                # Título con estilo
                self.set_font('Helvetica', 'B', 18)  # Texto más grande
                self.set_text_color(255, 255, 255)  # Texto blanco
                self.cell(0, 12, f"Mapa Conceptual: {self.tema}", 0, 1, 'C')
                
                # Subtítulo si hay curso o libro - MEJORAR CONTRASTE
                if self.curso or self.libro:
                    self.set_font('Helvetica', 'B', 12)  # Más pequeño para ajustarse
                    self.set_text_color(220, 220, 255)  # Blanco más saturado para mejor contraste
                    subtitulo = f"Curso: {self.curso}" if self.curso else ""
                    if self.libro:
                        subtitulo += f" - Libro: {self.libro}" if subtitulo else f"Libro: {self.libro}"
                    self.cell(0, 8, subtitulo, 0, 1, 'C')
                
                # Línea decorativa más visible
                self.set_draw_color(209, 213, 219)  # Color gris claro para mejor visibilidad
                self.set_line_width(1.0)  # Línea más gruesa
                self.line(10, 20, self.w - 10, 20)
                self.ln(10)  # Más espacio
            
            def footer(self):
                # Línea decorativa más visible
                self.set_y(-30)
                self.set_draw_color(209, 213, 219)  # Color gris claro
                self.set_line_width(1.0)  # Línea más gruesa
                self.line(10, self.h - 30, self.w - 10, self.h - 30)
                
                # Pie de página con estilo mejorado
                self.set_y(-25)
                self.set_font('Helvetica', 'B', 10)  # Negrita y más grande
                self.set_text_color(67, 56, 202)  # Color indigo-700 (más oscuro)
                self.cell(0, 10, "Este mapa conceptual fue generado por SMART_STUDENT", 0, 0, 'C')
                
                # Número de página con mejor contraste
                self.set_y(-15)
                self.set_font('Helvetica', 'I', 9)
                self.set_text_color(71, 85, 105)  # Color gris oscuro para mejor contraste
                fecha = datetime.datetime.now().strftime("%d/%m/%Y %H:%M")
                self.cell(0, 10, f'Generado el {fecha} - Pág {self.page_no()}', 0, 0, 'C')
        
        # Crear el PDF con la clase personalizada, pasando los parámetros correctamente
        pdf = PDF(tema=tema_formateado, curso=curso, libro=libro, orientation='L')  # Orientación horizontal (landscape)
        pdf.set_auto_page_break(auto=True, margin=35)  # Aumentar margen
        pdf.add_page()
        
        # Configurar margen después del encabezado personalizado
        pdf.set_top_margin(25)  # Ajustar margen superior para reflejar el encabezado reducido
        
        # Añadir la imagen si está disponible
        if img_path and os.path.exists(img_path):
            try:
                # Calcular dimensiones para ajustar la imagen
                page_width = pdf.w - 30  # Margen más amplio
                page_height = pdf.h - 70  # Más espacio para encabezado y pie de página
                
                # Calcular proporciones óptimas para la imagen
                from PIL import Image
                img = Image.open(img_path)
                img_width, img_height = img.size
                
                # Calcular factor de escala para ajustar la imagen proporcionalmente
                width_ratio = page_width / img_width
                height_ratio = page_height / img_height
                scale_factor = min(width_ratio, height_ratio) * 0.9  # 90% del tamaño disponible para dejar margen
                
                # Calcular nuevas dimensiones manteniendo la proporción
                new_width = img_width * scale_factor
                new_height = img_height * scale_factor
                
                # Centrar la imagen horizontalmente
                x_offset = (pdf.w - new_width) / 2
                
                # Añadir un fondo con color suave pero visible detrás de la imagen
                pdf.set_fill_color(237, 233, 254)  # Color indigo-100 (fondo visible pero suave)
                pdf.rect(x_offset - 8, pdf.get_y() - 8, new_width + 16, new_height + 16, style='F')
                
                # Añadir un borde alrededor de la imagen más visible
                pdf.set_draw_color(99, 102, 241)  # Color indigo-500 (más visible)
                pdf.set_line_width(1.0)  # Línea más gruesa
                pdf.rect(x_offset - 8, pdf.get_y() - 8, new_width + 16, new_height + 16)
                
                # Insertar imagen con las dimensiones calculadas
                pdf.image(img_path, x=x_offset, y=pdf.get_y(), w=new_width, h=new_height)
                
                # Actualizar la posición vertical después de la imagen
                pdf.set_y(pdf.get_y() + new_height + 15)
                
            except Exception as img_error:
                print(f"ERROR (map_logic): Error al añadir imagen al PDF: {img_error}")
                traceback.print_exc()
                # Continuamos sin la imagen y mostramos un mensaje de error
                pdf.set_text_color(220, 38, 38)  # Color rojo
                pdf.set_font('Helvetica', 'B', 12)  # Negrita para que se vea bien
                pdf.multi_cell(0, 10, "No se pudo mostrar la imagen del mapa conceptual.")
        
        # Generar PDF en memoria con manejo de errores de codificación
        try:
            pdf_bytes = pdf.output(dest="S").encode("latin-1", "replace")
            print(f"INFO (map_logic): PDF estilizado generado exitosamente ({len(pdf_bytes)} bytes)")
        except UnicodeEncodeError as e:
            print(f"WARN (map_logic): Problema de codificación al generar PDF: {e}")
            # Intentar una codificación alternativa
            pdf_bytes = pdf.output(dest="S").encode("ascii", "replace")
            print(f"INFO (map_logic): PDF generado con codificación alternativa ({len(pdf_bytes)} bytes)")
        
        # Limpiar imagen temporal si existe
        if img_path and os.path.exists(img_path):
            try:
                os.remove(img_path)
                print(f"INFO (map_logic): Imagen temporal eliminada: {img_path}")
            except:
                pass
                
        return pdf_bytes
        
    except Exception as e:
        print(f"ERROR (map_logic): Error generando PDF del mapa: {e}", file=sys.stderr)
        traceback.print_exc()
        return None
