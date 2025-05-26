# backend/config_logic.py
"""
config_logic.py - Configuración y funciones comunes para SMART_STUDENT (Versión Reflex Web)
Adaptado de la versión Kivy/Tkinter.
"""

import os
import sys
import traceback
import requests
from dotenv import load_dotenv
from pypdf import PdfReader  # Asegúrate: pip install pypdf
from passlib.context import CryptContext  # Asegúrate: pip install passlib bcrypt

# --- Cargar variables de entorno desde .env ---
load_dotenv()

# --- Configuración API Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print(
        "ERROR CRITICO (config_logic): La variable de entorno GEMINI_API_KEY no está definida en el archivo .env",
        file=sys.stderr,
    )
    # Considera lanzar un error si la API Key es esencial para iniciar
    # raise ValueError("API Key de Gemini no encontrada en .env")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"  # O la URL del modelo que prefieras

# --- Estructura de Cursos y PDFs ---
CURSOS = {
    ###################
    # ENSEÑANZA BÁSICA
    ###################
    "1ro Básico": {
        "Ciencias Naturales": "CNASM25E1B.pdf",
        "Matemáticas": "MATSA25E1B.pdf",
        "Historia": "HISSM25E1B.pdf",
        "Lenguaje y Literatura": "LYLSA25E1B.pdf",
    },
    "2do Básico": {
        "Ciencias Naturales": "CNASM25E2B.pdf",
        "Matemáticas": "MATSA25E2B.pdf",
        "Historia": "HISSM25E2B.pdf",
        "Lenguaje y Literatura": "LYLSA25E2B.pdf",
    },
    "3ro Básico": {
        "Ciencias Naturales": "CNASM25E3B.pdf",
        "Matemáticas": "MATSA25E3B.pdf",
        "Historia": "HISSM25E3B.pdf",
        "Lenguaje y Literatura": "LYLSA25E3B.pdf",
    },
    "4to Básico": {
        "Ciencias Naturales": "CNASM25E4B.pdf",
        "Matemáticas": "MATSA25E4B.pdf",
        "Historia": "HISSM25E4B.pdf",
        "Lenguaje y Literatura": "LYLSA25E4B.pdf",
    },
    "5to Básico": {
        "Ciencias Naturales": "CNASM25E5B.pdf",
        "Matemáticas": "MATSA25E5B.pdf",
        "Historia": "HISSM25E5B.pdf",
        "Lenguaje y Literatura": "LYLSA25E5B.pdf",
    },
    "6to Básico": {
        "Ciencias Naturales": "CNASM25E6B.pdf",
        "Matemáticas": "MATSA25E6B.pdf",
        "Historia": "HISSM25E6B.pdf",
        "Lenguaje y Literatura": "LYLSA25E6B.pdf",
    },
    "7mo Básico": {
        "Ciencias Naturales": "CNASM25E7B.pdf",
        "Matemáticas": "MATSA25E7B.pdf",
        "Historia": "HISSM25E7B.pdf",
        "Lenguaje y Literatura": "LYLSA25E7B.pdf",
    },
    "8vo Básico": {
        "Ciencias Naturales": "CNASM25E8B.pdf",
        "Matemáticas": "MATSA25E8B.pdf",
        "Historia": "HISSM25E8B.pdf",
        "Lenguaje y Literatura": "LYLSA25E8B.pdf",
    },

    ##################
    # ENSEÑANZA MEDIA
    ##################
    "1ro Medio": {
        "Biología": "BIOSA25E1M.pdf",
        "Física": "FISSA25E1M.pdf",
        "Química": "QUISA25E1M.pdf",
        "Historia": "HISSM25E1M.pdf",
        "Lenguaje y Literatura": "LYLSA25E1M.pdf",
        "Matemáticas": "MATSA25E1M.pdf",
    },
    "2do Medio": {
        "Biología": "BIOSA25E2M.pdf",
        "Física": "FISSA25E2M.pdf",
        "Química": "QUISA25E2M.pdf",
        "Historia": "HISSM25E2M.pdf",
        "Lenguaje y Literatura": "LYLSA25E2M.pdf",
        "Matemáticas": "MATSA25E2M.pdf",
    },
    "3ro Medio": {
        "Ciencias para la Ciudadanía": "CPCSA25E3M.pdf",
        "Lenguaje y Literatura": "LYLSA25E3M.pdf",
        "Matemáticas": "MATSA25E3M.pdf",
    },
    "4to Medio": {
        "Ciencias para la Ciudadanía": "CPCSA25E4M.pdf",
        "Lenguaje y Literatura": "LYLSA25E4M.pdf",
        "Matemáticas": "MATSA25E4M.pdf",
    },
}



