#!/usr/bin/env python3
"""
Script para verificar la estructura del proyecto y diagnosticar problemas con
la aplicación mi_app_estudio en Railway.
"""

import sys
import os
import traceback
import importlib
import inspect

def main():
    print("==== VERIFICACIÓN DE ESTRUCTURA Y DIAGNÓSTICO ====")
    
    # 1. Verificar la estructura del proyecto
    print("\n1. Verificando estructura del proyecto...")
    paths = [
        "mi_app_estudio/",
        "mi_app_estudio/__init__.py",
        "mi_app_estudio/mi_app_estudio.py",
        "mi_app_estudio/evaluaciones.py"
    ]
    
    for path in paths:
        if os.path.exists(path):
            print(f"✅ {path} existe")
        else:
            print(f"❌ {path} NO existe")
    
    # 2. Verificar contenido de archivos críticos
    print("\n2. Verificando contenido de archivos críticos...")
    
    try:
        with open("mi_app_estudio/evaluaciones.py", "r") as f:
            content = f.read()
            methods = ['get_score_color_tier', 'get_score_background_color', 'get_score_border_color']
            for method in methods:
                if method in content:
                    print(f"✅ El método {method} está definido en evaluaciones.py")
                else:
                    print(f"❌ El método {method} NO está definido en evaluaciones.py")
    except Exception as e:
        print(f"Error al leer evaluaciones.py: {e}")
    
    # 3. Intentar importar y verificar la disponibilidad de los métodos
    print("\n3. Intentando importar módulos y verificar métodos...")
    
    try:
        print("Importando mi_app_estudio.evaluaciones...")
        from mi_app_estudio import evaluaciones
        print("✅ Importación exitosa de evaluaciones")
        
        # Verificar la clase EvaluationState
        if hasattr(evaluaciones, "EvaluationState"):
            print("✅ La clase EvaluationState existe")
            
            # Verificar métodos en la clase
            es_class = getattr(evaluaciones, "EvaluationState")
            methods = ['get_score_color_tier', 'get_score_background_color', 'get_score_border_color']
            
            for method in methods:
                if hasattr(es_class, method):
                    print(f"✅ El método {method} existe en la clase EvaluationState")
                    # Verificar si es un método de instancia o un método estático/de clase
                    method_obj = getattr(es_class, method)
                    if inspect.isfunction(method_obj) or inspect.ismethod(method_obj):
                        print(f"   ✓ {method} es un método")
                    else:
                        print(f"   ⚠️ {method} NO es un método, es un {type(method_obj)}")
                else:
                    print(f"❌ El método {method} NO existe en la clase EvaluationState")
        else:
            print("❌ La clase EvaluationState NO existe")
        
    except Exception as e:
        print(f"❌ Error durante la importación: {type(e).__name__}: {e}")
        traceback.print_exc()
    
    # 4. Intentar importar mi_app_estudio directamente
    print("\n4. Importando mi_app_estudio directamente...")
    
    try:
        import mi_app_estudio
        print("✅ Importación exitosa de mi_app_estudio")
        print(f"   Módulo encontrado en: {mi_app_estudio.__file__}")
        
        # Listar atributos del módulo
        print("\n   Atributos principales del módulo:")
        attrs = [attr for attr in dir(mi_app_estudio) if not attr.startswith("__")]
        for attr in attrs[:10]:  # Mostrar solo los primeros 10 para no saturar
            print(f"   - {attr}")
        
        # Verificar la existencia del objeto app
        if hasattr(mi_app_estudio, "app"):
            print("\n✅ El objeto 'app' existe en mi_app_estudio")
        else:
            print("\n❌ El objeto 'app' NO existe en mi_app_estudio")
            
            # Buscar en mi_app_estudio.py
            with open("mi_app_estudio/mi_app_estudio.py", "r") as f:
                content = f.read()
                if "app = rx.App(" in content:
                    print("   ✓ Se encontró 'app = rx.App(' en mi_app_estudio.py")
                    
                    # Buscar la línea específica
                    lines = content.split("\n")
                    for i, line in enumerate(lines):
                        if "app = rx.App(" in line:
                            print(f"   ✓ Definición de app en línea {i+1}: {line.strip()}")
                            # Mostrar contexto
                            start = max(0, i-5)
                            end = min(len(lines), i+6)
                            print("\n   Contexto:")
                            for j in range(start, end):
                                print(f"   {j+1}: {lines[j].strip()}")
                else:
                    print("   ❌ NO se encontró 'app = rx.App(' en mi_app_estudio.py")
    except Exception as e:
        print(f"❌ Error durante la importación directa: {type(e).__name__}: {e}")
        traceback.print_exc()
    
    print("\n==== FIN DEL DIAGNÓSTICO ====")

if __name__ == "__main__":
    main()
