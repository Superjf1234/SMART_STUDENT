#!/usr/bin/env python
"""
Script para corregir problemas con lambda en rx.cond()
(Solución definitiva para errores de tipo en Reflex)
"""
import os
import re
import shutil
import datetime
import sys

print("=== SOLUCIÓN DEFINITIVA PARA LAMBDA EN RX.COND() ===")

# 1. Verificar el archivo state.py
print("\n1. Verificando y modificando state.py...")
project_root = '/workspaces/SMART_STUDENT'
state_file = os.path.join(project_root, 'mi_app_estudio', 'state.py')

try:
    with open(state_file, 'r') as f:
        content = f.read()
    
    # Patrón del código con error de lambda
    pattern = r"""                # Evaluar directamente la condición sin usar if con variable reactiva
                pdf_url_empty = CuestionarioState\.cuestionario_pdf_url == ""
                
                # En lugar de una función definida localmente, usamos directamente un lambda
                # Usamos rx\.cond para la bifurcación condicional basada en variables reactivas
                pdf_path = rx\.cond\(
                    ~pdf_url_empty,  # Si la URL no está vacía
                    lambda: str\(CuestionarioState\.cuestionario_pdf_url\)\.lstrip\('/'\),  # Procesar la URL
                    lambda: ""  # String vacío si la URL está vacía
                \)
                
                # Imprimimos un mensaje de depuración si la URL no está vacía
                if not pdf_url_empty:
                    print\(f"DEBUG: Usando PDF ya generado: \{CuestionarioState\.cuestionario_pdf_url\}"\)"""
    
    # Reemplazo corregido - solución más simple sin lambdas
    replacement = """                # En Reflex no podemos usar funciones ni lambdas con rx.cond directamente
                # En lugar de eso, definimos valores directamente y manejamos la lógica después
                pdf_url_not_empty = CuestionarioState.cuestionario_pdf_url != ""
                
                # Obtenemos la URL directamente sin usar rx.cond
                if pdf_url_not_empty:
                    print(f"DEBUG: Usando PDF ya generado: {CuestionarioState.cuestionario_pdf_url}")
                    # La URL es relativa, así que buscamos el archivo directamente
                    pdf_path = str(CuestionarioState.cuestionario_pdf_url).lstrip('/')
                else:
                    pdf_path = ""
                """
    
    # Aplicar reemplazo
    modified_content = re.sub(pattern, replacement, content)
    
    # Si el primer patrón no funciona, intenta con uno alternativo
    if modified_content == content:
        alt_pattern = r"""                # Evaluar directamente la condición sin usar if con variable reactiva
                pdf_url_empty = CuestionarioState\.cuestionario_pdf_url == ""
                
                # En lugar de una función definida localmente, usamos directamente un lambda
                # Usamos rx\.cond para la bifurcación condicional basada en variables reactivas
                pdf_path = rx\.cond\(
                    ~pdf_url_empty,  # Si la URL no está vacía
                    lambda: str\(CuestionarioState\.cuestionario_pdf_url\)\.lstrip\('/'\),  # Procesar la URL
                    lambda: ""  # String vacío si la URL está vacía
                \)"""
        
        alt_replacement = """                # En Reflex no podemos usar funciones ni lambdas con rx.cond directamente
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
        
        modified_content = re.sub(alt_pattern, alt_replacement, content)
    
    # Verificar si se hicieron cambios
    if modified_content != content:
        # Hacer backup
        backup_file = state_file + f".bak_lambda_final_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
        shutil.copy2(state_file, backup_file)
        print(f"  ✓ Backup creado en: {backup_file}")
        
        # Guardar el archivo modificado
        with open(state_file, 'w') as f:
            f.write(modified_content)
        print("  ✓ Archivo state.py modificado correctamente")
        print("  ✓ Se ha corregido el uso de lambda en rx.cond()")
    else:
        # Edición manual directa
        print("  ✗ No se encontró el patrón exacto. Aplicando corrección manual...")
        # Busca de manera más general
        pattern_manual = r"pdf_path = rx\.cond\(.+?lambda:.+?\)"
        
        # Reemplazo directo sin rx.cond
        replacement_manual = """                # En Reflex no podemos usar funciones ni lambdas con rx.cond directamente
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
        
        # Tratamos de aplicar el patrón manual
        manual_modified = re.sub(pattern_manual, replacement_manual, content, flags=re.DOTALL)
        
        if manual_modified != content:
            # Hacer backup
            backup_file = state_file + f".bak_manual_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
            shutil.copy2(state_file, backup_file)
            print(f"  ✓ Backup creado en: {backup_file}")
            
            # Guardar el archivo modificado
            with open(state_file, 'w') as f:
                f.write(manual_modified)
            print("  ✓ Archivo state.py modificado con método alternativo")
            print("  ✓ Se ha corregido el uso de lambda en rx.cond()")
        else:
            print("  ✗ No se pudo aplicar la corrección automática.")
            print("  ! RECOMENDACIÓN: Editar manualmente el archivo state.py")
            print("  ! Sustituir el bloque que usa rx.cond() con lambdas por una lógica simple if/else")
        
except Exception as e:
    print(f"  ✗ Error modificando state.py: {e}")

print("\n=== LECCIONES SOBRE RX.COND() EN REFLEX ===")
print("1. rx.cond() NO admite funciones ni lambdas como argumentos en esta versión de Reflex")
print("2. Para código condicional complejo, es mejor usar lógica if/else tradicional")
print("3. Usar rx.cond() solo para expresiones simples que no requieran funciones")
print("4. Alternativa: usar if/else con variables no reactivas (booleanas Python normales)")

print("\n=== SOLUCIÓN APLICADA ===")
print("La solución simplifica la lógica eliminando rx.cond() en favor de if/else simple.")
print("Pruebe de nuevo la descarga de PDF desde la aplicación.")
print("=== FIN DEL SCRIPT ===")
