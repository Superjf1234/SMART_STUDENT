#!/usr/bin/env python3
"""
Railway Development Mode Deployment
Usa modo desarrollo para evitar el build pesado de producción
"""

import os
import sys
import subprocess

def main():
    print("=== RAILWAY DEVELOPMENT MODE DEPLOYMENT ===")
    
    # Configurar variables básicas
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    # Configurar PYTHONPATH
    current_dir = os.getcwd()
    app_dir = os.path.join(current_dir, 'mi_app_estudio')
    python_path = f"{current_dir}:{app_dir}"
    os.environ['PYTHONPATH'] = python_path
    
    # Variables de entorno optimizadas
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=512'
    os.environ['NEXT_TELEMETRY_DISABLED'] = '1'
    
    print(f"Starting SMART_STUDENT on {host}:{port}")
    print(f"Working directory: {os.getcwd()}")
    
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
    
    print("Starting Reflex in development mode...")
    
    # Usar modo desarrollo para evitar el build pesado
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"Executing: {' '.join(cmd)}")
    
    # Ejecutar comando
    try:
        process = subprocess.Popen(
            cmd, 
            env=os.environ.copy(),
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        # Mostrar output en tiempo real
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.rstrip())
                # Si vemos que el servidor está listo, es una buena señal
                if 'App running' in output or 'Started server' in output:
                    print("✅ Server started successfully!")
        
        return_code = process.poll()
        print(f"Process ended with code: {return_code}")
        return return_code if return_code is not None else 0
        
    except Exception as e:
        print(f"Error executing command: {e}")
        return 1

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
