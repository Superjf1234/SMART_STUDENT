#!/usr/bin/env python3
"""
RAILWAY COPY CONFIG: Copy rxconfig.py to execution directory
"""

import os
import sys
import shutil

def main():
    print("📋 RAILWAY COPY CONFIG STRATEGY")
    print("=" * 50)
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"🔌 Puerto: {port}")
    print(f"🌐 Host: {host}")
    
    # GEMINI API KEY (fallback)
    os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    print("🔑 GEMINI_API_KEY configurado")
    
    # Paths
    base_path = '/app'
    app_path = '/app/mi_app_estudio'
    
    # ESTRATEGIA: Copiar rxconfig.py al directorio de la app
    try:
        if os.path.exists(f'{base_path}/rxconfig.py'):
            print("✅ Found rxconfig.py in base path")
            
            # Copiar rxconfig.py al directorio de la app
            shutil.copy(f'{base_path}/rxconfig.py', f'{app_path}/rxconfig.py')
            print("📋 Copied rxconfig.py to app directory")
            
            # Cambiar al directorio de la app
            os.chdir(app_path)
            print(f"📁 Working dir: {os.getcwd()}")
            
            # Verificar que ahora existe
            if os.path.exists('rxconfig.py'):
                print("✅ rxconfig.py now available in working directory")
            else:
                print("❌ Failed to copy rxconfig.py")
                return
                
        else:
            print("❌ rxconfig.py not found in base path")
            return
            
    except Exception as e:
        print(f"❌ Error copying config: {e}")
        return
    
    # Comando
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"🚀 Command: {' '.join(cmd)}")
    print("Running with rxconfig.py in working directory...")
    
    # Ejecutar
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
