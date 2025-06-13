#!/usr/bin/env python3
"""
RAILWAY STRATEGY: Ejecutar desde directorio raíz para evitar problemas de imports
"""

import os
import sys

def main():
    print("🎯 RAILWAY ROOT STRATEGY")
    print("=" * 50)
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"🔌 Puerto: {port}")
    print(f"🌐 Host: {host}")
    
    # GEMINI API KEY (fallback)
    os.environ["GEMINI_API_KEY"] = "AIzaSyAOkMCAA84tHALCkCPskyV0jFKnBz2pSiA"
    print("🔑 GEMINI_API_KEY configurado")
    
    # CAMBIO CLAVE: Ejecutar desde /app (raíz) NO desde /app/mi_app_estudio
    base_path = '/app'
    app_module_path = '/app/mi_app_estudio'
    
    # Configurar paths
    os.environ["PYTHONPATH"] = f"{base_path}:{app_module_path}"
    sys.path.insert(0, base_path)
    
    # Cambiar al directorio BASE (no al subdirectorio)
    os.chdir(base_path)
    print(f"📁 Working dir: {os.getcwd()}")
    
    # Test import desde el directorio raíz
    try:
        import mi_app_estudio.mi_app_estudio
        print("✅ Import successful from root")
    except Exception as e:
        print(f"❌ Import error: {e}")
        
        # Backup strategy: simple module import
        try:
            sys.path.insert(0, app_module_path)
            os.chdir(app_module_path)
            import mi_app_estudio
            print("✅ Fallback import successful")
        except Exception as e2:
            print(f"❌ Fallback failed: {e2}")
            return
    
    # Ejecutar reflex desde el directorio raíz
    # Cambiar al directorio de la app solo para la ejecución de reflex
    os.chdir(app_module_path)
    print(f"📁 Switched to app dir: {os.getcwd()}")
    
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"🚀 Command: {' '.join(cmd)}")
    print("Executing from app directory with proper PYTHONPATH...")
    
    # Ejecutar
    os.execv(sys.executable, cmd)

if __name__ == "__main__":
    main()
