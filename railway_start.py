#!/usr/bin/env python3
"""
Railway Start Script - Optimizado para Railway deployment
"""

import os
import sys
import subprocess
import time

def setup_environment():
    """Configurar variables de entorno necesarias"""
    port = os.environ.get('PORT', '8080')
    os.environ.setdefault('HOST', '0.0.0.0')
    os.environ.setdefault('PORT', port)
    os.environ.setdefault('PYTHONPATH', '/app:/app/mi_app_estudio')
    os.environ.setdefault('REFLEX_ENV', 'dev')  # Usar dev en Railway
    os.environ.setdefault('NODE_OPTIONS', '--max-old-space-size=256')
    
    print(f"=== RAILWAY DEPLOYMENT START ===")
    print(f"PORT: {port}")
    print(f"HOST: 0.0.0.0")
    print(f"PYTHONPATH: {os.environ.get('PYTHONPATH')}")
    print(f"REFLEX_ENV: {os.environ.get('REFLEX_ENV')}")
    
    return port

def test_app_import():
    """Probar si la aplicación se puede importar"""
    try:
        import mi_app_estudio.mi_app_estudio
        print("✓ App import successful")
        return True
    except Exception as e:
        print(f"✗ App import failed: {e}")
        return False

def start_reflex_app(port):
    """Iniciar la aplicación Reflex"""
    # Cambiar al directorio de la aplicación
    if os.path.exists('/app/mi_app_estudio'):
        os.chdir('/app/mi_app_estudio')
        print(f"Working directory: {os.getcwd()}")
    
    # Comando optimizado para Railway
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', '0.0.0.0',
        '--backend-port', str(port),
        '--env', 'dev'  # Usar dev para evitar problemas de build
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    try:
        # Ejecutar con output en tiempo real
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            env=os.environ.copy()
        )
        
        # Imprimir output en tiempo real
        for line in process.stdout:
            print(line.rstrip())
            
        return process.wait()
        
    except Exception as e:
        print(f"Error starting app: {e}")
        return 1

def main():
    """Función principal"""
    try:
        # Configurar entorno
        port = setup_environment()
        
        # Probar importación
        if not test_app_import():
            print("ERROR: No se puede importar la aplicación")
            return 1
        
        # Iniciar aplicación
        return start_reflex_app(port)
        
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
