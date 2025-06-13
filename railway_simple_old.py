#!/usr/bin/env python3
"""
Railway Production Start - Ultra Simplified
"""

import os
import sys
import subprocess
import time

def main():
    """Inicio ultra-simplificado para Railway"""
    
    # Configuración básica
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"=== RAILWAY ULTRA SIMPLE START ===")
    print(f"PORT: {port}")
    print(f"HOST: {host}")
    
    # Configurar PYTHONPATH
    os.environ['PYTHONPATH'] = '/app:/app/mi_app_estudio'
    print(f"PYTHONPATH: {os.environ['PYTHONPATH']}")
    
    # Test import
    try:
        sys.path.insert(0, '/app')
        sys.path.insert(0, '/app/mi_app_estudio')
        import mi_app_estudio.mi_app_estudio
        print("✓ App import successful")
    except Exception as e:
        print(f"✗ App import failed: {e}")
        return 1
    
    # Cambiar directorio
    os.chdir('/app/mi_app_estudio')
    print(f"Working directory: {os.getcwd()}")
    
    # Comando ultra-simple
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    # Ejecutar sin esperar
    try:
        result = subprocess.run(cmd, timeout=300)  # 5 minutos max
        return result.returncode
    except subprocess.TimeoutExpired:
        print("Process timeout - but this might be normal for a web app")
        return 0
    except Exception as e:
        print(f"Error: {e}")
        return 1

if __name__ == '__main__':
    sys.exit(main())
