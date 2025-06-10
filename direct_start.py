#!/usr/bin/env python3
"""
Railway Direct Command - Ultra Simple
Comando directo sin complicaciones
"""

import os
import sys
import subprocess

def main():
    print("=== RAILWAY DIRECT COMMAND ===")
    
    # Variables básicas
    port = os.environ.get('PORT', '8080')
    host = '0.0.0.0'
    
    print(f"Port: {port}, Host: {host}")
    
    # Configurar PYTHONPATH básico
    current_dir = os.getcwd()
    os.environ['PYTHONPATH'] = f"{current_dir}:{current_dir}/mi_app_estudio"
    
    # Ir al directorio de la aplicación
    os.chdir('mi_app_estudio')
    print(f"Working in: {os.getcwd()}")
    
    # Comando ultra-simple
    cmd = [
        sys.executable, '-m', 'reflex', 'run',
        '--backend-host', host,
        '--backend-port', port
    ]
    
    print(f"Command: {' '.join(cmd)}")
    
    # Ejecutar directamente
    os.execvpe(cmd[0], cmd, os.environ)

if __name__ == '__main__':
    main()
