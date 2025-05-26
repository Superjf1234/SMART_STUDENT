#!/usr/bin/env python
"""
Script de prueba para verificar la corrección del error StringCastedVar
"""
import os
import re
import sys
import reflex as rx

# Simulación de las condiciones que causan el error
class MockCuestionarioState:
    cuestionario_tema = "Test Tema"
    cuestionario_libro = "Test Libro" 
    cuestionario_curso = "Test Curso"

# Prueba del caso que fallaba
def test_original_case():
    print("Probando caso original (debería fallar):")
    try:
        tema_value = rx.cond(
            (MockCuestionarioState.cuestionario_tema != "") & (MockCuestionarioState.cuestionario_tema != None),
            MockCuestionarioState.cuestionario_tema,
            "tema"
        )
        s_tema = re.sub(r'[\\/*?:"<>|]', "", tema_value)[:50]
        print(f"  ✓ Éxito inesperado: {s_tema}")
    except Exception as e:
        print(f"  ✗ Error esperado: {e}")

# Prueba del caso corregido
def test_fixed_case():
    print("\nProbando caso corregido (debería funcionar):")
    try:
        tema_value = rx.cond(
            (MockCuestionarioState.cuestionario_tema != "") & (MockCuestionarioState.cuestionario_tema != None),
            MockCuestionarioState.cuestionario_tema,
            "tema"
        )
        s_tema = re.sub(r'[\\/*?:"<>|]', "", str(tema_value))[:50]
        print(f"  ✓ Éxito: {s_tema}")
    except Exception as e:
        print(f"  ✗ Error inesperado: {e}")

if __name__ == "__main__":
    print("=== TEST DE CORRECCIÓN STRINGCASTEDVAR ===")
    test_original_case()
    test_fixed_case()
    print("=== FIN DEL TEST ===")
