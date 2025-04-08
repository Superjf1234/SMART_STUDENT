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

def generar_preguntas(libro, tema, texto_pdf):
    """Genera texto crudo de preguntas (3 tipos) usando la API Gemini."""
    print(f"INFO (eval_logic): Generando preguntas para L={libro}, T={tema}")
    preguntas_texto = {"alt": "", "vf": "", "sm": ""}
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

    try:
        print("INFO (eval_logic): API call - Alternativas...")
        preguntas_texto["alt"] = config_logic.llamar_api_gemini(prompt_alt)
        print("INFO (eval_logic): API call - V/F...")
        preguntas_texto["vf"] = config_logic.llamar_api_gemini(prompt_vf)
        print("INFO (eval_logic): API call - Selección Múltiple...")
        preguntas_texto["sm"] = config_logic.llamar_api_gemini(prompt_sm)
        print("INFO (eval_logic): Llamadas API completadas.")
    except Exception as e:
        print(f"ERROR (eval_logic): Error al llamar a la API - {e}", file=sys.stderr)
        traceback.print_exc()
        return {
            "alternativas": "Error al generar preguntas de alternativas.",
            "verdadero_falso": "Error al generar preguntas de verdadero/falso.",
            "seleccion_multiple": "Error al generar preguntas de selección múltiple.",
        }

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
        return preguntas

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
                    ):
                        if tipo_prev == "seleccion_multiple" and corrs_prev:
                            is_valid = True
                        elif tipo_prev != "seleccion_multiple" and corr_prev:
                            is_valid = True
                    if is_valid:
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
                preguntas.append(pregunta_actual)
            else:
                print(
                    f"WARN (parse): Descartando última pregunta incompleta: {pregunta_actual.get('pregunta')[:30]}..."
                )

    return preguntas

def generar_evaluacion_logica(curso, libro, tema):
    """
    Función principal para generar una evaluación completa (lógica desacoplada).
    Retorna: {'status': 'EXITO'/'ERROR_...', 'preguntas': list|None, 'message': str|None}
    """
    print(
        f"INFO (eval_logic): Iniciando generación evaluación para C={curso}, L={libro}, T={tema}"
    )
    resultado = {"status": "ERROR", "preguntas": None, "message": "Error desconocido"}

    if not curso or not libro or not tema:
        resultado["message"] = "Curso, libro y tema son requeridos."
        resultado["status"] = "ERROR_INPUT"
        print(f"ERROR (eval_logic): {resultado['message']}")
        return resultado

    try:
        print("INFO (eval_logic): Extrayendo texto PDF...")
        archivo = config_logic.CURSOS.get(curso, {}).get(libro)
        if not archivo:
            resultado["message"] = (
                f"Libro '{libro}' no encontrado para curso '{curso}'."
            )
            resultado["status"] = "ERROR_CONFIG"
            print(f"ERROR (eval_logic): {resultado['message']}")
            return resultado
        texto_pdf = config_logic.extraer_texto_pdf(curso, archivo)
        print(f"INFO (eval_logic): Texto extraído ({len(texto_pdf)} chars).")

        preguntas_generadas_raw = generar_preguntas(libro, tema, texto_pdf)

        api_errors = []
        for tipo, texto in preguntas_generadas_raw.items():
            if not isinstance(texto, str) or "Error" in texto[:10] or not texto.strip():
                error_info = (
                    f"Tipo '{tipo}': {str(texto)[:100] if texto else 'Respuesta vacía'}"
                )
                api_errors.append(error_info)
                print(f"WARN (eval_logic): Problema API detectado - {error_info}")

        if len(api_errors) == 3:
            resultado["message"] = (
                "La API falló o retornó error/vacío para los 3 tipos de pregunta.\nErrores:\n"
                + "\n".join(api_errors)
            )
            resultado["status"] = "ERROR_API_TOTAL"
            print(f"ERROR (eval_logic): {resultado['message']}")
            return resultado
        elif api_errors:
            print(f"WARN (eval_logic): Errores parciales de API: {api_errors}")

        print("INFO (eval_logic): Parseando preguntas generadas...")
        preguntas_parseadas_total = []
        for tipo, texto in preguntas_generadas_raw.items():
            if isinstance(texto, str) and "Error" not in texto[:10] and texto.strip():
                try:
                    preguntas_parseadas_tipo = parsear_preguntas(texto, tipo)
                    preguntas_parseadas_total.extend(preguntas_parseadas_tipo)
                except Exception as e_parse:
                    print(
                        f"ERROR (eval_logic): Excepción parseando tipo '{tipo}': {e_parse}",
                        file=sys.stderr,
                    )
                    traceback.print_exc()
            else:
                print(
                    f"INFO (eval_logic): Saltando parseo para tipo '{tipo}' debido a error/respuesta vacía API."
                )

        if not preguntas_parseadas_total:
            resultado["message"] = (
                "No se pudieron parsear preguntas válidas desde la(s) respuesta(s) de la API."
            )
            resultado["status"] = "ERROR_PARSE"
            if api_errors:
                resultado["message"] += "\n(Errores API detectados para algunos tipos)"
            print(f"ERROR (eval_logic): {resultado['message']}")
            return resultado

        random.shuffle(preguntas_parseadas_total)
        resultado["preguntas"] = preguntas_parseadas_total
        resultado["status"] = "EXITO"
        resultado["message"] = (
            f"Generadas {len(preguntas_parseadas_total)} preguntas válidas."
        )
        if len(preguntas_parseadas_total) < 5:
            resultado["message"] += " (Advertencia: número bajo de preguntas)"
        if api_errors:
            resultado[
                "message"
            ] += "\n(Advertencia: API falló para algunos tipos de pregunta)"

    except FileNotFoundError as e_fnf:
        print(
            f"ERROR (eval_logic): Archivo PDF no encontrado - {e_fnf}", file=sys.stderr
        )
        resultado["status"] = "ERROR_PDF_NOT_FOUND"
        resultado["message"] = f"No se encontró el archivo PDF necesario: {e_fnf}"
    except IOError as e_io:
        print(f"ERROR (eval_logic): Error de lectura PDF - {e_io}", file=sys.stderr)
        resultado["status"] = "ERROR_PDF_READ"
        resultado["message"] = f"Error al leer el archivo PDF: {e_io}"
    except Exception as e:
        print(
            f"ERROR (eval_logic): Excepción general en generar_evaluacion_logica: {e}",
            file=sys.stderr,
        )
        traceback.print_exc()
        resultado["status"] = "ERROR_INESPERADO"
        resultado["message"] = f"Ocurrió un error interno inesperado: {e}"

    print(f"INFO (eval_logic): Finalizado. Status: {resultado['status']}")
    return resultado

