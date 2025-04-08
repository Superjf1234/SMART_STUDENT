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
import logging

# --- Configuración de logging ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s (%(module)s): %(message)s')

# --- Cargar variables de entorno desde .env ---
load_dotenv()

# --- Configuración API Gemini ---
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logging.critical("La variable de entorno GEMINI_API_KEY no está definida en el archivo .env")
    # Considera lanzar un error si la API Key es esencial para iniciar
    # raise ValueError("API Key de Gemini no encontrada en .env")
GEMINI_API_URL = os.getenv("GEMINI_API_URL", "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent")

# --- Estructura de Cursos y PDFs ---
# Asegúrate de que los nombres de archivo PDF coincidan con los que pongas en assets/pdfs/...
CURSOS = {
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
    # ... (Completa con TODOS tus cursos y archivos) ...
    "8vo Básico": {
        "Ciencias Naturales": "CNASM25E8B.pdf",
        "Matemáticas": "MATSA25E8B.pdf",
        "Historia": "HISSM25E8B.pdf",
        "Lenguaje y Literatura": "LYLSA25E8B.pdf",
    },
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

# --- Configuración de Hashing de Contraseñas ---
# Crear contexto de hashing (hacer esto una sola vez)
# Usamos bcrypt, que es un estándar seguro. Necesita 'pip install bcrypt'
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- EJEMPLO de HASHES - ¡NO ALMACENAR ASÍ EN PRODUCCIÓN! ---
# Estos hashes deberías generarlos una vez y almacenarlos de forma segura
# (por ejemplo, en tu base de datos junto al usuario).
# Para generar un hash: print(pwd_context.hash("tu_contraseña_plana"))
usuarios_hashes_ejemplo = {
    "estudiante": pwd_context.hash("clave123"),  # Genera un hash diferente cada vez
    "profe": pwd_context.hash("segura456"),
    "felipe": pwd_context.hash("1234"),
    # Añade aquí los usuarios y hashes que necesites para probar
}
logging.info("Hashes de ejemplo cargados (¡SOLO PARA DESARROLLO!)")
# Reemplaza usuarios_hashes_ejemplo con tu método real de carga de usuarios/hashes


# --- Función de Validación de Login (Adaptada) ---
def validar_credenciales(username, password_plana):
    """
    Valida las credenciales del usuario usando hashes seguros.
    ¡NECESITA un método seguro para cargar/buscar usuarios y hashes!
    """
    logging.debug(f"Validando credenciales para '{username}'...")
    # --- ¡REEMPLAZAR ESTO con tu lógica real de búsqueda de usuarios/hashes! ---
    if username in usuarios_hashes_ejemplo:
        hash_almacenado = usuarios_hashes_ejemplo[username]
        # --- Fin de lógica de ejemplo ---

        try:
            # Verificar la contraseña plana contra el hash almacenado
            es_valido = pwd_context.verify(password_plana, hash_almacenado)
            logging.debug(f"Resultado de verificación para '{username}': {es_valido}")
            return es_valido
        except Exception as e_hash:
            # Errores posibles: hash inválido, problema con passlib/bcrypt
            logging.error(f"Verificando hash para '{username}' - {e_hash}")
            traceback.print_exc()
            return False
    else:
        logging.debug(f"Usuario '{username}' no encontrado en el sistema (ejemplo).")
        return False


# --- Funciones de Manejo de PDFs (Adaptadas) ---
def obtener_directorio_pdf(curso):
    """
    Obtiene el directorio relativo donde se esperan los PDFs de un curso.
    Asume que los PDFs están en 'assets/pdfs/nombre_curso_normalizado/'.
    """
    # Normalizar nombre del curso para usarlo como nombre de carpeta
    # Reemplaza espacios, quita caracteres especiales excepto guiones bajos/altos
    nivel_normalizado = "".join(c if c.isalnum() else "_" for c in curso.lower()).strip("_")
    # Ruta relativa desde la raíz del proyecto Reflex
    base_path = "assets/pdfs"
    dir_path = os.path.join(base_path, nivel_normalizado)
    logging.debug(f"Ruta PDF calculada para curso '{curso}': '{dir_path}'")
    # Podrías añadir una verificación si el directorio existe aquí si es necesario
    # if not os.path.isdir(dir_path):
    #     logging.warning(f"El directorio '{dir_path}' no existe.")
    return dir_path


def extraer_texto_pdf(curso, archivo):
    """
    Extrae el texto de un archivo PDF ubicado en la ruta relativa del proyecto.
    Lanza excepciones específicas en caso de error.
    """
    directorio = obtener_directorio_pdf(curso)
    ruta_completa = os.path.join(directorio, archivo)

    try:
        logging.info(f"Intentando leer PDF desde: '{ruta_completa}'")
        if not os.path.exists(ruta_completa):
            error_msg = f"Archivo PDF no encontrado en la ruta esperada: {ruta_completa}"
            logging.error(error_msg)
            raise FileNotFoundError(error_msg)

        with open(ruta_completa, "rb") as f:
            pdf = PdfReader(f)
            texto = ""
            num_paginas = len(pdf.pages)
            logging.info(f"Leyendo {num_paginas} páginas de '{archivo}'...")
            for i, page in enumerate(pdf.pages):
                try:
                    texto_pagina = page.extract_text()
                    if texto_pagina:
                        texto += texto_pagina + "\n"
                except Exception as e_page:
                    # Advertir sobre página específica pero continuar
                    logging.warning(f"Error al extraer texto de página {i+1}/{num_paginas} de '{archivo}': {e_page}")
                    texto += "[Error en página]\n"  # Añadir marcador

            palabras = texto.split()
            num_palabras = len(palabras)
            # Limitar a ~50k caracteres para evitar prompts excesivamente largos (ajustar según necesidad)
            max_chars = 50000
            if len(texto) > max_chars:
                logging.info(f"Texto truncado a {max_chars} caracteres (original: {len(texto)}, {num_palabras} palabras)")
                texto = texto[:max_chars]
            # limitar palabras también
            # if num_palabras > 10000:
            #     logging.info(f"Texto truncado a 10000 palabras (original: {num_palabras})")
            #     texto = " ".join(palabras[:10000])

            logging.info(f"Texto extraído de '{archivo}' (longitud: {len(texto)} chars, aprox: {num_palabras} palabras)")
            return texto.strip()

    except FileNotFoundError as e_fnf:
        # Relanzar FileNotFoundError específicamente
        raise e_fnf
    except Exception as e:
        error_msg = f"No se pudo leer o procesar el PDF '{archivo}': {e}"
        logging.error(error_msg)
        traceback.print_exc()
        # Lanzar una excepción genérica de IO o una personalizada
        raise IOError(error_msg) from e


# --- Funciones de API Gemini (Adaptadas, sin Tkinter) ---
# NOTA: Considera mover estas a api_logic.py y usar la librería google-generativeai


def llamar_api_gemini(prompt):
    """Llama a la API de Gemini para generar contenido. Devuelve texto o mensaje de error."""
    if not GEMINI_API_KEY:
        error_msg = "Error: API Key de Gemini no configurada."
        logging.error(error_msg)
        return error_msg  # Devolver mensaje de error

    headers = {"Content-Type": "application/json"}
    # Limitar longitud del prompt (ajustar según modelo y necesidad)
    max_prompt_len = 30000  # Caracteres, no tokens necesariamente
    if len(prompt) > max_prompt_len:
        logging.warning(f"Prompt truncado a {max_prompt_len} caracteres (original: {len(prompt)})")
        prompt = prompt[:max_prompt_len]

    data = {"contents": [{"parts": [{"text": prompt}]}]}
    api_url_completa = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    logging.info(f"Llamando API Gemini (URL: ...{GEMINI_API_URL[-20:]}, prompt len: {len(prompt)})")

    try:
        # Timeout más largo puede ser necesario para generación compleja
        response = requests.post(api_url_completa, headers=headers, json=data, timeout=180)
        response.raise_for_status()  # Lanza HTTPError para respuestas 4xx/5xx
        respuesta_json = response.json()

        # Validaciones robustas de la respuesta
        if not isinstance(respuesta_json.get("candidates"), list) or not respuesta_json["candidates"]:
            error_msg = "Error: Respuesta de la API no contiene 'candidates' válidos."
            logging.error(f"{error_msg} Respuesta: {respuesta_json}")
            return error_msg  # Devolver mensaje de error

        candidate = respuesta_json["candidates"][0]
        finish_reason = candidate.get("finishReason", "UNKNOWN")

        # Comprobar si el contenido fue bloqueado
        if finish_reason != "STOP":
            logging.warning(f"Finish Reason no fue STOP: {finish_reason}")
            if finish_reason == "SAFETY":
                safety_ratings = candidate.get("safetyRatings", [])
                error_msg = f"Error: Contenido bloqueado por seguridad (Razón: {finish_reason}). Ratings: {safety_ratings}"
                logging.error(error_msg)
                return error_msg  # Devolver mensaje de error
            # Podrías manejar otros finish_reason aquí (MAX_TOKENS, etc.)

        # Extraer texto de las partes
        content = candidate.get("content", {})
        parts = content.get("parts", [])
        if not isinstance(parts, list) or not parts:
            error_msg = f"Error: Formato de 'content'/'parts' inválido o ausente (Finish Reason: {finish_reason})."
            logging.error(f"{error_msg} Candidate: {candidate}")
            return error_msg  # Devolver mensaje de error

        texto_generado = ""
        for part in parts:
            if "text" in part and isinstance(part["text"], str):
                texto_generado += part["text"]

        if not texto_generado:
            # Esto puede pasar si la API devuelve partes vacías o sin texto
            logging.warning(f"No se encontró texto útil en la respuesta (Finish Reason: {finish_reason}). Parts: {parts}")
            # Podrías devolver un error o un string vacío dependiendo de cómo lo manejes
            return "Advertencia: La API no devolvió texto útil."

        logging.info("Texto recibido de la API Gemini.")
        return texto_generado  # Devolver texto generado

    except requests.exceptions.Timeout:
        error_msg = "Error: Timeout al conectar con la API de Gemini."
        logging.error(error_msg)
        return error_msg  # Devolver mensaje de error
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión con la API de Gemini: {e}"
        logging.error(error_msg)
        return error_msg  # Devolver mensaje de error
    except KeyError as e_key:
        error_msg = f"Error al procesar la respuesta de la API (Falta clave: {e_key})."
        logging.error(f"{error_msg} Respuesta: {response.text[:500]}...")
        return error_msg  # Devolver mensaje de error
    except Exception as e_gen:
        error_msg = f"Ocurrió un error inesperado al llamar a la API: {e_gen}"
        logging.error(error_msg)
        traceback.print_exc()
        return error_msg  # Devolver mensaje de error


def verificar_api_gemini():
    """Verifica si la API de Gemini está accesible. Devuelve True/False."""
    if not GEMINI_API_KEY:
        logging.error("No se puede verificar API, key no configurada.")
        return False

    logging.info("Verificando conexión con API Gemini...")
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
            logging.info("Verificación de API Gemini exitosa (HTTP 200).")
            return True
        else:
            logging.warning(f"Verificación API devolvió status {response.status_code} pero sin error HTTP.")
            return False  # Considerar false si no es 200 OK

    except requests.exceptions.Timeout:
        logging.error("Timeout durante verificación de API.")
        return False
    except requests.exceptions.RequestException as e:
        logging.error(f"RequestException durante verificación de API: {e}")
        return False
    except Exception as e_verif:
        logging.error(f"Excepción general durante verificación de API: {e_verif}")
        traceback.print_exc()
        return False


# --- Puedes añadir aquí un bloque if __name__ == "__main__": para probar funciones ---
if __name__ == "__main__":
    logging.info("--- Ejecutando pruebas de config_logic.py ---")

    # Prueba de validación (cambia usuarios/contraseñas para probar)
    logging.info("\nProbando validación:")
    user_test = "felipe"
    pass_test_ok = "1234"
    pass_test_fail = "incorrecta"
    logging.info(f"Validando {user_test}/{pass_test_ok}: {validar_credenciales(user_test, pass_test_ok)}")
    logging.info(f"Validando {user_test}/{pass_test_fail}: {validar_credenciales(user_test, pass_test_fail)}")
    logging.info(f"Validando usuario_inexistente/pass: {validar_credenciales('usuario_inexistente', 'pass')}")

    # Prueba de ruta PDF
    logging.info("\nProbando ruta PDF:")
    logging.info(f"Ruta para 1ro Básico: {obtener_directorio_pdf('1ro Básico')}")
    # Crea el directorio y un archivo dummy si quieres probar extraer_texto_pdf
    # ej_curso = "1ro Básico"
    # ej_libro_nombre = "Matemáticas"
    # ej_archivo = CURSOS.get(ej_curso, {}).get(ej_libro_nombre)
    # if ej_archivo:
    #     pdf_dir = obtener_directorio_pdf(ej_curso)
    #     os.makedirs(pdf_dir, exist_ok=True)
    #     dummy_pdf_path = os.path.join(pdf_dir, ej_archivo)
    #     # Crear un PDF dummy requeriría fpdf u otra lib, omitido por simplicidad
    #     # logging.info(f"Intentando extraer de (debe existir y ser PDF válido): {dummy_pdf_path}")
    #     # try:
    #     #     texto = extraer_texto_pdf(ej_curso, ej_archivo)
    #     #     logging.info(f"Texto extraído (dummy): {texto[:100]}...")
    #     # except Exception as e:
    #     #     logging.error(f"Error extracción (esperado si es dummy): {e}")

    # Prueba verificación API (requiere conexión y API Key válida)
    logging.info("\nProbando verificación API:")
    if GEMINI_API_KEY and "TU_API_KEY" not in GEMINI_API_KEY:  # Evitar si no se puso key real
        api_ok = verificar_api_gemini()
        logging.info(f"Resultado verificación API: {api_ok}")
    else:
        logging.info("Saltando verificación API (API Key no configurada o es placeholder).")

    logging.info("\n--- Pruebas finalizadas ---")
