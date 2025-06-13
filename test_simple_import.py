#!/usr/bin/env python3
"""
Test simple para verificar la importación de EvaluationState
"""

import sys
import os

# Añadir paths
sys.path.insert(0, '/workspaces/SMART_STUDENT')

print("=== TEST SIMPLE DE IMPORTACIÓN ===")

try:
    print("1. Probando importación directa del módulo state...")
    from mi_app_estudio.state import AppState
    print("✅ AppState importado correctamente")
    
    print("2. Probando importación directa del módulo evaluaciones...")
    from mi_app_estudio import evaluaciones
    print("✅ Módulo evaluaciones importado correctamente")
    
    print("3. Probando acceso a la clase EvaluationState...")
    EvaluationState = evaluaciones.EvaluationState
    print("✅ Clase EvaluationState accesible")
    
    print("4. Verificando método get_score_color_tier...")
    if hasattr(EvaluationState, 'get_score_color_tier'):
        print("✅ Método get_score_color_tier existe")
        method = getattr(EvaluationState, 'get_score_color_tier')
        print(f"   Tipo: {type(method)}")
    else:
        print("❌ Método get_score_color_tier NO existe")
        
    print("5. Probando importación desde evaluaciones...")
    from mi_app_estudio.evaluaciones import EvaluationState as ES
    print("✅ EvaluationState importado desde evaluaciones")
    
    print("6. Probando importación del archivo principal...")
    # NO importar el archivo completo, solo verificar que no hay errores sintácticos
    import ast
    with open('/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py', 'r') as f:
        content = f.read()
    
    try:
        ast.parse(content)
        print("✅ Archivo mi_app_estudio.py tiene sintaxis válida")
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en mi_app_estudio.py: {e}")
        
    print("\n=== TODAS LAS IMPORTACIONES EXITOSAS ===")
    
except Exception as e:
    print(f"❌ Error durante las pruebas: {e}")
    import traceback
    traceback.print_exc()
