#!/usr/bin/env python3
"""
Script para agregar la función generate_map faltante al archivo state.py
"""

import os
import re
import shutil
from pathlib import Path

def fix_state_py():
    # Ruta al archivo state.py
    state_path = Path('/workspaces/SMART_STUDENT/mi_app_estudio/state.py')
    
    # Crear copia de seguridad
    backup_path = state_path.with_suffix('.py.bak_generate_map')
    shutil.copy2(state_path, backup_path)
    print(f"Creada copia de seguridad en {backup_path}")
    
    # Leer contenido del archivo
    with open(state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Definición de la función generate_map
    generate_map_function = '''
    async def generate_map(self):
        """Genera un mapa conceptual del tema seleccionado."""
        print("DEBUG: Iniciando generate_map...")
        if not self.selected_tema:
            self.error_message_ui = "Ingresa un tema."
            yield
            return
        if not BACKEND_AVAILABLE:
            self.error_message_ui = "Servicio no disponible."
            yield
            return
        self.is_generating_mapa = True
        self.error_message_ui = ""
        self.mapa_image_url = ""
        self.mapa_mermaid_code = ""
        yield
        try:
            if not all(hasattr(map_logic, fn) for fn in ["generar_nodos_localmente", "generar_mermaid_code", "generar_visualizacion_html"]):
                raise AttributeError("Funciones de map_logic faltantes.")
            print(f"DEBUG: Llamando map_logic.generar_nodos_localmente con T='{self.selected_tema}'")
            resultado_nodos = map_logic.generar_nodos_localmente(self.selected_tema.strip())
            print(f"DEBUG: Resultado nodos: {resultado_nodos}")
            
            # PASO 1: Convertir los nodos a formato de texto estructurado para Mermaid
            if resultado_nodos.get("status") == "EXITO" and "nodos" in resultado_nodos:
                nodos = resultado_nodos["nodos"]
                estructura_texto = f"- Nodo Central: {self.selected_tema.strip().title()}\\n"
                
                for nodo in nodos:
                    titulo = nodo.get("titulo", "")
                    if titulo:
                        estructura_texto += f"  - Nodo Secundario: {titulo}\\n"
                        
                        for subnodo in nodo.get("subnodos", []):
                            estructura_texto += f"    - Nodo Terciario: {subnodo}\\n"
                
                # PASO 2: Generar código Mermaid a partir de la estructura de texto
                print("DEBUG: Generando código Mermaid a partir de la estructura...")
                orientation = "LR" if self.mapa_orientacion_horizontal else "TD"
                mermaid_code, error_mermaid = map_logic.generar_mermaid_code(estructura_texto, orientation)
                
                if error_mermaid:
                    raise Exception(f"Error generando código Mermaid: {error_mermaid}")
                
                if not mermaid_code:
                    raise Exception("No se generó código Mermaid válido")
                
                self.mapa_mermaid_code = mermaid_code
                
                # PASO 3: Generar HTML para visualización
                print("DEBUG: Generando HTML para visualización del mapa...")
                html_url = map_logic.generar_visualizacion_html(mermaid_code, self.selected_tema)
                
                if not html_url:
                    raise Exception("No se pudo generar la visualización HTML")
                
                # PASO 4: Actualizar la URL de la imagen para mostrarla en la UI
                self.mapa_image_url = html_url
                print(f"DEBUG: HTML URL generada: {html_url[:100]}...")
                
                # Incrementar el contador de mapas creados
                self.mapas_creados_count += 1
                print(f"DEBUG: Incrementado contador de mapas a {self.mapas_creados_count}")
                
                # Persistir el contador en la BD si está disponible
                if BACKEND_AVAILABLE and hasattr(db_logic, "update_user_stats") and self.logged_in_username:
                    try:
                        db_logic.update_user_stats(self.logged_in_username, mapas_count=self.mapas_creados_count)
                    except Exception as e:
                        print(f"ERROR: No se pudo actualizar contador de mapas en BD: {e}")
            else:
                raise Exception(f"Error en resultado de nodos: {resultado_nodos.get('status')}")
                
        except AttributeError as ae:
            self.error_message_ui = f"Error config map: {ae}"
            print(f"ERROR Config: {self.error_message_ui}")
        except Exception as e:
            self.error_message_ui = f"Error generando mapa: {str(e)}"
            print(f"ERROR G-MAP: {traceback.format_exc()}")
        finally:
            self.is_generating_mapa = False
            yield'''
    
    # Buscar dónde insertar la función (después de generate_summary)
    generate_summary_pattern = r'async def generate_summary\(self\):.*?\n        yield\n'
    match = re.search(generate_summary_pattern, content, re.DOTALL)
    
    if match:
        # Posición donde termina generate_summary
        end_pos = match.end()
        
        # Insertar la función generate_map
        new_content = content[:end_pos] + "\n" + generate_map_function + content[end_pos:]
        
        # Guardar el archivo modificado
        with open(state_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Función generate_map añadida correctamente")
        return True
    else:
        print("No se pudo encontrar la función generate_summary. Buscando antes de download_pdf...")
        
        # Intentar encontrar download_pdf como alternativa
        download_pdf_pattern = r'async def download_pdf\(self\):.*?\n        yield\n'
        match = re.search(download_pdf_pattern, content, re.DOTALL)
        
        if match:
            # Posición donde comienza download_pdf
            start_pos = match.start()
            
            # Insertar la función generate_map antes de download_pdf
            new_content = content[:start_pos] + generate_map_function + "\n\n" + content[start_pos:]
            
            # Guardar el archivo modificado
            with open(state_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            print("Función generate_map añadida antes de download_pdf")
            return True
        else:
            print("No se pudo encontrar un lugar adecuado para insertar la función. Abortando.")
            return False

if __name__ == "__main__":
    fix_state_py()
