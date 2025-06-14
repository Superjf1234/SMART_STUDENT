#!/usr/bin/env python3
"""
Script para probar la importación de módulos después del fix de Railway.
"""

import sys
import os

def test_imports():
    """Probar todas las importaciones clave."""
    print("🔧 PRUEBA DE IMPORTS DESPUÉS DEL FIX RAILWAY")
    print("=" * 50)
    
    tests = [
        ("reflex", "import reflex as rx"),
        ("state", "import state"),
        ("cuestionario", "import cuestionario"),
        ("review_components", "import review_components"),
        ("utils", "import utils"),
        ("app_main", "import app_main"),
        ("app from app_main", "from app_main import app"),
    ]
    
    passed = 0
    failed = 0
    
    for name, import_statement in tests:
        try:
            exec(import_statement)
            print(f"✅ {name}: OK")
            passed += 1
        except Exception as e:
            print(f"❌ {name}: FAILED - {e}")
            failed += 1
    
    print("=" * 50)
    print(f"📊 RESULTADOS: {passed} pasaron, {failed} fallaron")
    
    if failed == 0:
        print("🎉 ¡Todos los imports funcionan correctamente!")
        return True
    else:
        print("⚠️ Algunos imports están fallando.")
        return False

def test_app_creation():
    """Probar la creación de la aplicación Reflex."""
    try:
        print("\n🚀 PROBANDO CREACIÓN DE APP...")
        import app_main
        if hasattr(app_main, 'app'):
            print("✅ App encontrada en app_main")
            print(f"   Tipo: {type(app_main.app)}")
            return True
        else:
            print("❌ No se encontró 'app' en app_main")
            return False
    except Exception as e:
        print(f"❌ Error creando app: {e}")
        return False

def main():
    """Función principal."""
    print(f"Working directory: {os.getcwd()}")
    print(f"Python version: {sys.version}")
    print(f"Python path: {sys.path[:3]}...")  # Show first 3 paths
    print()
    
    imports_ok = test_imports()
    app_ok = test_app_creation()
    
    if imports_ok and app_ok:
        print("\n🎉 ¡TODO FUNCIONANDO! Railway debería deployar correctamente.")
    else:
        print("\n❌ Hay problemas que resolver antes del deploy.")

if __name__ == "__main__":
    main()
