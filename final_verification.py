#!/usr/bin/env python3
"""
Script de verificación final para confirmar que todos los errores están resueltos
"""
import os
import sys
import importlib.util

def test_rxconfig():
    """Verificar que rxconfig.py es válido"""
    try:
        # Intentar importar rxconfig
        spec = importlib.util.spec_from_file_location("rxconfig", "rxconfig.py")
        rxconfig = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(rxconfig)
        
        # Verificar que config existe
        if hasattr(rxconfig, 'config'):
            print("✅ rxconfig.py: VÁLIDO")
            print(f"   - App name: {rxconfig.config.app_name}")
            print(f"   - Log level: {rxconfig.config.loglevel}")
            print(f"   - Backend port: {rxconfig.config.backend_port}")
            return True
        else:
            print("❌ rxconfig.py: Sin objeto config")
            return False
            
    except Exception as e:
        print(f"❌ rxconfig.py: ERROR - {e}")
        return False

def test_imports():
    """Verificar que las importaciones funcionan"""
    try:
        import reflex as rx
        print("✅ Reflex: IMPORTADO")
        
        import mi_app_estudio
        print("✅ mi_app_estudio: IMPORTADO")
        
        from mi_app_estudio import mi_app_estudio
        print("✅ mi_app_estudio.mi_app_estudio: IMPORTADO")
        
        if hasattr(mi_app_estudio, 'app'):
            print("✅ App object: ENCONTRADO")
            return True
        else:
            print("❌ App object: NO ENCONTRADO")
            return False
            
    except Exception as e:
        print(f"❌ Importaciones: ERROR - {e}")
        return False

def test_emergency_script():
    """Verificar que el script de emergencia es válido"""
    try:
        with open('emergency_railway_simple.py', 'r') as f:
            content = f.read()
            
        # Verificar sintaxis
        compile(content, 'emergency_railway_simple.py', 'exec')
        print("✅ emergency_railway_simple.py: SINTAXIS VÁLIDA")
        return True
        
    except SyntaxError as e:
        print(f"❌ emergency_railway_simple.py: SINTAXIS ERROR - {e}")
        return False
    except FileNotFoundError:
        print("❌ emergency_railway_simple.py: ARCHIVO NO ENCONTRADO")
        return False

def main():
    """Función principal de verificación"""
    print("🔍 VERIFICACIÓN FINAL - Smart Student")
    print("=" * 50)
    
    tests = [
        ("Configuración Reflex", test_rxconfig),
        ("Importaciones Python", test_imports),
        ("Script de Emergencia", test_emergency_script),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n📋 {name}:")
        try:
            if test_func():
                passed += 1
            else:
                print(f"   ⚠️  {name}: FALLÓ")
        except Exception as e:
            print(f"   ❌ {name}: EXCEPCIÓN - {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTADO: {passed}/{total} pruebas pasaron")
    
    if passed == total:
        print("🎉 ¡TODAS LAS VERIFICACIONES EXITOSAS!")
        print("🚀 La aplicación debería desplegarse correctamente en Railway")
        return True
    else:
        print("⚠️  Algunas verificaciones fallaron")
        print("🔧 Revisar errores antes del deploy")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
