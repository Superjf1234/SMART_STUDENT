#!/usr/bin/env python3
"""
Test rápido de imports para verificar que no hay errores de import
"""

import sys
import os

# Simular el entorno de Railway
sys.path.insert(0, "/workspaces/SMART_STUDENT")
os.chdir("/workspaces/SMART_STUDENT/mi_app_estudio")

print("🧪 TESTING IMPORTS...")

try:
    # Test import principal
    print("1. Importando mi_app_estudio...")
    import mi_app_estudio.mi_app_estudio
    print("   ✅ mi_app_estudio.mi_app_estudio OK")
    
    # Test imports de sub-módulos
    print("2. Importando state...")
    from mi_app_estudio.state import AppState
    print("   ✅ AppState OK")
    
    print("3. Importando cuestionario...")
    from mi_app_estudio.cuestionario import CuestionarioState
    print("   ✅ CuestionarioState OK")
    
    print("4. Importando evaluaciones...")
    from mi_app_estudio.evaluaciones import EvaluationState
    print("   ✅ EvaluationState OK")
    
    print("5. Importando review_components...")
    from mi_app_estudio.review_components import mensaje_respuesta_correcta
    print("   ✅ review_components OK")
    
    print("\n🎉 TODOS LOS IMPORTS FUNCIONAN CORRECTAMENTE")
    print("✅ La app debería arrancar sin errores de import en Railway")
    
except Exception as e:
    print(f"\n❌ ERROR DE IMPORT: {e}")
    print(f"Tipo: {type(e).__name__}")
    import traceback
    traceback.print_exc()
