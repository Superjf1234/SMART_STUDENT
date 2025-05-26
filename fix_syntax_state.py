#!/usr/bin/env python3
"""
Script para corregir problemas de sintaxis en el archivo state.py
"""

import re
import shutil
from pathlib import Path

def fix_state_py():
    # Rutas
    state_path = Path('/workspaces/SMART_STUDENT/mi_app_estudio/state.py')
    backup_path = state_path.with_suffix('.py.bak_syntax')
    
    # Crear respaldo
    shutil.copy2(state_path, backup_path)
    print(f"Creado respaldo en {backup_path}")
    
    # Leer el archivo
    with open(state_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Corregir problemas de sangría/indentación
    lines = content.split('\n')
    fixed_lines = []
    skip_next = False
    for i, line in enumerate(lines):
        if skip_next:
            skip_next = False
            continue
            
        # Corregir yield seguido de try sin línea vacía
        if line.strip() == 'yield' and i+1 < len(lines) and lines[i+1].strip().startswith('try:'):
            fixed_lines.append(line)
            fixed_lines.append('')
            continue
            
        # Corregir try sin sangría
        if line.strip() == 'try:' and not line.startswith('        try:'):
            fixed_lines.append('        try:')
            continue
            
        # Corregir except sin sangría
        if re.match(r'except\s+\w+\s+as\s+\w+:', line.strip()) and not line.startswith('        except'):
            fixed_lines.append('        ' + line.strip())
            continue
            
        # Corregir finally sin sangría
        if line.strip() == 'finally:' and not line.startswith('        finally:'):
            fixed_lines.append('        finally:')
            continue
            
        # Eliminar dobles líneas vacías entre métodos
        if line == '' and i > 0 and i+1 < len(lines):
            if lines[i-1] == '' and lines[i+1] == '':
                continue
                
        fixed_lines.append(line)
    
    # Volver a unir
    fixed_content = '\n'.join(fixed_lines)
    
    # Corregir ciclos yield-return juntos
    fixed_content = re.sub(r'yield\s+return', 'yield\n            return', fixed_content)
    
    # Guardar archivo arreglado
    with open(state_path, 'w', encoding='utf-8') as f:
        f.write(fixed_content)
    
    print("Correcciones de sintaxis completadas")
    return True

if __name__ == '__main__':
    fix_state_py()
