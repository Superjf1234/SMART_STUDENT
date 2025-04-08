# backend/map_logic.py
import os
import traceback
import sys
import random  # Puede que aún uses random para IDs si lo dejaste

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


# ELIMINADO: Verificación de mmdc y MERMAID_AVAILABLE


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

    if not curso, not libro, not tema_usuario:
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