# Verificación de integridad de CURSOS al cargar el módulo
print(f"INFO (config_logic): Cargados {len(CURSOS)} cursos con sus libros correspondientes")
for curso, libros in CURSOS.items():
    print(f"  - {curso}: {len(libros)} libros")

# --- Configuración de Hashing de Contraseñas ---
# Crear contexto de hashing (hacer esto una sola vez)
# Usamos bcrypt, que es un estándar seguro. Necesita 'pip install bcrypt'
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- EJEMPLO de HASHES - ¡NO ALMACENAR ASÍ EN PRODUCCIÓN! ---
# Estos hashes deberías generarlos una vez y almacenarlos de forma segura
# (por ejemplo, en tu base de datos junto al usuario).
# Para generar un hash: print(pwd_context.hash("tu_contraseña_plana"))
# IMPORTANTE: Usamos hashes pre-calculados para mantener consistencia entre reinicios
usuarios_hashes_ejemplo = {
    "estudiante": "$2b$12$LJNYuw82bm7z6ZmZ3Fc97uDRtAAJei8vl2DZi4BQm8RfCLUzV/jIK",  # clave123
    "profe": "$2b$12$Y7.3sV02.t.fptwdQV/SXOQcOCq1FHz7OE8lCZUGX06Kz.sZAiLTO",  # segura456
    "felipe": "$2b$12$7PnRxmra6m5/TZ1ZxVdC1.8T0H48RfAK9GnSmwcCSZ7sIJYrkOZ7S",  # 1234
    "test": "$2b$12$qE1qdIpJ0M/NaJO3.P4YaeYH1glAKZ8dPVxX0GJnTMNZx8BAtHFZ2",  # 123
    # Añade aquí los usuarios y hashes que necesites para probar
}
print("INFO (config_logic): Hashes de ejemplo cargados (¡SOLO PARA DESARROLLO!)")
# Reemplaza usuarios_hashes_ejemplo con tu método real de carga de usuarios/hashes


# --- Función de Validación de Login (Adaptada) ---
def validar_credenciales(username, password_plana):
    """
    Valida las credenciales del usuario usando hashes seguros.
    ¡NECESITA un método seguro para cargar/buscar usuarios y hashes!
    """
    print(f"DEBUG (config_logic): Validando credenciales para '{username}'...")
    # --- ¡REEMPLAZAR ESTO con tu lógica real de búsqueda de usuarios/hashes! ---
    if username in usuarios_hashes_ejemplo:
        hash_almacenado = usuarios_hashes_ejemplo[username]
        # --- Fin de lógica de ejemplo ---

        try:
            # Verificar la contraseña plana contra el hash almacenado
            es_valido = pwd_context.verify(password_plana, hash_almacenado)
            print(
                f"DEBUG (config_logic): Resultado de verificación para '{username}': {es_valido}"
            )
            return es_valido
        except Exception as e_hash:
            # Errores posibles: hash inválido, problema con passlib/bcrypt
            print(
                f"ERROR (config_logic): Verificando hash para '{username}' - {e_hash}",
                file=sys.stderr,
            )
            traceback.print_exc()
            return False
    else:
        print(
            f"DEBUG (config_logic): Usuario '{username}' no encontrado en el sistema (ejemplo)."
        )
        return False


# --- Funciones de Manejo de PDFs (Adaptadas) ---
def obtener_directorio_pdf(curso):
    """
    Obtiene el directorio relativo donde se esperan los PDFs de un curso.
    Asume que los PDFs están en 'assets/pdfs/nombre_curso_normalizado/'.
    """
    # Normalizar nombre del curso para usarlo como nombre de carpeta
    # Reemplaza espacios, quita caracteres especiales excepto guiones bajos/altos
    nivel_normalizado = "".join(c if c.isalnum() else "_" for c in curso.lower()).strip(
        "_"
    )
    # Ruta relativa desde la raíz del proyecto Reflex
    base_path = "assets/pdfs"
    dir_path = os.path.join(base_path, nivel_normalizado)
    print(
        f"DEBUG (config_logic): Ruta PDF calculada para curso '{curso}': '{dir_path}'"
    )
    # Podrías añadir una verificación si el directorio existe aquí si es necesario
    # if not os.path.isdir(dir_path):
    #     print(f"WARN (config_logic): El directorio '{dir_path}' no existe.")
    return dir_path


