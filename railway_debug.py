#!/usr/bin/env python3
"""
Railway Debug Script - Para diagnosticar problemas
"""

import os
import sys
import subprocess
import time
import signal

def signal_handler(signum, frame):
    print(f"Received signal {signum}")
    sys.exit(0)

# Manejar señales
signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

def main():
    """Debug y inicio para Railway"""
    
    print("=== RAILWAY DEBUG START ===")
    print(f"Python version: {sys.version}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Environment variables:")
    for key in ['PORT', 'HOST', 'PYTHONPATH', 'PATH']:
        print(f"  {key}: {os.environ.get(key, 'NOT SET')}")
    
    # Configurar entorno
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    os.environ['PYTHONPATH'] = '/app:/app/mi_app_estudio'
    
    print(f"\nTrying to start on {host}:{port}")
    
    # Test básico de Python
    print("\n=== PYTHON PATHS ===")
    for path in sys.path:
        print(f"  {path}")
    
    # Test import
    print("\n=== IMPORT TEST ===")
    try:
        sys.path.insert(0, '/app')
        sys.path.insert(0, '/app/mi_app_estudio')
        
        # Test import paso a paso
        print("Importing reflex...")
        import reflex as rx
        print("✓ Reflex imported")
        
        print("Importing mi_app_estudio...")
        import mi_app_estudio.mi_app_estudio
        print("✓ App imported")
        
    except Exception as e:
        print(f"✗ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    # Cambiar directorio
    if os.path.exists('/app/mi_app_estudio'):
        os.chdir('/app/mi_app_estudio')
        print(f"\nChanged to: {os.getcwd()}")
    
    # Verificar archivos
    print(f"\n=== FILES CHECK ===")
    important_files = ['mi_app_estudio.py', 'rxconfig.py']
    for file in important_files:
        if os.path.exists(file):
            print(f"✓ {file} exists")
        else:
            print(f"✗ {file} missing")
    
    # Comando de inicio
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port,
        '--env', 'dev'
    ]
    
    print(f"\n=== STARTING APP ===")
    print(f"Command: {' '.join(cmd)}")
    
    # Ejecutar con output en tiempo real
    try:
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Leer output línea por línea
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip())
        
        return process.poll()
        
    except Exception as e:
        print(f"Error starting app: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        print(f"Process exited with code: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
