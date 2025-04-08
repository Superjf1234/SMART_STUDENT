# backend/resumen_logic.py
# Lógica para generar resúmenes y puntos clave, adaptada para Reflex (sin Tkinter).

import os
import traceback
import sys

try:
    # Importar FPDF para generar PDF. Asegúrate: pip install fpdf
    from fpdf import FPDF

    FPDF_AVAILABLE = True
except ImportError:
    print(
        "ERROR CRITICO (resumen_logic): Falta la librería 'fpdf'. Los PDF no se podrán generar.",
        file=sys.stderr,
    )
    # Puedes definir FPDF como None para manejarlo, o dejar que falle si es esencial.
    FPDF_AVAILABLE = False
    FPDF = None  # Para evitar errores si se intenta usar

# Importar desde los módulos de backend adaptados
try:
    # Asume que config_logic está en el mismo paquete (backend)
    from . import config_logic
except ImportError:
    # Fallback si se ejecuta standalone
    print(
        "WARN (resumen_logic): Ejecutando en modo standalone o error import relativo. Usando imports directos."
    )
    import config_logic


def formatear_puntos(puntos_texto):
    """Formatea puntos clave: numera, limpia intros/asteriscos, limita palabras."""
    # (Misma lógica de formateo que la versión anterior, revisada para claridad)
    if not puntos_texto or not isinstance(puntos_texto, str):
        return "No se generaron puntos relevantes o el formato es incorrecto."

    lineas = puntos_texto.split("\n")
    puntos_finales = []
    contador = 1
    intro_keywords = [
        "aquí hay",
        "aquí están",
        "estos son",
        "puntos clave sobre",
        "puntos relevantes sobre",
        "extraídos del texto",
        "estrictamente relacionados",
        "7 puntos clave",
        "puntos clave extraídos",
        "con un máximo de",
        "máximo de 15 palabras",
        "basado en el texto",
        "del texto proporcionado",
        "lista de puntos",
    ]

    for linea in lineas:
        linea_strip = linea.strip()
        if not linea_strip or linea_strip in ["---", "***", "```"]:
            continue

        texto_analisis = linea_strip
        # Quitar prefijo solo para análisis de intro
        if len(texto_analisis) > 1:
            if texto_analisis[0].isdigit() and texto_analisis[1] in ".)":
                texto_analisis = texto_analisis[2:].strip()
            elif texto_analisis[0] in "*-•":
                texto_analisis = texto_analisis[1:].strip()
        texto_analisis_lower = texto_analisis.lower()

        is_intro = any(intro in texto_analisis_lower for intro in intro_keywords)
        if not is_intro and (
            texto_analisis_lower.startswith("puntos clave")
            or texto_analisis_lower.startswith("puntos relevantes")
        ):
            is_intro = True

        if is_intro:
            # print(f"DEBUG formatear_puntos: Ignorando línea intro/header: '{linea_strip}'")
            continue

        # Limpieza final del texto del punto
        punto_texto_final = linea_strip
        if len(punto_texto_final) > 1:
            if punto_texto_final[0].isdigit() and punto_texto_final[1] in ".)":
                punto_texto_final = punto_texto_final[2:].strip()
            elif punto_texto_final[0] in "*-•":
                punto_texto_final = punto_texto_final[1:].strip()
        punto_texto_final = punto_texto_final.replace("**", "")

        # Limitar palabras y añadir numeración
        palabras = punto_texto_final.split()
        max_palabras = 15  # Límite de palabras
        max_puntos = 7  # Límite de puntos
        if len(palabras) > 0 and contador <= max_puntos:
            texto_punto = " ".join(palabras[:max_palabras])  # Trunca si excede
            puntos_finales.append(f"{contador}. {texto_punto}\n")  # Salto simple
            contador += 1

        if contador > max_puntos:
            break

    resultado = "".join(puntos_finales).strip()
    return (
        resultado
        if puntos_finales
        else "No se pudieron extraer o formatear los puntos."
    )