def extraer_texto_pdf(curso, archivo):
    """
    Extrae el texto de un archivo PDF ubicado en la ruta relativa del proyecto.
    Lanza excepciones específicas en caso de error.
    """
    directorio = obtener_directorio_pdf(curso)
    ruta_completa = os.path.join(directorio, archivo)

    try:
        print(f"INFO (config_logic): Intentando leer PDF desde: '{ruta_completa}'")
        if not os.path.exists(ruta_completa):
            error_msg = (
                f"Archivo PDF no encontrado en la ruta esperada: {ruta_completa}"
            )
            print(f"ERROR (config_logic): {error_msg}")
            raise FileNotFoundError(error_msg)

        with open(ruta_completa, "rb") as f:
            pdf = PdfReader(f)
            texto = ""
            num_paginas = len(pdf.pages)
            print(
                f"INFO (config_logic): Leyendo {num_paginas} páginas de '{archivo}'..."
            )
            for i, page in enumerate(pdf.pages):
                try:
                    texto_pagina = page.extract_text()
                    if texto_pagina:
                        texto += texto_pagina + "\n"
                except Exception as e_page:
                    # Advertir sobre página específica pero continuar
                    print(
                        f"WARN (config_logic): Error al extraer texto de página {i+1}/{num_paginas} de '{archivo}': {e_page}"
                    )
                    texto += "[Error en página]\n"  # Añadir marcador

            palabras = texto.split()
            num_palabras = len(palabras)
            # Limitar a ~50k caracteres para evitar prompts excesivamente largos (ajustar según necesidad)
            max_chars = 50000
            if len(texto) > max_chars:
                print(
                    f"INFO (config_logic): Texto truncado a {max_chars} caracteres (original: {len(texto)}, {num_palabras} palabras)"
                )
                texto = texto[:max_chars]
            # limitar palabras también
            # if num_palabras > 10000:
            #     print(
            #         f"INFO: Texto truncado a 10000 palabras (original: {num_palabras})"
            #     )
            #     texto = " ".join(palabras[:10000])

            print(
                f"INFO (config_logic): Texto extraído de '{archivo}' (longitud: {len(texto)} chars, aprox: {num_palabras} palabras)"
            )
            return texto.strip()

    except FileNotFoundError as e_fnf:
        # Relanzar FileNotFoundError específicamente
        raise e_fnf
    except Exception as e:
        error_msg = f"No se pudo leer o procesar el PDF '{archivo}': {e}"
        print(f"ERROR (config_logic): {error_msg}", file=sys.stderr)
        traceback.print_exc()
        # Lanzar una excepción genérica de IO o una personalizada
        raise IOError(error_msg) from e


# --- Funciones de API Gemini (Adaptadas, sin Tkinter) ---
# NOTA: Considera mover estas a api_logic.py y usar la librería google-generativeai


