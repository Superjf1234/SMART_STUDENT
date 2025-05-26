#!/usr/bin/env python3
"""
Script para eliminar el decorador @rx.var suelto al final del archivo state.py
y agregar el método language_text faltante.
"""

import re

def fix_state_py():
    # Ruta al archivo state.py
    state_path = '/workspaces/SMART_STUDENT/mi_app_estudio/state.py'
    
    # Leer contenido del archivo
    with open(state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Eliminar el último @rx.var suelto y agregar language_text
    fixed_content = re.sub(r'@rx.var\s*$', 
                          r'''@rx.var
    def language_text(self) -> str:
        """Returns the translated language text."""
        return self.translate("language")
        
    # --- FIN CLASE AppState ---''', 
                          content)
    
    # Guardar el archivo modificado
    with open(state_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("Archivo state.py corregido correctamente.")
    return True

if __name__ == "__main__":
    fix_state_py()