def calcular_resultado_logica(preguntas_originales, respuestas_usuario):
    """
    Calcula la nota final basada en las preguntas y las respuestas del usuario.
    Retorna: dict {'score': float, 'correct_count': int, 'total_questions': int} o None si hay error grave.
    """
    if (
        not preguntas_originales
        or not isinstance(respuestas_usuario, dict)
        or len(preguntas_originales) != len(respuestas_usuario)
    ):
        print(
            f"ERROR (eval_logic): Discrepancia preguntas ({len(preguntas_originales)}) / respuestas ({len(respuestas_usuario)}) o formato incorrecto.",
            file=sys.stderr,
        )
        return None

    notas = []
    correctas_count = 0
    total_questions = len(preguntas_originales)

    for idx, q in enumerate(preguntas_originales):
        tipo = q.get("tipo")
        respuesta_usr = respuestas_usuario.get(idx)
        nota_pregunta = 1.0

        try:
            if respuesta_usr is not None:
                if tipo == "alternativas" or tipo == "verdadero_falso":
                    resp_correcta = q.get("correcta")
                    if (
                        resp_correcta
                        and isinstance(respuesta_usr, str)
                        and respuesta_usr.lower() == resp_correcta.lower()
                    ):
                        nota_pregunta = 7.0
                        correctas_count += 1
                elif tipo == "seleccion_multiple":
                    resp_correctas_set = set(q.get("correctas", []))
                    resp_usr_set = (
                        set(str(r).lower() for r in respuesta_usr)
                        if isinstance(respuesta_usr, set)
                        else set()
                    )
                    if resp_correctas_set and resp_usr_set == resp_correctas_set:
                        nota_pregunta = 7.0
                        correctas_count += 1
            else:
                print(
                    f"DEBUG (eval_logic calc): Sin respuesta para P{idx+1}. Nota = 1.0"
                )

        except Exception as e_calc:
            print(
                f"ERROR (eval_logic calc): Calculando nota P{idx+1} - {e_calc}",
                file=sys.stderr,
            )
            traceback.print_exc()
            nota_pregunta = 1.0

        notas.append(nota_pregunta)

    if not notas:
        print("ERROR (eval_logic calc): No se calcularon notas.", file=sys.stderr)
        return {"score": 1.0, "correct_count": 0, "total_questions": total_questions}

    promedio = round(sum(notas) / len(notas), 1)
    print(
        f"INFO (eval_logic calc): Resultado: Nota={promedio}, Correctas={correctas_count}/{total_questions}"
    )

    return {
        "score": promedio,
        "correct_count": correctas_count,
        "total_questions": total_questions,
    }

def guardar_resultado_evaluacion(username, curso, libro, tema, nota):
    """
    Guarda el resultado de una evaluación en la base de datos usando db_logic.
    Retorna True si fue exitoso, False en caso contrario.
    """
    print(
        f"INFO (eval_logic): Intentando guardar resultado para '{username}' - C={curso}, L={libro}, T={tema}, N={nota}"
    )
    if not username:
        print(
            "ERROR (eval_logic): Se requiere username para guardar resultado.",
            file=sys.stderr,
        )
        return False
    try:
        exito = db_logic.guardar_evaluacion(
            username, curso, libro, tema, nota
        )
        if exito:
            print("INFO (eval_logic): Resultado guardado vía db_logic.")
            return True
        else:
            print(
                "ERROR (eval_logic): db_logic.guardar_evaluacion reportó fallo.",
                file=sys.stderr,
            )
            return False
    except Exception as e_save:
        print(
            f"ERROR (eval_logic): Excepción al intentar guardar resultado vía db_logic: {e_save}",
            file=sys.stderr,
        )
        traceback.print_exc()
        return False
