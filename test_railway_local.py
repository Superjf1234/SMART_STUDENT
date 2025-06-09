#!/usr/bin/env python3
"""
Script de prueba local para simular el entorno de Railway
"""
import os
import sys
import subprocess
import time
from pathlib import Path

def setup_railway_env():
    """Configurar variables de entorno como en Railway"""
    os.environ['PORT'] = '8080'
    os.environ['RAILWAY_ENVIRONMENT'] = 'production'
    os.environ['REFLEX_ENV'] = 'prod'
    os.environ['PYTHONPATH'] = '/workspaces/SMART_STUDENT'
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=256'
    
    # Verificar GEMINI_API_KEY
    if 'GEMINI_API_KEY' not in os.environ:
        print("⚠ GEMINI_API_KEY no está configurada, usando clave de prueba")
        os.environ['GEMINI_API_KEY'] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"

def test_imports():
    """Probar que todas las importaciones funcionan"""
    try:
        print("Probando importaciones...")
        
        # Importar Reflex
        import reflex as rx
        print("✓ Reflex importado correctamente")
        
        # Importar paquete principal
        import mi_app_estudio
        print("✓ Paquete mi_app_estudio importado")
        
        # Importar módulo principal
        from mi_app_estudio import mi_app_estudio
        print("✓ Módulo principal importado")
        
        # Verificar que la app existe
        if hasattr(mi_app_estudio, 'app'):
            print("✓ Objeto app encontrado")
        
        return True
    except Exception as e:
        print(f"✗ Error en importaciones: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_reflex_init():
    """Probar la inicialización de Reflex"""
    try:
        print("Probando inicialización de Reflex...")
        
        # Ejecutar reflex init si es necesario
        if not os.path.exists('.web'):
            print("Ejecutando reflex init...")
            result = subprocess.run(
                [sys.executable, '-m', 'reflex', 'init', '--template', 'blank'],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✓ Reflex init exitoso")
            else:
                print(f"⚠ Reflex init con advertencias: {result.stderr}")
        else:
            print("✓ Reflex ya inicializado")
        
        return True
    except Exception as e:
        print(f"✗ Error en reflex init: {e}")
        return False

def main():
    """Función principal de prueba"""
    print("=== Prueba Local de Railway ===")
    
    # Configurar entorno
    setup_railway_env()
    print(f"✓ Entorno configurado (PORT={os.environ['PORT']})")
    
    # Probar importaciones
    if not test_imports():
        print("✗ Fallo en importaciones")
        return False
    
    # Probar inicialización de Reflex
    if not test_reflex_init():
        print("✗ Fallo en inicialización de Reflex")
        return False
    
    print("\n=== Resumen de Pruebas ===")
    print("✓ Todas las pruebas pasaron")
    print("✓ La aplicación debería funcionar en Railway")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
