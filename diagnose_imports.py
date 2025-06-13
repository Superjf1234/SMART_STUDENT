#!/usr/bin/env python3
"""
Script para diagnosticar problemas de importación en la aplicación mi_app_estudio.
Este script intentará importar los módulos principales y mostrará errores detallados.
"""

import sys
import traceback

def main():
    print("==== DIAGNÓSTICO DE IMPORTACIÓN DE MI_APP_ESTUDIO ====")
    
    try:
        print("\n1. Intentando importar el módulo mi_app_estudio...")
        import mi_app_estudio
        print("✅ Importación exitosa")
    except Exception as e:
        print(f"❌ Error importando mi_app_estudio: {type(e).__name__}: {e}")
        print("\nTraceback completo:")
        traceback.print_exc()
        
        # Intentar importaciones parciales para diagnóstico
        try:
            print("\n2. Intentando importar evaluaciones.py...")
            from mi_app_estudio import evaluaciones
            print("✅ módulo evaluaciones importado correctamente")
            
            # Verificar los métodos helper
            print("\n3. Verificando métodos helper en EvaluationState...")
            if hasattr(evaluaciones.EvaluationState, 'get_score_color_tier'):
                print("✅ EvaluationState.get_score_color_tier existe")
            else:
                print("❌ EvaluationState.get_score_color_tier NO EXISTE")
                
            if hasattr(evaluaciones.EvaluationState, 'get_score_background_color'):
                print("✅ EvaluationState.get_score_background_color existe")
            else:
                print("❌ EvaluationState.get_score_background_color NO EXISTE")
                
            if hasattr(evaluaciones.EvaluationState, 'get_score_border_color'):
                print("✅ EvaluationState.get_score_border_color existe")
            else:
                print("❌ EvaluationState.get_score_border_color NO EXISTE")
                
            # Inspeccionar el archivo
            print("\n4. Contenido de EvaluationState (parcial):")
            with open("mi_app_estudio/evaluaciones.py", "r") as f:
                content = f.read()
            if "get_score_color_tier" in content:
                print("✅ 'get_score_color_tier' está en el contenido del archivo")
                
                # Mostrar el contexto alrededor de get_score_color_tier
                start = content.find("get_score_color_tier")
                if start > 0:
                    context_start = max(0, start - 100)
                    context_end = min(len(content), start + 500)
                    print("\nContexto alrededor de get_score_color_tier:")
                    print(content[context_start:context_end])
            else:
                print("❌ 'get_score_color_tier' NO está en el contenido del archivo")
                
        except Exception as e2:
            print(f"❌ Error en el diagnóstico: {type(e2).__name__}: {e2}")
            traceback.print_exc()
    
    print("\n==== FIN DEL DIAGNÓSTICO ====")

if __name__ == "__main__":
    main()
