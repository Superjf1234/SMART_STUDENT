#!/usr/bin/env python3
"""
Script para verificar y corregir errores de sintaxis en mi_app_estudio.py
"""

import ast
import traceback

def check_syntax():
    try:
        with open('/workspaces/SMART_STUDENT/mi_app_estudio/mi_app_estudio.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Intentar parsear el archivo
        ast.parse(content)
        print("✅ Sintaxis del archivo correcta")
        return True
        
    except SyntaxError as e:
        print(f"❌ Error de sintaxis en línea {e.lineno}: {e.msg}")
        print(f"Texto problemático: {e.text}")
        return False
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        traceback.print_exc()
        return False

def test_import():
    try:
        import sys
        sys.path.insert(0, '/workspaces/SMART_STUDENT')
        
        # Intentar importar el módulo
        import mi_app_estudio.mi_app_estudio as app_module
        print("✅ Importación del módulo exitosa")
        return True
    except Exception as e:
        print(f"❌ Error al importar el módulo: {e}")
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("=== VERIFICACIÓN DE SINTAXIS ===")
    syntax_ok = check_syntax()
    
    if syntax_ok:
        print("\n=== VERIFICACIÓN DE IMPORTACIÓN ===")
        import_ok = test_import()
        
        if import_ok:
            print("\n✅ ARCHIVO VERIFICADO CORRECTAMENTE")
        else:
            print("\n❌ PROBLEMAS CON LA IMPORTACIÓN")
    else:
        print("\n❌ PROBLEMAS DE SINTAXIS DETECTADOS")
