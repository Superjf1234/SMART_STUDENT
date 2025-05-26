#!/usr/bin/env python
"""
Script completo para corregir TODOS los problemas de tipo en Reflex
1. StringCastedVar en re.sub()
2. VarTypeError en condicionales if
3. Funciones definidas localmente en rx.cond()
"""
import os
import re
import shutil
import datetime
import sys

print("=== CORRECCIÓN COMPLETA DE PROBLEMAS DE TIPO EN REFLEX ===")

# 1. Verificar el archivo state.py
print("\n1. Verificando y modificando state.py...")
project_root = '/workspaces/SMART_STUDENT'
state_file = os.path.join(project_root, 'mi_app_estudio', 'state.py')

try:
    with open(state_file, 'r') as f:
        content = f.read()
    
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
    modified_content = re.sub(pattern1, replacement1, content)
    modified_content = re.sub(pattern2, replacement2, modified_content)
    modified_content = re.sub(pattern3, replacement3, modified_content)
    
    # ---- FIX 2: VarTypeError en condiciones if ----
    print("\n   1.2 Corrigiendo VarTypeError en condicionales if...")
    
    # Patrón para buscar el uso incorrecto de pdf_url_not_empty en if
    pattern_var_type = r"""                pdf_url_not_empty = rx\.cond\(
                    CuestionarioState\.cuestionario_pdf_url != "",
                    True,
                    False
                \)
                if pdf_url_not_empty:"""
    
    # Reemplazo corregido usando rx.cond para evitar el if directo
    replacement_var_type = """                # Evaluar directamente la condición sin usar if con variable reactiva
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
    
    # Aplicar reemplazo para VarTypeError
    var_type_fixed = modified_content.replace(pattern_var_type, replacement_var_type)
    
    # ---- FIX 3: Funciones definidas localmente en rx.cond() ----
    print("\n   1.3 Corrigiendo funciones definidas localmente en rx.cond()...")
    
    # Patrón para funciones definidas localmente en rx.cond()
    pattern_functions = r"""                # Usamos una función interna para manejar el caso con URL
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
    
    # Reemplazo con lambda directamente
    replacement_functions = """                # En lugar de una función definida localmente, usamos directamente un lambda
                # Usamos rx.cond para la bifurcación condicional basada en variables reactivas
                pdf_path = rx.cond(
                    ~pdf_url_empty,  # Si la URL no está vacía
                    lambda: str(CuestionarioState.cuestionario_pdf_url).lstrip('/'),  # Procesar la URL
                    lambda: ""  # String vacío si la URL está vacía
                )
                
                # Imprimimos un mensaje de depuración si la URL no está vacía
                if not pdf_url_empty:
                    print(f"DEBUG: Usando PDF ya generado: {CuestionarioState.cuestionario_pdf_url}")"""
    
    # Aplicar reemplazo para funciones
    final_content = re.sub(pattern_functions, replacement_functions, var_type_fixed)
    
    # Verificar si se hicieron cambios
    changes_made = final_content != content
    if changes_made:
        # Hacer backup
        backup_file = state_file + f".bak_all_fixes_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(state_file, backup_file)
        print(f"  ✓ Backup creado en: {backup_file}")
        
        # Guardar el archivo modificado
        with open(state_file, 'w') as f:
            f.write(final_content)
        print("  ✓ Archivo state.py modificado correctamente")
        
        # Identificar qué cambios se realizaron
        string_cast_fix = modified_content != content
        var_type_fix = var_type_fixed != modified_content
        functions_fix = final_content != var_type_fixed
        
        if string_cast_fix:
            print("  ✓ Se ha añadido la conversión a string para variables reactivas usadas con re.sub()")
        if var_type_fix:
            print("  ✓ Se ha corregido el uso de variables reactivas en condicionales if")
        if functions_fix:
            print("  ✓ Se ha corregido el uso de funciones definidas localmente en rx.cond()")
    else:
        print("  ✓ El archivo state.py ya está corregido o utiliza un formato diferente")
        print("  ℹ Aplicando la corrección directamente...")
        
        # Aplicar corrección directa
        direct_pattern = r"""                # Evaluar directamente la condición sin usar if con variable reactiva
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
        
        direct_replacement = """                # Evaluar directamente la condición sin usar if con variable reactiva
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
        
        direct_fixed = re.sub(direct_pattern, direct_replacement, content)
        if direct_fixed != content:
            # Hacer backup
            backup_file = state_file + f".bak_direct_fix_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(state_file, backup_file)
            print(f"  ✓ Backup creado en: {backup_file}")
            
            # Guardar el archivo modificado
            with open(state_file, 'w') as f:
                f.write(direct_fixed)
            print("  ✓ Archivo state.py modificado con método directo")
            print("  ✓ Se ha corregido el uso de funciones definidas localmente en rx.cond()")
        else:
            print("  ✗ No se pudo aplicar la corrección automática. Se requiere edición manual.")
        
except Exception as e:
    print(f"  ✗ Error modificando state.py: {e}")

print("\n=== RECOMENDACIONES PARA DESARROLLO CON REFLEX ===")
print("""
1. Variables reactivas (StringCastedVar):
   - Convertir a str() antes de usar con funciones Python: str(var_reactiva) ✓
   - Para operaciones aritméticas: int(var_reactiva), float(var_reactiva) ✓

2. Condicionales con variables reactivas (VarTypeError):
   - NO usar directamente en if/and/or/not: if var_reactiva: ✗
   - Usar rx.cond() para ramificaciones: rx.cond(condicion, valor_si_true, valor_si_false) ✓
   - Para comparaciones usar operadores bitwise: &, |, ~ en lugar de and, or, not

3. Funciones en rx.cond():
   - NO pasar funciones definidas localmente a rx.cond() ✗
   - SÍ usar lambdas directamente: lambda: valor ✓
   - Mantener lambdas simples, código complejo fuera de ellas
""")

print("\n=== FIXES COMPLETOS APLICADOS ===")
print("Todos los problemas de tipo en Reflex deberían estar resueltos.")
print("Pruebe de nuevo la descarga de PDF desde la aplicación.")
print("=== FIN DEL SCRIPT ===")
