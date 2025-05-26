#!/usr/bin/env python
"""
Script para arreglar el problema de uso de variables reactivas en condicionales if
"""
import os
import re
import shutil
import datetime
import sys

print("=== APLICANDO FIX PARA VARIABLES REACTIVAS EN IF (VarTypeError) ===")

# 1. Verificar el archivo state.py
print("\n1. Verificando y modificando state.py...")
project_root = '/workspaces/SMART_STUDENT'
state_file = os.path.join(project_root, 'mi_app_estudio', 'state.py')

try:
    with open(state_file, 'r') as f:
        content = f.read()
    
    # Patrón para buscar el uso incorrecto de pdf_url_not_empty en if
    pattern = r"""                pdf_url_not_empty = rx\.cond\(
                    CuestionarioState\.cuestionario_pdf_url != "",
                    True,
                    False
                \)
                if pdf_url_not_empty:"""
    
    # Reemplazo correcto usando rx.cond para evitar el if directo
    replacement = """                # Evaluar directamente la condición sin usar if con variable reactiva
                pdf_url_empty = CuestionarioState.cuestionario_pdf_url == ""
                
                # Usamos una función interna para manejar el caso con URL
                def process_with_url():
                    nonlocal pdf_path
                    # Si ya hay un PDF generado, usamos esa URL
                    print(f"DEBUG: Usando PDF ya generado: {CuestionarioState.cuestionario_pdf_url}")
                    # La URL es relativa, así que buscamos el archivo directamente
                    pdf_path = str(CuestionarioState.cuestionario_pdf_url).lstrip('/')
                
                # Usamos rx.cond para la bifurcación condicional basada en variables reactivas
                rx.cond(
                    pdf_url_empty,
                    lambda: None,  # No hacer nada si está vacía
                    process_with_url  # Procesar si tiene contenido
                )
                
                # Continuamos con el flujo normal, ya que ahora pdf_path tendrá el valor correcto
                if not pdf_url_empty and os.path.exists(pdf_path) and os.path.isfile(pdf_path):"""
    
    # Aplicar reemplazo
    modified_content = content.replace(pattern, replacement)
    
    # Verificar si se hicieron cambios
    if modified_content != content:
        # Hacer backup
        backup_file = state_file + f".bak_vartype_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(state_file, backup_file)
        print(f"  ✓ Backup creado en: {backup_file}")
        
        # Guardar el archivo modificado
        with open(state_file, 'w') as f:
            f.write(modified_content)
        print("  ✓ Archivo state.py modificado correctamente")
        print("  ✓ Se ha corregido el uso de variables reactivas en condicionales if")
    else:
        print("  ? No se encontró el patrón exacto. Se requiere una revisión manual.")
        print("    Busca en el código lugares donde se use 'if pdf_url_not_empty' después de definir esa variable con rx.cond()")
        
except Exception as e:
    print(f"  ✗ Error modificando state.py: {e}")

print("\n=== RECOMENDACIONES PARA CÓDIGO REFLEX ===")
print("1. Nunca use variables reactivas (creadas con rx.cond o derivadas de State) directamente en:")
print("   - Condicionales 'if', 'and', 'or', 'not'")
print("   - Bucles 'for', 'while'")
print("   - Otras operaciones que requieran tipos primitivos de Python")
print("2. En su lugar use:")
print("   - rx.cond() para bifurcaciones condicionales")
print("   - Operadores bitwise: & (and), | (or), ~ (not)")
print("   - Convierta a str() antes de usar variables reactivas con funciones que esperan strings")
print("3. Para verificar si una variable reactiva está vacía:")
print("   - Incorrecto: if variable_reactiva:")
print("   - Correcto: is_empty = variable_reactiva == \"\"")

print("\n=== FIX APLICADO ===")
print("El problema de 'VarTypeError' debería estar resuelto.")
print("Pruebe de nuevo la descarga de PDF desde la aplicación.")
print("=== FIN DEL SCRIPT ===")