def llamar_api_gemini(prompt):
    """Llama a la API de Gemini con un prompt y devuelve la respuesta."""
    try:
        url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        headers = {"Content-Type": "application/json"}
        if GEMINI_API_KEY:
            headers["x-goog-api-key"] = GEMINI_API_KEY
        
        # Aumentar el límite de tokens en la solicitud
        data = {
            "contents": [{"parts":[{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192,  # Aumentar el límite de tokens en la salida
                "topP": 0.8,
                "topK": 40
            }
        }
        # Limitar longitud del prompt (ajustar según modelo y necesidad)
        max_prompt_len = 30000  # Caracteres, no tokens necesariamente
        if len(prompt) > max_prompt_len:
            print(
                f"WARN (config_logic): Prompt truncado a {max_prompt_len} caracteres (original: {len(prompt)})"
            )
            prompt = prompt[:max_prompt_len]

        api_url_completa = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        print(
            f"INFO (config_logic): Llamando API Gemini (URL: ...{GEMINI_API_URL[-20:]}, prompt len: {len(prompt)})"
        )

        try:
            # Timeout más largo puede ser necesario para generación compleja
            response = requests.post(
                api_url_completa, headers=headers, json=data, timeout=180
            )
            response.raise_for_status()  # Lanza HTTPError para respuestas 4xx/5xx
            respuesta_json = response.json()

            # Validaciones robustas de la respuesta
            if (
                not isinstance(respuesta_json.get("candidates"), list)
                or not respuesta_json["candidates"]
            ):
                error_msg = "Error: Respuesta de la API no contiene 'candidates' válidos."
                print(
                    f"ERROR API (config_logic): {error_msg} Respuesta: {respuesta_json}",
                    file=sys.stderr,
                )
                return error_msg  # Devolver mensaje de error

            candidate = respuesta_json["candidates"][0]
            finish_reason = candidate.get("finishReason", "UNKNOWN")

            # Comprobar si el contenido fue bloqueado
            if finish_reason != "STOP":
                print(
                    f"WARN API (config_logic): Finish Reason no fue STOP: {finish_reason}"
                )
                if finish_reason == "SAFETY":
                    safety_ratings = candidate.get("safetyRatings", [])
                    error_msg = f"Error: Contenido bloqueado por seguridad (Razón: {finish_reason}). Ratings: {safety_ratings}"
                    print(f"ERROR API (config_logic): {error_msg}", file=sys.stderr)
                    return error_msg  # Devolver mensaje de error
                # Podrías manejar otros finish_reason aquí (MAX_TOKENS, etc.)

            # Extraer texto de las partes
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            if not isinstance(parts, list) or not parts:
                error_msg = f"Error: Formato de 'content'/'parts' inválido o ausente (Finish Reason: {finish_reason})."
                print(
                    f"ERROR API (config_logic): {error_msg} Candidate: {candidate}",
                    file=sys.stderr,
                )
                return error_msg  # Devolver mensaje de error

            texto_generado = ""
            for part in parts:
                if "text" in part and isinstance(part["text"], str):
                    texto_generado += part["text"]

            if not texto_generado:
                # Esto puede pasar si la API devuelve partes vacías o sin texto
                print(
                    f"WARN API (config_logic): No se encontró texto útil en la respuesta (Finish Reason: {finish_reason}). Parts: {parts}",
                    file=sys.stderr,
                )
                # Podrías devolver un error o un string vacío dependiendo de cómo lo manejes
                return "Advertencia: La API no devolvió texto útil."

            print("INFO (config_logic): Texto recibido de la API Gemini.")
            return texto_generado  # Devolver texto generado

        except requests.exceptions.Timeout:
            error_msg = "Error: Timeout al conectar con la API de Gemini."
            print(f"ERROR API (config_logic): {error_msg}", file=sys.stderr)
            return error_msg  # Devolver mensaje de error
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de conexión con la API de Gemini: {e}"
            print(f"ERROR API (config_logic): {error_msg}", file=sys.stderr)
            return error_msg  # Devolver mensaje de error
        except KeyError as e_key:
            error_msg = f"Error al procesar la respuesta de la API (Falta clave: {e_key})."
            print(
                f"ERROR API (config_logic): {error_msg} Respuesta: {response.text[:500]}...",
                file=sys.stderr,
            )
            return error_msg  # Devolver mensaje de error
        except Exception as e_gen:
            error_msg = f"Ocurrió un error inesperado al llamar a la API: {e_gen}"
            print(f"ERROR API (config_logic): {error_msg}", file=sys.stderr)
            traceback.print_exc()
            return error_msg  # Devolver mensaje de error

    except Exception as e:
        error_msg = f"Ocurrió un error inesperado al llamar a la API: {e}"
        print(f"ERROR API (config_logic): {error_msg}", file=sys.stderr)
        traceback.print_exc()
        return error_msg  # Devolver mensaje de error


def verificar_api_gemini():
    """Verifica si la API de Gemini está accesible. Devuelve True/False."""
    if not GEMINI_API_KEY:
        print(
            "ERROR (config_logic): No se puede verificar API, key no configurada.",
            file=sys.stderr,
        )
        return False

    print("INFO (config_logic): Verificando conexión con API Gemini...")
    try:
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            json={"contents": [{"parts": [{"text": "Verificación rápida"}]}]},
            timeout=20,  # Timeout corto para verificación
        )
        response.raise_for_status()  # Chequea errores HTTP

        # Una verificación simple es suficiente, no necesitamos validar el contenido exacto aquí
        if response.status_code == 200:
            print("INFO (config_logic): Verificación de API Gemini exitosa (HTTP 200).")
            return True
        else:
            print(
                f"WARN (config_logic): Verificación API devolvió status {response.status_code} pero sin error HTTP.",
                file=sys.stderr,
            )
            return False  # Considerar false si no es 200 OK

    except requests.exceptions.Timeout:
        print(
            "ERROR (config_logic): Timeout durante verificación de API.",
            file=sys.stderr,
        )
        return False
    except requests.exceptions.RequestException as e:
        print(
            f"ERROR (config_logic): RequestException durante verificación de API: {e}",
            file=sys.stderr,
        )
        return False
    except Exception as e_verif:
        print(
            f"ERROR (config_logic): Excepción general durante verificación de API: {e_verif}",
            file=sys.stderr,
        )
        traceback.print_exc()
        return False


def _curso_sort_key(curso: str) -> tuple:
    """Helper function to sort cursos in correct order."""
    # Extraer el número y el nivel
    numero = ""
    for char in curso:
        if char.isdigit():
            numero += char
    
    # Convertir a int para ordenamiento numérico
    num = int(numero) if numero else 0
    
    # Prioridad: Básico = 0, Medio = 1
    prioridad = 1 if "Medio" in curso else 0
    
    return (prioridad, num)

def obtener_lista_cursos():
    """Retorna la lista de cursos ordenada para la lista desplegable."""
    # Obtener lista de cursos de CURSOS
    lista_cursos = list(CURSOS.keys())
    
    # Ordenar usando la función helper
    lista_cursos.sort(key=_curso_sort_key)
    
    return lista_cursos


# --- Puedes añadir aquí un bloque if __name__ == "__main__": para probar funciones ---
if __name__ == "__main__":
    print("--- Ejecutando pruebas de config_logic.py ---")

    # Prueba de validación (cambia usuarios/contraseñas para probar)
    print("\nProbando validación:")
    user_test = "felipe"
    pass_test_ok = "1234"
    pass_test_fail = "incorrecta"
    print(
        f"Validando {user_test}/{pass_test_ok}: {validar_credenciales(user_test, pass_test_ok)}"
    )
    print(
        f"Validando {user_test}/{pass_test_fail}: {validar_credenciales(user_test, pass_test_fail)}"
    )
    print(
        f"Validando usuario_inexistente/pass: {validar_credenciales('usuario_inexistente', 'pass')}"
    )

    # Prueba de ruta PDF
    print("\nProbando ruta PDF:")
    print(f"Ruta para 1ro Básico: {obtener_directorio_pdf('1ro Básico')}")
    # Crea el directorio y un archivo dummy si quieres probar extraer_texto_pdf
    # ej_curso = "1ro Básico"
    # ej_libro_nombre = "Matemáticas"
    # ej_archivo = CURSOS.get(ej_curso, {}).get(ej_libro_nombre)
    # if ej_archivo:
    #     pdf_dir = obtener_directorio_pdf(ej_curso)
    #     os.makedirs(pdf_dir, exist_ok=True)
    #     dummy_pdf_path = os.path.join(pdf_dir, ej_archivo)
    #     # Crear un PDF dummy requeriría fpdf u otra lib, omitido por simplicidad
    #     # print(f"Intentando extraer de (debe existir y ser PDF válido): {dummy_pdf_path}")
    #     # try:
    #     #     texto = extraer_texto_pdf(ej_curso, ej_archivo)
    #     #     print(f"Texto extraído (dummy): {texto[:100]}...")
    #     # except Exception as e:
    #     #     print(f"Error extracción (esperado si es dummy): {e}")

    # Prueba verificación API (requiere conexión y API Key válida)
    print("\nProbando verificación API:")
    if (
        GEMINI_API_KEY and "TU_API_KEY" not in GEMINI_API_KEY
    ):  # Evitar si no se puso key real
        api_ok = verificar_api_gemini()
        print(f"Resultado verificación API: {api_ok}")
    else:
        print("Saltando verificación API (API Key no configurada o es placeholder).")

    print("\n--- Pruebas finalizadas ---")
