#!/usr/bin/env python
"""
Script para validar las correcciones de descarga de PDF/HTML en el cuestionario
"""
import sys
import os
import traceback
from pathlib import Path

# Agregar la raíz del proyecto al path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

try:
    print("\n=== VALIDACIÓN DE CORRECCIONES DE DESCARGA DE CUESTIONARIO ===\n")
    
    # Importar módulos necesarios
    print("1. Importando módulos...")
    from mi_app_estudio.state import AppState, get_safe_var_list, get_safe_var_value
    from mi_app_estudio.cuestionario import CuestionarioState
    print("   ✓ Módulos importados correctamente\n")
    
    # Crear datos de prueba para simular un cuestionario
    preguntas_prueba = [
        {
            "tipo": "alternativas",
            "pregunta": "¿Pregunta de prueba 1?",
            "alternativas": [
                {"letra": "a", "texto": "Opción A"},
                {"letra": "b", "texto": "Opción B"},
                {"letra": "c", "texto": "Opción C"}
            ],
            "correcta": "b",
            "explicacion": "Esta es la explicación"
        },
        {
            "tipo": "verdadero_falso",
            "pregunta": "¿Pregunta de prueba 2?",
            "alternativas": [
                {"letra": "a", "texto": "Verdadero"},
                {"letra": "b", "texto": "Falso"}
            ],
            "correcta": "a",
            "explicacion": "Explicación de la segunda pregunta"
        },
        {
            "tipo": "seleccion_multiple",
            "pregunta": "¿Pregunta de prueba 3?",
            "alternativas": [
                {"letra": "a", "texto": "Opción A"},
                {"letra": "b", "texto": "Opción B"},
                {"letra": "c", "texto": "Opción C"}
            ],
            "correctas": ["a", "c"],
            "explicacion": "Explicación de la tercera pregunta"
        }
    ]
    
    # Probar la función get_safe_var_value
    print("2. Probando get_safe_var_value...")
    # Simular variable reactiva con una clase simple
    class MockVar:
        def __init__(self, value):
            self._var_value = value
        
        def __str__(self):
            return f"<reflex.Var>123456789</reflex.Var>{self._var_value}"
    
    mock_var = MockVar("test_value")
    result = get_safe_var_value(mock_var, "default")
    print(f"   - Resultado: {result}")
    if result == "test_value":
        print("   ✓ get_safe_var_value funciona correctamente\n")
    else:
        print("   ✗ get_safe_var_value no devuelve el valor esperado\n")
        
    # Probar la función get_safe_var_list
    print("3. Probando get_safe_var_list...")
    # Simular lista reactiva
    class MockList:
        def __init__(self, values):
            self._var_value = values
        
        def __getitem__(self, index):
            return self._var_value[index]
        
        def __len__(self):
            return len(self._var_value)
            
        def __str__(self):
            return f"<reflex.Var>987654321</reflex.Var>{str(self._var_value)}"
    
    mock_list = MockList(preguntas_prueba)
    result_list = get_safe_var_list(mock_list, [])
    print(f"   - Resultado tiene {len(result_list)} elementos")
    if len(result_list) == len(preguntas_prueba):
        print("   ✓ get_safe_var_list funciona correctamente\n")
    else:
        print("   ✗ get_safe_var_list no devuelve el número esperado de elementos\n")
    
    print("\n=== FIN DE LA VALIDACIÓN ===\n")
    
    # Consejo final
    print("Si esta validación fue exitosa, las correcciones deberían solucionar")
    print("el problema de la descarga del cuestionario en formato HTML.")
    print("\nPara probar en la aplicación real:")
    print("1. Ejecuta 'python -m mi_app_estudio run'")
    print("2. Ve a la pestaña de cuestionario")
    print("3. Genera un cuestionario")
    print("4. Haz clic en el botón de descargar PDF")
    
except Exception as e:
    print(f"ERROR: {e}")
    traceback.print_exc()
