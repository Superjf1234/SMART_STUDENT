"""
Utilidades para la aplicación SMART_STUDENT.
Contiene funciones comunes utilizadas en varios módulos de la aplicación.
"""

import os
import datetime
from fpdf import FPDF
from typing import List, Dict, Any, Optional

def generate_pdf_report_from_answers(
    titulo: str,
    subtitulo: str = "",
    preguntas: List[Dict[str, Any]] = [],
    mostrar_respuestas: bool = True,
    output_dir: str = os.path.join("assets", "pdfs"),
    filename_prefix: str = "informe"
) -> str:
    """
    Genera un PDF con preguntas y respuestas.
    
    Args:
        titulo: Título principal del informe
        subtitulo: Subtítulo o descripción adicional
        preguntas: Lista de diccionarios con las preguntas y respuestas
        mostrar_respuestas: Si es True, incluye las respuestas en el PDF
        output_dir: Directorio donde se guardará el PDF
        filename_prefix: Prefijo para el nombre del archivo
        
    Returns:
        str: URL relativa al archivo PDF generado
    """
    try:
        # Asegurar que existe el directorio de salida
        os.makedirs(output_dir, exist_ok=True)
        
        # Crear un PDF
        pdf = FPDF()
        pdf.add_page()
        
        # Configurar márgenes
        pdf.set_margins(20, 20, 20)
        pdf.set_auto_page_break(auto=True, margin=25)

        # Configuración de la fuente
        try:
            pdf.set_font("Arial", "B", 18)
        except:
            print("WARN: Font 'Arial' not found, using default.")
            pdf.set_font("helvetica", "B", 18)

        # Encabezado con estilo
        pdf.set_fill_color(230, 230, 250)  # Color lavanda claro de fondo
        pdf.rect(10, 10, pdf.w - 20, 30, 'F')
        
        # Título con marco
        pdf.set_xy(10, 15)
        pdf.cell(0, 10, titulo.upper(), 0, 1, "C")
        
        # Subtítulo
        if subtitulo:
            try:
                pdf.set_font("Arial", "I", 12)
            except:
                pdf.set_font("helvetica", "I", 12)
            pdf.cell(0, 7, subtitulo, 0, 1, "C")
            
        # Fecha actual
        try:
            pdf.set_font("Arial", "", 10)
        except:
            pdf.set_font("helvetica", "", 10)
        pdf.cell(0, 7, f"Generado el: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1, "C")
        pdf.ln(15)

        # Preguntas
        try:
            pdf.set_font("Arial", "B", 14)
        except:
            pdf.set_font("helvetica", "B", 14)
            
        # Título de sección
        pdf.set_fill_color(240, 240, 240)  # Color gris muy claro
        pdf.cell(0, 10, "CUESTIONARIO", 0, 1, "L", 1)
        pdf.ln(5)

        for i, pregunta in enumerate(preguntas):
            # Número de pregunta y texto
            try:
                pdf.set_font("Arial", "B", 12)
                pdf.set_text_color(0, 0, 200)  # Azul para el número de pregunta
            except:
                pdf.set_font("helvetica", "B", 12)
                
            # Rectángulo coloreado para la pregunta
            pdf.set_fill_color(245, 245, 245)  # Gris muy claro casi blanco
            pdf.rect(pdf.x, pdf.y, pdf.w - 40, 10, 'F')
            
            # Número y texto de la pregunta
            pdf.cell(10, 10, f"{i+1}.", 0, 0)
            
            # Texto de la pregunta (ahora en negro)
            pdf.set_text_color(0, 0, 0)
            pregunta_texto = pregunta.get('pregunta', '')
            pdf.multi_cell(0, 10, pregunta_texto)
            pdf.ln(2)  # Espacio después del texto de la pregunta

            # Mostrar alternativas si existen
            alternativas = pregunta.get("alternativas", [])
            opciones = pregunta.get("opciones", [])
            
            # Usar cualquiera de los dos formatos de alternativas
            if alternativas or opciones:
                try:
                    pdf.set_font("Arial", "", 10)  # Fuente más pequeña para alternativas
                except:
                    pdf.set_font("helvetica", "", 10)
                
                # Intenta primero alternativas, luego opciones si no hay alternativas
                items_to_display = alternativas if alternativas else opciones
                
                for alt in items_to_display:
                    alt_text = ""
                    if isinstance(alt, dict):
                        # Diferentes formatos posibles
                        if 'letra' in alt and 'texto' in alt:
                            alt_text = f"{alt.get('letra', '-')}) {alt.get('texto', '')}"
                        elif 'id' in alt and 'texto' in alt:
                            alt_text = f"{alt.get('id', '-')}) {alt.get('texto', '')}"
                        elif 'label' in alt:
                            alt_text = f"• {alt.get('label', '')}"
                        else:
                            # Fallback para otro formato
                            alt_text = str(alt)
                    else:
                        alt_text = f"• {alt}"
                    
                    pdf.cell(10, 6, "", 0, 0)  # Sangría para alternativas
                    pdf.multi_cell(0, 6, alt_text)  # Altura de línea reducida para alternativas
                
                pdf.ln(5)  # Espacio después de la lista de alternativas

        # Página de respuestas (opcional)
        if mostrar_respuestas and preguntas:
            pdf.add_page()
            try:
                pdf.set_font("Arial", "B", 16)
            except:
                pdf.set_font("helvetica", "B", 16)

            # Encabezado de respuestas con estilo
            pdf.set_fill_color(200, 230, 200)  # Color verde claro para respuestas
            pdf.rect(10, 10, pdf.w - 20, 20, 'F')
            
            pdf.set_xy(10, 15)
            pdf.cell(0, 10, "RESPUESTAS Y EXPLICACIONES", 0, 1, "C")
            pdf.ln(10)

            # Título de sección
            try:
                pdf.set_font("Arial", "B", 14)
            except:
                pdf.set_font("helvetica", "B", 14)
                
            pdf.set_fill_color(230, 255, 230)  # Verde muy claro
            pdf.cell(0, 10, "SOLUCIONES DETALLADAS", 0, 1, "L", 1)
            pdf.ln(5)

            # Listar respuestas
            for i, pregunta in enumerate(preguntas):
                # Configurar fuentes
                try:
                    pdf.set_font("Arial", "B", 12)
                except:
                    pdf.set_font("helvetica", "B", 12)
                
                # Número de pregunta resaltado
                pdf.set_text_color(0, 100, 0)  # Verde oscuro
                pdf.cell(10, 10, f"{i+1}.", 0, 0)
                
                # Texto de la pregunta (resumido)
                pregunta_texto = pregunta.get('pregunta', '')
                pregunta_corta = pregunta_texto[:80] + '...' if len(pregunta_texto) > 80 else pregunta_texto
                pdf.set_text_color(0, 0, 0)  # Negro para el texto normal
                pdf.multi_cell(0, 10, pregunta_corta)
                
                # Respuestas con mejor formato
                pdf.set_x(pdf.l_margin + 10)  # Sangría para la respuesta
                
                # Extraer respuesta correcta según los diferentes formatos
                try:
                    pdf.set_font("Arial", "", 11)
                except:
                    pdf.set_font("helvetica", "", 11)
                
                # Líneas para separar respuestas y explicaciones
                pdf.set_fill_color(245, 245, 245)  # Gris muy claro
                
                # Construir texto de respuesta
                respuesta_texto = ""
                
                # Intentar extraer respuestas en varios formatos
                if pregunta.get("respuesta_correcta") is not None:
                    # Formato de la aplicación para respuestas únicas
                    respuesta_texto = f"Respuesta correcta: {pregunta.get('respuesta_correcta')}"
                elif pregunta.get("tipo") == "seleccion_multiple" and pregunta.get("correctas"):
                    # Formato para selección múltiple
                    respuestas_list = pregunta.get("correctas", [])
                    if respuestas_list:
                        respuesta_texto = f"Respuestas correctas: {', '.join(str(r) for r in respuestas_list)}"
                elif pregunta.get("correcta") is not None:
                    # Formato simple con una sola respuesta
                    respuesta_texto = f"Respuesta correcta: {pregunta.get('correcta')}"
                else:
                    # Si no hay respuestas explícitas, buscar en alternativas
                    alternativas = pregunta.get("alternativas", [])
                    opciones = pregunta.get("opciones", [])
                    items = alternativas if alternativas else opciones
                    
                    # Buscar las respuestas correctas entre las alternativas
                    correctas = []
                    for alt in items:
                        if isinstance(alt, dict) and alt.get("correcta", False):
                            # Formato con valor booleano correcta:True
                            letra = alt.get("letra", alt.get("id", ""))
                            correctas.append(letra)
                    
                    if correctas:
                        respuesta_texto = f"Respuesta(s) correcta(s): {', '.join(correctas)}"
                
                # Si no tenemos respuesta_texto, mostrar un mensaje
                if not respuesta_texto:
                    respuesta_texto = "Respuesta no especificada"
                
                # Mostrar la respuesta
                pdf.set_text_color(0, 0, 150)  # Azul para respuestas
                pdf.cell(0, 8, respuesta_texto, 0, 1, 'L', 1)
                pdf.ln(2)
                
                # Explicación
                explicacion = pregunta.get('explicacion', 'Sin explicación disponible')
                if explicacion:
                    pdf.set_x(pdf.l_margin + 10)  # Sangría para la explicación
                    pdf.set_text_color(0, 0, 0)  # Negro para explicaciones
                    try:
                        pdf.set_font("Arial", "I", 10)  # Cursiva para la explicación
                    except:
                        pdf.set_font("helvetica", "I", 10)
                    
                    pdf.multi_cell(0, 6, f"Explicación: {explicacion}")
                
                pdf.ln(8)  # Espacio entre preguntas
                
        # Pie de página con información
        pdf.set_y(-30)
        try:
            pdf.set_font("Arial", "I", 8)
        except:
            pdf.set_font("helvetica", "I", 8)
        pdf.set_text_color(128, 128, 128)  # Gris para el pie de página
        pdf.cell(0, 10, f"Generado por SMART_STUDENT - {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 0, "C")
        
        # Guardar en un archivo
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        filename = f"{filename_prefix}_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)

        # Guardar el PDF
        pdf.output(filepath)
        print(f"PDF generado exitosamente en: {filepath}")
        
        # Copiar a directorio público para acceso web
        try:
            import shutil
            public_dir = os.path.join(".web", "public", "assets", "pdfs")
            os.makedirs(public_dir, exist_ok=True)
            public_path = os.path.join(public_dir, filename)
            shutil.copy2(filepath, public_path)
            print(f"PDF copiado a directorio público: {public_path}")
        except Exception as e:
            print(f"Advertencia: No se pudo copiar el PDF al directorio público: {e}")

        # Devolver la URL relativa del archivo
        return f"/assets/pdfs/{filename}"

    except Exception as e:
        print(f"ERROR generando PDF: {e}")
        import traceback
        traceback.print_exc()
        
        # Intentar crear un PDF de error para depuración
        try:
            error_pdf = FPDF()
            error_pdf.add_page()
            try:
                error_pdf.set_font("Arial", "B", 16)
            except:
                error_pdf.set_font("helvetica", "B", 16)
                
            error_pdf.cell(0, 10, "ERROR AL GENERAR PDF", 0, 1, "C")
            error_pdf.ln(10)
            
            try:
                error_pdf.set_font("Arial", "", 12)
            except:
                error_pdf.set_font("helvetica", "", 12)
                
            error_pdf.cell(0, 10, f"Error: {e}", 0, 1, "L")
            error_pdf.cell(0, 10, f"Fecha: {datetime.datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", 0, 1, "L")
            
            # Asegurar que existe el directorio de salida
            os.makedirs(output_dir, exist_ok=True)
            
            # Guardar PDF de error
            error_filename = f"error_pdf_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
            error_filepath = os.path.join(output_dir, error_filename)
            error_pdf.output(error_filepath)
            print(f"Se generó un PDF de error en: {error_filepath}")
            return f"/assets/pdfs/{error_filename}"
        except:
            # Si falla hasta el PDF de error, simplemente devolver cadena vacía
            print("Falló incluso la generación del PDF de error")
            return ""
