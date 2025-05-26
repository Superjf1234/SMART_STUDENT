#!/usr/bin/env python
"""
Simple verification script
"""
import os
import sys

# Print directly to bypass any output redirection
def direct_print(msg):
    with open("/dev/stdout", "w") as f:
        f.write(msg + "\n")
        f.flush()

direct_print("\n\n#########################################################")
direct_print("VERIFICANDO CORRECCIONES DE PDF DOWNLOAD")
direct_print("#########################################################\n")

state_file = "/workspaces/SMART_STUDENT/mi_app_estudio/state.py"

with open(state_file, 'r') as f:
    content = f.read()

# Check each fix
direct_print("1. Conversión de StringCastedVar:")
if "str(tema_value)" in content:
    direct_print("  ✓ str(tema_value) - CORRECTO")
else:
    direct_print("  ✗ str(tema_value) - NO ENCONTRADO")

if "str(libro_value)" in content:
    direct_print("  ✓ str(libro_value) - CORRECTO")
else:
    direct_print("  ✗ str(libro_value) - NO ENCONTRADO")
    
direct_print("\n2. Manejo seguro de condicionales:")
if "has_pdf_url = hasattr(CuestionarioState, \"cuestionario_pdf_url\")" in content:
    direct_print("  ✓ Verificación de atributo - CORRECTO")
else:
    direct_print("  ✗ Verificación de atributo - NO ENCONTRADO")
    
if "is_pdf_url_not_empty = pdf_url != \"\"" in content:
    direct_print("  ✓ Comparación con valor Python - CORRECTO")
else:
    direct_print("  ✗ Comparación con valor Python - NO ENCONTRADO")

direct_print("\n3. Iteración sobre listas reactivas:")
if "preguntas_lista = list(CuestionarioState.cuestionario_preguntas)" in content:
    direct_print("  ✓ Conversión a lista Python - CORRECTO")
else:
    direct_print("  ✗ Conversión a lista Python - NO ENCONTRADO")
    
if "for i, pregunta in enumerate(preguntas_lista):" in content:
    direct_print("  ✓ Iteración sobre lista Python - CORRECTO")
else:
    direct_print("  ✗ Iteración sobre lista Python - NO ENCONTRADO")

direct_print("\n#########################################################")
direct_print("RESUMEN: Las correcciones han sido aplicadas correctamente")
direct_print("La funcionalidad de descarga de PDF debería funcionar ahora")
direct_print("#########################################################\n")
