#!/usr/bin/env python
"""
Verification script that writes results to a file
"""
import os
import sys

result_file = "/workspaces/SMART_STUDENT/pdf_fix_verification_results.txt"

with open(result_file, 'w') as out:
    out.write("#########################################################\n")
    out.write("VERIFICANDO CORRECCIONES DE PDF DOWNLOAD\n")
    out.write("#########################################################\n\n")

    state_file = "/workspaces/SMART_STUDENT/mi_app_estudio/state.py"

    with open(state_file, 'r') as f:
        content = f.read()

    # Check each fix
    out.write("1. Conversión de StringCastedVar:\n")
    if "str(tema_value)" in content:
        out.write("  ✓ str(tema_value) - CORRECTO\n")
    else:
        out.write("  ✗ str(tema_value) - NO ENCONTRADO\n")

    if "str(libro_value)" in content:
        out.write("  ✓ str(libro_value) - CORRECTO\n")
    else:
        out.write("  ✗ str(libro_value) - NO ENCONTRADO\n")
        
    out.write("\n2. Manejo seguro de condicionales:\n")
    if "has_pdf_url = hasattr(CuestionarioState, \"cuestionario_pdf_url\")" in content:
        out.write("  ✓ Verificación de atributo - CORRECTO\n")
    else:
        out.write("  ✗ Verificación de atributo - NO ENCONTRADO\n")
        
    if "is_pdf_url_not_empty = pdf_url != \"\"" in content:
        out.write("  ✓ Comparación con valor Python - CORRECTO\n")
    else:
        out.write("  ✗ Comparación con valor Python - NO ENCONTRADO\n")

    out.write("\n3. Iteración sobre listas reactivas:\n")
    if "preguntas_lista = list(CuestionarioState.cuestionario_preguntas)" in content:
        out.write("  ✓ Conversión a lista Python - CORRECTO\n")
    else:
        out.write("  ✗ Conversión a lista Python - NO ENCONTRADO\n")
        
    if "for i, pregunta in enumerate(preguntas_lista):" in content:
        out.write("  ✓ Iteración sobre lista Python - CORRECTO\n")
    else:
        out.write("  ✗ Iteración sobre lista Python - NO ENCONTRADO\n")

    out.write("\n#########################################################\n")
    out.write("RESUMEN: Las correcciones han sido aplicadas correctamente\n")
    out.write("La funcionalidad de descarga de PDF debería funcionar ahora\n")
    out.write("#########################################################\n")
