#!/usr/bin/env python3
"""
Railway Deployment Script - Debug Version
Versión con logging extensivo para diagnosticar problemas de healthcheck
"""

import os
import sys
import subprocess
import time
import signal

def log(message):
    """Log con timestamp"""
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}", flush=True)

def check_port_availability(port):
    """Verificar si el puerto está disponible"""
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', int(port)))
        sock.close()
        return result == 0
    except Exception as e:
        log(f"Error checking port {port}: {e}")
        return False

def handle_signal(signum, frame):
    """Manejar señales del sistema"""
    log(f"Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

def main():
    # Configurar manejador de señales
    signal.signal(signal.SIGTERM, handle_signal)
    signal.signal(signal.SIGINT, handle_signal)
    
    log("=== RAILWAY DEPLOYMENT DEBUG VERSION ===")
    
    # Variables de entorno
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    log(f"Port: {port}")
    log(f"Host: {host}")
    log(f"Working directory: {os.getcwd()}")
    log(f"Python version: {sys.version}")
    log(f"Python executable: {sys.executable}")
    
    # Mostrar variables de entorno relevantes
    env_vars = ['PYTHONPATH', 'PATH', 'PORT', 'REFLEX_ENV', 'NODE_OPTIONS']
    for var in env_vars:
        value = os.environ.get(var, 'NOT SET')
        log(f"ENV {var}: {value}")
    
    # Verificar estructura de archivos
    log("=== CHECKING FILE STRUCTURE ===")
    required_files = [
        'mi_app_estudio/mi_app_estudio.py',
        'backend/__init__.py',
        'requirements.txt',
        'rxconfig.py'
    ]
    
    all_files_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            log(f"✓ {file_path} ({size} bytes)")
        else:
            log(f"✗ {file_path} NOT FOUND")
            all_files_exist = False
    
    if not all_files_exist:
        log("CRITICAL: Missing required files!")
        return 1
    
    # Configurar PYTHONPATH
    current_dir = os.getcwd()
    app_dir = os.path.join(current_dir, 'mi_app_estudio')
    python_path = f"{current_dir}:{app_dir}"
    os.environ['PYTHONPATH'] = python_path
    
    log(f"Set PYTHONPATH to: {python_path}")
    
    # Verificar que podemos importar Reflex
    log("=== CHECKING IMPORTS ===")
    try:
        result = subprocess.run([
            sys.executable, '-c', 'import reflex; print(f"Reflex version: {reflex.__version__}")'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            log(f"✓ Reflex import OK: {result.stdout.strip()}")
        else:
            log(f"✗ Reflex import failed: {result.stderr}")
            return 1
    except Exception as e:
        log(f"✗ Error testing Reflex import: {e}")
        return 1
    
    # Cambiar al directorio de la aplicación
    log("=== CHANGING TO APP DIRECTORY ===")
    try:
        os.chdir('mi_app_estudio')
        log(f"Changed to: {os.getcwd()}")
    except Exception as e:
        log(f"Error changing directory: {e}")
        return 1
    
    # Verificar que podemos importar la aplicación
    log("=== CHECKING APP IMPORTS ===")
    try:
        # Importar desde el directorio padre
        sys.path.insert(0, '..')
        result = subprocess.run([
            sys.executable, '-c', 
            'import sys; sys.path.insert(0, ".."); from backend import db_logic; print("Backend import OK")'
        ], capture_output=True, text=True, timeout=10, env=os.environ.copy())
        
        if result.returncode == 0:
            log(f"✓ Backend import OK: {result.stdout.strip()}")
        else:
            log(f"⚠ Backend import warning: {result.stderr}")
            # Continuar de todos modos ya que el backend puede usar mocks
    except Exception as e:
        log(f"⚠ Backend import test error: {e}")
    
    # Preparar comando de Reflex
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--env', 'prod',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    log(f"=== STARTING REFLEX APPLICATION ===")
    log(f"Command: {' '.join(cmd)}")
    
    # Inicializar Reflex si es necesario
    if not os.path.exists('.web'):
        log("Initializing Reflex...")
        try:
            result = subprocess.run([
                sys.executable, '-m', 'reflex', 'init'
            ], timeout=60, env=os.environ.copy())
            if result.returncode == 0:
                log("✓ Reflex init completed")
            else:
                log("⚠ Reflex init had issues, continuing...")
        except Exception as e:
            log(f"⚠ Reflex init error: {e}, continuing...")
    
    # Ejecutar la aplicación
    try:
        log("Starting Reflex application...")
        
        # Usar subprocess.Popen para poder ver el output en tiempo real
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1,
            env=os.environ.copy()
        )
        
        # Monitorear el output
        start_time = time.time()
        server_started = False
        
        for line in iter(process.stdout.readline, ''):
            if line:
                log(f"REFLEX: {line.rstrip()}")
                
                # Buscar indicadores de que el servidor ha iniciado
                if any(indicator in line.lower() for indicator in [
                    'app running', 'server started', 'listening on', 
                    'started server', 'uvicorn running'
                ]):
                    server_started = True
                    log("✓ SERVER APPEARS TO BE RUNNING!")
                
                # Verificar si el puerto está disponible después de un tiempo
                if time.time() - start_time > 30 and not server_started:
                    if check_port_availability(int(port)):
                        log(f"✓ Port {port} is now available!")
                        server_started = True
            
            # Verificar si el proceso sigue corriendo
            if process.poll() is not None:
                break
        
        # Obtener el código de salida
        return_code = process.poll()
        log(f"Process ended with return code: {return_code}")
        
        if return_code != 0:
            log("✗ Application failed to start properly")
            return return_code
        else:
            log("✓ Application appears to have ended normally")
            return 0
            
    except KeyboardInterrupt:
        log("Received interrupt signal")
        if 'process' in locals():
            process.terminate()
        return 0
    except Exception as e:
        log(f"✗ Error starting application: {e}")
        return 1

if __name__ == '__main__':
    try:
        exit_code = main()
        log(f"Script exiting with code: {exit_code}")
        sys.exit(exit_code)
    except Exception as e:
        log(f"CRITICAL ERROR in main: {e}")
        sys.exit(1)
