#!/usr/bin/env python3
"""
RAILWAY DIRECT - REESCRITO PARA IMPORTS RELATIVOS
"""

import os
import sys

def main():
    """NUEVA ESTRATEGIA: Sin imports complejos, dejar que Reflex maneje todo"""
    
    print("🔄 RAILWAY DIRECT - NUEVA ESTRATEGIA")
    print("=" * 50)
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"🔌 Puerto: {port}")
    print(f"🌐 Host: {host}")
    
    # GEMINI API KEY (fallback)
    os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    print("🔑 GEMINI_API_KEY configurado")
    
    # Estrategia: Probar diferentes directorios
    app_paths = ['/app/mi_app_estudio', '/app']
    
    for app_path in app_paths:
        if os.path.exists(app_path):
            os.chdir(app_path)
            print(f"📁 Working dir: {os.getcwd()}")
            
            # Verificar archivos necesarios
            if os.path.exists('mi_app_estudio.py') or os.path.exists('mi_app_estudio/mi_app_estudio.py'):
                print("✅ App files found")
                break
            elif os.path.exists('rxconfig.py'):
                print("✅ Reflex config found")
                break
    
    # Comando simple - dejar que Reflex maneje los imports
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"🚀 Command: {' '.join(cmd)}")
    print("Letting Reflex auto-discover and handle imports...")
    
    # Ejecutar
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