def formatear_resumen(resumen_texto, tema_solicitado):
    """Formatea el resumen: elimina títulos/intros no deseados y asteriscos."""
    # (Misma lógica de formateo que la versión anterior, revisada)
    if not resumen_texto or not isinstance(resumen_texto, str):
        return "No se generó un resumen o el formato es incorrecto."

    resumen_limpio = resumen_texto.strip()
    unwanted_titles = [
        "** Resumen Extendido y Detallado del Texto **",
        f"Resumen Extenso y Detallado del Texto '{tema_solicitado}'",
        "Aquí está un resumen extenso y detallado",
        "Resumen del texto:",
        "Resumen detallado:",
        "```markdown",
        "```",
    ]

    lines = resumen_limpio.split("\n")
    cleaned_lines = []
    start_processing = False

    for linea in lines:
        linea_strip = linea.strip()
        # Comprobar si es un título/intro no deseado (ignorando mayúsculas/minúsculas y espacios extra)
        is_unwanted = any(
            unwanted.lower() in linea_strip.lower() for unwanted in unwanted_titles
        )

        if not start_processing:
            # Empezar si NO es basura Y parece contenido real
            if (
                not is_unwanted
                and linea_strip
                and (
                    linea_strip[0].isdigit()
                    or linea_strip.startswith("*")
                    or len(linea_strip) > 25
                )
            ):
                start_processing = True
            elif (
                not is_unwanted and not linea_strip
            ):  # Permitir empezar con línea vacía si no es basura
                start_processing = True
            else:
                # print(f"DEBUG formatear_resumen: Saltando línea inicial: '{linea_strip}'")
                continue

        if is_unwanted:
            # print(f"DEBUG formatear_resumen: Eliminando título/intro: '{linea_strip}'")
            continue

        # Eliminar ** y añadir línea limpia
        linea_final = linea.replace("**", "")
        cleaned_lines.append(
            linea_final
        )  # Mantener saltos de línea originales entre párrafos limpios

    return "\n".join(cleaned_lines).strip()


