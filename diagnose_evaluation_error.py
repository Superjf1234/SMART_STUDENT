#!/usr/bin/env python3
"""
Script para diagnosticar el error de EvaluationState.get_score_color_tier()
"""

import sys
import os

# Agregar paths
sys.path.insert(0, '/workspaces/SMART_STUDENT')
sys.path.insert(0, '/workspaces/SMART_STUDENT/mi_app_estudio')

print("=== DIAGNÓSTICO DEL ERROR EvaluationState ===")

try:
    print("1. Importando EvaluationState...")
    from mi_app_estudio.evaluaciones import EvaluationState
    print("✅ EvaluationState importado exitosamente")
    
    print("\n2. Verificando método get_score_color_tier...")
    if hasattr(EvaluationState, 'get_score_color_tier'):
        print("✅ Método get_score_color_tier existe")
        method = getattr(EvaluationState, 'get_score_color_tier')
        print(f"   Tipo: {type(method)}")
        print(f"   Es propiedad rx.var: {'rx.var' in str(type(method))}")
    else:
        print("❌ Método get_score_color_tier NO existe")
        
    print("\n3. Verificando eval_score_rounded...")
    if hasattr(EvaluationState, 'eval_score_rounded'):
        print("✅ Propiedad eval_score_rounded existe")
    else:
        print("❌ Propiedad eval_score_rounded NO existe")
        
    print("\n4. Listando métodos relacionados con score...")
    methods = [attr for attr in dir(EvaluationState) if 'score' in attr.lower()]
    for method in sorted(methods):
        print(f"   - {method}")
        
    print("\n5. Intentando crear instancia de prueba...")
    # No crear instancia real, solo verificar que la clase esté bien definida
    print(f"✅ Clase EvaluationState: {EvaluationState}")
    
    print("\n6. Verificando importación en mi_app_estudio.py...")
    with open('/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py', 'r') as f:
        content = f.read()
        if 'from .evaluaciones import EvaluationState' in content:
            print("✅ Importación correcta encontrada en mi_app_estudio.py")
        else:
            print("❌ Importación no encontrada en mi_app_estudio.py")
            
        # Buscar usos problemáticos
        if '.get_score_color_tier()' in content:
            print("❌ Encontrado uso incorrecto: .get_score_color_tier()")
            lines = content.split('\n')
            for i, line in enumerate(lines, 1):
                if '.get_score_color_tier()' in line:
                    print(f"   Línea {i}: {line.strip()}")
        else:
            print("✅ No se encontraron usos incorrectos con ()")
            
        if '.get_score_color_tier' in content and not '.get_score_color_tier()' in content:
            print("✅ Uso correcto encontrado: .get_score_color_tier (sin paréntesis)")

except Exception as e:
    print(f"❌ Error durante diagnóstico: {e}")
    import traceback
    traceback.print_exc()
    
print("\n=== FIN DEL DIAGNÓSTICO ===")
