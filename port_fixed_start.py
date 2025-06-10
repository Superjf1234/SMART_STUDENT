#!/usr/bin/env python3
"""
Railway Port-Fixed Deployment
Soluciona el problema de "service unavailable" configurando el puerto correcto
"""

import os
import sys
import subprocess

def main():
    print("=== RAILWAY PORT-FIXED DEPLOYMENT ===")
    
    # Obtener el puerto de Railway (puede cambiar dinámicamente)
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"Railway PORT detected: {port}")
    print(f"Host: {host}")
    
    # Configurar PYTHONPATH
    current_dir = os.getcwd()
    app_dir = os.path.join(current_dir, 'mi_app_estudio')
    python_path = f"{current_dir}:{app_dir}"
    os.environ['PYTHONPATH'] = python_path
    
    # Variables de entorno optimizadas
    os.environ['NODE_OPTIONS'] = '--max-old-space-size=512'
    os.environ['NEXT_TELEMETRY_DISABLED'] = '1'
    
    print(f"PYTHONPATH: {python_path}")
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
    
    print("Starting Reflex with dynamic port configuration...")
    
    # Comando con puerto dinámico - SIN --frontend-port
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'dev',  # Usar dev para evitar build pesado
        '--backend-host', host,
        '--backend-port', port
        # NO incluir --frontend-port para que use el mismo puerto
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
                # Verificar que el servidor esté escuchando en el puerto correcto
                if f':{port}' in output or 'App running' in output:
                    print(f"✅ Server listening on port {port}")
        
        return_code = process.poll()
        print(f"Process ended with code: {return_code}")
        return return_code if return_code is not None else 0
        
    except Exception as e:
        print(f"Error executing command: {e}")
        
        # Fallback: Comando más simple
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
