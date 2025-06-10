#!/usr/bin/env python3
"""
Script definitivo para Railway - SMART_STUDENT
Versión final con argumentos corregidos.
"""

import os
import sys
import subprocess
import time

def main():
    print("=== SMART_STUDENT Railway Deploy v2.0 ===")
    
    # Variables de entorno
    port = os.environ.get('PORT', '8080')
    
    print(f"Puerto configurado: {port}")
    
    # Verificar que estamos en el directorio correcto
    if not os.path.exists('mi_app_estudio'):
        print("ERROR: Directorio mi_app_estudio no encontrado")
        sys.exit(1)
    
    # Comando corregido para Reflex (SIN --frontend-host)
    cmd = [
        'python', '-m', 'reflex', 'run',
        '--env', 'prod',
        '--backend-host', '0.0.0.0',
        '--backend-port', port
    ]
    
    print(f"Ejecutando: {' '.join(cmd)}")
    
    try:
        # Ejecutar Reflex
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"ERROR: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
