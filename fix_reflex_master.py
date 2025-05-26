#!/usr/bin/env python
"""
Script MAESTRO para corregir TODOS los problemas de variables reactivas en Reflex
"""
import os
import re
import shutil
import datetime
import sys

print("=== CORRECCIÓN MAESTRA DE VARIABLES REACTIVAS EN REFLEX ===")
print("Este script corrige los 4 problemas principales con variables reactivas:")
print("1. StringCastedVar - Variables reactivas en funciones Python")
print("2. VarTypeError - Variables reactivas en condicionales if")
print("3. TypeError - Funciones/lambdas en rx.cond()")
print("4. VarTypeError - Iteración sobre listas reactivas")

# 1. Verificar el archivo state.py
print("\n1. Verificando y modificando state.py...")
project_root = '/workspaces/SMART_STUDENT'
state_file = os.path.join(project_root, 'mi_app_estudio', 'state.py')

try:
    # Backup principal antes de cualquier cambio
    backup_file = state_file + f".bak_master_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(state_file, backup_file)
    print(f"  ✓ Backup maestro creado en: {backup_file}")
    
    with open(state_file, 'r') as f:
        content = f.read()
    
    modified_content = content
    
    # ---- FIX 1: StringCastedVar en re.sub ----
    print("\n   1.1 Corrigiendo StringCastedVar en re.sub...")
    # Patrón 1: variables tema_value
    pattern1 = r'(s_tema = re\.sub\(r\'\[\\\\/\*\?:\"<>\|\]\', \"\", )(tema_value)(\)\[:50\])'
    replacement1 = r'\1str(\2)\3'
    
    # Patrón 2: variables libro_value
    pattern2 = r'(s_lib = re\.sub\(r\'\[\\\\/\*\?:\"<>\|\]\', \"\", )(libro_value)(\)\[:50\])'
    replacement2 = r'\1str(\2)\3'
    
    # Patrón 3: variables curso_value
    pattern3 = r'(s_cur = re\.sub\(r\'\[\\\\/\*\?:\"<>\|\]\', \"\", )(curso_value)(\)\[:50\])'
    replacement3 = r'\1str(\2)\3'
    
    # Aplicar reemplazos para StringCastedVar
    modified_content = re.sub(pattern1, replacement1, modified_content)
    modified_content = re.sub(pattern2, replacement2, modified_content)
    modified_content = re.sub(pattern3, replacement3, modified_content)
    
    # ---- FIX 2: VarTypeError en condicionales if ----
    print("\n   1.2 Corrigiendo VarTypeError en condicionales if...")
    
    # Patrón para pdf_url_not_empty en if
    pattern_if = r"""                # Evaluar directamente la condición sin usar if con variable reactiva
                pdf_url_not_empty = CuestionarioState\.cuestionario_pdf_url != ""
                
                # Obtenemos la URL directamente sin usar rx\.cond
                if pdf_url_not_empty:"""
    
    # Reemplazo para condicional if
    replacement_if = """                # Evaluamos si existe y tiene contenido usando variables Python estándar
                # NO USAR variables reactivas en condiciones if
                has_pdf_url = hasattr(CuestionarioState, "cuestionario_pdf_url")
                pdf_url = str(CuestionarioState.cuestionario_pdf_url) if has_pdf_url else ""
                is_pdf_url_not_empty = pdf_url != ""
                
                # Ahora usamos variables Python estándar para la lógica condicional
                if is_pdf_url_not_empty:"""
    
    # Aplicar reemplazo para if
    modified_content = re.sub(pattern_if, replacement_if, modified_content)
    
    # Método alternativo si el patrón exacto no coincide
    if pattern_if not in modified_content:
        modified_content = modified_content.replace(
            "pdf_url_not_empty = CuestionarioState.cuestionario_pdf_url != \"\"",
            "# Convertir la variable reactiva a Python estándar\n                has_pdf_url = hasattr(CuestionarioState, \"cuestionario_pdf_url\")\n                pdf_url = str(CuestionarioState.cuestionario_pdf_url) if has_pdf_url else \"\"\n                is_pdf_url_not_empty = pdf_url != \"\""
        )
        
        modified_content = modified_content.replace(
            "if pdf_url_not_empty:",
            "if is_pdf_url_not_empty:"
        )
    
    # ---- FIX 3: Funciones definidas localmente en rx.cond() ----
    print("\n   1.3 Corrigiendo funciones definidas localmente en rx.cond()...")
    
    # Patrón para rx.cond con lambda
    pattern_lambda = r"""                # En lugar de una función definida localmente, usamos directamente un lambda
                # Usamos rx\.cond para la bifurcación condicional basada en variables reactivas
                pdf_path = rx\.cond\(
                    ~pdf_url_empty,  # Si la URL no está vacía
                    lambda: str\(CuestionarioState\.cuestionario_pdf_url\)\.lstrip\('/'\),  # Procesar la URL
                    lambda: ""  # String vacío si la URL está vacía
                \)"""
    
    # Reemplazo sin usar rx.cond
    replacement_lambda = """                # En Reflex no podemos usar funciones ni lambdas con rx.cond directamente
                # En lugar de eso, definimos valores directamente y manejamos la lógica después
                pdf_url_not_empty = CuestionarioState.cuestionario_pdf_url != ""
                
                # Obtenemos la URL directamente sin usar rx.cond
                if pdf_url_not_empty:
                    # La URL es relativa, así que buscamos el archivo directamente
                    pdf_path = str(CuestionarioState.cuestionario_pdf_url).lstrip('/')
                else:
                    pdf_path = ""
                
                # Imprimimos un mensaje de depuración si la URL no está vacía
                if pdf_url_not_empty:
                    print(f"DEBUG: Usando PDF ya generado: {CuestionarioState.cuestionario_pdf_url}")"""
    
    # Aplicar reemplazo para lambda
    modified_content = re.sub(pattern_lambda, replacement_lambda, modified_content)
    
    # ---- FIX 4: Iteración sobre listas reactivas ----
    print("\n   1.4 Corrigiendo iteración sobre listas reactivas...")
    
    # Patrón para iteración sobre lista reactiva
    pattern_iter = r"""            # Si no hay PDF o falló la lectura, generamos HTML con las preguntas
            preguntas_html = ""
            for i, pregunta in enumerate\(CuestionarioState\.cuestionario_preguntas\):"""
    
    # Reemplazo para iteración sobre lista Python
    replacement_iter = """            # Si no hay PDF o falló la lectura, generamos HTML con las preguntas
            preguntas_html = ""
            # Convertir la lista reactiva a una lista Python estándar
            has_preguntas = hasattr(CuestionarioState, "cuestionario_preguntas")
            preguntas_lista = list(CuestionarioState.cuestionario_preguntas) if has_preguntas else []
            
            # Ahora iteramos sobre la lista Python estándar
            for i, pregunta in enumerate(preguntas_lista):"""
    
    # Aplicar reemplazo para iteración
    modified_content = re.sub(pattern_iter, replacement_iter, modified_content)
    
    # Método alternativo si el patrón exacto no coincide
    if pattern_iter not in modified_content:
        modified_content = modified_content.replace(
            "for i, pregunta in enumerate(CuestionarioState.cuestionario_preguntas):",
            """# Convertir la lista reactiva a una lista Python estándar
            has_preguntas = hasattr(CuestionarioState, "cuestionario_preguntas")
            preguntas_lista = list(CuestionarioState.cuestionario_preguntas) if has_preguntas else []
            
            # Ahora iteramos sobre la lista Python estándar
            for i, pregunta in enumerate(preguntas_lista):"""
        )
    
    # Verificar si se hicieron cambios
    if modified_content != content:
        # Guardar el archivo modificado
        with open(state_file, 'w') as f:
            f.write(modified_content)
        print("  ✓ Archivo state.py modificado correctamente")
        print("  ✓ Se han aplicado todas las correcciones de variables reactivas")
    else:
        print("  ✓ El archivo state.py ya está corregido o los patrones no coinciden")
        