def generar_resumen_logica(curso, libro, tema, gen_puntos):
    """
    Función principal de lógica para generar resumen y puntos.
    Retorna dict: {'status': 'EXITO'/'ERROR_...', 'resumen': str|None, 'puntos': str|None, 'message': str|None}
    """
    print(
        f"INFO (resumen_logic): Iniciando generación para C={curso}, L={libro}, T={tema}, Puntos={gen_puntos}"
    )
    resultado = {
        "status": "ERROR",
        "resumen": None,
        "puntos": None,
        "message": "Error desconocido",
    }

    if not curso or not libro or not tema:
        resultado["message"] = "Curso, libro y tema son requeridos."
        resultado["status"] = "ERROR_INPUT"
        print(f"ERROR (resumen_logic): {resultado['message']}", file=sys.stderr)
        return resultado

    try:
        # 1. Extraer Texto PDF (usa config_logic y lanza excepciones)
        print("INFO (resumen_logic): Extrayendo texto PDF...")
        archivo = config_logic.CURSOS.get(curso, {}).get(libro)
        if not archivo:
            resultado["message"] = (
                f"Libro '{libro}' no encontrado para curso '{curso}'."
            )
            resultado["status"] = "ERROR_CONFIG"
            print(f"ERROR (resumen_logic): {resultado['message']}", file=sys.stderr)
            return resultado
        texto_pdf = config_logic.extraer_texto_pdf(
            curso, archivo
        )  # Puede lanzar FileNotFoundError, IOError
        print(f"INFO (resumen_logic): Texto extraído ({len(texto_pdf)} chars).")

        # 2. Generar Resumen (API)
        print("INFO (resumen_logic): Llamando API para resumen...")
        prompt_resumen = (
            f"Genera un resumen EXTENSO y DETALLADO sobre '{tema}' basado ESTRICTAMENTE en el texto proporcionado. "
            f"Estructura sugerida si aplica:\n1. [Título sección]:\n   [Contenido]\n2. [Título sección]:\n   [Contenido]\n...\nN. Conclusión:\n   [Contenido]\n\n"
            f"NO añadas introducciones como 'Aquí está el resumen'. Empieza directo con el contenido.\nTexto:\n{texto_pdf}"
        )
        # llamar_api_gemini devuelve texto o string de error
        resumen_raw = config_logic.llamar_api_gemini(prompt_resumen)

        if isinstance(resumen_raw, str) and "Error" in resumen_raw[:10]:
            print(
                f"WARN (resumen_logic): API retornó error para resumen: {resumen_raw}",
                file=sys.stderr,
            )
            resultado["message"] = f"API no generó resumen válido: {resumen_raw}"
            # No poner status ERROR_API_RESUMEN aún, por si los puntos funcionan
        elif isinstance(resumen_raw, str) and resumen_raw.strip():
            print("INFO (resumen_logic): Resumen recibido, formateando...")
            resultado["resumen"] = formatear_resumen(resumen_raw, tema)
        else:
            print(
                f"WARN (resumen_logic): API retornó respuesta vacía para resumen.",
                file=sys.stderr,
            )
            resultado["message"] = "API no generó contenido para el resumen."

        # 3. Generar Puntos Clave (API, si se solicitó)
        if gen_puntos:
            print("INFO (resumen_logic): Llamando API para puntos clave...")
            prompt_puntos = (
                f"Extrae exactamente 7 puntos clave concisos (máximo 15 palabras por punto) sobre '{tema}', "
                f"basados ESTRICTAMENTE en el texto proporcionado. Numéralos del 1 al 7. "
                f"No incluyas puntos de otros temas. No añadas introducciones.\nTexto:\n{texto_pdf}"
            )
            puntos_raw = config_logic.llamar_api_gemini(prompt_puntos)

            if isinstance(puntos_raw, str) and "Error" in puntos_raw[:10]:
                print(
                    f"WARN (resumen_logic): API retornó error para puntos: {puntos_raw}",
                    file=sys.stderr,
                )
                resultado["puntos"] = (
                    f"Error al generar puntos: {puntos_raw}"  # Guardar mensaje de error
                )
            elif isinstance(puntos_raw, str) and puntos_raw.strip():
                print("INFO (resumen_logic): Puntos recibidos, formateando...")
                resultado["puntos"] = formatear_puntos(puntos_raw)
            else:
                print(
                    f"WARN (resumen_logic): API retornó respuesta vacía para puntos.",
                    file=sys.stderr,
                )
                resultado["puntos"] = "La API no generó puntos relevantes."
        else:
            resultado["puntos"] = None  # No se pidieron

        # Determinar status final
        if resultado["resumen"] or (
            gen_puntos
            and resultado["puntos"]
            and "Error" not in str(resultado["puntos"])[:10]
        ):
            # Éxito si al menos el resumen o los puntos (si se pidieron y no dieron error API) se generaron
            resultado["status"] = "EXITO"
            resultado["message"] = "Generación completada."
            if not resultado["resumen"]:
                resultado["message"] += " (Advertencia: Falló generación de resumen)."
            if gen_puntos and (
                not resultado["puntos"] or "Error" in str(resultado["puntos"])[:10]
            ):
                resultado["message"] += " (Advertencia: Falló generación de puntos)."
        elif (
            not resultado["message"] or resultado["message"] == "Error desconocido"
        ):  # Si no hubo errores específicos pero tampoco contenido
            resultado["status"] = "ERROR_API_GENERAL"
            resultado["message"] = "La API no generó contenido útil."
            print(f"ERROR (resumen_logic): {resultado['message']}", file=sys.stderr)

    except FileNotFoundError as e_fnf:
        print(
            f"ERROR (resumen_logic): Archivo PDF no encontrado - {e_fnf}",
            file=sys.stderr,
        )
        resultado["status"] = "ERROR_PDF_NOT_FOUND"
        resultado["message"] = (
            f"No se encontró el archivo PDF: {os.path.basename(str(e_fnf))}"  # Más conciso
        )
    except IOError as e_io:
        print(f"ERROR (resumen_logic): Error de lectura PDF - {e_io}", file=sys.stderr)
        resultado["status"] = "ERROR_PDF_READ"
        resultado["message"] = f"Error al leer el archivo PDF: {e_io}"
    except Exception as e:
        print(
            f"ERROR (resumen_logic): Excepción general en generar_resumen_logica: {e}",
            file=sys.stderr,
        )
        traceback.print_exc()
        resultado["status"] = "ERROR_INESPERADO"
        resultado["message"] = f"Ocurrió un error interno inesperado: {e}"

    print(f"INFO (resumen_logic): Finalizado. Status: {resultado['status']}")
    return resultado


