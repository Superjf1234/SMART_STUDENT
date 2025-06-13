#!/usr/bin/env python3
"""
RAILWAY COPY CONFIG: Copia archivos de configuración necesarios
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
    
    # Directorios
    root_path = '/app'
    app_path = '/app/mi_app_estudio'
    
    # ESTRATEGIA: Copiar archivos de configuración necesarios
    config_files = ['rxconfig.py', 'requirements.txt']
    
    for config_file in config_files:
        source = f"{root_path}/{config_file}"
        target = f"{app_path}/{config_file}"
        
        if os.path.exists(source) and not os.path.exists(target):
            try:
                shutil.copy(source, target)
                print(f"📄 Copied {config_file}")
            except Exception as e:
                print(f"⚠️ Could not copy {config_file}: {e}")
    
    # Cambiar al directorio de la app
    os.chdir(app_path)
    print(f"📁 Working dir: {os.getcwd()}")
    
    # Verificar que ahora tenemos lo necesario
    if os.path.exists('rxconfig.py'):
        print("✅ rxconfig.py now available")
    else:
        print("❌ rxconfig.py still missing")
    
    # Comando
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"🚀 Command: {' '.join(cmd)}")
    
    # Ejecutar
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
