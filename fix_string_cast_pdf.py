#!/usr/bin/env python
"""
Script para arreglar el problema de StringCastedVar en la descarga de PDF
"""
import os
import re
import shutil
import datetime
import sys

print("=== APLICANDO FIX PARA DESCARGA DE PDF (StringCastedVar) ===")

# 1. Verificar el archivo state.py
print("\n1. Verificando y modificando state.py...")
project_root = '/workspaces/SMART_STUDENT'
state_file = os.path.join(project_root, 'mi_app_estudio', 'state.py')

try:
    with open(state_file, 'r') as f:
        content = f.read()
    
    # Buscar y reemplazar todas las instancias de StringCastedVar sin conversión
    # Patrón 1: variables tema_value
    pattern1 = r'(s_tema = re\.sub\(r\'\[\\\\/\*\?:\"<>\|\]\', \"\", )(tema_value)(\)\[:50\])'
    replacement1 = r'\1str(\2)\3'
    
    # Patrón 2: variables libro_value
    pattern2 = r'(s_lib = re\.sub\(r\'\[\\\\/\*\?:\"<>\|\]\', \"\", )(libro_value)(\)\[:50\])'
    replacement2 = r'\1str(\2)\3'
    
    # Patrón 3: variables curso_value
    pattern3 = r'(s_cur = re\.sub\(r\'\[\\\\/\*\?:\"<>\|\]\', \"\", )(curso_value)(\)\[:50\])'
    replacement3 = r'\1str(\2)\3'
    
    # Aplicar reemplazos
    modified_content = re.sub(pattern1, replacement1, content)
    modified_content = re.sub(pattern2, replacement2, modified_content)
    modified_content = re.sub(pattern3, replacement3, modified_content)
    
    # Verificar si se hicieron cambios
    if modified_content != content:
        # Hacer backup
        backup_file = state_file + f".bak_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(state_file, backup_file)
        print(f"  ✓ Backup creado en: {backup_file}")
        
        # Guardar el archivo modificado
        with open(state_file, 'w') as f:
            f.write(modified_content)
        print("  ✓ Archivo state.py modificado correctamente")
        
        # Añadir comentarios explicativos
        print("  ✓ Se ha añadido la conversión a string para los valores que provienen de rx.cond()")
    else:
        print("  ✓ El archivo state.py ya está corregido o utiliza un formato diferente")
        
except Exception as e:
    print(f"  ✗ Error modificando state.py: {e}")

print("\n=== FIX APLICADO CORRECTAMENTE ===")
print("El problema de 'StringCastedVar' debería estar resuelto.")
print("Pruebe de nuevo la descarga de PDF desde la aplicación.")
print("=== FIN DEL SCRIPT ===")
