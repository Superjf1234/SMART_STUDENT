# backend/eval_logic.py
# Lógica para generar preguntas, parsearlas y calcular/guardar resultados, sin Tkinter.

import os
import random
import traceback
import sys

# Importar desde los módulos de backend adaptados
try:
    # Asume que config_logic y db_logic están en el mismo paquete (backend)
    from . import config_logic
    from . import db_logic
except ImportError:
    # Fallback si se ejecuta standalone (menos común para lógica interna)
    print(
        "WARN (eval_logic): Ejecutando en modo standalone o error import relativo. Usando imports directos."
    )
    import config_logic
    import db_logic

# --- Funciones de Generación y Parseo (Basadas en tu versión Kivy) ---


def generar_preguntas(libro, tema, texto_pdf):
    """Genera texto crudo de preguntas (3 tipos) usando la API Gemini."""
    # NOTA: Esta función ahora usa config_logic.llamar_api_gemini
    print(f"INFO (eval_logic): Generando preguntas para L={libro}, T={tema}")
    preguntas_texto = {"alt": "", "vf": "", "sm": ""}
    # Prompts (pueden ser los mismos que en tu versión Kivy/Tkinter)
    prompt_alt = (
        f"Genera EXACTAMENTE 5 preguntas de opción múltiple sobre '{tema}' del libro '{libro}', basado en el texto. "
        f"Formato: 4 alternativas (a, b, c, d), marca solo UNA correcta con '(correcta)'. "
        f"Incluye una 'Explicación:' breve para cada una. Formato ESTRICTO requerido:\n"
        f"Pregunta X: [Texto pregunta]\na) [Opción a]\nb) [Opción b] (correcta)\nc) [Opción c]\nd) [Opción d]\nExplicación: [Texto explicación]\n\n"
        f"(Repetir para 5 preguntas)\nTexto base:\n{texto_pdf}"
    )
    prompt_vf = (
        f"Genera EXACTAMENTE 5 preguntas de Verdadero/Falso sobre '{tema}' del libro '{libro}', basado en el texto. "
        f"Marca UNA opción (Verdadero o Falso) con '(correcta)'. Incluye 'Explicación:'.\nFORMATO ESTRICTO:\n"
        f"Pregunta X: [Texto pregunta]\na) Verdadero (correcta)\nb) Falso\nExplicación: [Texto explicación]\n\n"
        f"(Repetir para 5 preguntas)\nTexto base:\n{texto_pdf}"
    )
    prompt_sm = (
        f"Genera EXACTAMENTE 5 preguntas de selección múltiple (PUEDEN tener VARIAS respuestas correctas) sobre '{tema}' del libro '{libro}', basado en el texto. "
        f"Formato: 4 alternativas (a, b, c, d), marca CADA correcta con '(correcta)'. Incluye 'Explicación:'.\nFORMATO ESTRICTO:\n"
        f"Pregunta X: [Texto pregunta]\na) [Opción a] (correcta)\nb) [Opción b]\nc) [Opción c] (correcta)\nd) [Opción d]\nExplicación: [Texto explicación]\n\n"
        f"(Repetir para 5 preguntas)\nTexto base:\n{texto_pdf}"
    )

    # Llamadas a la API (usando la función adaptada en config_logic)
    print("INFO (eval_logic): API call - Alternativas...")
    preguntas_texto["alt"] = config_logic.llamar_api_gemini(prompt_alt)
    print("INFO (eval_logic): API call - V/F...")
    preguntas_texto["vf"] = config_logic.llamar_api_gemini(prompt_vf)
    print("INFO (eval_logic): API call - Selección Múltiple...")
    preguntas_texto["sm"] = config_logic.llamar_api_gemini(prompt_sm)

    print("INFO (eval_logic): Llamadas API completadas.")
    # Devolver directamente el diccionario con los textos o mensajes de error
    return {
        "alternativas": preguntas_texto["alt"],
        "verdadero_falso": preguntas_texto["vf"],
        "seleccion_multiple": preguntas_texto["sm"],
    }