def generar_resumen_pdf_bytes(resumen_txt, puntos_txt, curso, libro, tema):
    """
    Genera el contenido de un PDF con el resumen y puntos clave.
    Retorna los bytes del PDF o None en caso de error.
    """
    if not FPDF_AVAILABLE:
        print(
            "ERROR (resumen_logic): FPDF no está disponible. No se puede generar PDF.",
            file=sys.stderr,
        )
        return None

    # Asegurar que tenemos algún texto para poner en el PDF
    resumen_valido = (
        resumen_txt and isinstance(resumen_txt, str) and resumen_txt.strip()
    )
    puntos_validos = (
        puntos_txt
        and isinstance(puntos_txt, str)
        and puntos_txt.strip()
        and "Error" not in puntos_txt[:10]
    )

    if not resumen_valido and not puntos_validos:
        print(
            "WARN (resumen_logic): No hay contenido válido (resumen o puntos) para generar PDF."
        )
        return None

    try:
        pdf = FPDF()
        pdf.add_page()
        # Usar márgenes estándar
        pdf.set_left_margin(15)
        pdf.set_right_margin(15)
        pdf.set_top_margin(15)
        pdf.set_auto_page_break(auto=True, margin=15)  # Margen inferior

        # Título Principal (Codificado correctamente)
        pdf.set_font("Helvetica", "B", 16)
        titulo = f"Resumen: {tema}"
        pdf.cell(
            0,
            10,
            titulo.encode("latin-1", "replace").decode("latin-1"),
            ln=True,
            align="C",
        )
        pdf.ln(5)

        # Metadatos (Codificado correctamente)
        pdf.set_font("Helvetica", "I", 10)
        meta = f"Curso: {curso} | Libro: {libro}"
        pdf.cell(
            0,
            8,
            meta.encode("latin-1", "replace").decode("latin-1"),
            ln=True,
            align="C",
        )
        pdf.ln(8)

        # --- Contenido del Resumen ---
        if resumen_valido:
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 8, "RESUMEN DETALLADO", ln=True)
            pdf.ln(2)
            pdf.set_font("Helvetica", "", 11)
            # Codificar a latin-1 reemplazando caracteres no soportados para FPDF base
            resumen_latin1 = resumen_txt.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(
                0, 6, resumen_latin1
            )  # Usar multi_cell para manejo automático de saltos

        # --- Contenido de Puntos Clave ---
        if puntos_validos:
            if resumen_valido:
                pdf.ln(10)  # Añadir separación si hubo resumen
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(0, 8, "PUNTOS RELEVANTES", ln=True)
            pdf.ln(2)
            pdf.set_font("Helvetica", "", 11)
            puntos_latin1 = puntos_txt.encode("latin-1", "replace").decode("latin-1")
            pdf.multi_cell(0, 6, puntos_latin1)  # multi_cell para formateo

        # Generar PDF en memoria como bytes
        # Usar 'latin-1' para la salida de FPDF si esa fue la codificación usada internamente
        pdf_bytes = pdf.output(dest="S").encode("latin-1")
        print(
            f"INFO (resumen_logic): PDF generado en memoria ({len(pdf_bytes)} bytes)."
        )
        return pdf_bytes

    except Exception as e:
        print(f"ERROR (resumen_logic): No se pudo generar PDF - {e}", file=sys.stderr)
        traceback.print_exc()
        return None


# --- NO hay interfaz gráfica aquí ---

if __name__ == "__main__":
    print("--- Ejecutando pruebas de resumen_logic.py ---")
    # Ejemplo de prueba (requiere config_logic funcional y quizás archivos PDF dummy)
    # test_curso = "1ro Medio"
    # test_libro = "Biología"
    # test_tema = "La Célula"
    # print(f"\nGenerando resumen y puntos para {test_curso}/{test_libro}/{test_tema}...")
    # resultado = generar_resumen_logica(test_curso, test_libro, test_tema, gen_puntos=True)
    # print("\nResultado Generación:")
    # print(f"  Status: {resultado['status']}")
    # print(f"  Message: {resultado['message']}")
    # print(f"  Resumen: {str(resultado['resumen'])[:200]}...")
    # print(f"  Puntos: {resultado['puntos']}")

    # if resultado['status'] == 'EXITO':
    #      print("\nGenerando PDF bytes...")
    #      pdf_data = generar_resumen_pdf_bytes(
    #           resultado['resumen'], resultado['puntos'],
    #           test_curso, test_libro, test_tema
    #      )
    #      if pdf_data:
    #          print(f"  PDF generado ({len(pdf_data)} bytes).")
    #          # Opcional: Guardar para verificar
    #          # try:
    #          #     with open("test_resumen.pdf", "wb") as f:
    #          #         f.write(pdf_data)
    #          #     print("  PDF guardado como test_resumen.pdf")
    #          # except Exception as e_write:
    #          #     print(f"  Error guardando PDF de prueba: {e_write}")
    #      else:
    #          print("  Fallo al generar PDF bytes.")

    print("\n--- Pruebas resumen_logic.py finalizadas ---")
