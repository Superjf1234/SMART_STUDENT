#!/usr/bin/env python3
"""
RAILWAY STRATEGY: Usar imports relativos desde dentro del directorio de la app
"""

import os
import sys

def main():
    print("🔄 RAILWAY RELATIVE IMPORTS STRATEGY")
    print("=" * 50)
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"🔌 Puerto: {port}")
    print(f"🌐 Host: {host}")
    
    # GEMINI API KEY (fallback)
    os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    print("🔑 GEMINI_API_KEY configurado")
    
    # Estrategia: trabajar desde dentro del directorio de la app
    app_path = '/app/mi_app_estudio'
    
    # Cambiar al directorio de la app
    os.chdir(app_path)
    print(f"📁 Working dir: {os.getcwd()}")
    
    # Configurar sys.path para imports relativos
    sys.path.insert(0, '.')  # Directorio actual
    sys.path.insert(0, '..')  # Directorio padre
    
    # Test import simple
    try:
        import mi_app_estudio  # Import simple, no relativo
        print("✅ Simple import successful")
    except Exception as e:
        print(f"❌ Simple import error: {e}")
        return
    
    # Comando simple
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"🚀 Command: {' '.join(cmd)}")
    print("Executing with relative imports from app directory...")
    
    # Ejecutar
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
