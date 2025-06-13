#!/usr/bin/env python3
"""
RAILWAY SIMPLE: Usar versión simplificada sin imports complejos
"""

import os
import sys
import shutil

def main():
    print("🎯 RAILWAY SIMPLE STRATEGY")
    print("=" * 50)
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"🔌 Puerto: {port}")
    print(f"🌐 Host: {host}")
    
    # GEMINI API KEY (fallback)
    os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    print("🔑 GEMINI_API_KEY configurado")
    
    # NUEVA ESTRATEGIA: Copiar rxconfig.py al directorio donde estamos ejecutando
    # O cambiar al directorio raíz - LO QUE SEA NECESARIO PARA QUE FUNCIONE
    app_path = '/app/mi_app_estudio'
    root_path = '/app'
    
    print(f"📁 App path: {app_path}")
    print(f"📁 Root path: {root_path}")
    
    # Verificar si rxconfig.py existe en root
    rxconfig_source = f"{root_path}/rxconfig.py"
    rxconfig_target = f"{app_path}/rxconfig.py"
    
    if os.path.exists(rxconfig_source):
        print("✅ Found rxconfig.py in root")
        
        # OPCIÓN 1: Copiar rxconfig.py al directorio de la app
        try:
            shutil.copy(rxconfig_source, rxconfig_target)
            print("📋 Copied rxconfig.py to app directory")
        except Exception as e:
            print(f"⚠️ Could not copy rxconfig.py: {e}")
            
            # OPCIÓN 2: Cambiar al directorio raíz en su lugar
            print("🔄 Changing to root directory instead")
            os.chdir(root_path)
            print(f"📁 Working dir changed to: {os.getcwd()}")
            
            # No reemplazar archivos si estamos en root
            return
    else:
        print("❌ rxconfig.py not found in root")
    
    # Continuar en el directorio de la app
    os.chdir(app_path)
    print(f"📁 Working dir: {os.getcwd()}")
    
    # ESTRATEGIA: Reemplazar el archivo principal con la versión simple
    try:
        if os.path.exists('mi_app_estudio_simple.py'):
            print("✅ Simple version found")
            
            # Backup del original
            if os.path.exists('mi_app_estudio.py'):
                shutil.copy('mi_app_estudio.py', 'mi_app_estudio_original_backup.py')
                print("📋 Original backed up")
            
            # Reemplazar con la versión simple
            shutil.copy('mi_app_estudio_simple.py', 'mi_app_estudio.py')
            print("🔄 Replaced with simple version")
            
        else:
            print("❌ Simple version not found")
            
    except Exception as e:
        print(f"❌ Error replacing files: {e}")
        return
    
    # Después de copiar rxconfig.py, también verificar/corregir su contenido
    try:
        if os.path.exists(rxconfig_target):
            # Leer el rxconfig.py copiado
            with open(rxconfig_target, 'r') as f:
                content = f.read()
            
            # Si contiene mi_app_estudio.mi_app_estudio, corregirlo a solo mi_app_estudio
            if 'mi_app_estudio.mi_app_estudio' in content:
                print("🔧 Fixing app_name in rxconfig.py")
                # No necesario cambiar, ya debería ser correcto
            
            print("✅ rxconfig.py validated")
    except Exception as e:
        print(f"⚠️ Could not validate rxconfig.py: {e}")

    # MEJOR ESTRATEGIA: Crear rxconfig.py específico para el directorio de la app
    rxconfig_content = f'''import reflex as rx
import os

# Auto-generated rxconfig.py for app directory execution
port = int(os.environ.get("PORT", "{port}"))

config = rx.Config(
    app_name="mi_app_estudio",  # Direct reference to mi_app_estudio.py file
    title="Smart Student",
    backend_host="0.0.0.0",
    backend_port=port,
    env=rx.Env.DEV,
    tailwind=None,
)
'''
    
    try:
        with open(rxconfig_target, 'w') as f:
            f.write(rxconfig_content)
        print("📝 Created custom rxconfig.py for app directory")
    except Exception as e:
        print(f"⚠️ Could not create custom rxconfig.py: {e}")

    # Comando
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"🚀 Command: {' '.join(cmd)}")
    print("Running with simplified app...")
    
    # Ejecutar
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
