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
GEMINI_API_URL = os.getenv("GEMINI_API_URL")
if not GEMINI_API_URL:
    print(
        "ERROR CRITICO (config_logic): La variable de entorno GEMINI_API_URL no está definida en el archivo .env",
        file=sys.stderr,
    )

# --- Estructura de Cursos y PDFs ---
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
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# --- EJEMPLO de HASHES - ¡NO ALMACENAR ASÍ EN PRODUCCIÓN! ---
usuarios_hashes_ejemplo = {
    "estudiante": pwd_context.hash("clave123"),
    "profe": pwd_context.hash("segura456"),
    "felipe": pwd_context.hash("1234"),
}
print("INFO (config_logic): Hashes de ejemplo cargados (¡SOLO PARA DESARROLLO!)")

# --- Función de Validación de Login (Adaptada) ---
def validar_credenciales(username, password_plana):
    print(f"DEBUG (config_logic): Validando credenciales para '{username}'...")
    if username in usuarios_hashes_ejemplo:
        hash_almacenado = usuarios_hashes_ejemplo[username]
        try:
            es_valido = pwd_context.verify(password_plana, hash_almacenado)
            print(
                f"DEBUG (config_logic): Resultado de verificación para '{username}': {es_valido}"
            )
            return es_valido
        except Exception as e_hash:
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
    nivel_normalizado = "".join(c if c.isalnum() else "_" for c in curso.lower()).strip(
        "_"
    )
    base_path = "assets/pdfs"
    dir_path = os.path.join(base_path, nivel_normalizado)
    print(
        f"DEBUG (config_logic): Ruta PDF calculada para curso '{curso}': '{dir_path}'"
    )
    return dir_path

def extraer_texto_pdf(curso, archivo):
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
                    print(
                        f"WARN (config_logic): Error al extraer texto de página {i+1}/{num_paginas} de '{archivo}': {e_page}"
                    )
                    texto += "[Error en página]\n"

            palabras = texto.split()
            num_palabras = len(palabras)
            max_chars = 50000
            if len(texto) > max_chars:
                print(
                    f"INFO (config_logic): Texto truncado a {max_chars} caracteres (original: {len(texto)}, {num_palabras} palabras)"
                )
                texto = texto[:max_chars]

            print(
                f"INFO (config_logic): Texto extraído de '{archivo}' (longitud: {len(texto)} chars, aprox: {num_palabras} palabras)"
            )
            return texto.strip()

    except FileNotFoundError as e_fnf:
        raise e_fnf
    except Exception as e:
        error_msg = f"No se pudo leer o procesar el PDF '{archivo}': {e}"
        print(f"ERROR (config_logic): {error_msg}", file=sys.stderr)
        traceback.print_exc()
        raise IOError(error_msg) from e

# --- Funciones de API Gemini (Adaptadas, sin Tkinter) ---
def llamar_api_gemini(prompt):
    if not GEMINI_API_KEY:
        error_msg = "Error: API Key de Gemini no configurada."
        print(f"ERROR (config_logic): {error_msg}", file=sys.stderr)
        return error_msg

    headers = {"Content-Type": "application/json"}
    max_prompt_len = 30000
    if len(prompt) > max_prompt_len:
        print(
            f"WARN (config_logic): Prompt truncado a {max_prompt_len} caracteres (original: {len(prompt)})"
        )
        prompt = prompt[:max_prompt_len]

    data = {"contents": [{"parts": [{"text": prompt}]}]}
    api_url_completa = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
    print(
        f"INFO (config_logic): Llamando API Gemini (URL: ...{GEMINI_API_URL[-20:]}, prompt len: {len(prompt)})"
    )

    try:
        response = requests.post(
            api_url_completa, headers=headers, json=data, timeout=180
        )
        response.raise_for_status()
        respuesta_json = response.json()

        if (
            not isinstance(respuesta_json.get("candidates"), list)
            or not respuesta_json["candidates"]
        ):
            error_msg = "Error: Respuesta de la API no contiene 'candidates' válidos."
            print(
                f"ERROR API (config_logic): {error_msg} Respuesta: {respuesta_json}",
                file=sys.stderr,
            )
            return error_msg

        candidate = respuesta_json["candidates"][0]
        finish_reason = candidate.get("finishReason", "UNKNOWN")

        if finish_reason != "STOP":
            print(
                f"WARN API (config_logic): Finish Reason no fue STOP: {finish_reason}"
            )
            if finish_reason == "SAFETY":
                safety_ratings = candidate.get("safetyRatings", [])
                error_msg = f"Error: Contenido bloqueado por seguridad (Razón: {finish_reason}). Ratings: {safety_ratings}"
                print(f"ERROR API (config_logic): {error_msg}", file=sys.stderr)
                return error_msg

        content = candidate.get("content", {})
        parts = content.get("parts", [])
        if not isinstance(parts, list) or not parts:
            error_msg = f"Error: Formato de 'content'/'parts' inválido o ausente (Finish Reason: {finish_reason})."
            print(
                f"ERROR API (config_logic): {error_msg} Candidate: {candidate}",
                file=sys.stderr,
            )
            return error_msg

        texto_generado = ""
        for part in parts:
            if "text" in part and isinstance(part["text"], str):
                texto_generado += part["text"]

        if not texto_generado:
            print(
                f"WARN API (config_logic): No se encontró texto útil en la respuesta (Finish Reason: {finish_reason}). Parts: {parts}",
                file=sys.stderr,
            )
            return "Advertencia: La API no devolvió texto útil."

        print("INFO (config_logic): Texto recibido de la API Gemini.")
        return texto_generado

    except requests.exceptions.Timeout:
        error_msg = "Error: Timeout al conectar con la API de Gemini."
        print(f"ERROR API (config_logic): {error_msg}", file=sys.stderr)
        return error_msg
    except requests.exceptions.RequestException as e:
        error_msg = f"Error de conexión con la API de Gemini: {e}"
        print(f"ERROR API (config_logic): {error_msg}", file=sys.stderr)
        return error_msg
    except KeyError as e_key:
        error_msg = f"Error al procesar la respuesta de la API (Falta clave: {e_key})."
        print(
            f"ERROR API (config_logic): {error_msg} Respuesta: {response.text[:500]}...",
            file=sys.stderr,
        )
        return error_msg
    except Exception as e_gen:
        error_msg = f"Ocurrió un error inesperado al llamar a la API: {e_gen}"
        print(f"ERROR API (config_logic): {error_msg}", file=sys.stderr)
        traceback.print_exc()
        return error_msg

def verificar_api_gemini():
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
            timeout=20,
        )
        response.raise_for_status()

        if response.status_code == 200:
            print("INFO (config_logic): Verificación de API Gemini exitosa (HTTP 200).")
            return True
        else:
            print(
                f"WARN (config_logic): Verificación API devolvió status {response.status_code} pero sin error HTTP.",
                file=sys.stderr,
            )
            return False

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

if __name__ == "__main__":
    print("--- Ejecutando pruebas de config_logic.py ---")

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

    print("\nProbando ruta PDF:")
    print(f"Ruta para 1ro Básico: {obtener_directorio_pdf('1ro Básico')}")

    print("\nProbando verificación API:")
    if (
        GEMINI_API_KEY and "TU_API_KEY" not in GEMINI_API_KEY
    ):
        api_ok = verificar_api_gemini()
        print(f"Resultado verificación API: {api_ok}")
    else:
        print("Saltando verificación API (API Key no configurada o es placeholder).")

    print("\n--- Pruebas finalizadas ---")
