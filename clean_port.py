#!/usr/bin/env python3
"""
Script para limpiar puertos en uso antes de ejecutar Reflex
"""
import os
import sys
import subprocess
import signal
import time

def clean_port(port):
    """Limpiar cualquier proceso que esté usando el puerto especificado"""
    print(f"Limpiando puerto {port}...")
    
    try:
        # Intentar con lsof primero
        result = subprocess.run(
            ['lsof', '-t', f'-i:{port}'],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0 and result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                if pid:
                    print(f"Terminando proceso {pid} que usa puerto {port}")
                    try:
                        os.kill(int(pid), signal.SIGTERM)
                        time.sleep(1)  # Dar tiempo para terminar graciosamente
                        # Verificar si el proceso aún está ejecutándose
                        try:
                            os.kill(int(pid), 0)  # Solo verificar si existe
                            os.kill(int(pid), signal.SIGKILL)  # Forzar si es necesario
                        except ProcessLookupError:
                            pass  # El proceso ya terminó
                    except (ProcessLookupError, ValueError):
                        pass  # El proceso ya terminó
                        
    except (subprocess.SubprocessError, FileNotFoundError):
        # Si lsof no está disponible, intentar con netstat
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
                        # Extraer PID de la línea de netstat
                        parts = line.split()
                        if len(parts) > 6:
                            pid_info = parts[-1]
                            if '/' in pid_info:
                                pid = pid_info.split('/')[0]
                                if pid.isdigit():
                                    print(f"Terminando proceso {pid} que usa puerto {port}")
                                    try:
                                        os.kill(int(pid), signal.SIGTERM)
                                        time.sleep(1)
                                        try:
                                            os.kill(int(pid), 0)
                                            os.kill(int(pid), signal.SIGKILL)
                                        except ProcessLookupError:
                                            pass
                                    except (ProcessLookupError, ValueError):
                                        pass
        except (subprocess.SubprocessError, FileNotFoundError):
            print(f"No se pudo verificar/limpiar el puerto {port}")
    
    # Esperar un poco para asegurar que el puerto se libere
    time.sleep(2)
    print(f"Puerto {port} limpiado")

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    clean_port(port)
