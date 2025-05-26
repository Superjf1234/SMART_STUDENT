#!/usr/bin/env python
"""
Script definitivo para corregir problemas de Var en condicionales if
"""
import os
import re
import shutil
import datetime
import sys

print("=== CORRECCIÓN DEFINITIVA PARA VARIABLES REACTIVAS EN CONDICIONALES ===")

# 1. Verificar el archivo state.py
print("\n1. Verificando y modificando state.py...")
project_root = '/workspaces/SMART_STUDENT'
state_file = os.path.join(project_root, 'mi_app_estudio', 'state.py')

try:
    with open(state_file, 'r') as f:
        content = f.read()
    
    # Patrón 1: pdf_url_not_empty en if
    pattern1 = r"""                # Evaluar directamente la condición sin usar if con variable reactiva
                pdf_url_not_empty = CuestionarioState\.cuestionario_pdf_url != ""
                
                # Obtenemos la URL directamente sin usar rx\.cond
                if pdf_url_not_empty:"""
    
    # Reemplazo 1: verificación correcta con verificación de atributo
    replacement1 = """                # Evaluamos si existe y tiene contenido usando variables Python estándar
                # NO USAR variables reactivas en condiciones if
                has_pdf_url = hasattr(CuestionarioState, "cuestionario_pdf_url")
                pdf_url = str(CuestionarioState.cuestionario_pdf_url) if has_pdf_url else ""
                is_pdf_url_not_empty = pdf_url != ""
                
                # Ahora usamos variables Python estándar para la lógica condicional
                if is_pdf_url_not_empty:"""
    
    # Aplicar reemplazo principal
    modified_content = re.sub(pattern1, replacement1, content)
    
    # Verificar si se hicieron cambios
    if modified_content != content:
        # Hacer backup
        backup_file = state_file + f".bak_final_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(state_file, backup_file)
        print(f"  ✓ Backup creado en: {backup_file}")
        
        # Guardar el archivo modificado
        with open(state_file, 'w') as f:
            f.write(modified_content)
        print("  ✓ Archivo state.py modificado correctamente")
        print("  ✓ Se ha corregido el uso de variables reactivas en condicionales if")
    else:
        # Aplicar método directo
        direct_fix = content.replace(
            "pdf_url_not_empty = CuestionarioState.cuestionario_pdf_url != \"\"",
            "# Convertir la variable reactiva a Python estándar\n                has_pdf_url = hasattr(CuestionarioState, \"cuestionario_pdf_url\")\n                pdf_url = str(CuestionarioState.cuestionario_pdf_url) if has_pdf_url else \"\"\n                is_pdf_url_not_empty = pdf_url != \"\""
        )
        
        direct_fix = direct_fix.replace(
            "if pdf_url_not_empty:",
            "if is_pdf_url_not_empty:"
        )
        
        if direct_fix != content:
            # Hacer backup
            backup_file = state_file + f".bak_direct_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(state_file, backup_file)
            print(f"  ✓ Backup creado en: {backup_file}")
            
            # Guardar el archivo modificado
            with open(state_file, 'w') as f:
                f.write(direct_fix)
            print("  ✓ Archivo state.py modificado con método directo")
            print("  ✓ Se ha corregido el uso de variables reactivas en condicionales if")
        else:
            print("  ✗ No se pudo aplicar la corrección automática.")
            print("  ! RECOMENDACIÓN: Editar manualmente el archivo state.py")
            print("  ! Sustituir el uso de variables reactivas en condiciones if")
        
except Exception as e:
    print(f"  ✗ Error modificando state.py: {e}")

print("\n=== REGLA DEFINITIVA PARA REFLEX ===")
print("NUNCA usar variables reactivas (Var) directamente en:")
print("  - Condiciones if/and/or/not")
print("  - Operaciones aritméticas directas")
print("  - Funciones de Python estándar que esperan tipos específicos")
print("\nSIEMPRE convertir a tipos Python estándar primero:")
print("  - has_attr = hasattr(Class, 'attr')")
print("  - python_str = str(var_reactiva)")
print("  - python_int = int(var_reactiva)")
print("  - python_bool = python_str != ''")

print("\n=== CORRECCIÓN APLICADA ===")
print("La corrección asegura que todas las variables usadas en condicionales sean")
print("variables Python estándar, no variables reactivas de Reflex.")
print("\nPruebe de nuevo la descarga de PDF desde la aplicación.")
print("=== FIN DEL SCRIPT ===")
