#!/usr/bin/env python3
"""
Railway Production Start - Backend Only Mode
Para servir tanto API como archivos estáticos desde un solo puerto
"""

import os
import sys
import subprocess
import time

def main():
    """Inicio para Railway - solo backend que sirve todo"""
    
    # Configuración
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"=== RAILWAY BACKEND-ONLY START ===")
    print(f"PORT: {port}")
    print(f"HOST: {host}")
    
    # Configurar PYTHONPATH
    os.environ['PYTHONPATH'] = '/app:/app/mi_app_estudio'
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
    
    # Variables críticas para Reflex
    os.environ['REFLEX_BACKEND_HOST'] = host
    os.environ['REFLEX_BACKEND_PORT'] = port
    
    # Cambiar directorio
    os.chdir('/app/mi_app_estudio')
    print(f"Working directory: {os.getcwd()}")
    
    # Test de importación
    try:
        sys.path.insert(0, '/app')
        sys.path.insert(0, '/app/mi_app_estudio')
        import mi_app_estudio.mi_app_estudio
        print("✓ App import successful")
    except Exception as e:
        print(f"✗ App import failed: {e}")
        return 1
    
    print("=== Starting Reflex Backend Only ===")
    
    # ESTRATEGIA: Usar reflex run --backend-only 
    # Esto hace que el backend sirva tanto la API como los archivos estáticos
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-only',
        '--backend-host', host,
        '--backend-port', port,
        '--env', 'prod'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Ejecutar el proceso
        process = subprocess.Popen(cmd, 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.STDOUT,
                                 universal_newlines=True,
                                 bufsize=1)
        
        print(f"Process started with PID: {process.pid}")
        
        # Mostrar output en tiempo real
        for line in process.stdout:
            print(line.rstrip())
            
        # Esperar a que termine
        return_code = process.wait()
        print(f"Process exited with code: {return_code}")
        return return_code
        
    except KeyboardInterrupt:
        print("Received interrupt signal")
        if 'process' in locals():
            process.terminate()
        return 0
    except Exception as e:
        print(f"Error starting app: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
