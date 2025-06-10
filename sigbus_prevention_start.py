#!/usr/bin/env python3
"""
Railway Deployment Script - SIGBUS ERROR PREVENTION
Previene completamente el error SIGBUS evitando el build de producción
"""

import os
import sys
import subprocess

def main():
    print("=== RAILWAY DEPLOYMENT - SIGBUS PREVENTION ===")
    
    # Configurar variables básicas
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"PORT: {port}")
    print(f"HOST: {host}")
    
    # Configurar PYTHONPATH
    current_dir = os.getcwd()
    app_dir = os.path.join(current_dir, 'mi_app_estudio')
    python_path = f"{current_dir}:{app_dir}"
    os.environ['PYTHONPATH'] = python_path
    
    # FORZAR variables de entorno que previenen el build pesado
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=256'  # Reducir aún más
    os.environ['NEXT_TELEMETRY_DISABLED'] = '1'
    os.environ['NODE_ENV'] = 'development'  # FORZAR development
    os.environ['REFLEX_ENV'] = 'development'  # FORZAR development en Reflex
    
    print(f"PYTHONPATH: {python_path}")
    print(f"NODE_OPTIONS: {os.environ['NODE_OPTIONS']}")
    print(f"NODE_ENV: {os.environ['NODE_ENV']}")
    print(f"REFLEX_ENV: {os.environ['REFLEX_ENV']}")
    
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
    
    print("Starting Reflex in DEVELOPMENT mode (no production build)...")
    
    # COMANDO SIMPLE SIN ARGUMENTOS DE PRODUCCIÓN
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
        # NO usar --env, NO usar --frontend-port
        # Esto fuerza el modo de desarrollo por defecto
    ]
    
    print(f"FINAL COMMAND: {' '.join(cmd)}")
    
    # Ejecutar comando con el entorno forzado
    try:
        # Usar os.execvpe para reemplazar completamente el proceso
        # Esto evita cualquier interferencia
        print("Executing command via os.execvpe...")
        os.execvpe(cmd[0], cmd, os.environ)
        
    except Exception as e:
        print(f"Error with execvpe: {e}")
        print("Trying with subprocess...")
        
        # Fallback: subprocess
        try:
            result = subprocess.run(cmd, env=os.environ.copy())
            return result.returncode
        except Exception as e2:
            print(f"Subprocess also failed: {e2}")
            return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
