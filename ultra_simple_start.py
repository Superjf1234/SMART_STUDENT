#!/usr/bin/env python3
"""
Railway Deployment Script - Ultra Simple Version
Versión ultra-simplificada para Railway
"""

import os
import sys
import subprocess

def main():
    # Configurar variables de entorno
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"Starting SMART_STUDENT on {host}:{port}")
    print(f"Working directory: {os.getcwd()}")
    
    # Configurar PYTHONPATH para las importaciones
    current_dir = os.getcwd()
    app_dir = os.path.join(current_dir, 'mi_app_estudio')
    
    # Configurar PYTHONPATH
    python_path = f"{current_dir}:{app_dir}"
    os.environ['PYTHONPATH'] = python_path
    
    print(f"PYTHONPATH set to: {python_path}")
    
    # Ir al directorio de la aplicación
    if os.path.exists('mi_app_estudio'):
        os.chdir('mi_app_estudio')
        print(f"Changed to: {os.getcwd()}")
    else:
        print("ERROR: mi_app_estudio directory not found")
        return 1
    
    # Verificar archivos críticos
    if not os.path.exists('mi_app_estudio.py'):
        print("ERROR: Main app file not found")
        return 1
    
    # Comando de inicio simplificado para Railway
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port,
        '--frontend-port', port
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    # Ejecutar comando
    try:
        # Usar subprocess.run para mejor manejo
        result = subprocess.run(cmd, env=os.environ.copy())
        return result.returncode
    except Exception as e:
        print(f"Error executing command: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
