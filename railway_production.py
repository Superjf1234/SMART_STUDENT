#!/usr/bin/env python3
"""
Railway Production Start - Optimized for single port deployment
"""

import os
import sys
import subprocess
import time

def main():
    """Inicio optimizado para Railway - un solo puerto"""
    
    # Configuración
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"=== RAILWAY PRODUCTION START ===")
    print(f"PORT: {port}")
    print(f"HOST: {host}")
    
    # Configurar PYTHONPATH
    os.environ['PYTHONPATH'] = '/app:/app/mi_app_estudio'
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
    
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
    
    # Variables de entorno para Reflex
    os.environ['REFLEX_BACKEND_HOST'] = host
    os.environ['REFLEX_BACKEND_PORT'] = port
    os.environ['REFLEX_FRONTEND_PORT'] = port
    
    print("=== Starting Reflex App ===")
    
    # Para Railway: usar reflex run con configuración de producción
    # --backend-only para servir tanto frontend como backend desde el mismo puerto
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port,
        '--frontend-port', port,
        '--env', 'prod'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # En Railway, necesitamos que el proceso se mantenga corriendo
        process = subprocess.Popen(cmd)
        print(f"Process started with PID: {process.pid}")
        
        # Mantener el proceso corriendo
        process.wait()
        return process.returncode
        
    except KeyboardInterrupt:
        print("Received interrupt signal")
        return 0
    except Exception as e:
        print(f"Error starting app: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
