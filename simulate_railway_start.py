#!/usr/bin/env python3
"""
Script para simular el comportamiento de inicio de Reflex en Railway.
"""

import sys
import os
import traceback

# Simular entorno de Railway
os.environ["PORT"] = "3000"
os.environ["RAILWAY"] = "true"

def main():
    print("==== SIMULACIÓN DE INICIO EN RAILWAY ====")
    
    try:
        print("\n1. Importando el módulo mi_app_estudio...")
        import mi_app_estudio
        
        print("\n2. Accediendo a la app...")
        app = mi_app_estudio.app
        print(f"✅ App encontrada: {app}")
        
        # Probar las funciones principales que se utilizan en el inicio
        print("\n3. Probando la función index...")
        index_result = mi_app_estudio.index()
        print("✅ Función index ejecutada correctamente")
        
        print("\n4. Probando main_dashboard...")
        main_dashboard = mi_app_estudio.main_dashboard()
        print("✅ Función main_dashboard ejecutada correctamente")
        
        print("\n5. Probando login_page...")
        login_page = mi_app_estudio.login_page()
        print("✅ Función login_page ejecutada correctamente")
        
        print("\n✅ Todas las funciones críticas funcionan correctamente")
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        print("\nTraceback completo:")
        traceback.print_exc()
        
        # Análisis de errores específicos
        if "VarAttributeError" in str(type(e)) or "get_score_color_tier" in str(e):
            print("\n⚠️ ANÁLISIS: Este parece ser un problema con los métodos helper que agregamos en EvaluationState.")
            try:
                from mi_app_estudio import evaluaciones
                print("\nComprobando los métodos en EvaluationState:")
                
                state_class = evaluaciones.EvaluationState
                instance = evaluaciones.EvaluationState()
                
                for method in ['get_score_color_tier', 'get_score_background_color', 'get_score_border_color']:
                    if hasattr(state_class, method):
                        print(f"✅ {method} existe como método de clase")
                    else:
                        print(f"❌ {method} NO existe como método de clase")
                
                # Verificar si evaluaciones.py tiene los métodos
                with open("mi_app_estudio/evaluaciones.py", "r") as f:
                    content = f.read()
                    for method in ['get_score_color_tier', 'get_score_background_color', 'get_score_border_color']:
                        if method in content:
                            print(f"✅ {method} está en el contenido del archivo evaluaciones.py")
                        else:
                            print(f"❌ {method} NO está en el contenido del archivo evaluaciones.py")
                
            except Exception as e2:
                print(f"Error en el análisis: {e2}")
        
    print("\n==== FIN DE LA SIMULACIÓN ====")

if __name__ == "__main__":
    main()