def parsear_preguntas(texto_raw, tipo_evaluacion):
    """Parsea el texto crudo de preguntas de la API en una lista de diccionarios estructurados."""
    preguntas = []
    if (
        not texto_raw
        or "Pregunta" not in texto_raw
        or "Error:" in texto_raw
        or "Error " in texto_raw
    ):
        print(
            f"WARN (eval_logic): Texto vacío, erróneo o sin 'Pregunta' para parsear tipo {tipo_evaluacion}: {texto_raw[:100]}...",
            file=sys.stderr,
        )
        return preguntas  # Devuelve lista vacía si el texto de entrada ya indica error

    lineas = texto_raw.strip().split("\n")
    pregunta_actual = None

    for i, linea_original in enumerate(lineas):
        linea = linea_original.strip()
        if not linea:
            continue

        if linea.startswith("Pregunta ") and ":" in linea:
            if pregunta_actual:
                if pregunta_actual.get("alternativas"):
                    tipo_prev = pregunta_actual.get("tipo")
                    alts_prev = pregunta_actual.get("alternativas", [])
                    corr_prev = pregunta_actual.get("correcta")
                    corrs_prev = pregunta_actual.get("correctas")
                    exp_prev = pregunta_actual.get("explicacion")
                    is_valid = False
                    expected_alts = 2 if tipo_prev == "verdadero_falso" else 4
                    if (
                        len(alts_prev) == expected_alts and exp_prev
                    ):  # Requiere explicación
                        if tipo_prev == "seleccion_multiple" and corrs_prev:
                            is_valid = True
                        elif tipo_prev != "seleccion_multiple" and corr_prev:
                            is_valid = True
                    if is_valid:
                        print(
                            f"DEBUG (parse): Añadiendo pregunta válida: {pregunta_actual.get('pregunta')[:30]}..."
                        )
                        preguntas.append(pregunta_actual)
                    else:
                        print(
                            f"WARN (parse): Descartando pregunta incompleta: {pregunta_actual.get('pregunta')[:30]}..."
                        )

            try:
                pregunta_texto = linea.split(":", 1)[1].strip()
                if not pregunta_texto:
                    continue
                pregunta_actual = {
                    "tipo": tipo_evaluacion,
                    "pregunta": pregunta_texto,
                    "alternativas": [],
                    "correcta": None,
                    "correctas": [],
                    "explicacion": "",
                }
                print(
                    f"\nDEBUG (parse): Nueva Pregunta ({tipo_evaluacion}): {pregunta_texto[:50]}..."
                )
            except IndexError:
                print(
                    f"WARN (parse): Línea pregunta mal formada: '{linea}'",
                    file=sys.stderr,
                )
                pregunta_actual = None
                continue

        elif (
            pregunta_actual
            and len(linea) > 2
            and linea[0].isalpha()
            and linea[1] in ".)"
        ):
            try:
                letra = linea[0].lower()
                texto_alt_raw = linea.split(")", 1)[1].strip()
                es_correcta = "(correcta)" in texto_alt_raw.lower()
                texto_alt_limpio = (
                    texto_alt_raw.replace("(correcta)", "")
                    .replace("(Correcta)", "")
                    .strip()
                )
                if texto_alt_limpio:
                    pregunta_actual["alternativas"].append(
                        {"letra": letra, "texto": texto_alt_limpio}
                    )
                    print(
                        f"  DEBUG (parse): Alt {letra}: '{texto_alt_limpio}' (Correcta: {es_correcta})"
                    )
                    if es_correcta:
                        if tipo_evaluacion == "seleccion_multiple":
                            pregunta_actual["correctas"].append(letra)
                        elif pregunta_actual["correcta"] is None:
                            pregunta_actual["correcta"] = letra
                else:
                    print(f"WARN (parse): Alternativa vacía descartada: '{linea}'")
            except IndexError:
                print(
                    f"WARN (parse): Línea alternativa mal formada: '{linea}'",
                    file=sys.stderr,
                )
                continue

        elif pregunta_actual and linea.startswith("Explicación:"):
            try:
                exp_texto = linea.split(":", 1)[1].strip()
                if exp_texto:
                    pregunta_actual["explicacion"] = exp_texto
                    print(
                        f"  DEBUG (parse): Explicación encontrada: '{exp_texto[:50]}...'"
                    )
            except IndexError:
                print(
                    f"WARN (parse): Línea explicación mal formada: '{linea}'",
                    file=sys.stderr,
                )
                pregunta_actual["explicacion"] = "[Error al parsear explicación]"

    if pregunta_actual:
        if pregunta_actual.get("alternativas"):
            tipo_prev = pregunta_actual.get("tipo")
            alts_prev = pregunta_actual.get("alternativas", [])
            corr_prev = pregunta_actual.get("correcta")
            corrs_prev = pregunta_actual.get("correctas")
            exp_prev = pregunta_actual.get("explicacion")
            is_valid = False
            expected_alts = 2 if tipo_prev == "verdadero_falso" else 4
            if len(alts_prev) == expected_alts and exp_prev:
                if tipo_prev == "seleccion_multiple" and corrs_prev:
                    is_valid = True
                elif tipo_prev != "seleccion_multiple" and corr_prev:
                    is_valid = True
            if is_valid:
                print(
                    f"DEBUG (parse): Añadiendo última pregunta válida: {pregunta_actual.get('pregunta')[:30]}..."
                )
                preguntas.append(pregunta_actual)
            else:
                print(
                    f"WARN (parse): Descartando última pregunta incompleta: {pregunta_actual.get('pregunta')[:30]}..."
                )

    print(
        f"INFO (eval_logic): Parseadas {len(preguntas)} preguntas válidas de tipo {tipo_evaluacion}."
    )
    return preguntas


