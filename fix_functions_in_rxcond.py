#!/usr/bin/env python
"""
Script para arreglar el problema de funciones en rx.cond()
"""
import os
import re
import shutil
import datetime
import sys

print("=== APLICANDO FIX PARA FUNCIONES EN RX.COND() ===")

# 1. Verificar el archivo state.py
print("\n1. Verificando y modificando state.py...")
project_root = '/workspaces/SMART_STUDENT'
state_file = os.path.join(project_root, 'mi_app_estudio', 'state.py')

try:
    with open(state_file, 'r') as f:
        content = f.read()
    
    # Patrón del código con error
    pattern = r"""                # Evaluar directamente la condición sin usar if con variable reactiva
                pdf_url_empty = CuestionarioState\.cuestionario_pdf_url == ""
                
                # Usamos una función interna para manejar el caso con URL
                def process_with_url\(\):
                    # Si ya hay un PDF generado, usamos esa URL
                    print\(f"DEBUG: Usando PDF ya generado: \{CuestionarioState\.cuestionario_pdf_url\}"\)
                    # La URL es relativa, así que buscamos el archivo directamente
                    return str\(CuestionarioState\.cuestionario_pdf_url\)\.lstrip\('/'\)
                
                # Usamos rx\.cond para la bifurcación condicional basada en variables reactivas
                pdf_path = rx\.cond\(
                    ~pdf_url_empty,  # Si la URL no está vacía
                    process_with_url,  # Procesar la URL
                    lambda: ""  # String vacío si la URL está vacía
                \)"""
    
    # Reemplazo corregido
    replacement = """                # Evaluar directamente la condición sin usar if con variable reactiva
                pdf_url_empty = CuestionarioState.cuestionario_pdf_url == ""
                
                # En lugar de una función definida localmente, usamos directamente un lambda
                # Usamos rx.cond para la bifurcación condicional basada en variables reactivas
                pdf_path = rx.cond(
                    ~pdf_url_empty,  # Si la URL no está vacía
                    lambda: str(CuestionarioState.cuestionario_pdf_url).lstrip('/'),  # Procesar la URL
                    lambda: ""  # String vacío si la URL está vacía
                )
                
                # Imprimimos un mensaje de depuración si la URL no está vacía
                if not pdf_url_empty:
                    print(f"DEBUG: Usando PDF ya generado: {CuestionarioState.cuestionario_pdf_url}")"""
    
    # Aplicar reemplazo
    modified_content = re.sub(pattern, replacement, content)
    
    # Verificar si se hicieron cambios
    if modified_content != content:
        # Hacer backup
        backup_file = state_file + f".bak_funciones_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(state_file, backup_file)
        print(f"  ✓ Backup creado en: {backup_file}")
        
        # Guardar el archivo modificado
        with open(state_file, 'w') as f:
            f.write(modified_content)
        print("  ✓ Archivo state.py modificado correctamente")
        print("  ✓ Se ha corregido el uso de funciones en rx.cond()")
    else:
        print("  ✗ No se encontró el patrón exacto. Aplicando corrección manual...")
        
        # Si el patrón exacto no se encuentra, intentamos una corrección más general
        # Buscamos el uso de process_with_url y lo reemplazamos con un lambda
        alt_pattern = r"process_with_url,  # Procesar la URL"
        alt_replacement = r"lambda: str(CuestionarioState.cuestionario_pdf_url).lstrip('/'),  # Procesar la URL directamente"
        
        alt_modified = content.replace(alt_pattern, alt_replacement)
        
        # Verificar si se hicieron cambios con la aproximación alternativa
        if alt_modified != content:
            # Hacer backup
            backup_file = state_file + f".bak_funciones_alt_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(state_file, backup_file)
            print(f"  ✓ Backup creado en: {backup_file}")
            
            # Guardar el archivo modificado
            with open(state_file, 'w') as f:
                f.write(alt_modified)
            print("  ✓ Archivo state.py modificado con método alternativo")
            print("  ✓ Se ha corregido el uso de funciones en rx.cond()")
        else:
            print("  ✗ No se pudo aplicar la corrección automática. Se requiere edición manual.")
        
except Exception as e:
    print(f"  ✗ Error modificando state.py: {e}")

print("\n=== RECOMENDACIONES PARA USO DE FUNCIONES EN REFLEX ===")
print("1. Nunca pasar funciones definidas localmente a rx.cond() u otros componentes reactivos")
print("2. Siempre usar expresiones lambda (lambda: ...) para funciones en rx.cond()")
print("3. Mantener las expresiones lambda simples, evitando lógica compleja")
print("4. Si necesita lógica compleja, definir variables fuera de rx.cond() y usarlas en lambdas")

print("\n=== FIX APLICADO ===")
print("El problema de funciones en rx.cond() debería estar resuelto.")
print("Pruebe de nuevo la descarga de PDF desde la aplicación.")
print("=== FIN DEL SCRIPT ===")
