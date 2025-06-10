#!/usr/bin/env python3
"""
Script de limpieza agresiva de puertos
"""
import subprocess
import os
import signal
import time

def aggressive_port_cleanup():
    """Limpieza agresiva de todos los puertos problemáticos"""
    ports_to_clean = [8080, 8081, 3000, 3001, 3002, 8000, 8001]
    
    print("🧹 Iniciando limpieza agresiva de puertos...")
    
    # Método 1: Usando netstat
    try:
        result = subprocess.run(['netstat', '-tulpn'], capture_output=True, text=True)
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                for port in ports_to_clean:
                    if f':{port}' in line and 'LISTEN' in line:
                        parts = line.split()
                        if len(parts) > 6:
                            pid_info = parts[-1]
                            if '/' in pid_info:
                                pid = pid_info.split('/')[0]
                                if pid.isdigit():
                                    print(f"🔪 Matando proceso {pid} en puerto {port}")
                                    try:
                                        os.kill(int(pid), signal.SIGKILL)
                                    except:
                                        pass
    except:
        pass
    
    # Método 2: Buscar procesos específicos
    problematic_processes = ['python', 'node', 'uvicorn', 'reflex']
    
    for proc_name in problematic_processes:
        try:
            result = subprocess.run(['pgrep', '-f', proc_name], capture_output=True, text=True)
            if result.returncode == 0:
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    if pid and pid.isdigit():
                        try:
                            # Verificar si el proceso está usando uno de nuestros puertos
                            lsof_result = subprocess.run(['lsof', '-p', pid], capture_output=True, text=True)
                            if any(f':{port}' in lsof_result.stdout for port in ports_to_clean):
                                print(f"🎯 Matando proceso {proc_name} ({pid}) que usa puerto problemático")
                                os.kill(int(pid), signal.SIGKILL)
                        except:
                            pass
        except:
            pass
    
    # Método 3: Forzar limpieza con fuser (si está disponible)
    for port in ports_to_clean:
        try:
            subprocess.run(['fuser', '-k', f'{port}/tcp'], capture_output=True)
        except:
            pass
    
    print("✅ Limpieza agresiva completada")
    time.sleep(2)

if __name__ == "__main__":
    aggressive_port_cleanup()
