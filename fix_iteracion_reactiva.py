#!/usr/bin/env python
"""
Script para corregir problemas de iteración sobre variables reactivas
"""
import os
import re
import shutil
import datetime
import sys

print("=== CORRECCIÓN PARA ITERACIÓN SOBRE VARIABLES REACTIVAS ===")

# 1. Verificar el archivo state.py
print("\n1. Verificando y modificando state.py...")
project_root = '/workspaces/SMART_STUDENT'
state_file = os.path.join(project_root, 'mi_app_estudio', 'state.py')

try:
    with open(state_file, 'r') as f:
        content = f.read()
    
    # Patrón para la iteración incorrecta sobre CuestionarioState.cuestionario_preguntas
    pattern = r"""            # Si no hay PDF o falló la lectura, generamos HTML con las preguntas
            preguntas_html = ""
            for i, pregunta in enumerate\(CuestionarioState\.cuestionario_preguntas\):"""
    
    # Reemplazo correcto convirtiendo la variable reactiva a una lista Python
    replacement = """            # Si no hay PDF o falló la lectura, generamos HTML con las preguntas
            preguntas_html = ""
            # Convertir la lista reactiva a una lista Python estándar
            has_preguntas = hasattr(CuestionarioState, "cuestionario_preguntas")
            preguntas_lista = list(CuestionarioState.cuestionario_preguntas) if has_preguntas else []
            
            # Ahora iteramos sobre la lista Python estándar
            for i, pregunta in enumerate(preguntas_lista):"""
    
    # Aplicar reemplazo
    modified_content = re.sub(pattern, replacement, content)
    
    # Verificar si se hicieron cambios
    if modified_content != content:
        # Hacer backup
        backup_file = state_file + f".bak_iteracion_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(state_file, backup_file)
        print(f"  ✓ Backup creado en: {backup_file}")
        
        # Guardar el archivo modificado
        with open(state_file, 'w') as f:
            f.write(modified_content)
        print("  ✓ Archivo state.py modificado correctamente")
        print("  ✓ Se ha corregido la iteración sobre variables reactivas")
    else:
        # Intentar un método más directo
        direct_pattern = r"for i, pregunta in enumerate\(CuestionarioState\.cuestionario_preguntas\):"
        direct_replacement = """# Convertir la lista reactiva a una lista Python estándar
            has_preguntas = hasattr(CuestionarioState, "cuestionario_preguntas")
            preguntas_lista = list(CuestionarioState.cuestionario_preguntas) if has_preguntas else []
            
            # Ahora iteramos sobre la lista Python estándar
            for i, pregunta in enumerate(preguntas_lista):"""
        
        direct_content = content.replace(direct_pattern, direct_replacement)
        
        if direct_content != content:
            # Hacer backup
            backup_file = state_file + f".bak_iteracion_direct_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(state_file, backup_file)
            print(f"  ✓ Backup creado en: {backup_file}")
            
            # Guardar el archivo modificado
            with open(state_file, 'w') as f:
                f.write(direct_content)
            print("  ✓ Archivo state.py modificado con método directo")
            print("  ✓ Se ha corregido la iteración sobre variables reactivas")
        else:
            print("  ✗ No se pudo aplicar la corrección automática.")
            print("  ! RECOMENDACIÓN: Editar manualmente el archivo state.py")
            print("  ! Buscar y reemplazar la iteración sobre CuestionarioState.cuestionario_preguntas")
        
except Exception as e:
    print(f"  ✗ Error modificando state.py: {e}")

print("\n=== NUEVA REGLA PARA REFLEX ===")
print("No se puede iterar directamente sobre variables reactivas (listas, diccionarios, etc.)")
print("\nSOLUCIÓN CORRECTA:")
print("1. Verificar si el atributo existe: has_attr = hasattr(Class, 'attr')")
print("2. Convertir a lista Python: python_list = list(Class.attr) if has_attr else []")
print("3. Iterar sobre la lista Python: for item in python_list:")

print("\n=== CORRECCIÓN APLICADA ===")
print("La corrección asegura que se utilice una lista Python estándar para la iteración,")
print("no una variable reactiva de Reflex.")
print("\nPruebe de nuevo la descarga de PDF desde la aplicación.")
print("=== FIN DEL SCRIPT ===")
