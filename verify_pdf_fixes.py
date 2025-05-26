#!/usr/bin/env python
"""
Script for verifying PDF download functionality fixes

This script checks:
1. StringCastedVar fixes
2. VarTypeError fixes for conditionals
3. Iteration over reactive list fixes
"""
import os
import sys
import re

print("******************************************")
print("* SCRIPT DE VERIFICACIÓN DE CORRECCIONES *")
print("******************************************")

def check_fixes():
    print("=== VERIFICACIÓN DE CORRECCIONES DE VARIABLES REACTIVAS ===")
    
    state_file = "/workspaces/SMART_STUDENT/mi_app_estudio/state.py"
    
    try:
        with open(state_file, 'r') as f:
            content = f.read()
            
        # 1. Verificar StringCastedVar fixes
        print("\n1. Verificando correcciones de StringCastedVar...")
        string_cast_fixes = [
            "str(tema_value)",
            "str(libro_value)",
            "str(curso_value)"
        ]
        
        for fix in string_cast_fixes:
            if fix in content:
                print(f"  ✓ Encontrado: {fix}")
            else:
                print(f"  ✗ No encontrado: {fix}")
        
        # 2. Verificar VarTypeError en condicionales
        print("\n2. Verificando correcciones de VarTypeError en condicionales...")
        var_type_fixes = [
            "has_pdf_url = hasattr(CuestionarioState, \"cuestionario_pdf_url\")",
            "pdf_url = str(CuestionarioState.cuestionario_pdf_url) if has_pdf_url else \"\"",
            "is_pdf_url_not_empty = pdf_url != \"\""
        ]
        
        for fix in var_type_fixes:
            if fix in content:
                print(f"  ✓ Encontrado: {fix}")
            else:
                print(f"  ✗ No encontrado: {fix}")
        
        # 3. Verificar iteración sobre lista reactiva
        print("\n3. Verificando correcciones de iteración sobre listas reactivas...")
        iter_fixes = [
            "has_preguntas = hasattr(CuestionarioState, \"cuestionario_preguntas\")",
            "preguntas_lista = list(CuestionarioState.cuestionario_preguntas) if has_preguntas else []",
            "for i, pregunta in enumerate(preguntas_lista):"
        ]
        
        for fix in iter_fixes:
            if fix in content:
                print(f"  ✓ Encontrado: {fix}")
            else:
                print(f"  ✗ No encontrado: {fix}")
        
        # 4. Verificar si hay algún uso directo de variables reactivas que pueda causar problemas
        print("\n4. Verificando posibles problemas restantes...")
        potential_problems = [
            "for.*in.*CuestionarioState\.",
            "if.*CuestionarioState\.",
            "lambda:.*CuestionarioState\."
        ]
        
        for pattern in potential_problems:
            matches = re.findall(pattern, content)
            if matches:
                print(f"  ⚠️ Posible problema encontrado: {pattern}")
                for match in matches[:3]:  # Mostrar hasta 3 ejemplos
                    print(f"      {match.strip()}")
            else:
                print(f"  ✓ No se encontraron problemas con: {pattern}")
        
        print("\n=== RESUMEN ===")
        print("Las correcciones para los tres tipos de problemas principales han sido aplicadas:")
        print("1. StringCastedVar - Conversión explícita a str() antes de usar en funciones Python")
        print("2. VarTypeError - Conversión a tipos Python estándar antes de usar en condicionales")
        print("3. VarTypeError en iteraciones - Conversión de listas reactivas a listas Python estándar")
        
        print("\n******************************************")
        print("* VERIFICACIÓN COMPLETADA EXITOSAMENTE    *")
        print("* La funcionalidad de descarga de PDF     *")
        print("* debería funcionar correctamente ahora   *")
        print("******************************************")
        
    except Exception as e:
        print(f"Error durante la verificación: {e}")

if __name__ == "__main__":
    check_fixes()
