#!/usr/bin/env python3
"""
RAILWAY UNIVERSAL FIX: Copia rxconfig.py donde se necesite
"""

import os
import sys
import shutil

def main():
    print("🔧 RAILWAY UNIVERSAL FIX")
    print("=" * 50)
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"🔌 Puerto: {port}")
    print(f"🌐 Host: {host}")
    
    # GEMINI API KEY
    os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    print("🔑 GEMINI_API_KEY configurado")
    
    # Detectar donde estamos y copiar rxconfig.py si es necesario
    current_dir = os.getcwd()
    base_dir = '/app'
    app_dir = '/app/mi_app_estudio'
    
    print(f"📁 Current dir: {current_dir}")
    
    # SOLUCIÓN UNIVERSAL: Copiar rxconfig.py donde se necesite
    rxconfig_source = os.path.join(base_dir, 'rxconfig.py')
    
    if not os.path.exists('rxconfig.py') and os.path.exists(rxconfig_source):
        print(f"📋 Copying rxconfig.py to {current_dir}")
        shutil.copy(rxconfig_source, 'rxconfig.py')
        print("✅ rxconfig.py copied successfully")
    elif os.path.exists('rxconfig.py'):
        print("✅ rxconfig.py already exists")
    else:
        print("❌ rxconfig.py not found anywhere")
        
        # Crear un rxconfig.py básico
        basic_config = f'''import reflex as rx
import os

port = int(os.environ.get("PORT", "{port}"))

config = rx.Config(
    app_name="mi_app_estudio",
    title="Smart Student",
    backend_host="{host}",
    backend_port=port,
    env=rx.Env.DEV,
    tailwind=None,
)
'''
        with open('rxconfig.py', 'w') as f:
            f.write(basic_config)
        print("✅ Created basic rxconfig.py")
    
    # Comando
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"🚀 Command: {' '.join(cmd)}")
    print("Executing with rxconfig.py available...")
    
    # Ejecutar
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
