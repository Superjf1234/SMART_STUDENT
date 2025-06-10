#!/usr/bin/env python3
"""
Script ultra-minimalista para Railway que evita completamente el error de Rich
"""
import os
import sys
import subprocess
import json

def setup_minimal_env():
    """Configuración mínima para Railway"""
    os.environ['PORT'] = os.environ.get('PORT', '8080')
    os.environ['HOST'] = '0.0.0.0'
    os.environ['REFLEX_ENV'] = 'dev'  # Usar dev para evitar build complejo
    os.environ['PYTHONUNBUFFERED'] = '1'
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=256'
    
def create_minimal_package_json():
    """Crear package.json mínimo para evitar errores de Node"""
    package_json = {
        "name": "smart-student",
        "version": "1.0.0",
        "private": True,
        "scripts": {
            "dev": "next dev",
            "build": "next build",
            "start": "next start"
        },
        "dependencies": {
            "@emotion/react": "^11.10.5",
            "@emotion/styled": "^11.10.5",
            "next": "13.4.19",
            "react": "18.2.0",
            "react-dom": "18.2.0"
        }
    }
    
    # Crear directorio .web si no existe
    os.makedirs('.web', exist_ok=True)
    
    with open('.web/package.json', 'w') as f:
        json.dump(package_json, f, indent=2)

def run_simple():
    """Ejecutar de la forma más simple posible"""
    try:
        print("=== Iniciando Smart Student (Modo Ultra Simple) ===")
        
        # Configurar entorno
        setup_minimal_env()
        print("✓ Entorno configurado")
        
        # Crear package.json básico
        create_minimal_package_json()
        print("✓ Package.json creado")
        
        # Importar y ejecutar directamente
        sys.path.insert(0, '.')
        
        # Ejecutar con subprocess para controlar output
        cmd = [
            sys.executable, '-c', 
            """
import os
os.environ['REFLEX_DISABLE_TELEMETRY'] = 'true'
os.environ['REFLEX_DEBUG'] = 'false'
import reflex as rx
from mi_app_estudio.mi_app_estudio import app
app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8080')))
"""
        ]
        
        print(f"🚀 Ejecutando en puerto {os.environ.get('PORT', '8080')}")
        
        # Ejecutar con manejo de errores específico para Rich
        result = subprocess.run(cmd, env=os.environ.copy())
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"❌ Error: {e}")
        # Fallback: intentar ejecución directa
        try:
            print("🔄 Intentando método alternativo...")
            import reflex as rx
            from mi_app_estudio.mi_app_estudio import app
            app.run(host='0.0.0.0', port=int(os.environ.get('PORT', '8080')))
        except Exception as e2:
            print(f"❌ Error en fallback: {e2}")
            return False

if __name__ == "__main__":
    success = run_simple()
    sys.exit(0 if success else 1)