def generar_evaluacion_logica(curso, libro, tema):
    """
    Función principal para generar una evaluación completa.
    
    Retorna:
        dict: {'status': 'EXITO'/'ERROR', 'preguntas': list|None, 'message': str}
    """
    print(f"DEBUG: Iniciando evaluación para Curso={curso}, Libro={libro}, Tema={tema}")
    resultado = {"status": "ERROR", "preguntas": None, "message": "Error desconocido"}
    if not curso or not libro or not tema:
        print("DEBUG: Faltan parámetros obligatorios (curso, libro, tema).")
        resultado["status"] = "ERROR_INPUT"
        resultado["message"] = "Curso, libro y tema son requeridos."
        return resultado
    try:
        texto_pdf = config_logic.extraer_texto_pdf(curso, config_logic.CURSOS.get(curso, {}).get(libro, ""))
        print(f"DEBUG: Texto PDF extraído ({len(texto_pdf)} caracteres).")
        preguntas_texto = generar_preguntas(libro, tema, texto_pdf)
        print(f"DEBUG: Preguntas generadas: {preguntas_texto}")
        preguntas_parseadas = []
        for tipo, texto in preguntas_texto.items():
            if isinstance(texto, str) and texto.strip() and "Error" not in texto:
                parseadas = parsear_preguntas(texto, tipo)
                print(f"DEBUG: Preguntas parseadas para tipo {tipo}: {parseadas}")
                preguntas_parseadas.extend(parseadas)
        if not preguntas_parseadas:
            print("DEBUG: No se pudieron parsear preguntas válidas.")
            resultado["status"] = "ERROR_PARSE"
            resultado["message"] = "No se pudieron parsear preguntas válidas."
            return resultado
        import random
        random.shuffle(preguntas_parseadas)
        resultado["preguntas"] = preguntas_parseadas[:15]
        resultado["status"] = "EXITO"
        resultado["message"] = f"Generadas {len(resultado['preguntas'])} preguntas."
        print(f"DEBUG: Evaluación generada exitosamente: {resultado}")
    except Exception as e:
        print(f"ERROR: Excepción en generar_evaluacion_logica: {e}")
        resultado["message"] = str(e)
    return resultado


def calcular_resultado_logica(preguntas_originales, respuestas_usuario):
    """
    Calcula la puntuación final de la evaluación.
    
    Retorna:
        dict: {'score': float, 'correct_count': int, 'total_questions': int}
    """
    if (not preguntas_originales or not isinstance(respuestas_usuario, dict)
            or len(preguntas_originales) != len(respuestas_usuario)):
        print("ERROR (eval_logic): Discrepancia entre preguntas y respuestas.")
        return None
    correct_count = 0
    total = len(preguntas_originales)
    for i, pregunta in enumerate(preguntas_originales):
        tipo = pregunta.get("tipo")
        respuesta_correcta = pregunta.get("respuesta_correcta")
        user_respuesta = respuestas_usuario.get(i)
        if tipo == "opcion_multiple" and isinstance(user_respuesta, str) and user_respuesta.lower() == respuesta_correcta.lower():
            correct_count += 1
        elif tipo == "seleccion_multiple":
            correct_set = set(respuesta_correcta) if isinstance(respuesta_correcta, list) else set()
            user_set = user_respuesta if isinstance(user_respuesta, set) else set()
            if user_set == correct_set:
                correct_count += 1
    score = round((correct_count / total) * 100, 2) if total else 0.0
    print(f"INFO (eval_logic): Resultado score: {score}, Correctas: {correct_count}/{total}")
    return {"score": score, "correct_count": correct_count, "total_questions": total}


