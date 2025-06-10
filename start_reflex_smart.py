#!/usr/bin/env python3
"""
Script para encontrar un puerto libre y ejecutar Reflex
"""
import socket
import subprocess
import sys
import os
import time

def find_free_port(start_port=8080, max_attempts=50):
    """Encontrar un puerto libre comenzando desde start_port"""
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('localhost', port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No se pudo encontrar un puerto libre entre {start_port} y {start_port + max_attempts}")

def kill_port_processes():
    """Matar procesos que puedan estar usando puertos comunes"""
    common_ports = [8080, 8081, 3000, 3001]
    
    for port in common_ports:
        try:
            result = subprocess.run(
                ['netstat', '-tulpn'],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if f':{port}' in line and 'LISTEN' in line:
                        parts = line.split()
                        if len(parts) > 6:
                            pid_info = parts[-1]
                            if '/' in pid_info:
                                pid = pid_info.split('/')[0]
                                if pid.isdigit():
                                    print(f"🔪 Terminando proceso {pid} en puerto {port}")
                                    try:
                                        os.kill(int(pid), 9)  # SIGKILL directo
                                    except (ProcessLookupError, ValueError):
                                        pass
        except Exception as e:
            print(f"Error limpiando puerto {port}: {e}")

def start_reflex_with_free_ports():
    """Iniciar Reflex con puertos libres automáticamente"""
    print("🧹 Limpiando puertos existentes...")
    kill_port_processes()
    
    # Esperar un poco para que los puertos se liberen
    time.sleep(3)
    
    print("🔍 Buscando puertos libres...")
    try:
        backend_port = find_free_port(8080)
        frontend_port = find_free_port(3000)
        
        print(f"✅ Puerto backend: {backend_port}")
        print(f"✅ Puerto frontend: {frontend_port}")
        
        # Configurar variables de entorno
        os.environ['PORT'] = str(backend_port)
        os.environ['BACKEND_PORT'] = str(backend_port)
        os.environ['FRONTEND_PORT'] = str(frontend_port)
        
        print(f"🚀 Iniciando Reflex...")
        print(f"   Backend: http://localhost:{backend_port}")
        print(f"   Frontend: http://localhost:{frontend_port}")
        
        # Ejecutar Reflex
        cmd = [
            sys.executable, '-m', 'reflex', 'run',
            '--backend-port', str(backend_port),
            '--frontend-port', str(frontend_port)
        ]
        
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Fallback: intentar solo con reflex run
        print("🔄 Intentando con configuración por defecto...")
        subprocess.run([sys.executable, '-m', 'reflex', 'run'])

if __name__ == "__main__":
    start_reflex_with_free_ports()
