#!/usr/bin/env python3
"""
Script para agregar los métodos de descarga de PDF al archivo state.py
"""

import os
import shutil
from pathlib import Path
import re

def fix_state_py():
    # Ruta al archivo state.py
    state_path = Path('/workspaces/SMART_STUDENT/mi_app_estudio/state.py')
    
    # Crear copia de seguridad
    backup_path = state_path.with_suffix('.py.bak_pdf_download_methods')
    shutil.copy2(state_path, backup_path)
    print(f"Creada copia de seguridad en {backup_path}")
    
    # Leer contenido del archivo
    with open(state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Definición de los métodos auxiliares
    pdf_download_methods = '''
    async def download_resumen_pdf(self):
        """Descarga el resumen actual en formato PDF"""
        print("DEBUG: Iniciando download_resumen_pdf...")
        if not self.resumen_content:
            self.error_message_ui = "No hay resumen para descargar."
            yield
            return

        s_tema = re.sub(r'[\\/*?:"<>|]', "", self.selected_tema or "tema")[:50]
        s_lib = re.sub(r'[\\/*?:"<>|]', "", self.selected_libro or "libro")[:50]
        s_cur = re.sub(r'[\\/*?:"<>|]', "", self.selected_curso or "curso")[:50]
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fname_base = f"Resumen_{s_cur}_{s_lib}_{s_tema}_{timestamp}".replace(" ", "_")

        try:
            pdf_generado = False
            if hasattr(resumen_logic, "generar_resumen_pdf_bytes"):
                print("DEBUG: Intentando generar PDF con resumen_logic...")
                try:
                    pdf_bytes = resumen_logic.generar_resumen_pdf_bytes(
                        resumen_txt=self.resumen_content,
                        puntos_txt=self.puntos_content if self.include_puntos else "",
                        titulo=f"Resumen: {self.selected_tema or 'General'}",
                        subtitulo=f"Curso: {self.selected_curso or 'N/A'} - Libro: {self.selected_libro or 'N/A'}",
                    )
                    if isinstance(pdf_bytes, bytes) and pdf_bytes.startswith(b"%PDF"):
                        fname = f"{fname_base}.pdf"
                        print(f"DEBUG: PDF generado ({len(pdf_bytes)} bytes). Descargando como {fname}")
                        yield rx.download(data=pdf_bytes, filename=fname)
                        pdf_generado = True
                    else:
                        print("WARN: resumen_logic.generar_resumen_pdf_bytes no devolvió un PDF válido.")
                except Exception as pdf_e:
                    print(f"WARN: Error en generación de PDF con resumen_logic (usando fallback HTML): {pdf_e}")

            if not pdf_generado:
                print("DEBUG: Generando fallback HTML...")
                html_content = f"""<!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Resumen: {s_tema}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                        h1 {{ color: #2563eb; }}
                        h2 {{ color: #4b5563; margin-top: 30px; }}
                        .resumen {{ background-color: #f3f4f6; padding: 20px; border-radius: 5px; }}
                        .puntos {{ margin-top: 30px; }}
                        .puntos ol {{ padding-left: 20px; }}
                    </style>
                </head>
                <body>
                    <h1>Resumen: {self.selected_tema}</h1>
                    <h3>Curso: {self.selected_curso} - Libro: {self.selected_libro}</h3>
                    <hr>
                    <div class="resumen">
                        {self.resumen_content.replace('\\n', '<br>')}
                    </div>
                    
                    {f'<h2>Puntos Clave:</h2><div class="puntos">{self.puntos_content.replace("\\n", "<br>")}</div>' if self.puntos_content and self.include_puntos else ''}
                    
                    <hr>
                    <footer>
                        <p><i>Generado por SMART_STUDENT el {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</i></p>
                    </footer>
                </body>
                </html>"""
                fname = f"{fname_base}.html"
                print(f"DEBUG: Descargando resumen como HTML: {fname}")
                yield rx.download(data=html_content.encode("utf-8", errors='replace'), filename=fname)

        except Exception as e:
            self.error_message_ui = f"Error descarga: {str(e)}"
            print(f"ERROR DWNLD PDF/HTML: {traceback.format_exc()}")
            yield

    async def download_map_pdf(self):
        """Descarga el mapa conceptual actual en formato PDF"""
        print("DEBUG: Iniciando download_map_pdf...")
        if not self.mapa_mermaid_code or not self.mapa_image_url:
            self.error_message_ui = "No hay mapa conceptual para descargar."
            yield
            return

        s_tema = re.sub(r'[\\/*?:"<>|]', "", self.selected_tema or "tema")[:50]
        s_lib = re.sub(r'[\\/*?:"<>|]', "", self.selected_libro or "libro")[:50]
        s_cur = re.sub(r'[\\/*?:"<>|]', "", self.selected_curso or "curso")[:50]
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fname_base = f"Mapa_{s_cur}_{s_lib}_{s_tema}_{timestamp}".replace(" ", "_")

        try:
            pdf_generado = False
            if hasattr(map_logic, "generar_mapa_pdf_bytes"):
                print("DEBUG: Intentando generar PDF del mapa con map_logic...")
                try:
                    pdf_bytes = map_logic.generar_mapa_pdf_bytes(
                        mermaid_code=self.mapa_mermaid_code,
                        tema=self.selected_tema,
                        curso=self.selected_curso,
                        libro=self.selected_libro,
                        html_url=self.mapa_image_url
                    )
                    if isinstance(pdf_bytes, bytes) and pdf_bytes.startswith(b"%PDF"):
                        fname = f"{fname_base}.pdf"
                        print(f"DEBUG: PDF del mapa generado ({len(pdf_bytes)} bytes). Descargando como {fname}")
                        yield rx.download(data=pdf_bytes, filename=fname)
                        pdf_generado = True
                    else:
                        print("WARN: map_logic.generar_mapa_pdf_bytes no devolvió un PDF válido.")
                except Exception as pdf_e:
                    print(f"WARN: Error en generación de PDF del mapa (usando fallback HTML): {pdf_e}")
                    traceback.print_exc()

            if not pdf_generado:
                print("DEBUG: Generando mapa fallback HTML...")
                html_content = f"""<!DOCTYPE html>
                <html lang="es">
                <head>
                    <meta charset="UTF-8">
                    <title>Mapa Conceptual: {s_tema}</title>
                    <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 40px; }}
                        h1 {{ color: #2563eb; }}
                        .mermaid {{ background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
                    </style>
                </head>
                <body>
                    <h1>Mapa Conceptual: {self.selected_tema}</h1>
                    <h3>Curso: {self.selected_curso} - Libro: {self.selected_libro}</h3>
                    <hr>
                    <div class="mermaid">
                        {self.mapa_mermaid_code}
                    </div>
                    <script>
                        mermaid.initialize({{
                            startOnLoad: true,
                            theme: 'default',
                            themeVariables: {{
                                primaryColor: '#d4e8ff',
                                primaryTextColor: '#003366',
                                primaryBorderColor: '#7fb3ff',
                                lineColor: '#4b5563',
                                fontSize: '16px'
                            }}
                        }});
                    </script>
                    <hr>
                    <footer>
                        <p><i>Generado por SMART_STUDENT el {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</i></p>
                    </footer>
                </body>
                </html>"""
                fname = f"{fname_base}.html"
                print(f"DEBUG: Descargando mapa como HTML: {fname}")
                yield rx.download(data=html_content.encode("utf-8", errors='replace'), filename=fname)

        except Exception as e:
            self.error_message_ui = f"Error al descargar mapa: {str(e)}"
            print(f"ERROR DWNLD MAP PDF/HTML: {traceback.format_exc()}")
            yield

    async def download_cuestionario_pdf(self):
        """Descarga el cuestionario actual en formato PDF"""
        # Importamos solo cuando se necesita para evitar dependencias circulares
        from .cuestionario import CuestionarioState
        
        print("DEBUG: Iniciando download_cuestionario_pdf...")
        
        # Verificar disponibilidad de preguntas
        print("DEBUG: Verificando disponibilidad de preguntas...")
        
        try:
            # Intentar acceder directamente al array de preguntas
            preguntas_array = CuestionarioState.cuestionario_preguntas
            
            # Intentar convertir a Python para verificar su contenido
            try:
                preguntas_py = preguntas_array.to_py()
                print(f"DEBUG: Array de preguntas convertido exitosamente. Cantidad: {len(preguntas_py) if preguntas_py else 0}")
                
                # Si no hay preguntas, mostrar error
                if not preguntas_py or len(preguntas_py) == 0:
                    print("DEBUG: No hay preguntas disponibles en el array")
                    self.error_message_ui = "No hay preguntas en el cuestionario para descargar."
                    yield
                    return
            except Exception as e:
                print(f"DEBUG: Error al convertir array de preguntas: {e}")
                # Intentar acceder directamente al primer elemento para verificar si hay preguntas
                try:
                    primera_pregunta = preguntas_array[0]
                    # Si llegamos aquí, hay al menos una pregunta
                    print("DEBUG: Verificación alternativa de preguntas exitosa")
                except Exception as e:
                    print(f"DEBUG: No se pudo acceder a la primera pregunta: {e}")
                    self.error_message_ui = "No hay preguntas en el cuestionario para descargar."
                    yield
                    return
                
        except Exception as e:
            print(f"DEBUG: Error al verificar preguntas: {e}")
            self.error_message_ui = "Error al acceder a las preguntas del cuestionario."
            yield
            return

        # Obtener información del cuestionario
        print("DEBUG: Obteniendo información de tema, libro y curso...")
        
        # Variables para usar en nombres de archivo
        tema_val = "tema"
        lib_val = "libro"
        cur_val = "curso"
        
        try:
            # Obtener tema de manera segura
            try:
                tema_val = CuestionarioState.cuestionario_tema.to_py() or tema_val
                print(f"DEBUG: Tema obtenido: {tema_val}")
            except Exception as e:
                print(f"DEBUG: Error obteniendo tema: {e}")
                try:
                    tema_val = CuestionarioState.selected_tema.to_py() or tema_val
                    print(f"DEBUG: Tema alternativo obtenido: {tema_val}")
                except:
                    pass
            
            # Obtener libro de manera segura
            try:
                lib_val = CuestionarioState.cuestionario_libro.to_py() or lib_val
                print(f"DEBUG: Libro obtenido: {lib_val}")
            except Exception as e:
                print(f"DEBUG: Error obteniendo libro: {e}")
                try:
                    lib_val = CuestionarioState.selected_libro.to_py() or lib_val
                    print(f"DEBUG: Libro alternativo obtenido: {lib_val}")
                except:
                    pass
                    
            # Obtener curso de manera segura
            try:
                cur_val = CuestionarioState.cuestionario_curso.to_py() or cur_val
                print(f"DEBUG: Curso obtenido: {cur_val}")
            except Exception as e:
                print(f"DEBUG: Error obteniendo curso: {e}")
                try:
                    cur_val = CuestionarioState.selected_curso.to_py() or cur_val
                    print(f"DEBUG: Curso alternativo obtenido: {cur_val}")
                except:
                    pass
        except Exception as e:
            print(f"DEBUG: Error general obteniendo información: {e}")
            # Continuar con valores por defecto
        
        # Sanitizar nombres de archivos
        s_tema = re.sub(r'[\\/*?:"<>|]', "", str(tema_val))[:50]
        s_lib = re.sub(r'[\\/*?:"<>|]', "", str(lib_val))[:50]
        s_cur = re.sub(r'[\\/*?:"<>|]', "", str(cur_val))[:50]
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        fname_base = f"Cuestionario_{s_cur}_{s_lib}_{s_tema}_{timestamp}".replace(" ", "_")
        print(f"DEBUG: Nombre base para archivo: {fname_base}")

        # Verificar si ya existe un PDF y descargarlo directamente
        try:
            pdf_url_val = None
            try:
                pdf_url_val = CuestionarioState.cuestionario_pdf_url.to_py()
            except:
                print("DEBUG: No se pudo obtener la URL del PDF desde CuestionarioState")

            if pdf_url_val:
                print(f"DEBUG: URL de PDF encontrada: {pdf_url_val}")
                # Verificar si ya existe el archivo
                filename = os.path.basename(pdf_url_val)
                asset_path = os.path.join("assets", "pdfs", filename)
                
                if os.path.exists(asset_path) and os.path.getsize(asset_path) > 0:
                    print(f"DEBUG: PDF existente encontrado: {asset_path}")
                    # Verificar si el archivo es un PDF válido
                    with open(asset_path, 'rb') as f:
                        is_pdf = f.read(4).startswith(b'%PDF')
                    
                    if is_pdf:
                        print(f"DEBUG: PDF válido, descargando...")
                        with open(asset_path, 'rb') as f:
                            pdf_bytes = f.read()
                        
                        yield rx.download(
                            data=pdf_bytes, 
                            filename=filename,
                            # También podríamos usar fname_base + ".pdf" para un nombre más específico
                        )
                        # Si llegamos aquí, la descarga fue exitosa
                        return
                    else:
                        print("DEBUG: El archivo no es un PDF válido")
                else:
                    print(f"DEBUG: PDF no encontrado en: {asset_path}")
            else:
                print("DEBUG: No hay URL de PDF disponible")
        except Exception as e:
            print(f"ERROR: Al intentar usar PDF existente: {e}")
            # Continuamos con el fallback

        # Fallback: Generar HTML con las preguntas
        try:
            print("DEBUG: Generando fallback HTML para cuestionario...")
            
            # Convertir preguntas a HTML
            preguntas_html = ""
            try:
                for i, pregunta in enumerate(CuestionarioState.cuestionario_preguntas):
                    pregunta_py = pregunta.to_py() if hasattr(pregunta, "to_py") else pregunta
                    if isinstance(pregunta_py, dict):
                        texto_pregunta = pregunta_py.get("pregunta", "")
                        explicacion = pregunta_py.get("explicacion", "")
                        
                        preguntas_html += f"""
                        <div class="pregunta">
                            <h3>Pregunta {i+1}</h3>
                            <p>{texto_pregunta}</p>
                            <div class="explicacion">
                                <h4>Respuesta:</h4>
                                <p>{explicacion}</p>
                            </div>
                        </div>
                        <hr>
                        """
            except Exception as e:
                print(f"ERROR: Generando HTML para preguntas: {e}")
                preguntas_html = f"<p>Error al procesar las preguntas: {e}</p>"
            
            html_content = f"""<!DOCTYPE html>
            <html lang="es">
            <head>
                <meta charset="UTF-8">
                <title>Cuestionario: {s_tema}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
                    h1 {{ color: #2563eb; }}
                    h2 {{ color: #4b5563; margin-top: 30px; }}
                    .pregunta {{ background-color: #f9fafb; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                    .explicacion {{ background-color: #e6f7f2; padding: 10px; border-radius: 5px; margin-top: 10px; }}
                </style>
            </head>
            <body>
                <h1>Cuestionario: {s_tema}</h1>
                <h3>Curso: {s_cur} - Libro: {s_lib}</h3>
                <hr>
                
                {preguntas_html}
                
                <footer>
                    <p><i>Generado por SMART_STUDENT el {datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</i></p>
                </footer>
            </body>
            </html>
            """
            
            fname = f"{fname_base}.html"
            print(f"DEBUG: Descargando cuestionario como HTML: {fname}")
            yield rx.download(data=html_content.encode("utf-8", errors='replace'), filename=fname)
            
        except Exception as e:
            self.error_message_ui = f"Error al generar cuestionario: {str(e)}"
            print(f"ERROR DWNLD CUESTIONARIO: {traceback.format_exc()}")
            yield'''
    
    # Buscar donde insertar las funciones (después de download_pdf)
    download_pdf_pattern = r'async def download_pdf\(self\):.*?\n            yield\n'
    match = re.search(download_pdf_pattern, content, re.DOTALL)
    
    if match:
        # Posición donde termina download_pdf
        end_pos = match.end()
        
        # Insertar las funciones de descarga
        new_content = content[:end_pos] + "\n" + pdf_download_methods + content[end_pos:]
        
        # Guardar el archivo modificado
        with open(state_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Métodos de descarga de PDF añadidos correctamente")
        return True
    else:
        print("No se pudo encontrar la función download_pdf. Abortando.")
        return False

if __name__ == "__main__":
    fix_state_py()
