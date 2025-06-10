#!/usr/bin/env python3
"""
Script de inicio mejorado para Reflex que limpia puertos en uso
"""
import os
import sys
import subprocess
import signal
import time

def clean_port(port):
    """Limpiar cualquier proceso que esté usando el puerto especificado"""
    print(f"🧹 Limpiando puerto {port}...")
    
    try:
        # Intentar con netstat
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
                                print(f"🔪 Terminando proceso {pid} que usa puerto {port}")
                                try:
                                    os.kill(int(pid), signal.SIGTERM)
                                    time.sleep(1)
                                    # Verificar si el proceso aún está ejecutándose
                                    try:
                                        os.kill(int(pid), 0)
                                        os.kill(int(pid), signal.SIGKILL)
                                        print(f"  ⚡ Proceso {pid} terminado por la fuerza")
                                    except ProcessLookupError:
                                        print(f"  ✅ Proceso {pid} terminado graciosamente")
                                except (ProcessLookupError, ValueError):
                                    print(f"  ❓ Proceso {pid} ya había terminado")
                    
    except (subprocess.SubprocessError, FileNotFoundError):
        print(f"❌ No se pudo verificar/limpiar el puerto {port}")
    
    # Esperar un poco para asegurar que el puerto se libere
    time.sleep(2)
    print(f"✅ Puerto {port} limpiado")

def start_reflex():
    """Iniciar Reflex con puerto limpio"""
    port = int(os.environ.get('PORT', '8080'))
    
    print(f"🚀 Iniciando Reflex en puerto {port}...")
    
    # Limpiar puerto antes de iniciar
    clean_port(port)
    
    # Ejecutar Reflex
    try:
        subprocess.run([sys.executable, '-m', 'reflex', 'run'])
    except KeyboardInterrupt:
        print("\n🛑 Deteniendo Reflex...")
        clean_port(port)
        print("👋 Reflex detenido")

if __name__ == "__main__":
    start_reflex()
