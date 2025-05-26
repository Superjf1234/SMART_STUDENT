#!/usr/bin/env python
"""
Test script to verify the fix for reactive variable iteration

This script simulates the problematic section of the code with a mock of the reactive
variables to ensure that our fix will work correctly.
"""

import sys
import os
import re
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

print("=== TEST DE ITERACIÓN SOBRE VARIABLES REACTIVAS ===")

# Importar las funciones de utilidad
try:
    from mi_app_estudio.state import get_safe_var_value, get_safe_var_list
    print("✅ Importación exitosa de funciones de utilidad")
except ImportError as e:
    print(f"❌ Error importando funciones de utilidad: {e}")
    sys.exit(1)

# Clase Mock para simular variable reactiva
class MockVar:
    def __init__(self, value):
        self._var_value = value
    
    def __str__(self):
        return f"<reflex.Var>-12345678</reflex.Var>{str(self._var_value)}"

# Clase Mock para simular CuestionarioState
class MockCuestionarioState:
    cuestionario_preguntas = MockVar([
        {"pregunta": "Pregunta 1", "explicacion": "Explicación 1", "correcta": "a"},
        {"pregunta": "Pregunta 2", "explicacion": "Explicación 2", "correcta": "b"},
        {"pregunta": "Pregunta 3", "explicacion": "Explicación 3", "correcta": "c"}
    ])
    
    cuestionario_tema = MockVar("Sistema Respiratorio")
    cuestionario_libro = MockVar("Libro de Ciencias")
    cuestionario_curso = MockVar("5to Básico")
    cuestionario_pdf_url = MockVar("/assets/pdfs/test_pdf_12345.pdf")

# Función de prueba para simular la parte problemática del código
def test_iteracion_reactiva():
    print("\n1. Probando iteración sobre lista reactiva:")
    try:
        # Obtener la lista de manera segura
        preguntas_lista = get_safe_var_list(MockCuestionarioState.cuestionario_preguntas, [])
        
        # Iterar sobre la lista
        for i, pregunta in enumerate(preguntas_lista):
            print(f"  ✅ Pregunta {i+1}: {pregunta['pregunta']}")
        
        print("  ✅ Iteración exitosa sobre lista reactiva convertida")
        return True
    except Exception as e:
        print(f"  ❌ Error durante la iteración: {e}")
        return False

# Función para probar la conversión de variables reactivas a strings
def test_conversion_vars():
    print("\n2. Probando conversión de variables reactivas a strings:")
    try:
        # Obtener valores de manera segura
        tema_str = get_safe_var_value(MockCuestionarioState.cuestionario_tema, "tema")
        libro_str = get_safe_var_value(MockCuestionarioState.cuestionario_libro, "libro")
        curso_str = get_safe_var_value(MockCuestionarioState.cuestionario_curso, "curso")
        
        # Usar en re.sub
        s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_str)[:50]
        s_lib = re.sub(r'[\\/*?:"<>|]', "", libro_str)[:50]
        s_cur = re.sub(r'[\\/*?:"<>|]', "", curso_str)[:50]
        
        print(f"  ✅ Tema: {s_tema}")
        print(f"  ✅ Libro: {s_lib}")
        print(f"  ✅ Curso: {s_cur}")
        
        return True
    except Exception as e:
        print(f"  ❌ Error durante la conversión: {e}")
        return False

# Función para probar la obtención segura de URL del PDF
def test_pdf_url():
    print("\n3. Probando obtención segura de URL del PDF:")
    try:
        # Obtener URL de manera segura
        pdf_url = get_safe_var_value(MockCuestionarioState.cuestionario_pdf_url, "")
        
        # Verificar contenido
        if pdf_url:
            print(f"  ✅ URL del PDF: {pdf_url}")
            return True
        else:
            print("  ❌ URL del PDF vacía")
            return False
    except Exception as e:
        print(f"  ❌ Error obteniendo URL del PDF: {e}")
        return False

# Ejecutar las pruebas
if __name__ == "__main__":
    success_iter = test_iteracion_reactiva()
    success_conv = test_conversion_vars()
    success_pdf = test_pdf_url()
    
    # Resumen
    print("\n=== RESUMEN DE PRUEBAS ===")
    print(f"Iteración sobre lista reactiva: {'✅ EXITOSA' if success_iter else '❌ FALLIDA'}")
    print(f"Conversión de variables reactivas: {'✅ EXITOSA' if success_conv else '❌ FALLIDA'}")
    print(f"Obtención segura de URL del PDF: {'✅ EXITOSA' if success_pdf else '❌ FALLIDA'}")
    
    if success_iter and success_conv and success_pdf:
        print("\n✅✅✅ TODAS LAS PRUEBAS EXITOSAS ✅✅✅")
        print("La solución implementada debería resolver el problema de VarTypeError en la descarga de PDF")
    else:
        print("\n❌❌❌ ALGUNAS PRUEBAS FALLARON ❌❌❌")
        print("Es necesario revisar la implementación")
