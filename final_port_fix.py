#!/usr/bin/env python3
"""
Script definitivo para resolver el problema de puertos en Reflex
"""
import os
import sys
import subprocess
import socket
import time
import signal

def kill_all_on_port(port):
    """Matar todos los procesos en un puerto específico"""
    print(f"🔪 Matando procesos en puerto {port}...")
    
    # Método con fuser (más efectivo)
    try:
        subprocess.run(['fuser', '-k', f'{port}/tcp'], 
                      stdout=subprocess.DEVNULL, 
                      stderr=subprocess.DEVNULL)
        time.sleep(1)
    except:
        pass
    
    # Método con netstat como respaldo
    try:
        result = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True)
        if result.returncode == 0:
            for line in result.stdout.split('\n'):
                if f':{port}' in line and 'LISTEN' in line:
                    parts = line.split()
                    if len(parts) > 6:
                        pid_info = parts[-1]
                        if '/' in pid_info:
                            pid = pid_info.split('/')[0]
                            if pid.isdigit():
                                try:
                                    os.kill(int(pid), signal.SIGKILL)
                                    print(f"  ✅ Proceso {pid} terminado")
                                except:
                                    pass
    except:
        pass

def is_port_free(port):
    """Verificar si un puerto está libre"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except:
        return False

def find_free_port_pair():
    """Encontrar un par de puertos libres para backend y frontend"""
    backend_candidates = [8080, 8081, 8082, 8083, 8084, 8000, 8001]
    frontend_candidates = [3000, 3001, 3002, 3003, 3004]
    
    for backend_port in backend_candidates:
        if is_port_free(backend_port):
            for frontend_port in frontend_candidates:
                if is_port_free(frontend_port):
                    return backend_port, frontend_port
    
    # Si no encontramos puertos libres, forzar limpieza
    print("⚠️  No se encontraron puertos libres, forzando limpieza...")
    for port in backend_candidates + frontend_candidates:
        kill_all_on_port(port)
    
    time.sleep(3)
    
    # Intentar de nuevo
    for backend_port in backend_candidates:
        if is_port_free(backend_port):
            for frontend_port in frontend_candidates:
                if is_port_free(frontend_port):
                    return backend_port, frontend_port
    
    raise Exception("No se pudieron liberar puertos")

def main():
    """Función principal"""
    print("🚀 Iniciando Reflex con resolución automática de puertos...")
    
    try:
        # Encontrar puertos libres
        backend_port, frontend_port = find_free_port_pair()
        
        print(f"✅ Backend port: {backend_port}")
        print(f"✅ Frontend port: {frontend_port}")
        
        # Configurar variables de entorno
        os.environ['PORT'] = str(backend_port)
        os.environ['BACKEND_PORT'] = str(backend_port)
        os.environ['FRONTEND_PORT'] = str(frontend_port)
        
        # Preparar comando
        cmd = [
            sys.executable, '-m', 'reflex', 'run',
            '--backend-port', str(backend_port),
            '--frontend-port', str(frontend_port),
            '--backend-host', '0.0.0.0'
        ]
        
        print(f"🎯 Ejecutando: {' '.join(cmd)}")
        print(f"📱 La aplicación estará disponible en:")
        print(f"   - Backend:  http://localhost:{backend_port}")
        print(f"   - Frontend: http://localhost:{frontend_port}")
        print()
        
        # Ejecutar Reflex
        subprocess.run(cmd)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("🔄 Intentando con configuración por defecto...")
        
        # Limpiar puerto 8080 como último recurso
        kill_all_on_port(8080)
        time.sleep(2)
        
        subprocess.run([sys.executable, '-m', 'reflex', 'run'])

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n🛑 Aplicación detenida por el usuario")
        # Limpiar puertos al salir
        for port in [8080, 8081, 8082, 3000, 3001, 3002]:
            kill_all_on_port(port)