def guardar_resultado_evaluacion(username, curso, libro, tema, nota):
    """
    Guarda el resultado de la evaluación en la base de datos.
    
    Retorna:
        bool: True si fue exitoso, False en caso contrario.
    """
    print(f"INFO (eval_logic): Guardando evaluación para {username} - Curso: {curso}, Libro: {libro}, Tema: {tema}, Nota: {nota}")
    try:
        nota_float = float(nota)
    except (ValueError, TypeError):
        print(f"ERROR (eval_logic): Nota inválida: {nota}")
        return False
    from datetime import datetime
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        conn = db_logic.get_db_connection()
        with conn:
            cursor = conn.cursor()
            insert_query = """
                INSERT INTO evaluacion_historial (username, curso, libro, tema, fecha, nota)
                VALUES (?, ?, ?, ?, ?, ?)
            """
            cursor.execute(insert_query, (username, curso, libro, tema, fecha_actual, nota_float))
            print(f"INFO (eval_logic): Evaluación guardada correctamente para {username}.")
            return True
    except Exception as e:
        print(f"ERROR (eval_logic): No se pudo guardar la evaluación: {e}")
        return False


def transformar_preguntas_a_formato_ui(preguntas_filtradas, tipo_ui):
    """
    Transforma las preguntas (ya filtradas por tipo) al formato esperado por la UI.
    
    Args:
        preguntas_filtradas (list): Lista de preguntas parseadas y filtradas por tipo.
        tipo_ui (str): Tipo de pregunta para la UI ('opcion_multiple' o 'seleccion_multiple').
    
    Retorna:
        list: Lista de preguntas formateadas para la UI.
    """
    preguntas_ui = []
    for pregunta in preguntas_filtradas:
        opciones_ui = []
        for alt in pregunta.get("alternativas", []):
            opciones_ui.append({
                "id": alt.get("letra", ""),
                "texto": alt.get("texto", "")
            })
            
        respuesta_correcta = None
        if tipo_ui == "opcion_multiple":
            respuesta_correcta = pregunta.get("correcta") 
        elif tipo_ui == "seleccion_multiple":
            respuesta_correcta = pregunta.get("correctas", [])
        else:
            print(f"WARN (transform): Tipo UI desconocido '{tipo_ui}' para pregunta: {pregunta.get('pregunta')}")
            respuesta_correcta = None 

        pregunta_ui = {
            "tipo": tipo_ui,
            "pregunta": pregunta.get("pregunta", ""),
            "opciones": opciones_ui,
            "respuesta_correcta": respuesta_correcta,
            "explicacion": pregunta.get("explicacion", "")
        }
        preguntas_ui.append(pregunta_ui)
    return preguntas_ui


def generar_evaluacion_funcional(curso, libro, tema, tipo_ui="opcion_multiple"):
    """
    Genera la evaluación, filtra por tipo y transforma las preguntas al formato esperado por la UI.
    
    Args:
        curso (str): El curso seleccionado.
        libro (str): El libro seleccionado.
        tema (str): El tema de la evaluación.
        tipo_ui (str): Tipo de pregunta para la UI ("opcion_multiple" o "seleccion_multiple").
        
    Retorna:
        dict: Resultado con 'status', 'preguntas' (transformadas y filtradas) y 'message'.
    """
    result = generar_evaluacion_logica(curso, libro, tema)
    
    if result.get("status") == "EXITO" and result.get("preguntas"):
        preguntas_parseadas = result.get("preguntas")
        
        preguntas_filtradas = []
        if tipo_ui == "opcion_multiple":
            preguntas_filtradas = [
                p for p in preguntas_parseadas 
                if p.get("tipo") in ["alternativas", "verdadero_falso"]
            ]
            print(f"INFO (eval_func): Filtrando para 'opcion_multiple'. Encontradas {len(preguntas_filtradas)} de {len(preguntas_parseadas)}.")
        elif tipo_ui == "seleccion_multiple":
            preguntas_filtradas = [
                p for p in preguntas_parseadas 
                if p.get("tipo") == "seleccion_multiple"
            ]
            print(f"INFO (eval_func): Filtrando para 'seleccion_multiple'. Encontradas {len(preguntas_filtradas)} de {len(preguntas_parseadas)}.")
        else:
            print(f"WARN (eval_func): Tipo UI no reconocido '{tipo_ui}'. No se aplicará filtro específico.")
            preguntas_filtradas = [] 

        if not preguntas_filtradas:
             result["status"] = "ERROR_NO_MATCHING_QUESTIONS"
             result["message"] = f"No se pudieron generar preguntas del tipo '{tipo_ui}' para este tema. Intenta con otro tipo o tema."
             result["preguntas"] = [] 
             print(f"WARN (eval_func): {result['message']}")
             return result 

        preguntas_ui = transformar_preguntas_a_formato_ui(preguntas_filtradas, tipo_ui)
        result["preguntas"] = preguntas_ui
        result["message"] = f"Generadas {len(preguntas_ui)} preguntas de tipo '{tipo_ui}'."
        print(f"INFO (eval_func): {result['message']}")

    return result