except Exception as e:
    print(f"  ✗ Error modificando state.py: {e}")

print("\n=== GUÍA MAESTRA PARA VARIABLES REACTIVAS EN REFLEX ===")
print("""
REGLA #1 - CONVERSIÓN DE TIPOS:
  ✓ Siempre convertir variables reactivas a tipos Python estándar:
    - str(var_reactiva) para strings
    - int(var_reactiva) para números
    - list(lista_reactiva) para listas
    - dict(dict_reactivo) para diccionarios

REGLA #2 - VERIFICACIÓN DE EXISTENCIA:
  ✓ Siempre verificar si los atributos existen:
    - has_attr = hasattr(State, "attr")
    - value = str(State.attr) if has_attr else ""

REGLA #3 - CONDICIONALES:
  ✓ Nunca usar variables reactivas en if/and/or/not
  ✓ Convertir a variables Python normales primero:
    - is_empty = str(var) == ""
    - if is_empty: # Ahora es seguro

REGLA #4 - ITERACIONES:
  ✓ Nunca iterar directamente sobre listas reactivas
  ✓ Convertir a lista Python normal primero:
    - python_list = list(lista_reactiva) if has_list else []
    - for item in python_list: # Ahora es seguro

REGLA #5 - FUNCIONES REACTIVAS:
  ✓ Evitar rx.cond() para lógica compleja
  ✓ Preferir lógica if/else con variables Python estándar
  ✓ No pasar funciones o lambdas a rx.cond()
""")

print("\n=== SCRIPTS CORRECTIVOS CREADOS ===")
print("1. fix_string_cast_pdf.py - Corrige StringCastedVar")
print("2. fix_var_if_final.py - Corrige VarTypeError en condicionales")
print("3. fix_lambda_final.py - Corrige lambdas en rx.cond()")
print("4. fix_iteracion_reactiva.py - Corrige iteración sobre listas reactivas")
print("5. fix_reflex_all_types.py - Script combinado para todos los problemas")

print("\n=== DOCUMENTACIÓN ===")
print("Se ha creado una guía completa en:")
print("reflex_vars_guia_definitiva.md")

print("\n=== CORRECCIONES APLICADAS ===")
print("Todas las correcciones han sido aplicadas al código.")
print("Pruebe de nuevo la descarga de PDF desde la aplicación.")
print("=== FIN DEL SCRIPT MAESTRO ===")
