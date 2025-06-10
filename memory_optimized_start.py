#!/usr/bin/env python3
"""
Railway Deployment Script - Memory Optimized
Versión optimizada para manejar limitaciones de memoria de Railway
"""

import os
import sys
import subprocess

def main():
    print("=== RAILWAY DEPLOYMENT - MEMORY OPTIMIZED ===")
    
    # Configurar variables de entorno para optimizar memoria
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    # Variables de optimización de memoria para Next.js y Node.js
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=512'
    os.environ['NEXT_TELEMETRY_DISABLED'] = '1'
    os.environ['NODE_ENV'] = 'production'
    
    # Configurar PYTHONPATH
    current_dir = os.getcwd()
    app_dir = os.path.join(current_dir, 'mi_app_estudio')
    python_path = f"{current_dir}:{app_dir}"
    os.environ['PYTHONPATH'] = python_path
    
    print(f"Starting SMART_STUDENT on {host}:{port}")
    print(f"NODE_OPTIONS: {os.environ.get('NODE_OPTIONS')}")
    print(f"PYTHONPATH: {python_path}")
    
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
    
    print("Files OK, starting Reflex...")
    
    # Comando de inicio con configuración de desarrollo (más estable)
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'dev',  # Cambiar a dev para evitar el build pesado
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    # Ejecutar comando
    try:
        result = subprocess.run(cmd, env=os.environ.copy())
        return result.returncode
    except Exception as e:
        print(f"Error executing command: {e}")
        
        # Fallback: Intentar con menos optimizaciones
        print("Trying fallback command...")
        fallback_cmd = [
            sys.executable, '-m', 'reflex', 'run',
            '--backend-host', host,
            '--backend-port', port
        ]
        
        try:
            result = subprocess.run(fallback_cmd, env=os.environ.copy())
            return result.returncode
        except Exception as e2:
            print(f"Fallback also failed: {e2}")
            return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