def iniciar_evaluacion(resumen_content, puntos_content, include_puntos):
    """
    Inicia una evaluación basada en el contenido del resumen y puntos clave.

    Args:
        resumen_content (str): Contenido del resumen.
        puntos_content (str): Puntos clave del resumen.
        include_puntos (bool): Si se deben incluir los puntos clave.

    Returns:
        dict: Resultado de la evaluación con preguntas generadas.
    """
    if not resumen_content:
        return {"status": "ERROR", "message": "El contenido del resumen está vacío."}
        
    # Prepara el contenido combinando resumen y puntos si es necesario
    content = resumen_content
    if include_puntos and puntos_content:
        content += "\n\nPuntos clave:\n" + puntos_content

    try:
        # Genera preguntas directamente del contenido sin usar extraer_texto_pdf
        preguntas_parseadas = []
        
        # Genera preguntas para "alternativas" (opción múltiple)
        prompt_alt = (
            f"Genera EXACTAMENTE 5 preguntas de opción múltiple basadas en el siguiente texto: "
            f"Formato: 4 alternativas (a, b, c, d), marca solo UNA correcta con '(correcta)'. "
            f"Incluye 'Explicación:' breve para cada una.\nFORMATO ESTRICTO REQUERIDO:\n"
            f"Pregunta X: [Texto pregunta]\na) [Opción a]\nb) [Opción b] (correcta)\nc) [Opción c]\nd) [Opción d]\nExplicación: [Texto explicación]\n\n"
            f"Texto base:\n{content[:2000]}"  # Limitar longitud para evitar tokens excesivos
        )
        
        texto_alt = config_logic.llamar_api_gemini(prompt_alt)
        if texto_alt and "Error" not in texto_alt:
            alt_parseadas = parsear_preguntas(texto_alt, "alternativas")
            preguntas_parseadas.extend(alt_parseadas)
        
        # Si hay suficientes preguntas, devolver resultado exitoso
        if preguntas_parseadas:
            # Transformar las preguntas al formato esperado por la UI
            preguntas_ui = []
            for pregunta in preguntas_parseadas:
                opciones_ui = []
                for alt in pregunta.get("alternativas", []):
                    opciones_ui.append({
                        "id": alt.get("letra", ""),
                        "texto": alt.get("texto", "")
                    })
                
                pregunta_ui = {
                    "tipo": "opcion_multiple",
                    "pregunta": pregunta.get("pregunta", ""),
                    "opciones": opciones_ui,
                    "respuesta_correcta": pregunta.get("correcta"),
                    "explicacion": pregunta.get("explicacion", "")
                }
                preguntas_ui.append(pregunta_ui)
            
            # Mezclar preguntas para variar orden
            import random
            random.shuffle(preguntas_ui)
            
            return {
                "status": "EXITO", 
                "preguntas": preguntas_ui,
                "message": f"Generadas {len(preguntas_ui)} preguntas de evaluación."
            }
        else:
            return {"status": "ERROR", "message": "No se pudieron generar preguntas válidas."}
            
    except Exception as e:
        import traceback
        print(f"ERROR en iniciar_evaluacion: {e}")
        print(traceback.format_exc())
        return {"status": "ERROR", "message": f"Error inesperado: {str(e)}"}
