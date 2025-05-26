#!/usr/bin/env python
"""
Script completo para corregir problemas de tipo en Reflex (StringCastedVar y VarTypeError)
"""
import os
import re
import shutil
import datetime
import sys

print("=== CORRECCIÓN DE PROBLEMAS DE TIPO EN REFLEX ===")

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
    
    # Reemplazo correcto usando rx.cond para evitar el if directo
    replacement_var_type = """                # Evaluar directamente la condición sin usar if con variable reactiva
                pdf_url_empty = CuestionarioState.cuestionario_pdf_url == ""
                
                # Usamos una función interna para manejar el caso con URL
                def process_with_url():
                    # Si ya hay un PDF generado, usamos esa URL
                    print(f"DEBUG: Usando PDF ya generado: {CuestionarioState.cuestionario_pdf_url}")
                    # La URL es relativa, así que buscamos el archivo directamente
                    return str(CuestionarioState.cuestionario_pdf_url).lstrip('/')
                
                # Usamos rx.cond para la bifurcación condicional basada en variables reactivas
                pdf_path = rx.cond(
                    ~pdf_url_empty,  # Si la URL no está vacía
                    process_with_url,  # Procesar la URL
                    lambda: ""  # String vacío si la URL está vacía
                )
                
                # Continuamos con el flujo normal, verificando si pdf_path tiene contenido
                if pdf_path and os.path.exists(pdf_path) and os.path.isfile(pdf_path):"""
    
    # Aplicar reemplazo para VarTypeError
    final_content = modified_content.replace(pattern_var_type, replacement_var_type)
    
    # Verificar si se hicieron cambios
    changes_made = final_content != content
    if changes_made:
        # Hacer backup
        backup_file = state_file + f".bak_complete_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(state_file, backup_file)
        print(f"  ✓ Backup creado en: {backup_file}")
        
        # Guardar el archivo modificado
        with open(state_file, 'w') as f:
            f.write(final_content)
        print("  ✓ Archivo state.py modificado correctamente")
        
        # Identificar qué cambios se realizaron
        string_cast_fix = modified_content != content
        var_type_fix = final_content != modified_content
        
        if string_cast_fix:
            print("  ✓ Se ha añadido la conversión a string para variables reactivas usadas con re.sub()")
        if var_type_fix:
            print("  ✓ Se ha corregido el uso de variables reactivas en condicionales if")
    else:
        print("  ✓ El archivo state.py ya está corregido o utiliza un formato diferente")
        
except Exception as e:
    print(f"  ✗ Error modificando state.py: {e}")

print("\n=== RECOMENDACIONES PARA DESARROLLO CON REFLEX ===")
print("1. Variables reactivas (Vars) y operaciones:")
print("   - Convierta a str() antes de usar variables reactivas con funciones estándar de Python")
print("   - Ejemplo: re.sub(pattern, repl, str(mi_var_reactiva)) ✓")

print("\n2. Condicionales con variables reactivas:")
print("   - NO use directamente en if/and/or/not: if mi_var_reactiva: ✗")
print("   - Use rx.cond() para ramificaciones condicionales: rx.cond(condicion, valor_si_true, valor_si_false) ✓")
print("   - Para comparaciones use operadores bitwise: &, |, ~ en lugar de and, or, not")
print("   - Ejemplo: if (var_a & var_b): ✗  -> rx.cond((var_a & var_b), func_true, func_false) ✓")

print("\n3. Manipulación segura de valores reactivos:")
print("   - Evite operaciones directas, mejor use funciones que se ejecutan a través de rx.cond")
print("   - Si necesita un valor no reactivo, convierta a un tipo Python: str(), int(), etc.")
print("   - Para strings use .format() o f-strings con conversión previa: f\"{str(var)}\" ✓")

print("\n=== FIX COMPLETO APLICADO ===")
print("Los problemas de tipo en Reflex deberían estar resueltos.")
print("Pruebe de nuevo la descarga de PDF desde la aplicación.")
print("=== FIN DEL SCRIPT ===")
