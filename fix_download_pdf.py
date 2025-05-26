#!/usr/bin/env python3
"""
Script para agregar el método download_pdf al archivo state.py
"""

import os
import shutil
from pathlib import Path
import re

def fix_state_py():
    # Ruta al archivo state.py
    state_path = Path('/workspaces/SMART_STUDENT/mi_app_estudio/state.py')
    
    # Crear copia de seguridad
    backup_path = state_path.with_suffix('.py.bak_download_pdf')
    shutil.copy2(state_path, backup_path)
    print(f"Creada copia de seguridad en {backup_path}")
    
    # Leer contenido del archivo
    with open(state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Definición del método download_pdf
    download_pdf_method = '''
    async def download_pdf(self):
        """Función general para descargar PDFs según el contexto actual (resumen, mapa o cuestionario)"""
        print(f"DEBUG: Iniciando download_pdf para pestaña {self.active_tab}...")
        
        try:
            # Determinar qué tipo de contenido descargar según la pestaña activa
            if self.active_tab == "resumen":
                async for result in self.download_resumen_pdf():
                    yield result
            elif self.active_tab == "mapa":
                async for result in self.download_map_pdf():
                    yield result
            elif self.active_tab == "cuestionario":
                async for result in self.download_cuestionario_pdf():
                    yield result
            elif self.active_tab == "evaluacion":
                # Si hay una implementación específica para evaluaciones la usaríamos aquí
                # Por ahora, mostramos un mensaje informativo
                self.error_message_ui = "La descarga de PDF para evaluaciones no está implementada aún."
                yield
            else:
                self.error_message_ui = f"No se puede descargar PDF para la pestaña {self.active_tab}."
                yield
        except Exception as e:
            self.error_message_ui = f"Error al descargar PDF: {str(e)}"
            print(f"ERROR download_pdf: {e}")
            yield'''
    
    # Buscar donde insertar la función (después de generate_summary)
    generate_summary_pattern = r'async def generate_summary\(self\):.*?\n            yield\n'
    match = re.search(generate_summary_pattern, content, re.DOTALL)
    
    if match:
        # Posición donde termina generate_summary
        end_pos = match.end()
        
        # Insertar la función download_pdf
        new_content = content[:end_pos] + "\n" + download_pdf_method + content[end_pos:]
        
        # Guardar el archivo modificado
        with open(state_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print("Método download_pdf añadido correctamente")
        return True
    else:
        print("No se pudo encontrar la función generate_summary. Abortando.")
        return False

if __name__ == "__main__":
    fix_state_py()
