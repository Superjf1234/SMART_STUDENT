#!/usr/bin/env python3
"""
Railway Production Start - Simplified approach
"""

import os
import sys
import subprocess
import time

def main():
    """Inicio simplificado para Railway"""
    
    # Configuración
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"=== RAILWAY SIMPLIFIED START ===")
    print(f"PORT: {port}")
    print(f"HOST: {host}")
    
    # Configurar entorno
    os.environ['PYTHONPATH'] = '/app:/app/mi_app_estudio'
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
    
    print("=== Starting Reflex App ===")
    
    # Comando simplificado - dejar que Reflex maneje la configuración
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port,
        '--env', 'prod'
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    try:
        # Usar exec para reemplazar el proceso actual
        # Esto es importante para Railway
        os.execvp(sys.executable, cmd)
        
    except Exception as e:
        print(f"Error starting app: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
