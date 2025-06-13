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
    
    # Cambiar al directorio de la app
    app_path = '/app/mi_app_estudio'
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
