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
    
    # NUEVA ESTRATEGIA: Siempre ejecutar desde el directorio raíz
    # donde está rxconfig.py, pero verificar que la app existe
    base_path = '/app'
    app_path = '/app/mi_app_estudio'
    
    # Verificar que los archivos necesarios existen
    rxconfig_exists = os.path.exists(f'{base_path}/rxconfig.py')
    app_exists = os.path.exists(f'{app_path}/mi_app_estudio.py')
    
    print(f"📁 Base path: {base_path}")
    print(f"📁 App path: {app_path}")
    print(f"✅ rxconfig.py exists: {rxconfig_exists}")
    print(f"✅ mi_app_estudio.py exists: {app_exists}")
    
    if not rxconfig_exists:
        print("❌ rxconfig.py not found in base path")
        return
    
    if not app_exists:
        print("❌ mi_app_estudio.py not found in app path")
        return
    
    # CRÍTICO: Cambiar al directorio base donde está rxconfig.py
    os.chdir(base_path)
    print(f"📁 Working dir: {os.getcwd()}")
    
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
